import torch
import torch.nn.functional as F
import numpy as np

from .likelihood import Likelihood
from .datacard import ReadDataCard
from .predictions import Predictions
from .ewpo import EWPO
from . import sm

class ProfileLikelihood(Likelihood):
    _TOP_PARAMETER_NAMES = ["D6tg", "D6qq18", "D6qq11", "D6qq38", "D6qq31", "D6qt8", "D6qt1", "D6ut8", "D6ut1", "D6qu8", "D6qu1", "D6dt8", "D6dt1", "D6qd8", "D6qd1", "D6tw" , "D6bw" ,"D6phiq3", "D6tz", "D6phiqm", "D6phit", "D6phiphi"]
    _HIGGS_PARAMETER_NAMES = ["D6fg", "D6fb", "D6fphi2", "D6fmu", "D6ftop", "D6fbot", "D6ftau", "D6fww", "D6fbb", "D6fw", "D6fbw", "D6ftg", "D6fwww", "D6fphiQ3", "D6fphiu1", "D6fphid1", "D6fphi1", "D6fLLLL", "D6fphiQ1", "D6fphie1"]
    _SECTOR_PARAMETER_NAMES = {"top": _TOP_PARAMETER_NAMES, "higgs": _HIGGS_PARAMETER_NAMES}

    parameter_names = _TOP_PARAMETER_NAMES
    dims_parameter = len(parameter_names)
    dims_nuisance = 0

    def __init__(self, params: dict, device: torch.device):
        self.sector = params.get("sector", "top")
        if self.sector not in self._SECTOR_PARAMETER_NAMES:
            raise ValueError(
                f"sector={self.sector!r} not recognized; "
                f"available: {list(self._SECTOR_PARAMETER_NAMES)}"
            )
        self.parameter_names = list(self._SECTOR_PARAMETER_NAMES[self.sector])

        # allow the run yaml to further restrict to a subset of the sector's basis,
        # e.g. parameter_names: [D6tz, D6tg, D6phiq3, D6phiqm, D6phit]. Operators
        # omitted here are FIXED AT ZERO (SM) -- not profiled, not marginalized.
        if params.get("parameter_names"):
            unknown = [p for p in params["parameter_names"]
                       if p not in self.parameter_names]
            if unknown:
                raise ValueError(
                    f"parameter_names not in the {self.sector} basis: {unknown}; "
                    f"available: {self.parameter_names}"
                )
            self.parameter_names = list(params["parameter_names"])
        self.dims_parameter = len(self.parameter_names)
        datacard = ReadDataCard(params["datacard"])
        self.device = device
        self.pred = Predictions(device)
        self.ewpo = EWPO(device)
        self.higgsnames = datacard.higgs_names()
        sm_values = torch.tensor([sm.sm_values[key] for key in self.higgsnames], device=device)
        higgs_sm = []
        smeft_matr = self.pred.get_smeft_matrix(datacard.get_data_WCs, self.parameter_names)

        n_meas = len(datacard.all_identifiers)
        n_params = self.dims_parameter
        self.n_groups = len(datacard.identifiers)
        self.smeft_coeffs = torch.zeros(
            (n_meas, n_params, n_params + 1), device=device
        )
        self.smeft_offset = torch.zeros((n_meas, ), device=device)
        self.norm_indices = torch.zeros((n_meas, ), dtype=torch.int64, device=device)
        self.norm_start = torch.zeros((self.n_groups, ), device=device)
        self.bin_widths = torch.zeros((n_meas, ), device=device)
        self.measurements = torch.zeros((n_meas, ), device=device)
        self.backgrounds = torch.zeros((n_meas, ), device=device)
        self.dist_mask = torch.zeros((n_meas, ), dtype = torch.bool, device=device)

        self.decay = [None] * n_meas
        decay = []
        decay_measurement_indices = []

        self.err_theo = torch.zeros((n_meas, ), device=device)
        self.err_pois = torch.zeros((n_meas, 2), device=device)
        self.err_gauss = torch.zeros((n_meas, ), device=device)
        # PATCHED: per-bin syst VECTOR retained for the correlation matrix. Width
        # comes from the datacard's global nuisance ordering -- never hardcoded.
        n_nuis = len(datacard.nuis_order)
        err_syst_list = torch.zeros((n_meas, n_nuis), device=device)

        count = 0
        group_slices = []          # PATCHED-2: contiguous row range per observation
        for group_count, group_id in enumerate(datacard.identifiers):
            bins = datacard.get_subids(group_id)
            group_lo = count
            self.norm_start[group_count] = 0. if len(bins) > 1 else 1.
            for sub_id in bins:
                err_pois = np.array(datacard.poiss_unc(sub_id))
                err_stat = np.array(datacard.stat_unc(sub_id))
                err_syst = np.array(datacard.syst_unc(sub_id))
                err_theo = np.array(datacard.theo_unc(sub_id))
                
                # Make this nicer, where?
                if self.pred.decay_indices(datacard.decay[sub_id]) == [-1]:
                    smeft = torch.tensor(datacard.get_WC_data("WC", sub_id), device=device)
                    for i, (j, k) in enumerate(smeft_matr):
                        self.smeft_coeffs[count, j, k] = smeft[i] * datacard.luminosity[sub_id]
                    self.dist_mask[count] = True
                else:
                    smeft = torch.tensor(datacard.get_WC_data("Higgs", sub_id),device=device)     
                    smeft_ind = (sm_values[:, None] * smeft) * datacard.luminosity[sub_id]
                    split = [s for s in torch.split(smeft_ind, 5) if torch.any(s != 0)][0]
                    higgs_sm.extend(split.unbind(dim=1))
                    decay.extend(self.pred.decay_indices(datacard.decay[sub_id]))
                    decay_measurement_indices.extend([count] * split.shape[1])
                    self.dist_mask[count] = False
                
                self.smeft_offset[count] = datacard.get_pred(sub_id) * datacard.luminosity[sub_id]
                self.norm_indices[count] = group_count
                self.bin_widths[count] = (
                    datacard.get_bin_width(sub_id) if len(bins) > 1 else 0.
                )
                self.measurements[count] = datacard.measurements[sub_id]
                self.backgrounds[count] = datacard.backgrounds[sub_id]
                self.err_theo[count] = np.sum(err_theo)
                self.err_gauss[count] = np.sqrt(np.sum(err_stat**2) + np.sum(err_syst**2))
                self.err_pois[count] = torch.tensor(err_pois, device=device)

                # PATCHED: syst_unc() already returns a full-length vector over the
                # global nuisance ordering, 0.0 at every non-syst position
                # (datacard.py:236 fills only type=="syst"), so no mask is needed.
                err_syst_list[count] = torch.tensor(err_syst, device=device)
                
                count += 1
            group_slices.append((group_lo, count))   # PATCHED-2
        
        #Also for Higgs
        self.higgs_sm = torch.stack(higgs_sm, dim=0) if higgs_sm else torch.full((1, 5), 0.0 ,device=device)
        self.decay = torch.tensor(decay, device=device) if decay else torch.tensor([0], device=device)
        self.decay_measurement_indices = torch.tensor(decay_measurement_indices, device=device) if decay else torch.tensor([0], device=device)
        self.sig_mask = (torch.sum(self.err_pois, 1) == 0)
        self.err_pois = self.err_pois.transpose(0,1)
        self.meas_back_diff = self.measurements - self.backgrounds

        # PATCHED: within-experiment systematic correlation (arXiv:2411.00942).
        # R_ii = 1 exactly; R_ij = rho * (S_i . S_j) / (sigma_i sigma_j), i != j.
        # S_i . S_j is nonzero only for SHARED nuisance positions, i.e. identical
        # type+label+energy+name (datacard.py:255) -- so ATLAS and CMS entries,
        # or differently-named sources, never correlate. Theory (err_theo) is
        # linearly summed and does NOT enter here: the RFit box stays an
        # uncorrelated per-bin plateau.
        self.syst_rho = float(params.get("syst_correlation_rho", 0.99))
        sigma_exp = self.err_gauss.clone()
        sigma_exp_safe = torch.where(sigma_exp > 0, sigma_exp, torch.ones_like(sigma_exp))

        num = torch.matmul(err_syst_list, err_syst_list.t())
        off = self.syst_rho * num / (sigma_exp_safe[:, None] * sigma_exp_safe[None, :])
        eye = torch.eye(n_meas, device=device, dtype=off.dtype)
        corr = eye + off * (1.0 - eye)          # diagonal stays exactly 1
        corr = 0.5 * (corr + corr.t())          # kill roundoff asymmetry

        # PATCHED-2: optional published within-observable correlation block.
        # REPLACES the name-derived off-diagonals for bin pairs inside that
        # observation; name-matching still generates all CROSS-group entries.
        self.n_blocks_substituted = 0
        for group_count, group_id in enumerate(datacard.identifiers):
            block = datacard.bin_correlation(group_id)
            if block is None:
                continue
            lo, hi = group_slices[group_count]
            n_g = hi - lo
            B = torch.tensor(np.asarray(block, dtype=np.float64),
                             device=device, dtype=corr.dtype)
            if B.shape != (n_g, n_g):
                raise ValueError(
                    f"bin_correlation for {group_id} has shape {tuple(B.shape)}, "
                    f"expected ({n_g}, {n_g})")
            B = 0.5 * (B + B.t())
            if not torch.allclose(torch.diagonal(B),
                                  torch.ones(n_g, device=device, dtype=B.dtype),
                                  atol=1e-6):
                raise ValueError(
                    f"bin_correlation for {group_id} must be a CORRELATION matrix "
                    f"(unit diagonal); got diag={torch.diagonal(B).tolist()}")
            corr[lo:hi, lo:hi] = B
            self.n_blocks_substituted += 1

        # PD guard. A substituted (negative) within-group block and the
        # name-derived (positive) cross-group entries come from disjoint data and
        # can conflict; shrinkage toward the identity repairs it and preserves the
        # unit diagonal exactly. Exceeding corr_max_shrinkage is a hard failure.
        corr64 = corr.double()
        corr64 = 0.5 * (corr64 + corr64.t())
        eigs = torch.linalg.eigvalsh(corr64)
        lam_min = eigs.min().item()
        floor = float(params.get("corr_eigenvalue_floor", 1e-3))
        max_a = float(params.get("corr_max_shrinkage", 0.10))
        self.corr_shrinkage = 0.0
        if lam_min < floor:
            a = (floor - lam_min) / (1.0 - lam_min)
            if a > max_a:
                raise ValueError(
                    f"correlation matrix needs shrinkage a={a:.4f} > {max_a} to reach "
                    f"eigenvalue floor {floor:g} (lambda_min={lam_min:.3e}). The "
                    f"within-group blocks and the name-derived cross-group entries "
                    f"are physically inconsistent -- fix the inputs, do not raise "
                    f"the cap.")
            n_r = corr64.shape[0]
            corr64 = (1.0 - a) * corr64 + a * torch.eye(n_r, dtype=corr64.dtype,
                                                        device=device)
            self.corr_shrinkage = a
            print(f"[sfitter] correlation shrunk toward identity by a={a:.4f} "
                  f"(lambda_min {lam_min:.3e} -> {floor:.3e}); "
                  f"{self.n_blocks_substituted} published block(s) substituted")
        cond = (eigs.max() / max(lam_min, 1e-300)).item()
        print(f"[sfitter] correlation matrix cond(R) = {cond:.3e}, "
              f"{self.n_blocks_substituted} published block(s)")

        # keep the PRE-shrinkage matrix so the block-reproduction test is exact
        self.corr = corr
        self.corr_inv = torch.linalg.inv(corr64).to(off.dtype)
        

    def log_likelihood(self, param: torch.Tensor):
        if self.sector == "top":
            return self.log_likelihood_top(param)
        return self.log_likelihood_higgs(param)

    def log_likelihood_higgs(self, param: torch.Tensor):
        batch_shape = param.shape[:-1]
        param = param.reshape(-1, param.shape[-1])

        branching_ratios, deltas = self.pred.compute(param)
        decay_br = branching_ratios[:, self.decay]
        delta_smeft = torch.index_add(
            torch.zeros(
                (param.shape[0], self.measurements.shape[0], self.higgs_sm.shape[1]),
                device=param.device
            ),
            -2,
            self.decay_measurement_indices,
            self.higgs_sm[None, :, :] * decay_br[:, :, None],
        )

        
        # param is already in the same D6fww/D6fbb basis as self.parameter_names
        # and self.smeft_coeffs, so no rotation is needed here (matches how
        # log_likelihood_top feeds param into its own bilinear form).
        param_padded = F.pad(param, (0, 1), value=1.)
        prediction = torch.where(
                self.dist_mask,
                F.bilinear(param, param_padded, self.smeft_coeffs, self.smeft_offset),
                torch.sum(deltas[:, None] * delta_smeft, dim=2) + self.smeft_offset,
                )
        
        background_diff = prediction - self.backgrounds
        measurement_diff = self.measurements - prediction
        x0 = torch.where( (self.meas_back_diff < 0) & (self.backgrounds != 0), background_diff, measurement_diff).abs()
        sign0 = torch.sign(measurement_diff)
        zsigma = torch.where(self.backgrounds != 0, self.err_theo / (self.meas_back_diff + 1e-30) * background_diff, self.err_theo.abs())

        measurements_eps = torch.where(self.measurements != 0, self.measurements, 1e-30)
        scaledata = torch.stack(
            [measurements_eps, self.backgrounds * self.err_pois[1]], dim=-1
        )
        sign_x0 = sign0 * x0
        scalepred = torch.stack(
            [measurements_eps - sign_x0, self.backgrounds + sign_x0], dim=-1
        ) * self.err_pois.T
        poishatshift = zsigma[:, :, None] * self.err_pois.T
        poishatshift = torch.where(scaledata < scalepred, -poishatshift, poishatshift)
        scalepred += poishatshift  
        mask = scalepred < 0
        scaledata = torch.where(mask, scaledata - scalepred, scaledata)
        scalepred = scalepred.clip(min=1e-30)
        ccs = -2 * (
            (scaledata - scalepred) * torch.log(scalepred) +
            torch.lgamma(scalepred + 1) -
            torch.lgamma(scaledata + 1)
        )

        chi_gauss = torch.where(
            (x0 < zsigma) | (self.err_gauss == 0.), 0., (x0 - zsigma) / self.err_gauss
        )
        
        res = 0.
        for cc, m in zip(ccs.unbind(dim=-1), mask.unbind(dim=-1)):
            checkchi = torch.where(
                (self.sig_mask) | (res < 0),
                0.,
                cc
            )
            res += torch.where(
                checkchi <= 0,
                torch.where(self.backgrounds !=0 , -1e-5, 0),
                torch.where(m, 0., 1 / checkchi.clip(min=1e-30))
            )

        chi = torch.where(
            (torch.where(self.sig_mask, res < 0, res <= 0)),
            0,
            sign0 / ((1 / chi_gauss.square().clip(min=1e-30)) + res).clip(min=1e-30).sqrt()
        )

        chi2 = chi.square().sum(dim=-1)   # For full chi2

        #chi2 = torch.matmul(chi, torch.matmul(self.corr_inv, chi.T)) # Try to include corr

        chi2 += self.ewpo.compute_chi2(param) # EWPOs chi2

        #prior = param.square().sum(dim=-1) / 3.**2
        #chi2 += prior

        return -chi2.reshape(batch_shape)


    def log_likelihood_top(self, param: torch.Tensor):
        batch_shape = param.shape[:-1]
        param = param.reshape(-1, param.shape[-1])

        param_padded = F.pad(param, (0, 1), value=1.)
        prediction = F.bilinear(param, param_padded, self.smeft_coeffs, self.smeft_offset)
        norms = torch.index_add(
            self.norm_start.expand(*param.shape[:-1], -1),
            -1,
            self.norm_indices,
            prediction * self.bin_widths
        )
        pred_norm = prediction / norms[..., self.norm_indices]
        resid = self.measurements - pred_norm
        x0 = torch.abs(resid)
        # PATCHED: SIGNED RFit pull. The box clamp is applied PER BIN, before the
        # contraction, so a bin inside its box contributes nothing even through
        # an off-diagonal. torch.sign sits outside the where(), so the zero
        # branch stays exactly 0 and no NaN leaks from err_gauss == 0 bins.
        chi = torch.where(
            (x0 < self.err_theo) | (self.err_gauss == 0.),
            torch.zeros_like(x0),
            torch.sign(resid) * (x0 - self.err_theo) / self.err_gauss
        )
        chi2 = torch.einsum('bi,ij,bj->b', chi, self.corr_inv, chi)
        return -chi2.reshape(batch_shape)

    def log_prior(self, x: torch.Tensor) -> torch.Tensor:

        return torch.zeros_like(x[...,0])

