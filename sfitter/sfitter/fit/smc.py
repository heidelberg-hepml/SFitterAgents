import math
from typing import Callable

import torch
import numpy as np

from .fitter import Fitter, FitResults
from .markov import MarkovChainFunc, markov_chain, langevin_markov_chain
from ..util.optimize import maximize

L2PI = math.log(2*math.pi)


def sequential_monte_carlo(
    x: torch.Tensor,
    log_prob_func: Callable[(torch.Tensor, int), torch.Tensor],
    log_weight_func: Callable[(torch.Tensor, int), torch.Tensor],
    marginal_mask: torch.Tensor,
    total_steps: int,
    mcmc_func: MarkovChainFunc,
    mcmc_steps: int,
    mcmc_step_size: float | list[float],
    resampling_threshold: float = 0.,
    no_resampling_steps: int = 0,
) -> tuple[torch.Tensor, torch.Tensor, list]:
    """
    Runs sequential Monte Carlo/annealed importance sampling. For d-dimensional inputs,
    d_marginal components are kept constant. SMC is performed for multiple independent
    batches. For each batch, marginal_idx and marginal_mask specify which components are
    kept constant and they are initialized from the values in marginal_x. Optionally, a
    transport function that can be defined in subclasses is applied in each temperature
    step. The points are evolved using MCMC and resampling steps are performed if the
    effective sample size is low.

    Args:
        batch_size: number of samples per point
        marginal_mask: mask that is True for components kept constant, shape (..., d)
        mcmc_func: function to perform MCMC steps
        mcmc_steps: number of MCMC steps per temperature
        mcmc_step_size: MCMC step size
        annealing_schedule: annealing schedules for likelihood, prior, latent space
        resampling_threshold: threshold for effective sample size, below which the batch
            is resampled

    Returns:
        x: tensor with sampled points, shape (..., d)
        log_w: tensor with log-weights of the samples, shape (..., )
        acceptances: acceptances of the MCMC steps

    """
    batch_size = len(x)
    log_w = torch.zeros_like(x[:,:,0])
    acceptances = []

    const_step_size = isinstance(mcmc_step_size, float)
    for i in range(total_steps):
        with torch.no_grad():
            log_w += log_weight_func(xx, i)
        log_w_sum = log_w.logsumexp(dim=1, keepdim=True)
        log_w_norm = log_w - log_w_sum

        if resampling_threshold > 0. or i == total_steps - 1: # and total_steps - i > no_resampling_steps:
            eff_sample_size = 1 / (2 * log_w_norm).exp().sum(dim=1)
            needs_resampling = eff_sample_size / batch_size < resampling_threshold
            if torch.any(needs_resampling):
                indices = torch.multinomial(
                    log_w_norm[needs_resampling].exp(), batch_size, replacement=True
                )
                xr = x[needs_resampling]
                x[needs_resampling] = torch.gather(xr, 1, indices[:,:,None].expand(xr.shape))
                log_w[needs_resampling] = log_w_sum[needs_resampling] - math.log(batch_size)

        x, acc = mcmc_func(
            x=x,
            log_prob_func=lambda xx: log_prob_func(xx, i + 1),
            step_size=mcmc_step_size if const_step_size else mcmc_step_size[i],
            steps=mcmc_steps,
            marginal_mask=marginal_mask,
        )
        acceptances.append(acc)

    return x, log_w, acceptances

