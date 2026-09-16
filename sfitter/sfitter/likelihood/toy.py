import torch
import torch.distributions as D

from .likelihood import Likelihood


class SchwurbelTransform(D.Transform):
    domain = D.constraints.independent(D.constraints.real,1)
    codomain = D.constraints.independent(D.constraints.real,1)
    bijective = True

    def _call(self, x):
        y = x.clone()
        y[:,3] += 1.5*torch.exp(-0.5*x[:,1]**2)
        y[:,2] = 0.4*x[:,2] + 0.6*x[:,1]
        return y

    def _inverse(self, y):
        x = y.clone()
        x[:,2] = (y[:,2] - 0.6*y[:,1]) / 0.4
        x[:,3] -= 1.5*torch.exp(-0.5*y[:,1]**2)
        return x

    def log_abs_det_jacobian(self, x, y):
        return torch.full_like(x[:,-1], 0.4).log()


class ToyLikelihood(Likelihood):
    dims_parameter = 4
    dims_nuisance = 0
    parameter_names = ["x1", "x2", "x3", "x4"]

    def __init__(self, params: dict, device: torch.device):
        modes = 2
        mu = torch.tensor([[-1.3, -1.0, 0.5, 0.1], [1.3, 1.0, 0.0, -0.4]], device=device)
        sigma = torch.tensor([[0.9, 1., 1., 1.], [0.85, 0.85, 0.85, 0.85]], device=device)
        mix = D.Categorical(torch.ones(modes, device=device))
        comp = D.Independent(D.Normal(mu, sigma), 1)
        gmm = D.MixtureSameFamily(mix, comp)
        self.dist = D.TransformedDistribution(gmm, [SchwurbelTransform()])

    def log_likelihood(self, x: torch.Tensor) -> torch.Tensor:
        return self.dist.log_prob(x.reshape((-1, x.shape[-1]))).reshape(x.shape[:-1])

    def log_prior(self, x: torch.Tensor) -> torch.Tensor:
        bounds = 10
        return torch.where(torch.all(x.abs() < bounds, dim=-1), (2*bounds)**(-4), 0.)
