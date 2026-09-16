import math
from datetime import timedelta
from time import time

import torch
import torch.nn.functional as F
import numpy as np
import vegas

from .fitter import Fitter, FitResults
from ..util.optimize import maximize

class VegasFitter(Fitter):
    def initialize(self):
        self.marginal_params = self.params.get("marginalize", {})
        self.profile_params = self.params.get("profile", {})
        self.profile_1d_params = {**self.profile_params, **self.params.get("profile_1d", {})}
        self.profile_2d_params = {**self.profile_params, **self.params.get("profile_2d", {})}

    def train(self):
        self.print("Training VEGAS")
        start_time = time()

        n_bins = 64

        dims = self.likelihood.dims_total
        rng = np.random.default_rng()
        m = vegas.AdaptiveMap(
            grid=[[-10, 10]] * dims, ninc=n_bins
        )
        for n in [100000]*30:
            x = np.empty((n, dims), float)
            jac = np.empty(n, float)
            y = rng.random((n, self.likelihood.dims_total))
            m.map(y, x, jac)
            w = jac * torch.exp(
                self.likelihood.log_likelihood(torch.tensor(x, device=self.device))
            ).cpu().numpy()
            m.add_training_data(y, w**2)
            m.adapt(alpha=0.3)
        self.vegas_grid = torch.tensor(m.extract_grid(), device=self.device)
        self.vegas_bin_widths = self.vegas_grid[:, 1:] - self.vegas_grid[:, :-1]
        print(self.vegas_bin_widths)
        self.vegas_log_probs = torch.log(1 / (self.vegas_bin_widths * n_bins))

        self.print(f"  Time:       {timedelta(seconds=int(time() - start_time))}")

    def sample_vegas(self, n_samples: int) -> tuple[torch.Tensor, torch.Tensor]:
        n_bins = self.vegas_grid.shape[1] - 1
        n_dims = self.vegas_grid.shape[0]
        bin_indices = torch.randint(0, n_bins, (n_samples, n_dims), device=self.device)[:, :, None]
        r = torch.rand((n_samples, n_dims), device=self.device)
        bin_widths = torch.gather(
            self.vegas_bin_widths[None].expand(n_samples, -1, -1), 2, bin_indices
        )[:, :, 0]
        log_probs = torch.gather(
            self.vegas_log_probs[None].expand(n_samples, -1, -1), 2, bin_indices
        )[:, :, 0].sum(dim=1)
        bin_offsets = torch.gather(
            self.vegas_grid[None].expand(n_samples, -1, -1), 2, bin_indices
        )[:, :, 0]
        x = bin_offsets + r * bin_widths
        return x, log_probs

    def marginalize(self) -> tuple[np.ndarray, list[np.ndarray], list[np.ndarray], float]:
        self.print("Marginalizing")
        start_time = time()

        log_weight_sum = None
        log_square_weight_sum = None
        eff_size = 0.
        marginal_samples = []
        marginal_weights = []
        marginal_log_likelihood = []
        for i in range(1):
            x, log_sample = self.sample_vegas(100000)
            print(log_sample)
            with torch.no_grad():
                log_likeli = self.likelihood.log_likelihood(x).flatten()
            log_w = log_likeli - log_sample
            w = log_w.exp()
            print(w.std() / w.mean())

            marginal_samples.append(x[:,:self.likelihood.dims_parameter])
            marginal_weights.append(1.0 + 0.0 * log_w.exp())
            marginal_log_likelihood.append(log_likeli)

            if log_weight_sum is None:
                log_weight_sum = log_w.logsumexp(dim=0)
                log_square_weight_sum = (2 * log_w).logsumexp(dim=0)
            else:
                log_weight_sum = torch.logaddexp(log_weight_sum, log_w.logsumexp(dim=0))
                log_square_weight_sum = torch.logaddexp(
                    log_square_weight_sum, (2 * log_w).logsumexp(dim=0)
                )
            eff_size_prev = eff_size
            eff_size = torch.exp(2 * log_weight_sum - log_square_weight_sum).item()

        marginal_samples = torch.cat(marginal_samples, dim=0)
        marginal_weights = torch.cat(marginal_weights, dim=0)
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
        marginal_weights = marginal_weights.cpu().numpy()

        n_bins = self.marginal_params.get("n_bins")
        n_bins_1d = n_bins or self.marginal_params["n_bins_1d"]
        n_bins_2d = n_bins or self.marginal_params["n_bins_2d"]
        bins_1d = np.linspace(lower_bounds, upper_bounds, n_bins_1d + 1, axis=1)
        bins_2d = np.linspace(lower_bounds, upper_bounds, n_bins_2d + 1, axis=1)

        self.print(f"  Time:       {timedelta(seconds=int(time() - start_time))}")
        self.print(f"  N_eff/N:    {eff_size / len(marginal_samples)}")

        n_params = self.likelihood.dims_parameter
        marginal_1d = [
            np.histogram(
                marginal_samples[:, i], bins_1d[i], weights=marginal_weights
            )[0] for i in range(n_params)
        ]
        marginal_2d = [
            np.histogram2d(
                marginal_samples[:, i],
                marginal_samples[:, j],
                (bins_2d[i], bins_2d[j]),
                weights=marginal_weights,
            )[0]
            for i in range(n_params - 1)
            for j in range(i + 1, n_params)
        ]
        return marginal_1d, bins_1d, marginal_2d, bins_2d, eff_size

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
        profile_1d, bins_1d = self.profile_1d_histogram()
        self.print(f"  Time: {timedelta(seconds=int(time() - start_time))}")

        self.print("Profiling (2D)")
        start_time = time()
        profile_2d, bins_2d = self.profile_2d_histogram()
        self.print(f"  Time: {timedelta(seconds=int(time() - start_time))}")

        return profile_1d, bins_1d, profile_2d, bins_2d

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
                x=x,
                log_prob_func=lambda xx: self.likelihood.log_likelihood(
                    xx
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
                x=x,
                log_prob_func=lambda xx: self.likelihood.log_likelihood(
                    xx
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
