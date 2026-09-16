from datetime import timedelta
from time import time

import torch
import torch.nn.functional as F

from .stacked import StackedMarginalFlow
from .masked import MaskedStackedMarginalFlow
from .smc_fitter import SMCFitter, L2PI
from .markov import markov_chain, langevin_markov_chain


class CraftFitter(SMCFitter):
    """
    Extends the SMC fitter with a machine-learned transfer step based on normalizing flows.
    Based on 2201.13117. See documentation for a table of settings.
    """
    state_dict_attrs = ["flow"]

    def initialize(self):
        """
        Initializes the network, optimizer and learning rate scheduler. See documentation for
        a table of network settings.
        """
        super().initialize()
        arch_params = self.params["architecture"]
        training_params = self.params["training"]

        self.annealing_schedule = self.get_annealing_schedule(
            temp_steps=self.smc_params["temperature_steps"],
            anneal_steps=self.smc_params["annealing_steps"],
            anneal_beta=self.smc_params["annealing_beta"],
        )
        flow_class = {
            "coupling": StackedMarginalFlow,
            "maf": MaskedStackedMarginalFlow,
        }[arch_params["type"]]
        self.flow = flow_class(
            dims_total = self.likelihood.dims_total,
            dims_parameter = self.likelihood.dims_parameter,
            blocks = len(self.annealing_schedule.beta_likelihood) - 1,
            spline_bins = arch_params["spline_bins"],
            layers = arch_params["layers"],
            hidden_nodes = arch_params["hidden_nodes"],
            activation = arch_params["activation"],
            spline_low = -arch_params["spline_bound"],
            spline_high = arch_params["spline_bound"],
        ).to(self.device)
        n_params = sum(p.numel() for p in self.flow.parameters() if p.requires_grad)
        print(f"  Trainable parameters: {n_params}")

        self.optimizer = torch.optim.Adam(
            self.flow.parameters(),
            lr=training_params["lr"],
            betas=training_params.get("adam_betas", [0.9, 0.999]),
            eps=training_params.get("adam_eps", 1e-6),
            weight_decay=training_params.get("weight_decay", 0.0),
        )

        training_len = (
            training_params["batches"] + len(self.annealing_schedule.beta_likelihood) - 2
        )
        self.lr_sched_mode = training_params["lr_scheduler"]
        if self.lr_sched_mode == "step":
            self.scheduler = torch.optim.lr_scheduler.StepLR(
                self.optimizer,
                step_size=training_params["lr_decay_epochs"],
                gamma=training_params["lr_decay_factor"],
            )
        elif self.lr_sched_mode == "one_cycle":
            self.scheduler = torch.optim.lr_scheduler.OneCycleLR(
                self.optimizer,
                training_params["max_lr"],
                total_steps=training_len,
            )
        elif self.lr_sched_mode == "cosine_annealing":
            self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer=self.optimizer,
                T_max=training_len,
            )
        else:
            raise ValueError(f"Unknown LR scheduler {self.lr_sched_mode}")

    def transport(
        self, x: torch.Tensor, step: int, marginal_mask: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Transport function used at the beginning of SMC temperature steps based on the
        previously trained flow networks.

        Args:
            x: input samples, shape (..., d)
            step: index of the temperature step
            marginal_mask: mask that is True for components kept constant, shape (..., d)
        Returns:
            y: transformed samples, shape (..., d)
            jac: log-jacobian determinant of the transformation, shape (..., )
        """
        with torch.no_grad():
            y, jac = self.flow(
                x[None], slice(step, step + 1), marginal_mask.expand(x.shape)[None]
            )
            return y[0], jac[0]

    def train(self):
        """
        Runs the CRAFT training. See documentation for a table of training settings.
        """
        super().train()

        self.print("Training model")
        start_time = time()

        training_params = self.params["training"]
        batches = training_params["batches"]

        beta_likelihood, beta_prior, beta_latent = (
            torch.tensor(beta, device=self.device) for beta in self.annealing_schedule
        )
        def log_prob_func(xx: torch.Tensor, step: slice):
            xx = xx * self.x_std + self.x_mean
            return (
                beta_likelihood[step,None,None] * self.likelihood.log_likelihood(xx) +
                beta_prior[step,None,None] * self.likelihood.log_prior(xx) +
                beta_latent[step,None,None] * torch.sum((-L2PI - xx.square()) / 2, dim=-1)
            )

        resampling_threshold = self.smc_params["resampling_threshold"]
        mcmc_steps = self.smc_params["mcmc_steps"]
        mcmc_step_size = self.smc_params["mcmc_step_size"]
        mcmc_func = {
            "standard": markov_chain,
            "langevin": langevin_markov_chain,
        }[self.smc_params["mcmc_type"]]

        sub_batches = training_params["sub_batches"]
        sub_batch_size = training_params["sub_batch_size"]
        batch_shape = (3 * sub_batches, sub_batch_size, self.likelihood.dims_total)
        mask_counts = torch.tensor([0,1,2], device=self.device).repeat_interleave(sub_batches)
        x = torch.zeros((0, *batch_shape), device=self.device)
        marginal_mask = torch.zeros((0, *batch_shape), device=self.device, dtype=torch.bool)
        log_w = torch.zeros((0, *batch_shape[:2]), device=self.device)
        w_sum = torch.zeros((0, batch_shape[0], 1), device=self.device)
        w_norm = torch.zeros((0, *batch_shape[:2]), device=self.device)
        acceptance = 0.
        average_loss = 0.
        average_rel_eff_size = 0.
        log_interval = training_params["log_interval"]
        blocks = len(beta_likelihood) - 1
        temp_steps = self.smc_params["temperature_steps"]

        for i in self.progress(range(batches + blocks - 1), leave=False):
            if i < batches:
                x = torch.cat((torch.randn((1, *batch_shape), device=self.device), x), dim=0)
                marginal_mask = F.pad(marginal_mask, pad=(0,0,0,0,0,0,1,0), value=0)
                log_w = F.pad(log_w, pad=(0,0,0,0,1,0), value=0.)
                w_sum = F.pad(w_sum, pad=(0,0,0,0,1,0), value=sub_batch_size)
                w_norm = F.pad(w_norm, pad=(0,0,0,0,1,0), value=1 / sub_batch_size)
                if i >= temp_steps:
                    marginal_mask[0] = torch.rand(
                        (batch_shape[0], 1, batch_shape[2]), device=self.device
                    ).argsort(dim=2) < mask_counts[:,None,None]
                    x[0] = torch.where(
                        marginal_mask[0], x[temp_steps, 0, :3*sub_batches, None], x[0]
                    )
            if i >= blocks:
                x = x[:-1]
                log_w = log_w[:-1]
                w_sum = w_sum[:-1]
                w_norm = w_norm[:-1]
                marginal_mask = marginal_mask[:-1]
            active_blocks = slice(max(i - batches + 1, 0), min(i + 1, blocks))
            active_blocks_shifted = slice(active_blocks.start + 1, active_blocks.stop + 1)
            log_prob_before = log_prob_func(x, active_blocks)
            x, log_jac = self.flow(x, active_blocks, marginal_mask)
            log_prob_after = log_prob_func(x, active_blocks_shifted)
            delta_w = log_prob_after - log_prob_before + log_jac

            loss = - torch.sum(w_norm * delta_w) / sub_batches / 3
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            self.scheduler.step()

            log_w += delta_w.detach()
            x = x.detach()
            w = log_w.exp()
            w_sum_before = w_sum
            w_sum = w.sum(dim=2, keepdim=True)
            w_norm = w / w_sum
            nans = w_norm.isnan().any(dim=2)
            average_loss += loss.item() + (w_sum / w_sum_before).log().sum() / sub_batches / 3

            eff_sample_size = 1 / w_norm.square().sum(dim=2)
            rel_eff_size = eff_sample_size / sub_batch_size
            average_rel_eff_size += rel_eff_size.mean().item()
            needs_resampling = rel_eff_size < resampling_threshold
            if torch.any(needs_resampling):
                #self.print(f"RESAMPLING {torch.count_nonzero(needs_resampling).item()}")
                indices = torch.multinomial(
                    w_norm[needs_resampling], sub_batch_size, replacement=True
                )
                xr = x[needs_resampling]
                x[needs_resampling] = torch.gather(xr, 1, indices[:,:,None].expand(xr.shape))
                log_w[needs_resampling] = torch.log(w_sum[needs_resampling] / sub_batch_size)

            x, acc = mcmc_func(
                x=x,
                log_prob_func=lambda xx: log_prob_func(xx, active_blocks_shifted),
                step_size=mcmc_step_size,
                steps=mcmc_steps,
                marginal_mask=marginal_mask,
            )
            acceptance += acc

            if (i + 1) % log_interval == 0:
                self.print(
                    f"  Batch {i + 1}: avg loss {average_loss / log_interval:.6f}, " +
                    f"acceptance {acceptance / log_interval:.4f}, " +
                    f"rel eff size {average_rel_eff_size / log_interval:.4f}, " +
                    f"lr {self.scheduler.get_last_lr()[0]:.4e}"
                )
                acceptance = 0.
                average_loss = 0.
                average_rel_eff_size = 0.

        self.print(f"  Time: {timedelta(seconds=int(time() - start_time))}")
