import torch
import numpy as np

from .likelihood import Likelihood


class SpiralLikelihood(Likelihood):
    dims_parameter = 2
    dims_nuisance = 0
    parameter_names = ["x1", "x2"]

    def __init__(self, params: dict, device: torch.device):
        self.sigma = params.get("sigma", 0.007)

    def log_likelihood(self, x: torch.Tensor) -> torch.Tensor:
        bb = 0.8
        r = torch.sqrt(x[...,0]**2 + x[...,1]**2)
        z = 0
        for offset in range(-2,2):
            sign = 1 if offset >= 0 else -1
            phi = torch.arctan2(x[..., 1], sign * x[..., 0]) % (2 * np.pi)
            bpos = r * phi if offset == 0 or offset == -2 else r * (2 * np.pi - phi)
            bound = torch.where(bpos > bb, 1, torch.exp(-(bpos - bb)**2 / (10 * self.sigma)))
            z += torch.exp(
                -(sign * r - (phi / (2 * np.pi) + offset)) ** 2 / (2 * self.sigma)
            ) * bound
        return z.log()

    def log_prior(self, x: torch.Tensor) -> torch.Tensor:
        return torch.zeros_like(x[...,0])


class FivePointLikelihood(Likelihood):
    dims_parameter = 2
    dims_nuisance = 0
    parameter_names = ["x1", "x2"]

    def __init__(self, params: dict, device: torch.device):
        self.outer_offset = params.get("outer_offset", 1.5)
        self.outer_sigma = params.get("outer_sigma", 0.2)
        self.inner_mag = params.get("inner_mag", 10)
        self.inner_sigma = params.get("inner_sigma", 0.4)

    def log_likelihood(self, x: torch.Tensor) -> torch.Tensor:
        z = 0
        for i, j in [[-1, -1], [1, -1], [1, 1], [-1, 1]]:
            z += torch.exp(
                - (
                    (x[..., 0] - self.outer_offset * i)**2 +
                    (x[..., 1] - self.outer_offset * j)**2
                ) / (2 * self.outer_sigma**2)
            ) / (2 * np.pi * self.outer_sigma**2)
        z += self.inner_mag * torch.exp(
            - (x[..., 0]**2 + x[..., 1]**2) / (2 * self.inner_sigma**2)
        ) / (2 * np.pi * self.inner_sigma**2)
        return z.log()

    def log_prior(self, x: torch.Tensor) -> torch.Tensor:
        return torch.zeros_like(x[...,0])
