from typing import Callable
import math

import torch


MarkovChainFunc = Callable[
    [torch.Tensor, Callable[[torch.Tensor], torch.Tensor], float, int, torch.Tensor | None],
    tuple[torch.Tensor, float]
]


def markov_chain(
    x: torch.Tensor,
    log_prob_func: Callable[[torch.Tensor], torch.Tensor],
    step_size: float,
    steps: int,
    marginal_mask: torch.Tensor | None,
) -> tuple[torch.Tensor, float]:
    """
    Runs simple Markov chains for each input point.

    Args:
        x: input points, shape (..., d)
        log_prob_func: function that returns log-probability given input tensor x
        step_size: Markov chain step size
        steps: number of steps
        marginal_mask: mask, true for components that are kept constant, shape (..., d)
    Returns:
        Tensor with evolved points, same shape as x
        Average acceptance
    """
    acceptance = 0.
    with torch.no_grad():
        log_prob = log_prob_func(x)
    for j in range(steps):
        x_step = x + math.sqrt(2 * step_size) * torch.randn_like(x)
        if marginal_mask is not None:
            x_step = torch.where(marginal_mask, x, x_step)
        with torch.no_grad():
            log_prob_step = log_prob_func(x_step)
        accept_prob = torch.clip(
            torch.exp(log_prob_step - log_prob), max=1
        )[:, None]
        accept_mask = torch.rand_like(accept_prob) < accept_prob
        x = torch.where(accept_mask, x_step.detach(), x.detach())
        log_prob = torch.where(accept_mask[..., 0], log_prob_step, log_prob)
        acceptance += accept_mask.float().mean().item()

    return x.detach(), acceptance / max(steps, 1)


def langevin_markov_chain(
    x: torch.Tensor,
    log_prob_func: Callable[[torch.Tensor], torch.Tensor],
    step_size: float,
    steps: int,
    marginal_mask: torch.Tensor | None,
) -> tuple[torch.Tensor, float]:
    """
    Runs Langevin Markov chains for each input point.

    Args:
        x: input points, shape (..., d)
        log_prob_func: function that returns log-probability given input tensor x
        step_size: Markov chain step size
        steps: number of steps
        marginal_mask: mask, true for components that are kept constant, shape (..., d)
    Returns:
        Tensor with evolved points, same shape as x
        Average acceptance
    """
    acceptance = 0.
    x.requires_grad = True
    if marginal_mask is not None:
        x = torch.where(marginal_mask, x.detach(), x)
    log_prob = log_prob_func(x)
    grad_log_prob = torch.autograd.grad(log_prob.sum(), x)[0]
    for j in range(steps):
        x_step = (
            x.detach()
            + step_size * grad_log_prob.detach()
            + math.sqrt(2 * step_size) * torch.randn_like(x)
        )
        x_step.requires_grad = True
        if marginal_mask is not None:
            x_step = torch.where(marginal_mask, x.detach(), x_step)
        log_prob_step = log_prob_func(x_step)
        grad_log_prob_step = torch.autograd.grad(log_prob_step.sum(), x_step)[0]

        log_transition = (
            -0.25
            / step_size
            * (
                torch.sum((x - x_step - step_size * grad_log_prob_step) ** 2, dim=-1)
                - torch.sum((x_step - x - step_size * grad_log_prob) ** 2, dim=-1)
            )
        )
        accept_prob = torch.clip(
            torch.exp(log_prob_step - log_prob + log_transition), max=1
        )[..., None]

        accept_mask = torch.rand_like(accept_prob) < accept_prob
        x = torch.where(accept_mask, x_step.detach(), x.detach())
        log_prob = torch.where(accept_mask[..., 0], log_prob_step, log_prob)
        grad_log_prob = torch.where(accept_mask, grad_log_prob_step, grad_log_prob)
        acceptance += accept_mask.float().mean().item()

    return x.detach(), acceptance / max(steps, 1)
