import math
import numpy as np

import torch
import torch.nn as nn

from .rational_quadratic_spline import unconstrained_rational_quadratic_spline


L2PI = math.log(2*math.pi)


class MLP(nn.Module):
    def __init__(
        self,
        features_in: int,
        features_out: int,
        layers: int,
        units: int,
        activation = nn.ReLU,
        layer_constructor = nn.Linear,
    ):
        super().__init__()
        input_dim = features_in
        layer_list = []
        for i in range(layers - 1):
            layer_list.append(layer_constructor(input_dim, units))
            layer_list.append(activation())
            input_dim = units
        layer_list.append(layer_constructor(input_dim, features_out))
        nn.init.zeros_(layer_list[-1].weight)
        nn.init.zeros_(layer_list[-1].bias)
        self.layers = nn.Sequential(*layer_list)

    def forward(self, x: torch.Tensor):
        return self.layers(x)


class ConditionalFlow(nn.Module):
    def __init__(
        self,
        dims_in: int,
        dims_c: int = 0,
        layers: int = 3,
        units: int = 32,
        bins: int = 10,
        spline_low: float = -10,
        spline_high: float = 10,
        activation = nn.LeakyReLU,
    ):
        super().__init__()

        self.dims_in = dims_in
        subnet_constructor = lambda features_in, features_out: MLP(
            features_in, features_out, layers, units, activation
        )

        n_perms = int(np.ceil(np.log2(dims_in)))
        blocks = int(2 * n_perms)
        self.masks = torch.tensor([
            [int(i) for i in np.binary_repr(i, n_perms)] for i in range(dims_in)
        ]).flip(dims=(1,)).bool().t().repeat_interleave(2, dim=0)
        self.masks[1::2, :] ^= True

        self.spline_low = spline_low
        self.spline_high = spline_high

        self.subnets = nn.ModuleList()
        for mask in self.masks:
            dims_cond = torch.count_nonzero(mask)
            self.subnets.append(subnet_constructor(
                dims_cond + dims_c,
                (dims_in - dims_cond) * (3 * bins + 1)
            ))

    def transform(
        self,
        x: torch.Tensor,
        c: torch.Tensor,
        inverse: bool
    ) -> tuple[torch.Tensor, torch.Tensor]:
        x = x.clone()
        jac = 0.
        if inverse:
            blocks = zip(reversed(self.masks), reversed(self.subnets))
        else:
            blocks = zip(self.masks, self.subnets)
        for mask, subnet in blocks:
            inv_mask = ~mask
            x_trafo = x[:,inv_mask]
            x_cond = torch.cat((x[:,mask], c), dim=1)
            subnet_out = subnet(x_cond).reshape((x.shape[0], x_trafo.shape[1], -1))
            bins = subnet_out.shape[-1] // 3
            x_out, block_jac = unconstrained_rational_quadratic_spline(
                x_trafo,
                subnet_out[:,:,:bins],
                subnet_out[:,:,bins:2*bins],
                subnet_out[:,:,2*bins:],
                inverse,
                self.spline_low,
                self.spline_high,
                self.spline_low,
                self.spline_high,
            )
            x[:,inv_mask] = x_out
            jac += block_jac.sum(dim=1)
        return x, jac

    def log_prob(self, x: torch.Tensor, c: torch.Tensor | None = None) -> torch.Tensor:
        if c is None:
            c = x[:,:0]
        z, jac = self.transform(x, c, False)
        return jac - (z.square().sum(dim=1) + L2PI) / 2

    def sample(
        self, c: torch.Tensor | None = None, n: int | None = None, device: torch.device = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if c is not None:
            n = len(c)
            device = c.device
        else:
            c = torch.zeros((n, 0), device=device)
        z = torch.randn((n, self.dims_in), device=device)
        x, jac = self.transform(z, c, True)
        return x, - (jac + (z.square().sum(dim=1) + L2PI) / 2)

