import math

import torch
import torch.nn as nn

from .rational_quadratic_spline import unconstrained_rational_quadratic_spline


class StackedLinear(nn.Module):
    """
    Efficient implementation of linear layers for ensembles of networks
    """
    def __init__(self, in_features: int, out_features: int, channels: int):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.channels = channels
        self.weight = nn.Parameter(torch.empty((channels, out_features, in_features)))
        self.bias = nn.Parameter(torch.empty((channels, out_features)))
        self.reset_parameters()

    def reset_parameters(self):
        for i in range(self.channels):
            torch.nn.init.kaiming_uniform_(self.weight[i], a=math.sqrt(5))
            fan_in, _ = torch.nn.init._calculate_fan_in_and_fan_out(self.weight[i])
            bound = 1 / math.sqrt(fan_in) if fan_in > 0 else 0
            torch.nn.init.uniform_(self.bias[i], -bound, bound)

    def forward(self, x: torch.Tensor, selection: slice = slice(None)):
        return torch.baddbmm(
            self.bias[selection,None,:], x, self.weight[selection].transpose(1,2)
        )


class StackedMLP(nn.Module):
    def __init__(
        self,
        features_in: int,
        features_out: int,
        channels: int,
        layers: int,
        hidden_nodes: int,
        activation = nn.ReLU,
    ):
        super().__init__()
        input_dim = features_in
        self.layers = nn.ModuleList()
        for i in range(layers - 1):
            self.layers.append(StackedLinear(input_dim, hidden_nodes, channels))
            self.layers.append(activation())
            input_dim = hidden_nodes
        self.layers.append(StackedLinear(input_dim, features_out, channels))
        nn.init.zeros_(self.layers[-1].weight)
        nn.init.zeros_(self.layers[-1].bias)

    def forward(self, x: torch.Tensor, selection: slice):
        for i, layer in enumerate(self.layers):
            x = layer(x, selection) if i % 2 == 0 else layer(x)
        return x


class StackedMarginalFlow(nn.Module):
    def __init__(
        self,
        dims_total: int,
        dims_parameter: int,
        blocks: int,
        spline_bins: int,
        layers: int,
        hidden_nodes: int,
        activation: str,
        spline_low: float,
        spline_high: float,
    ):
        super().__init__()

        self.spline_bins = spline_bins
        self.spline_low = spline_low
        self.spline_high = spline_high

        dims_first = dims_total // 2
        dims_second = dims_total - dims_first
        kwargs = dict(
            channels=blocks,
            layers=layers,
            hidden_nodes=hidden_nodes,
            activation=getattr(nn, activation),
        )
        self.first_subnets = StackedMLP(
            features_in=dims_first + dims_parameter,
            features_out=dims_second * (3 * spline_bins + 1),
            **kwargs,
        )
        self.second_subnets = StackedMLP(
            features_in=dims_second + dims_parameter,
            features_out=dims_first * (3 * spline_bins + 1),
            **kwargs,
        )
        self.register_buffer(
            "first_indices",
            torch.multinomial(
                torch.ones((blocks, dims_total)), dims_first, replacement=False
            ),
        )
        subnet_masks = torch.scatter(
            input=torch.zeros((blocks, dims_total), dtype=torch.bool),
            dim=1,
            index=self.first_indices,
            src=torch.tensor([[True]]).expand((blocks, dims_total)),
        )
        self.register_buffer(
            "second_indices",
            torch.arange(dims_total)[None,:].expand(blocks, -1)[~subnet_masks]
                 .reshape((blocks, dims_second))
        )

    def forward(
        self,
        x: torch.Tensor,
        selection: slice,
        marginal_mask: torch.Tensor,
        inverse: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        input_shape = x.shape
        x = x.reshape((x.shape[0], -1, x.shape[-1]))
        marginal_mask = marginal_mask.reshape(x.shape)
        first_indices = self.first_indices[selection, None, :].expand(-1, x.shape[1], -1)
        second_indices = self.second_indices[selection, None, :].expand(-1, x.shape[1], -1)
        if inverse:
            first_indices, second_indices = second_indices, first_indices
            first_subnets, second_subnets = self.first_subnets, self.second_subnets
        else:
            first_subnets, second_subnets = self.second_subnets, self.first_subnets

        x_first = torch.gather(x, -1, first_indices)
        x_second = torch.gather(x, -1, second_indices)
        marginal_mask_first = torch.gather(marginal_mask, -1, first_indices)
        marginal_mask_second = torch.gather(marginal_mask, -1, second_indices)

        subnet_out_first = first_subnets(
            torch.cat((x_first, marginal_mask), dim=-1), selection
        ).reshape((*x.shape[:2], x_second.shape[2], -1))
        subnet_out_first[marginal_mask_second] = 0.
        y_second, jac_second = unconstrained_rational_quadratic_spline(
            x_second,
            subnet_out_first[..., :self.spline_bins],
            subnet_out_first[..., self.spline_bins:2*self.spline_bins],
            subnet_out_first[..., 2*self.spline_bins:],
            inverse,
            self.spline_low,
            self.spline_high,
            self.spline_low,
            self.spline_high,
        )
        subnet_out_second = second_subnets(
            torch.cat((x_second, marginal_mask), dim=-1), selection
        ).reshape((*x.shape[:2], x_first.shape[2], -1))
        subnet_out_second[marginal_mask_first] = 0.
        y_first, jac_first = unconstrained_rational_quadratic_spline(
            x_first,
            subnet_out_second[..., :self.spline_bins],
            subnet_out_second[..., self.spline_bins:2*self.spline_bins],
            subnet_out_second[..., 2*self.spline_bins:],
            inverse,
            self.spline_low,
            self.spline_high,
            self.spline_low,
            self.spline_high,
        )
        y = torch.zeros_like(x)
        y.scatter_(-1, first_indices, y_first)
        y.scatter_(-1, second_indices, y_second)
        jac = jac_first.sum(dim=-1) + jac_second.sum(dim=-1)
        return y.reshape(input_shape), jac.reshape(input_shape[:-1])
