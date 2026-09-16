import math
from datetime import timedelta
from time import time
from typing import NamedTuple

import torch
import torch.nn.functional as F
from tqdm import tqdm
import numpy as np

from .fitter import Fitter, FitResults
from .markov import MarkovChainFunc, markov_chain, langevin_markov_chain
from ..util.optimize import maximize

L2PI = math.log(2*math.pi)


"""
TODO
  - fix boundary selection
"""


class AnnealingSchedule(NamedTuple):
    """
    NamedTuple wrapping the annealing schedule (inverse temperatures beta) for likelihood,
    prior and latent space

    Args:
        beta_likelihood: betas for the likelihood, shape (total_steps, )
        beta_prior: betas for the prior, shape (total_steps, )
        beta_latent: betas for the latent space, shape (total_steps, )
    """
    beta_likelihood: np.ndarray
    beta_prior: np.ndarray
    beta_latent: np.ndarray


class SMCFitter(Fitter):
    save_attrs = ["x_mean", "x_std"]
    """
    Fitter that implements marginalization and profiling based on sequential Monte Carlo.
    See documentation for a table of settings.
    """

    def initialize(self):
        """
        Initialize variables needed to run the SMC fitter
        """
        self.transport = None
        self.smc_params = self.params.get("smc", {})
        self.marginal_params = {**self.smc_params, **self.params.get("marginalize", {})}
        self.profile_params = {**self.smc_params, **self.params.get("profile", {})}
        self.profile_1d_params = {**self.profile_params, **self.params.get("profile_1d", {})}
        self.profile_2d_params = {**self.profile_params, **self.params.get("profile_2d", {})}
        self.prescale_params = {**self.marginal_params, **self.params.get("prescale", {})}
        self.x_mean = torch.zeros((self.likelihood.dims_total, ), device=self.device)
        self.x_std = torch.ones((self.likelihood.dims_total, ), device=self.device)

    def get_annealing_schedule(
        self, temp_steps: int, anneal_steps: int, anneal_beta: int
    ) -> tuple[np.ndarray, np.ndarray, np.array]:
        """
        Creates an annealing schedule that first linearly interpolates between the
        log-probabilities of latent space and prior * likelihood and then linearly
        anneals to anneal_beta * likelihood.

        Args:
            temp_steps: number of steps between latent space and posterior
            anneal_steps: number of steps between posterior and annealed likelihood
            anneal_beta: inverse temperature of the annealed likelihood

        Returns:
            AnnealingSchedule tuple
        """
        beta_likelihood = np.concatenate((
            np.linspace(0, 1, temp_steps + 1),
            np.linspace(1, anneal_beta, anneal_steps + 1)[1:]
        ))
        beta_prior = np.where(
            beta_likelihood < 1,
            beta_likelihood,
            (anneal_beta - beta_likelihood) / max(anneal_beta - 1, 1e-5)
        )
        beta_latent = np.maximum(1 - beta_likelihood, 0)
        return AnnealingSchedule(beta_likelihood, beta_prior, beta_latent)

    def sequential_monte_carlo(
        self,
        batch_size: int,
        marginal_x: torch.Tensor,
        marginal_idx: torch.Tensor,
        marginal_mask: torch.Tensor,
        mcmc_func: MarkovChainFunc,
        mcmc_steps: int,
        mcmc_step_size: float,
        annealing_schedule: AnnealingSchedule,
        resampling_threshold: float,
        no_resampling_steps: int,
    ) -> tuple[torch.Tensor, torch.Tensor, float]:
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
            marginal_x: values that are kept constant, shape (..., d_marginal)
            marginal_idx: indices of the values kept constant, shape (..., d_marginal)
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
            acceptance: average acceptance of the MCMC steps

        """
        x = torch.randn(
            (marginal_x.shape[0], batch_size, self.likelihood.dims_total), device=self.device
        )
        x.scatter_(
            2,
            marginal_idx[:,None,:].expand(-1, batch_size, -1),
            marginal_x[:,None,:].expand(-1, batch_size, -1)
        )
        x_mean = torch.where(marginal_mask, self.x_mean, 0.)
        x_std = torch.where(marginal_mask, self.x_std, 1.)
        x = (x - x_mean) / x_std
        log_w = torch.zeros_like(x[:,:,0])
        log_likelihood_max = torch.full_like(log_w[:,0], -np.inf)
        acceptance = 0.

        beta_likelihood, beta_prior, beta_latent = annealing_schedule
        def log_prob_func(xx: torch.Tensor, step: int):
            xx = xx * self.x_std + self.x_mean
            log_likelihood = self.likelihood.log_likelihood(xx)
            log_likelihood_max[:] = torch.maximum(
                log_likelihood_max, log_likelihood.detach().amax(dim=1)
            )
            return (
                beta_likelihood[step] * log_likelihood +
                beta_prior[step] * self.likelihood.log_prior(xx) +
                beta_latent[step] * torch.sum((-L2PI - xx.square()) / 2, dim=-1)
            )

        total_steps = len(beta_likelihood) - 1
        for i in range(total_steps):
            with torch.no_grad():
                if self.transport is None:
                    xx = x * self.x_std + self.x_mean
                    log_w += (
                        (beta_likelihood[i+1] - beta_likelihood[i])
                            * self.likelihood.log_likelihood(xx) +
                        (beta_prior[i+1] - beta_prior[i])
                            * self.likelihood.log_prior(xx) +
                        (beta_latent[i+1] - beta_latent[i])
                            * torch.sum((-L2PI - xx.square()) / 2, dim=-1)
                    )
                else:
                    log_prob_before = log_prob_func(x, i)
                    x, log_jac = self.transport(x, i, marginal_mask)
                    log_prob_after = log_prob_func(x, i + 1)
                    log_w += log_prob_after - log_prob_before + log_jac
            log_w_sum = log_w.logsumexp(dim=1, keepdim=True)
            log_w_norm = log_w - log_w_sum

            eff_sample_size = 1 / (2 * log_w_norm).exp().sum(dim=1)
            needs_resampling = eff_sample_size / batch_size < resampling_threshold
            if total_steps - i > no_resampling_steps and torch.any(needs_resampling):
                indices = torch.multinomial(
                    log_w_norm[needs_resampling].exp(), batch_size, replacement=True
                )
                xr = x[needs_resampling]
                x[needs_resampling] = torch.gather(xr, 1, indices[:,:,None].expand(xr.shape))
                log_w[needs_resampling] = log_w_sum[needs_resampling] - math.log(batch_size)

            x, acc = mcmc_func(
                x=x,
                log_prob_func=lambda xx: log_prob_func(xx, i + 1),
                step_size=mcmc_step_size,
                steps=mcmc_steps,
                marginal_mask=marginal_mask,
            )
            acceptance += acc

        return x, log_w, log_likelihood_max, acceptance / total_steps

    def train(self):
        if not self.prescale_params["enable"]:
            return

        self.print("Pre-scaling")
        start_time = time()

        mcmc_func = {
            "standard": markov_chain,
            "langevin": langevin_markov_chain,
        }[self.prescale_params["mcmc_type"]]
        x, log_w, _, acc = self.sequential_monte_carlo(
            batch_size=self.prescale_params["batch_size"],
            marginal_x=torch.zeros((1,0), device=self.device),
            marginal_idx=torch.zeros((1,0), device=self.device, dtype=torch.long),
            marginal_mask=torch.zeros(
                (1, 1, self.likelihood.dims_total), device=self.device, dtype=torch.bool
            ),
            mcmc_func=mcmc_func,
            mcmc_steps=self.prescale_params["mcmc_steps"],
            mcmc_step_size=self.prescale_params["mcmc_step_size"],
            annealing_schedule=self.get_annealing_schedule(
                temp_steps=self.prescale_params["temperature_steps"],
                anneal_steps=0,
                anneal_beta=1.,
            ),
            resampling_threshold=self.prescale_params["resampling_threshold"],
            no_resampling_steps=self.prescale_params["no_resampling_steps"],
        )
        #w_norm = (w[0] / w.sum())[:, None]
        w_norm = torch.exp(log_w[0] - log_w[0].logsumexp(dim=0))[:, None]
        self.x_mean = torch.sum(w_norm * x[0], dim=0)
        self.x_std = torch.sum(w_norm * (x[0] - self.x_mean)**2, dim=0).sqrt()

        self.print(f"  Time:       {timedelta(seconds=int(time() - start_time))}")
        self.print(f"  Acceptance: {acc:.4f}")


    def marginalize(self) -> tuple[np.ndarray, list[np.ndarray], list[np.ndarray], float]:
        """
        Draws samples from the probability distribution specified by prior and likelihood.
        The samples are then binned and histograms are made for the marginalized distributions
        of interest.

        Returns:
            bins: bins boundaries for all dimensions, shape (d, n_bins + 1)
            marginal_1d: 1d marginal histograms, list of arrays with shape (n_bins, )
            marginal_2d: 2d marginal histograms, list of arrays with shape (n_bins, n_bins)
            eff_size: Effective sample size
        """
        self.print("Marginalizing")
        start_time = time()

        mcmc_func = {
            "standard": markov_chain,
            "langevin": langevin_markov_chain,
        }[self.marginal_params["mcmc_type"]]
        target_sample_size = self.marginal_params["target_samples_eff"]
        log_weight_sum = None
        log_square_weight_sum = None
        eff_size = 0.
        acceptances = []
        marginal_samples = []
        marginal_log_likelihood = []
        if self.verbose:
            progress = tqdm(total=target_sample_size, leave=False)
        while eff_size < target_sample_size:
            x, log_w, _, acc = self.sequential_monte_carlo(
                batch_size=self.marginal_params["batch_size"],
                marginal_x=torch.zeros((1,0), device=self.device),
                marginal_idx=torch.zeros((1,0), device=self.device, dtype=torch.long),
                marginal_mask=torch.zeros(
                    (1, 1, self.likelihood.dims_total), device=self.device, dtype=torch.bool
                ),
                mcmc_func=mcmc_func,
                mcmc_steps=self.marginal_params["mcmc_steps"],
                mcmc_step_size=self.marginal_params["mcmc_step_size"],
                annealing_schedule=self.get_annealing_schedule(
                    temp_steps=self.marginal_params["temperature_steps"],
                    anneal_steps=0,
                    anneal_beta=1.,
                ),
                resampling_threshold=self.marginal_params["resampling_threshold"],
                no_resampling_steps=self.marginal_params["no_resampling_steps"],
            )
            marginal_samples.append(
                x[:,:,:self.likelihood.dims_parameter].reshape((-1, x.shape[-1]))
            )
            with torch.no_grad():
                marginal_log_likelihood.append(
                    self.likelihood.log_likelihood(x * self.x_std + self.x_mean).flatten()
                )
            acceptances.append(acc)
            if log_weight_sum is None:
                log_weight_sum = log_w[0].logsumexp(dim=0)
                log_square_weight_sum = (2 * log_w[0]).logsumexp(dim=0)
            else:
                log_weight_sum = torch.logaddexp(log_weight_sum, log_w[0].logsumexp(dim=0))
                log_square_weight_sum = torch.logaddexp(
                    log_square_weight_sum, (2 * log_w[0]).logsumexp(dim=0)
                )
            eff_size_prev = eff_size
            eff_size = torch.exp(2 * log_weight_sum - log_square_weight_sum).item()
            if self.verbose:
                progress.update(int(eff_size) - int(eff_size_prev))
        if self.verbose:
            progress.close()

        marginal_samples = torch.cat(marginal_samples, dim=0) * self.x_std + self.x_mean
        if (
            self.profile_1d_params["strategy"] == "histogram" or
            self.profile_2d_params["strategy"] == "histogram"
        ):
            self.marginal_log_likelihood, mll_argsort = torch.sort(
                torch.cat(marginal_log_likelihood, dim=0)
            )
            self.marginal_samples = marginal_samples[mll_argsort]

        lower_bounds = torch.quantile(
            marginal_samples, self.marginal_params["lower_bound_quantile"], dim=0
        ).cpu().numpy()
        upper_bounds = torch.quantile(
            marginal_samples, self.marginal_params["upper_bound_quantile"], dim=0
        ).cpu().numpy()
        bounds_diff = upper_bounds - lower_bounds
        lower_bounds -= bounds_diff / 4
        upper_bounds += bounds_diff / 4
        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds
        marginal_samples = marginal_samples.cpu().numpy()

        n_bins = self.marginal_params.get("n_bins")
        n_bins_1d = n_bins or self.marginal_params["n_bins_1d"]
        n_bins_2d = n_bins or self.marginal_params["n_bins_2d"]
        bins_1d = np.linspace(lower_bounds, upper_bounds, n_bins_1d + 1, axis=1)
        bins_2d = np.linspace(lower_bounds, upper_bounds, n_bins_2d + 1, axis=1)

        self.print(f"  Time:       {timedelta(seconds=int(time() - start_time))}")
        self.print(f"  Acceptance: {np.mean(acceptances):.4f}")
        self.print(f"  N_eff/N:    {eff_size / len(marginal_samples):.4f}")

        n_params = self.likelihood.dims_parameter
        marginal_1d = [
            np.histogram(marginal_samples[:, i], bins_1d[i])[0]
            for i in range(n_params)
        ]
        marginal_2d = [
            np.histogram2d(
                marginal_samples[:, i], marginal_samples[:, j], (bins_2d[i], bins_2d[j]),
            )[0]
            for i in range(n_params - 1)
            for j in range(i + 1, n_params)
        ]
        return marginal_1d, bins_1d, marginal_2d, bins_2d, eff_size

    def anneal_and_maximize(
        self, params: dict, marginal_x: torch.Tensor, marginal_idx: torch.Tensor
    ) -> tuple[torch.Tensor, float]:
        """
        Performs profiling by first running SMC with annealing and then follows the gradients
        to improve the maxima. The dimension indices and corresponding values for which the
        profiling is performed are specified by marginal_idx and marginal_x.

        Args:
            params: settings for annealing and maximizing
            marginal_x: values that are kept constant, shape (..., d_marginal)
            marginal_idx: indices of the values kept constant, shape (..., d_marginal)

        Returns:
            maximized likelihoods
            average acceptance of MCMC steps
        """
        mcmc_func = {
            "standard": markov_chain,
            "langevin": langevin_markov_chain,
        }[params["mcmc_type"]]
        marginal_mask = torch.zeros(
            (marginal_x.shape[0], 1, self.likelihood.dims_total),
            device=self.device,
            dtype=torch.bool
        )
        marginal_mask.scatter_(
            2,
            marginal_idx[:,None,:],
            torch.tensor([[[True]]], device=self.device).expand(
                marginal_x.shape[0], 1, marginal_x.shape[1]
            )
        )
        x, _, log_likelihood_max, acc = self.sequential_monte_carlo(
            batch_size=params["batch_size"],
            marginal_x=marginal_x,
            marginal_idx=marginal_idx,
            marginal_mask=marginal_mask,
            mcmc_func=mcmc_func,
            mcmc_steps=params["mcmc_steps"],
            mcmc_step_size=params["mcmc_step_size"],
            annealing_schedule=self.get_annealing_schedule(
                temp_steps=params["temperature_steps"],
                anneal_steps=params["annealing_steps"],
                anneal_beta=params["annealing_beta"],
            ),
            resampling_threshold=params["resampling_threshold"],
            no_resampling_steps=params["no_resampling_steps"],
        )
        log_likelihood_max = maximize(
            x=x,
            log_prob_func=lambda xx: self.likelihood.log_likelihood(
                xx * self.x_std + self.x_mean
            ),
            learning_rate=params["gd_learning_rate"],
            steps=params["gd_steps"],
            marginal_mask=marginal_mask,
            log_prob_max=log_likelihood_max[:,None],
        ).max(dim=1).values.exp()
        return log_likelihood_max, acc

    def profile(self) -> tuple[list[np.ndarray], list[np.ndarray]]:
        """
        Profiles the likelihood at points in the middle of the bins determined during
        marginalization.

        Returns:
            profile_1d: 1d profiled likelihoods, list of arrays with shape (n_bins, )
            profile_2d: 2d profiled likelihoods, list of arrays with shape (n_bins, n_bins)
        """
        self.print("Profiling (1D)")
        start_time = time()
        strategy_1d = self.profile_1d_params["strategy"]
        if strategy_1d == "histogram":
            profile_1d, bins_1d = self.profile_1d_histogram()
        elif strategy_1d == "annealing":
            profile_1d, bins_1d = self.profile_1d_annealing()
        else:
            raise ValueError(f"Unknown profiling strategy '{strategy_1d}'")
        self.print(f"  Time: {timedelta(seconds=int(time() - start_time))}")

        self.print("Profiling (2D)")
        start_time = time()
        strategy_2d = self.profile_2d_params["strategy"]
        if strategy_2d == "histogram":
            profile_2d, bins_2d = self.profile_2d_histogram()
        elif strategy_2d == "annealing":
            profile_2d, bins_2d = self.profile_2d_annealing()
        else:
            raise ValueError(f"Unknown profiling strategy '{strategy_2d}'")
        self.print(f"  Time: {timedelta(seconds=int(time() - start_time))}")

        return profile_1d, bins_1d, profile_2d, bins_2d

    def profile_1d_annealing(self) -> tuple[np.ndarray, np.ndarray]:
        n_points = self.profile_1d_params["n_points"]
        bins = np.linspace(self.lower_bounds, self.upper_bounds, n_points + 1, axis=1)
        points = torch.tensor((bins[:, :-1] + bins[:, 1:]) / 2, device=self.device)
        marginal_x = points.reshape((-1, 1))
        marginal_idx = torch.arange(
            self.likelihood.dims_parameter, device=self.device
        ).repeat_interleave(n_points)[:, None]
        acceptances = []
        profile_1d = []
        parallel_batches = self.profile_1d_params["parallel_batches"]
        for marg_x, marg_idx in zip(
            self.progress(marginal_x.split(parallel_batches), leave=False),
            marginal_idx.split(parallel_batches)
        ):
            x_max, acc = self.anneal_and_maximize(self.profile_1d_params, marg_x, marg_idx)
            acceptances.append(acc)
            profile_1d.append(x_max)
        profile_1d = torch.cat(profile_1d, dim=0).reshape(points.shape).cpu().numpy()
        self.print(f"  Acceptance: {np.mean(acceptances):.4f}")
        return profile_1d, bins

    def profile_2d_annealing(self) -> tuple[np.ndarray, np.ndarray]:
        n_points = self.profile_2d_params["n_points"]
        bins = np.linspace(self.lower_bounds, self.upper_bounds, n_points + 1, axis=1)
        points = torch.tensor((bins[:, :-1] + bins[:, 1:]) / 2, device=self.device)
        n_params = self.likelihood.dims_parameter
        marginal_idx = torch.tensor(
            [[i, j] for i in range(n_params - 1) for j in range(i + 1, n_params)],
            device=self.device
        ).repeat_interleave(n_points * n_points, dim=0)
        marginal_x = torch.stack([
            torch.cartesian_prod(points[i], points[j])
            for i in range(n_params - 1)
            for j in range(i + 1, n_params)
        ], dim=0).reshape((-1, 2))
        acceptances = []
        profile_2d = []
        parallel_batches = self.profile_2d_params["parallel_batches"]
        for marg_x, marg_idx in zip(
            self.progress(marginal_x.split(parallel_batches), leave=False),
            marginal_idx.split(parallel_batches)
        ):
            x_max, acc = self.anneal_and_maximize(self.profile_2d_params, marg_x, marg_idx)
            acceptances.append(acc)
            profile_2d.append(x_max)
        profile_2d = torch.cat(profile_2d, dim=0).reshape((-1, n_points, n_points)).cpu().numpy()
        self.print(f"  Acceptance: {np.mean(acceptances):.4f}")
        return profile_2d, bins

    def profile_1d_histogram(self) -> tuple[np.ndarray, np.ndarray]:
        n_params = self.likelihood.dims_parameter
        n_bins = self.profile_1d_params["n_points"]
        bins = np.linspace(self.lower_bounds, self.upper_bounds, n_bins + 1, axis=1)
        bin_widths = torch.tensor(
            (self.upper_bounds - self.lower_bounds) / n_bins,
            device=self.device
        )
        batch_size = self.profile_1d_params["batch_size"]
        points = (
            (torch.arange(n_bins, device=self.device) + 0.5) * bin_widths[:, None] +
            torch.tensor(self.lower_bounds, device=self.device)[:, None]
        )

        samples = self.marginal_samples
        x = []
        log_likeli_max = []
        for i in range(n_params):
            bin_idx = ((samples[:, i] - self.lower_bounds[i]) / bin_widths[i]).long()
            mask = (bin_idx >= 0) & (bin_idx < n_bins)
            bin_idx, masked_samples = bin_idx[mask], samples[mask]
            bin_max = torch.full((n_bins, ), 0, device=self.device)
            bin_max.scatter_reduce_(
                0,
                bin_idx,
                torch.arange(1, len(masked_samples) + 1, device=self.device),
                reduce="amax"
            )
            samples_max = F.pad(masked_samples, pad=(0,0,1,0), value=0)[bin_max]
            samples_max[:,i] = points[i]
            x.append(samples_max)
            log_likeli_max.append(
                F.pad(
                    self.marginal_log_likelihood[mask], pad=(1,0), value=-np.inf
                )[bin_max]
            )

        marginal_idx = torch.arange(
            n_params, device=self.device
        ).repeat_interleave(n_bins, dim=0)[:,None]
        marginal_mask = torch.zeros(
            (marginal_idx.shape[0], self.likelihood.dims_total),
            device=self.device,
            dtype=torch.bool
        )
        marginal_mask.scatter_(
            1,
            marginal_idx,
            torch.tensor([[True]], device=self.device).expand(*marginal_idx.shape)
        )
        x = torch.cat(x, dim=0)
        log_likeli_max = torch.cat(log_likeli_max, dim=0)
        profile_1d = []
        for x_batch, marg_idx in zip(
            self.progress(x.split(batch_size), leave=False), marginal_idx.split(batch_size)
        ):
            log_likeli_max = maximize(
                x=(x - self.x_mean) / self.x_std,
                log_prob_func=lambda xx: self.likelihood.log_likelihood(
                    xx * self.x_std + self.x_mean
                ),
                learning_rate=self.profile_1d_params["gd_learning_rate"],
                steps=self.profile_1d_params["gd_steps"],
                marginal_mask=marginal_mask,
                log_prob_max=log_likeli_max,
            )
            profile_1d.append(log_likeli_max.exp())

        return torch.cat(profile_1d, dim=0).reshape((-1, n_bins)).cpu().numpy(), bins

    def profile_2d_histogram(self) -> tuple[np.ndarray, np.ndarray]:
        n_params = self.likelihood.dims_parameter
        n_bins = self.profile_2d_params["n_points"]
        bins = np.linspace(self.lower_bounds, self.upper_bounds, n_bins + 1, axis=1)
        bin_widths = torch.tensor(
            (self.upper_bounds - self.lower_bounds) / n_bins,
            device=self.device
        )
        batch_size = self.profile_2d_params["batch_size"]
        points = (
            (torch.arange(n_bins, device=self.device) + 0.5) * bin_widths[:, None] +
            torch.tensor(self.lower_bounds, device=self.device)[:, None]
        )

        samples = self.marginal_samples
        marginal_idx = []
        x = []
        log_likeli_max = []
        for i in range(n_params - 1):
            for j in range(i + 1, n_params):
                bin_idx_i = ((samples[:, i] - self.lower_bounds[i]) / bin_widths[i]).long()
                bin_idx_j = ((samples[:, j] - self.lower_bounds[j]) / bin_widths[j]).long()
                mask = (
                    (bin_idx_i >= 0) & (bin_idx_i < n_bins) &
                    (bin_idx_j >= 0) & (bin_idx_j < n_bins)
                )
                bin_idx_i, bin_idx_j = bin_idx_i[mask], bin_idx_j[mask]
                masked_samples = samples[mask]
                bin_idx_ij = bin_idx_i * n_bins + bin_idx_j
                bin_max = torch.full((n_bins * n_bins, ), 0, device=self.device)
                bin_max.scatter_reduce_(
                    0,
                    bin_idx_ij,
                    torch.arange(1, len(masked_samples) + 1, device=self.device),
                    reduce="amax"
                )
                samples_max = F.pad(masked_samples, pad=(0,0,1,0), value=0)[bin_max]
                samples_max[:,i], samples_max[:,j] = torch.unbind(
                    torch.cartesian_prod(points[i], points[j]), dim=1
                )
                marginal_idx.append([i, j])
                x.append(samples_max)
                log_likeli_max.append(
                    F.pad(
                        self.marginal_log_likelihood[mask], pad=(1,0), value=-np.inf
                    )[bin_max]
                )

        marginal_idx = torch.tensor(
            marginal_idx, device=self.device
        ).repeat_interleave(n_bins * n_bins, dim=0)
        marginal_mask = torch.zeros(
            (marginal_idx.shape[0], self.likelihood.dims_total),
            device=self.device,
            dtype=torch.bool
        )
        marginal_mask.scatter_(
            1,
            marginal_idx,
            torch.tensor([[True]], device=self.device).expand(*marginal_idx.shape)
        )
        x = torch.cat(x, dim=0)
        log_likeli_max = torch.cat(log_likeli_max, dim=0)
        profile_2d = []
        for x_batch, marg_idx in zip(
            self.progress(x.split(batch_size), leave=False), marginal_idx.split(batch_size)
        ):
            log_likeli_max = maximize(
                x=(x - self.x_mean) / self.x_std,
                log_prob_func=lambda xx: self.likelihood.log_likelihood(
                    xx * self.x_std + self.x_mean
                ),
                learning_rate=self.profile_2d_params["gd_learning_rate"],
                steps=self.profile_2d_params["gd_steps"],
                marginal_mask=marginal_mask,
                log_prob_max=log_likeli_max,
            )
            profile_2d.append(log_likeli_max.exp())

        return torch.cat(profile_2d, dim=0).reshape((-1, n_bins, n_bins)).cpu().numpy(), bins

    def fit(self) -> FitResults:
        """
        Runs marginalization and profiling. Constructs FitResults object containing the
        results.

        Returns:
            Results of the fit
        """
        (
            marginal_1d, marginal_bins_1d, marginal_2d, marginal_bins_2d, eff_size
        ) = self.marginalize()
        profile_1d, profile_bins_1d, profile_2d, profile_bins_2d = self.profile()
        names_1d = self.likelihood.parameter_names
        names_2d = [
            (names_1d[i], names_1d[j])
            for i in range(len(names_1d) - 1)
            for j in range(i + 1, len(names_1d))
        ]
        return FitResults(
            parameters=names_1d,
            marginal_1d=dict(zip(names_1d, marginal_1d)),
            marginal_1d_bins=dict(zip(names_1d, marginal_bins_1d)),
            marginal_2d=dict(zip(names_2d, marginal_2d)),
            marginal_2d_bins=dict(zip(names_1d, marginal_bins_2d)),
            profile_1d=dict(zip(names_1d, profile_1d)),
            profile_1d_bins=dict(zip(names_1d, profile_bins_1d)),
            profile_2d=dict(zip(names_2d, profile_2d)),
            profile_2d_bins=dict(zip(names_1d, profile_bins_2d)),
            marginal_effective_size=eff_size,
        )
