from collections.abc import Iterable
from typing import Callable
import torch


#def build_optimizer_and_scheduler(
#    trainable_parameters: Iterable,
#    total_steps: int,
#    params: dict,
#) -> tuple[torch.optim.Optimizer, torch.optim.lr_scheduler.LRScheduler]:
#    """
#    Constructs optimizer and learning rate scheduler
#
#    """

def maximize(
    x: torch.Tensor,
    log_prob_func: Callable[[torch.Tensor], torch.Tensor],
    learning_rate: float,
    steps: int,
    marginal_mask: torch.Tensor | None = None,
    log_prob_max: torch.Tensor | None = None,
    optimizer: str = "lbfgs",
    step_callback: Callable[[int], None] | None = None,
) -> torch.Tensor:
    xp = torch.nn.Parameter(x.clone())
    if optimizer == "adam":
        opt = torch.optim.Adam([xp], learning_rate)
    elif optimizer == "lbfgs":
        opt = torch.optim.LBFGS([xp], line_search_fn="strong_wolfe")
    for i in range(steps):
        def closure():
            nonlocal log_prob_max
            xx = xp
            if marginal_mask is not None:
                xx = torch.where(marginal_mask, xx.detach(), xx)
            logp = log_prob_func(xx)
            if log_prob_max is None:
                log_prob_max = logp.detach()
            else:
                lpm_before = log_prob_max
                log_prob_max = torch.maximum(log_prob_max, logp.detach())
            loss = -logp.sum()
            opt.zero_grad()
            loss.backward()
            return loss
        if optimizer == "lbfgs":
            log_prob_max_before = log_prob_max
            opt.step(closure)
            if log_prob_max_before is not None:
                if (log_prob_max_before == log_prob_max).all():
                    break
        else:
            closure()
            opt.step()
        if step_callback is not None:
            step_callback(i)

    with torch.no_grad():
        log_prob_final = log_prob_func(xp)
        if log_prob_max is None:
            return log_prob_final
        else:
            return torch.maximum(log_prob_max, log_prob_final)
