import math
from datetime import timedelta
from time import time
from copy import copy
from types import SimpleNamespace

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from tqdm import tqdm

from .fitter import Fitter, FitResults
#from .smc import sequential_monte_carlo
from .flow import ConditionalFlow
from ..util.optimize import maximize
from .markov import MarkovChainFunc, markov_chain, langevin_markov_chain


def softclip(x, coeff=30.):
    return coeff * torch.log(x / coeff + 1)
    #return x

class StepSizeController:
    def __init__(self, step_size, target_acceptance=0.33, adjust_factor=2.):
        self.step_size = step_size
        self.target_acceptance = target_acceptance
        self.adjust_factor = adjust_factor
        self.momentum = 0

    def get(self):
        return self.step_size

    def update(self, acceptance):
        ratio = acceptance / self.target_acceptance - 1
        self.step_size *= self.adjust_factor ** min(max(-1, ratio), 1)


class FlowFitter(Fitter):
    save_attrs = ["x_mean", "x_std", "flow"]

    def initialize(self):
        arch_params = self.params["architecture"]
        self.prescale_params = self.params["prescale"]
        self.pretrain_params = self.params["pretrain"]
        self.training_params = self.params["training"]
        self.sampling_params = self.params["sampling"]
        self.profile_1d_params = self.params["profile_1d"]
        self.profile_2d_params = self.params["profile_2d"]

        self.flow = ConditionalFlow(
            dims_in = self.likelihood.dims_total,
            bins = arch_params["spline_bins"],
            layers = arch_params["layers"],
            units = arch_params["hidden_nodes"],
            activation = nn.LeakyReLU,
            spline_low = -arch_params["spline_bound"],
            spline_high = arch_params["spline_bound"],
        ).to(self.device)
        self.optimizer = torch.optim.Adam(
            self.flow.parameters(), lr=self.training_params["lr"]
        )

    def mc_sample_step(self, x, step_size_controller):
        return x + math.sqrt(
            2 * step_size_controller.get()
        ) * torch.randn_like(x)

    def mc_accept_reject(self, log_prob, log_prob_step, step_size_controller, acceptances):
        accept_prob = torch.exp(log_prob_step - log_prob)
        #print(accept_prob, log_prob_step - log_prob)
        accept_mask = torch.rand_like(accept_prob) < accept_prob
        acc = accept_mask.float().mean().item()
        step_size_controller.update(acc)
        acceptances.append(acc)
        return accept_mask

    def prescale(self):
        self.print("Prescaling")
        start_time = time()

        samples = self.prescale_params["samples"]
        smc_steps = self.prescale_params["smc_steps"]
        mcmc_steps = self.prescale_params["mcmc_steps"]
        resampling_threshold = self.prescale_params["smc_resampling_threshold"]
        step_size = self.prescale_params["step_size"]
        step_adjust_factor = self.prescale_params["step_adjust_factor"]
        target_acceptance = self.prescale_params["target_acceptance"]
        mean_init = self.prescale_params.get("mean_init")
        std_init = self.prescale_params.get("std_init")
        prior_width = self.prescale_params["prior_width"]
        prior_div = 2 * prior_width**2
        prior_norm = - self.likelihood.dims_parameter / 2 * math.log(
            2 * math.pi * prior_width**2
        )
        log_samples = math.log(samples)

        if mean_init is None:
            x_mean = torch.zeros(self.likelihood.dims_parameter, device=self.device)
        else:
            x_mean = torch.tensor(self.prescale_params["mean_init"], device=self.device)
        if std_init is None:
            x_std = torch.ones(self.likelihood.dims_parameter, device=self.device)
        else:
            x_std = torch.tensor(self.prescale_params["std_init"], device=self.device)

        acceptances = []
        self.step_size_controller = StepSizeController(
            step_size, target_acceptance, step_adjust_factor
        )
        x = prior_width * torch.randn(
            (samples, self.likelihood.dims_parameter), device=self.device
        )
        log_q = prior_norm - torch.sum(x.square() / prior_div, dim=1)
        log_p = self.likelihood.log_likelihood(x_mean + x_std * x)
        log_w = torch.zeros_like(x[:, 0])
        for i in self.progress(range(smc_steps), leave=False):
            log_w += (1 / smc_steps) * (log_p - log_q)
            log_w_sum = log_w.logsumexp(dim=0) #, keepdim=True)
            log_w_norm = log_w - log_w_sum

            eff_sample_size = 1 / (2 * log_w_norm).exp().sum() #dim=0)
            if eff_sample_size / samples < resampling_threshold or i == smc_steps - 1:
                indices = torch.multinomial(log_w_norm.exp(), samples, replacement=True)
                x = x[indices]
                log_p = log_p[indices]
                log_w[:] = log_w_sum - log_samples

            x_step = self.mc_sample_step(x, self.step_size_controller)
            log_p_step = self.likelihood.log_likelihood(x_mean + x_std * x_step)
            log_q = prior_norm - torch.sum(x.square() / prior_div, dim=1)
            log_q_step = prior_norm - torch.sum(x_step.square() / prior_div, dim=1)
            beta_pi = (i + 1) / smc_steps
            beta_qi = 1 - beta_pi
            log_prob = beta_pi * log_p + beta_qi * log_q
            log_prob_step = beta_pi * log_p_step + beta_qi * log_q_step

            accept_mask = self.mc_accept_reject(
                log_prob, log_prob_step, self.step_size_controller, acceptances
            )
            x = torch.where(accept_mask[:, None], x_step, x)
            log_p = torch.where(accept_mask, log_p_step, log_p)

        x_pp = x_mean + x_std * x
        x_mean = x_pp.mean(dim=0)
        x_std = x_pp.std(dim=0)
        x = (x_pp - x_mean) / x_std
        log_prob = log_p

        for i in self.progress(range(mcmc_steps), leave=False):
            x_step = self.mc_sample_step(x, self.step_size_controller)
            log_prob_step = self.likelihood.log_likelihood(x_mean + x_std * x_step)

            accept_mask = self.mc_accept_reject(
                log_prob, log_prob_step, self.step_size_controller, acceptances
            )
            x = torch.where(accept_mask[:, None], x_step, x)
            log_prob = torch.where(accept_mask, log_prob_step, log_prob)

        x_pp = x_mean + x_std * x
        self.x_mean = x_pp.mean(dim=0)
        self.x_std = x_pp.std(dim=0)
        print(self.x_std)

        self.print(f"  Acceptance: {np.mean(acceptances):.3f}")
        self.print(f"  Time:       {timedelta(seconds=int(time() - start_time))}")
        return (x_pp - self.x_mean) / self.x_std

    def pretrain(self, x):
        self.print("Pretraining flow network")
        start_time = time()

        epochs = self.pretrain_params["epochs"]
        log_interval = self.pretrain_params["log_interval"]
        batch_size = self.pretrain_params["batch_size"]
        steps = self.pretrain_params["mcmc_steps"]

        with torch.no_grad():
            x_pp = self.x_mean + self.x_std * x
            log_prob = self.likelihood.log_likelihood(x)

        for epoch in self.progress(range(epochs), leave=False):
            losses = []
            acceptances = []
            perm = torch.randperm(x.shape[0], device=self.device)
            for batch_idx in perm.split(batch_size):
                self.optimizer.zero_grad()
                loss = - self.flow.log_prob(x[batch_idx]).mean()
                loss.backward()
                self.optimizer.step()
                losses.append(loss.item())

                for i in range(steps):
                    x_step = self.mc_sample_step(x, self.step_size_controller)
                    x_pp_step = self.x_mean + self.x_std * x_step
                    with torch.no_grad():
                        log_prob_step = self.likelihood.log_likelihood(x_pp_step)
                    accept_mask = self.mc_accept_reject(
                        log_prob, log_prob_step, self.step_size_controller, acceptances
                    )
                    x = torch.where(accept_mask[:, None], x_step, x)
                    log_prob = torch.where(accept_mask, log_prob_step, log_prob)

            if (epoch + 1) % log_interval == 0:
                self.print(
                    f"  Epoch {epoch + 1}: loss {np.mean(losses):.4f}, " +
                    f"acc {np.min(acceptances):.3f} < {np.mean(acceptances):.3f} " +
                    f"< {np.max(acceptances):.3f}"
                )

        self.print(f"  Time:       {timedelta(seconds=int(time() - start_time))}")

    def main_training(self):
        self.print("Training flow network")
        start_time = time()

        batch_size = self.training_params["batch_size"]
        batches = self.training_params["batches"]
        log_interval = self.training_params["log_interval"]
        losses = []
        ess = []
        ess2 = []
        acceptances = []
        buffer_losses = []

        total_steps = self.training_params["steps"]
        mcmc_steps = self.training_params["mcmc_steps"]
        mcmc_step_size = self.training_params["mcmc_step_size"]
        step_size_adjust = self.training_params["step_size_adjust"]
        mcmc_func = {
            "standard": markov_chain,
            "langevin": langevin_markov_chain,
        }[self.training_params["mcmc_type"]]
        dbeta = 2 / total_steps
        #dbeta = 1 / total_steps
        #mcmc_step_sizes = np.full(total_steps, mcmc_step_size)
        step_size_controllers = [
            copy(self.step_size_controller) for _ in range(total_steps - 1)
        ]

        max_buffer_size = self.training_params["buffer_size"]
        min_buffer_size = self.training_params["min_buffer_size"]
        buffer_batches = self.training_params["buffer_batches"]
        buffer_replacement = self.training_params["buffer_replacement"]
        buffer_x = torch.zeros(
            (max_buffer_size * batch_size, self.likelihood.dims_parameter), device=self.device
        )
        buffer_w = torch.zeros((max_buffer_size * batch_size,), device=self.device)
        buffer_log_q = torch.zeros((max_buffer_size * batch_size,), device=self.device)
        buffer_size = 0
        buffer_index = 0

        for batch in self.progress(range(batches), leave=False):
            self.optimizer.zero_grad()
            with torch.no_grad():
                x, log_q = self.flow.sample(n=batch_size, device=self.device)
                x_pp = self.x_mean + self.x_std * x
                log_p = self.likelihood.log_likelihood(x_pp)
                #log_w = log_q.clone()
            w0 = torch.exp(log_p - log_q)
            ess.append((w0.sum().square() / w0.square().sum()).item())

            log_w = 0.
            for i in range(total_steps):
                log_w += dbeta * (log_p - log_q)

                if i == total_steps - 1:
                    continue

                beta_pi = 2 * (i + 1) / total_steps
                beta_qi = 1 - beta_pi
                log_prob = beta_pi * log_p + beta_qi * log_q
                x_step = self.mc_sample_step(x, step_size_controllers[i])
                with torch.no_grad():
                    log_q_step = self.flow.log_prob(x_step)
                    x_pp_step = self.x_mean + self.x_std * x_step
                    log_p_step = self.likelihood.log_likelihood(x_pp_step)
                log_prob_step = beta_pi * log_p_step + beta_qi * log_q_step
                accept_mask = self.mc_accept_reject(
                    log_prob, log_prob_step, step_size_controllers[i], acceptances
                )
                x = torch.where(accept_mask[:, None], x_step, x)
                log_q = torch.where(accept_mask, log_q_step, log_q)
                log_p = torch.where(accept_mask, log_p_step, log_p)

            log_sum_w = torch.logsumexp(log_w, dim=0)
            w = torch.exp(log_w - log_sum_w) * batch_size
            #w_clip = torch.clip(w, max=10.)
            w_clip = softclip(w)
            #w_clip /= w_clip.mean()
            ess2.append((w.sum().square() / w.square().sum()).item())
            log_g = self.flow.log_prob(x)
            loss = - torch.mean(w_clip * log_g)
            loss.backward()
            losses.append(loss.item())
            self.optimizer.step()

            if (batch + 1) % log_interval == 0:
                self.print(
                    f"  Batch {batch + 1}: loss {np.mean(losses):.4f}, " +
                    f"ESS {np.mean(ess):.2f}, " +
                    f"ESS2 {np.mean(ess2):.2f}" +
                    (
                        f", acc {np.min(acceptances):.3f} < {np.mean(acceptances):.3f} " +
                        f"< {np.max(acceptances):.3f}"
                        if total_steps > 1 else ""
                    ) +
                    (f", buf {np.mean(buffer_losses):.4f}" if len(buffer_losses) > 0 else "")
                )
                losses = []
                ess = []
                ess2 = []
                acceptances = []
                buffer_losses = []

            if buffer_batches == 0:
                continue

            buf_start_index = buffer_index * batch_size
            buf_stop_index = buf_start_index + batch_size
            buffer_x[buf_start_index:buf_stop_index] = x
            buffer_w[buf_start_index:buf_stop_index] = w
            buffer_log_q[buf_start_index:buf_stop_index] = log_q
            buffer_index = (buffer_index + 1) % max_buffer_size
            if buffer_size < max_buffer_size:
                buffer_size += 1

            if buffer_size < min_buffer_size:
                continue

            buf_end = buffer_size * batch_size
            indices = torch.multinomial(
                buffer_w[:buf_end], batch_size * buffer_batches, buffer_replacement
            )
            samples_w = buffer_w[:buf_end][indices]
            samples_x = buffer_x[:buf_end][indices]
            samples_log_q = buffer_log_q[:buf_end][indices]

            w_new = []
            log_q_new = []
            for batch_w, batch_x, batch_log_q in zip(
                samples_w.split(batch_size),
                samples_x.split(batch_size),
                samples_log_q.split(batch_size)
            ):
                self.optimizer.zero_grad()
                log_q = self.flow.log_prob(batch_x)
                log_w_corr = batch_log_q - log_q.detach()
                w_corr = log_w_corr.exp()
                w_new.append(batch_w * w_corr)
                log_q_new.append(log_q.detach())
                #w_clip = torch.clip(w_corr / w_corr.mean(), max=10.)
                w_clip = softclip(w_corr / w_corr.mean())
                loss = - torch.mean(w_clip * log_q)
                loss.backward()
                self.optimizer.step()
                buffer_losses.append(loss.item())
            buffer_w[:buf_end][indices] = torch.cat(w_new, dim=0)
            buffer_log_q[:buf_end][indices] = torch.cat(log_q_new, dim=0)

        self.print(f"  Time:       {timedelta(seconds=int(time() - start_time))}")

    def train(self):
        x_prescale = self.prescale()
        self.pretrain(x_prescale)
        self.main_training()

    def collect_samples(self):
        self.print("Collecting samples")
        start_time = time()

        batch_size = self.sampling_params["batch_size"]
        marginal_bins_1d = self.sampling_params["marginal_bins_1d"]
        marginal_bins_2d = self.sampling_params["marginal_bins_2d"]
        nbest = self.sampling_params.get("profile_leaderboard_size", 20)
        profile_bins_1d = self.sampling_params["profile_points_1d"]
        profile_bins_2d = self.sampling_params["profile_points_2d"]
        weight_clip = self.sampling_params["weight_clip"]

        param_range = torch.arange(self.likelihood.dims_parameter, device=self.device)
        param_indices_2d = torch.cartesian_prod(param_range, param_range)
        param_indices_2d = param_indices_2d[param_indices_2d[:,0] < param_indices_2d[:,1]]

        w_sum = 0.
        w2_sum = 0.
        hists_1d = 0.
        hists_2d = 0.
        for batch in self.progress(range(self.sampling_params["batches"]), leave=False):
            # Draw weighted samples using the trained flow
            with torch.no_grad():
                x, log_sample = self.flow.sample(n=batch_size, device=self.device)
                x = self.x_mean + self.x_std * x
                log_likeli = self.likelihood.log_likelihood(x).flatten()
            w = torch.exp(log_likeli - log_sample)

            # Initialize weight normalization and binning after the first batch
            if batch == 0:
                w_norm = w.mean()
                x_sorted, sort_indices = x.sort(dim=0)
                w_sorted = w[sort_indices]
                w_cumsum = w_sorted.cumsum(dim=0)
                w_cumsum = w_cumsum / w_cumsum[-1]
                index_low = torch.argmax(
                    (w_cumsum > self.sampling_params["lower_bound_quantile"]).long(), dim=0
                )
                index_high = torch.argmax(
                    (w_cumsum > self.sampling_params["upper_bound_quantile"]).long(), dim=0
                )
                x_low = torch.gather(x_sorted, 0, index_low[None, :])[0]
                x_high = torch.gather(x_sorted, 0, index_high[None, :])[0]
                x_diff = x_high - x_low
                margin_factor = self.sampling_params["margin_factor"]
                x_low -= x_diff * margin_factor
                x_high += x_diff * margin_factor
                x_diff = x_high - x_low
                bin_widths_marg_1d = x_diff / marginal_bins_1d
                bin_widths_marg_2d = x_diff / marginal_bins_2d
                bin_widths_prof_1d = x_diff / profile_bins_1d
                bin_widths_prof_2d = x_diff / profile_bins_2d

                marg_1d_bins = torch.arange(
                    marginal_bins_1d + 1, device=self.device
                ) * bin_widths_marg_1d[:, None] + x_low[:, None]
                marg_2d_bins = torch.arange(
                    marginal_bins_2d + 1, device=self.device
                ) * bin_widths_marg_2d[:, None] + x_low[:, None]
                prof_1d_bins = torch.arange(
                    profile_bins_1d + 1, device=self.device
                ) * bin_widths_prof_1d[:, None] + x_low[:, None]
                prof_2d_bins = torch.arange(
                    profile_bins_2d + 1, device=self.device
                ) * bin_widths_prof_2d[:, None] + x_low[:, None]
                prof_1d_points = prof_1d_bins[:, :-1] + 0.5 * bin_widths_prof_1d[:, None]
                prof_2d_points = prof_2d_bins[:, :-1] + 0.5 * bin_widths_prof_2d[:, None]

                w_low = torch.quantile(
                    w[w != 0], self.sampling_params["weight_lower_bound_quantile"]
                ) / w_norm
                w_high = torch.quantile(
                    w, self.sampling_params["weight_upper_bound_quantile"]
                ) / w_norm
                log_w_low = w_low.log10()
                log_w_high = w_high.log10()
                w_bin_count = self.sampling_params["weight_bins"]
                w_bins_lin = torch.linspace(
                    w_low,
                    w_high,
                    w_bin_count + 1,
                    device=self.device
                )
                w_hist_lin = torch.zeros_like(w_bins_lin[:-1])
                w_bins_log = torch.logspace(
                    log_w_low,
                    log_w_high,
                    w_bin_count + 1,
                    device=self.device
                )
                w_hist_log = torch.zeros_like(w_bins_log[:-1])

            # Normalize the weights and compute sum w and sum w^2 for effective sample size
            w = torch.clip(w / w_norm, max=weight_clip)
            w_sum += w.sum()
            w2_sum += w.square().sum()

            # Compute histogram over weights
            w_hist_lin += torch.histc(w, bins=w_bin_count, min=w_low, max=w_high)
            w_hist_log += torch.histc(w.log10(), bins=w_bin_count, min=log_w_low, max=log_w_high)

            # Compute 1d weighted histograms for all parameters
            bin_indices_marg_1d = ((x - x_low) / bin_widths_marg_1d + 1).floor().long().clamp(
                min=0, max=marginal_bins_1d + 1
            )
            n_hists_1d = bin_indices_marg_1d.shape[1]
            hists_1d += torch.zeros(
                (marginal_bins_1d + 2, n_hists_1d), device=self.device
            ).scatter_reduce_(
                dim=0,
                index=bin_indices_marg_1d,
                src=w[:, None].expand(-1, n_hists_1d),
                reduce="sum",
            ).T[:, 1:-1]

            # Compute 2d weighted histograms for all pairs of parameters
            n_bins = marginal_bins_2d + 2
            bin_indices_marg_1d = ((x - x_low) / bin_widths_marg_2d + 1).floor().long().clamp(
                min=0, max=marginal_bins_2d + 1
            )
            bin_indices_marg_2d = (
                n_bins * bin_indices_marg_1d[:, param_indices_2d[:,0]] +
                bin_indices_marg_1d[:, param_indices_2d[:,1]]
            )
            n_hists_2d = bin_indices_marg_2d.shape[1]
            hists_2d += torch.zeros(
                (n_bins**2, n_hists_2d), device=self.device
            ).scatter_reduce_(
                dim=0,
                index=bin_indices_marg_2d,
                src=w[:, None].expand(-1, n_hists_2d),
                reduce="sum",
            ).T.reshape(-1, n_bins, n_bins)[:, 1:-1, 1:-1]

            # Sort samples for efficient profiling
            log_likeli_sorted, log_likeli_argsort = torch.sort(log_likeli)
            log_likeli_sorted = F.pad(log_likeli_sorted, pad=(1,0), value=-np.inf)
            x_sorted = F.pad(x[log_likeli_argsort], pad=(0,0,1,0), value=0)
            index_range = torch.arange(1, x.shape[0] + 1, device=self.device)[:, None]

            # Find the points with the highest likelihood in each 1d bin
            bin_indices_prof_1d = (
                (x_sorted[1:] - x_low) / bin_widths_prof_1d + 1
            ).floor().long().clamp(min=0, max=profile_bins_1d + 1)
            indices_max = torch.zeros(
                (profile_bins_1d + 2, n_hists_1d), device=self.device, dtype=torch.long
            ).scatter_reduce_(
                dim=0,
                index=bin_indices_prof_1d,
                src=index_range.expand(-1, n_hists_1d),
                reduce="amax"
            ).T[:, 1:-1]
            x_max_1d_batch = torch.gather(
                input=x_sorted[:, None, :].expand(-1, profile_bins_1d, -1),
                dim=0,
                index=indices_max[:, :, None].expand(-1, -1, x.shape[1]),
            )
            #log_likeli_max_1d_batch = torch.gather(
            #    input=log_likeli_sorted[:, None].expand(-1, profile_bins_1d),
            #    dim=0,
            #    index=indices_max
            #)
            dim_range = torch.arange(x_max_1d_batch.shape[0])
            x_max_1d_batch[dim_range, :, dim_range] = prof_1d_points
            with torch.no_grad():
                batch_shape = x_max_1d_batch.shape[:-1]
                lb = []
                for xb in x_max_1d_batch.flatten(end_dim=-2).split(batch_size, dim=0):
                    lb.append(self.likelihood.log_likelihood(self.x_mean + self.x_std * xb))
                log_likeli_max_1d_batch = torch.cat(lb, dim=0).reshape(batch_shape)
            if batch == 0:
                #x_max_1d = x_max_1d_batch
                #log_likeli_max_1d = log_likeli_max_1d_batch
                x_max_1d = x_max_1d_batch[None].expand(nbest, -1, -1, -1)
                log_likeli_max_1d = log_likeli_max_1d_batch[None].expand(nbest, -1, -1)
            else:
                #mask = log_likeli_max_1d_batch > log_likeli_max_1d
                #x_max_1d = torch.where(
                #    mask[:, :, None], x_max_1d_batch, x_max_1d
                #)
                #log_likeli_max_1d = torch.where(
                #    mask, log_likeli_max_1d_batch, log_likeli_max_1d
                #)
                log_likeli_max_1d, order = torch.cat((
                    log_likeli_max_1d, log_likeli_max_1d_batch[None]
                ), dim=0).sort(dim=0, descending=True)
                log_likeli_max_1d = log_likeli_max_1d[:nbest]
                x_max_1d = torch.cat(
                    (x_max_1d, x_max_1d_batch[None]), dim=0
                ).gather(dim=0, index=order[..., None].expand(-1, -1, -1, x.shape[-1]))[:nbest]

            # Find the points with the highest likelihood in each 2d bin
            n_bins = profile_bins_2d + 2
            bin_indices_prof_1d = (
                (x_sorted[1:] - x_low) / bin_widths_prof_2d + 1
            ).floor().long().clamp(min=0, max=profile_bins_2d + 1)
            bin_indices_prof_2d = (
                n_bins * bin_indices_prof_1d[:, param_indices_2d[:,0]] +
                bin_indices_prof_1d[:, param_indices_2d[:,1]]
            )
            indices_max = torch.zeros(
                (n_bins**2, n_hists_2d), device=self.device, dtype=torch.long
            ).scatter_reduce_(
                dim=0,
                index=bin_indices_prof_2d,
                src=index_range.expand(-1, n_hists_2d),
                reduce="amax"
            ).T.reshape(-1, n_bins, n_bins)[:, 1:-1, 1:-1]
            x_max_2d_batch = torch.gather(
                input=x_sorted[:, None, None, :].expand(
                    -1, profile_bins_2d, profile_bins_2d, -1
                ),
                dim=0,
                index=indices_max[:, :, :, None].expand(-1, -1, -1, x.shape[1]),
            )
            #log_likeli_max_2d_batch = torch.gather(
            #    input=log_likeli_sorted[:, None, None].expand(
            #        -1, profile_bins_2d, profile_bins_2d
            #    ),
            #    dim=0,
            #    index=indices_max
            #)
            hist_range = torch.arange(param_indices_2d.shape[0], device=self.device)
            indices0 = param_indices_2d[:, 0]
            indices1 = param_indices_2d[:, 1]
            x_max_2d_batch[hist_range, :, :, indices0] = prof_2d_points[indices0, :, None]
            x_max_2d_batch[hist_range, :, :, indices1] = prof_2d_points[indices1, None, :]
            with torch.no_grad():
                batch_shape = x_max_2d_batch.shape[:-1]
                lb = []
                for xb in x_max_2d_batch.flatten(end_dim=-2).split(batch_size, dim=0):
                    lb.append(self.likelihood.log_likelihood(self.x_mean + self.x_std * xb))
                log_likeli_max_2d_batch = torch.cat(lb, dim=0).reshape(batch_shape)
            if batch == 0:
                x_max_2d = x_max_2d_batch
                log_likeli_max_2d = log_likeli_max_2d_batch
            else:
                mask = log_likeli_max_2d_batch > log_likeli_max_2d
                x_max_2d = torch.where(
                    mask[:, :, :, None], x_max_2d_batch, x_max_2d
                )
                log_likeli_max_2d = torch.where(
                    mask, log_likeli_max_2d_batch, log_likeli_max_2d
                )

        eff_size = w_sum.square() / w2_sum

        self.print(f"  Time:       {timedelta(seconds=int(time() - start_time))}")
        self.print(f"  N_eff:      {eff_size:.0f}")

        return SimpleNamespace(
            marginal_1d_hist=hists_1d,
            marginal_1d_bins=marg_1d_bins,
            marginal_2d_hist=hists_2d,
            marginal_2d_bins=marg_2d_bins,
            profile_1d_x=x_max_1d,
            profile_1d_points=prof_1d_points,
            profile_1d_bins=prof_1d_bins,
            profile_1d_ll=log_likeli_max_1d,
            profile_2d_x=x_max_2d,
            profile_2d_points=prof_2d_points,
            profile_2d_bins=prof_2d_bins,
            param_indices_2d=param_indices_2d,
            eff_size_rel=eff_size,
            w_bins_lin=w_bins_lin,
            w_hist_lin=w_hist_lin,
            w_bins_log=w_bins_log,
            w_hist_log=w_hist_log,
        )

    def profile_1d(self, x: torch.Tensor, points: torch.Tensor) -> torch.Tensor:
        self.print("Profiling (1D)")
        start_time = time()

        batch_size = self.profile_1d_params["batch_size"]
        #n_params = x.shape[0]
        #n_bins = x.shape[1]
        n_params = x.shape[1]
        n_bins = x.shape[2]
        nbest = 20
        x = x.reshape(-1, n_params)

        marginal_idx = torch.arange(
            n_params, device=self.device
        ).repeat_interleave(n_bins, dim=0).repeat(nbest)[:,None]
        marginal_mask = torch.zeros(
            (marginal_idx.shape[0], self.likelihood.dims_total),
            device=self.device,
            dtype=torch.bool,
        )
        marginal_mask.scatter_(
            1,
            marginal_idx,
            torch.tensor([[True]], device=self.device).expand(*marginal_idx.shape)
        )
        profile_1d = []
        for x_batch, marg_mask in zip(
            self.progress(x.split(batch_size), leave=False), marginal_mask.split(batch_size)
        ):
            if self.verbose:
                progress = tqdm(total=self.profile_1d_params["gd_steps"], leave=False)
                callback = lambda i: progress.update(1)
            else:
                callback = None
            log_likeli_max = maximize(
                x=(x_batch - self.x_mean) / self.x_std,
                log_prob_func=lambda xx: self.likelihood.log_likelihood(
                    xx * self.x_std + self.x_mean
                ),
                learning_rate=self.profile_1d_params["gd_learning_rate"],
                steps=self.profile_1d_params["gd_steps"],
                marginal_mask=marg_mask,
                optimizer=self.profile_1d_params["optimizer"],
                step_callback = callback,
            )
            profile_1d.append(log_likeli_max.exp())
            if self.verbose:
                progress.close()

        self.print(f"  Time: {timedelta(seconds=int(time() - start_time))}")
        #return torch.cat(profile_1d, dim=0).reshape(-1, n_bins)
        return torch.cat(profile_1d, dim=0).reshape(nbest, -1, n_bins).amax(dim=0)

    def profile_2d(
        self, x: torch.Tensor, points: torch.Tensor, param_indices: torch.Tensor
    ) -> torch.Tensor:
        self.print("Profiling (2D)")
        start_time = time()

        batch_size = self.profile_2d_params["batch_size"]
        n_params = x.shape[3]
        n_bins = x.shape[1]
        x = x.reshape(-1, n_params)

        marginal_idx = param_indices.repeat_interleave(n_bins * n_bins, dim=0)
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
        profile_2d = []
        for x_batch, marg_mask in zip(
            self.progress(x.split(batch_size), leave=False), marginal_mask.split(batch_size)
        ):
            if self.verbose:
                progress = tqdm(total=self.profile_2d_params["gd_steps"], leave=False)
                callback = lambda i: progress.update(1)
            else:
                callback = None
            log_likeli_max = maximize(
                x=(x_batch - self.x_mean) / self.x_std,
                log_prob_func=lambda xx: self.likelihood.log_likelihood(
                    xx * self.x_std + self.x_mean
                ),
                learning_rate=self.profile_2d_params["gd_learning_rate"],
                steps=self.profile_2d_params["gd_steps"],
                marginal_mask=marg_mask,
                optimizer=self.profile_2d_params["optimizer"],
                step_callback = callback,
            )
            profile_2d.append(log_likeli_max.exp())
            if self.verbose:
                progress.close()

        self.print(f"  Time: {timedelta(seconds=int(time() - start_time))}")

        return torch.cat(profile_2d, dim=0).reshape(-1, n_bins, n_bins)

    def fit(self) -> FitResults:
        """
        Runs marginalization and profiling. Constructs FitResults object containing the
        results.

        Returns:
            Results of the fit
        """
        result = self.collect_samples()
        marginal_1d = result.marginal_1d_hist.cpu().numpy()
        marginal_bins_1d = result.marginal_1d_bins.cpu().numpy()
        marginal_2d = result.marginal_2d_hist.cpu().numpy()
        marginal_bins_2d = result.marginal_2d_bins.cpu().numpy()
        profile_bins_1d = result.profile_1d_bins.cpu().numpy()
        profile_bins_2d = result.profile_2d_bins.cpu().numpy()
        eff_size = result.eff_size_rel.cpu().numpy()

        profile_1d = self.profile_1d(
            result.profile_1d_x, result.profile_1d_points
        ).cpu().numpy()
        #profile_1d = result.profile_1d_ll.exp().cpu().numpy()
        profile_2d = self.profile_2d(
            result.profile_2d_x, result.profile_2d_points, result.param_indices_2d
        ).cpu().numpy()

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
            w_bins_lin=result.w_bins_lin.cpu().numpy(),
            w_hist_lin=result.w_hist_lin.cpu().numpy(),
            w_bins_log=result.w_bins_log.cpu().numpy(),
            w_hist_log=result.w_hist_log.cpu().numpy(),
        )
