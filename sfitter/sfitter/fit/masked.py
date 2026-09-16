import torch
import torch.nn as nn

from .rational_quadratic_spline import unconstrained_rational_quadratic_spline
from .stacked import StackedLinear


class MaskedStackedLinear(StackedLinear):
    """
    Efficient implementation of linear layers for ensembles of networks
    """
    def __init__(
        self, in_degrees: torch.Tensor, out_degrees: torch.Tensor, channels: int
    ):
        super().__init__(in_degrees.shape[1], out_degrees.shape[1], channels)
        self.register_buffer(
            "mask", (out_degrees[:, :, None] >= in_degrees[:, None, :]).float()
        )

    def forward(self, x: torch.Tensor, selection: slice = slice(None)):
        return torch.baddbmm(
            self.bias[selection,None,:],
            x,
            (self.mask[selection] * self.weight[selection]).transpose(1,2)
        )


class MaskedStackedMLP(nn.Module):
    def __init__(
        self,
        autoregressive_features: int,
        conditional_features: int,
        output_multiplier: int,
        channels: int,
        layers: int,
        hidden_nodes: int,
        activation = nn.ReLU,
    ):
        super().__init__()
        self.autoregressive_features = autoregressive_features
        in_degrees = torch.rand((channels, autoregressive_features)).argsort(dim=1)
        hidden_degrees = (
            torch.arange(hidden_nodes) % autoregressive_features
        )[None,:].expand(channels, -1)
        out_degrees = torch.repeat_interleave(in_degrees - 1, output_multiplier, dim=1)
        self.conditional_layer = StackedLinear(conditional_features, hidden_nodes, channels)
        self.layers = nn.ModuleList()
        self.activations = nn.ModuleList()
        for i in range(layers - 1):
            self.layers.append(MaskedStackedLinear(in_degrees, hidden_degrees, channels))
            self.activations.append(activation())
            in_degrees = hidden_degrees
        self.layers.append(MaskedStackedLinear(in_degrees, out_degrees, channels))
        nn.init.zeros_(self.layers[-1].weight)
        nn.init.zeros_(self.layers[-1].bias)

    def forward(self, x: torch.Tensor, c: torch.Tensor, selection: slice):
        hidden_condition = self.conditional_layer(c, selection)
        for layer, activation in zip(self.layers, self.activations):
            x = activation(layer(x, selection) + hidden_condition)
        return self.layers[-1](x, selection)


class MaskedStackedMarginalFlow(nn.Module):
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
        self.subnets = MaskedStackedMLP(
            autoregressive_features=dims_total,
            conditional_features=dims_parameter,
            output_multiplier=3 * spline_bins + 1,
            channels=blocks,
            layers=layers,
            hidden_nodes=hidden_nodes,
            activation=getattr(nn, activation),
        )

    def forward(
        self,
        x: torch.Tensor,
        selection: slice,
        marginal_mask: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        input_shape = x.shape
        x = x.reshape((x.shape[0], -1, x.shape[-1]))
        marginal_mask = marginal_mask.reshape(x.shape)
        subnet_out = self.subnets(x, marginal_mask.float(), selection).reshape((*x.shape, -1))
        subnet_out[marginal_mask] = 0.
        y, jac = unconstrained_rational_quadratic_spline(
            x,
            subnet_out[..., :self.spline_bins],
            subnet_out[..., self.spline_bins:2*self.spline_bins],
            subnet_out[..., 2*self.spline_bins:],
            False,
            self.spline_low,
            self.spline_high,
            self.spline_low,
            self.spline_high,
        )
        return y.reshape(input_shape), jac.sum(dim=-1).reshape(input_shape[:-1])
