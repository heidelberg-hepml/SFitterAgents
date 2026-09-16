import numpy as np
import torch
import torch.nn.functional as F
from . import sm


class Predictions:
    def __init__(self, device: torch.device):
        # All Wilson coefficients from the Higgs, Di-Boson, EWPO
        
        (
            d6fg, d6fb, d6fphi2, d6fmu, d6ftop, d6fbot,
            d6ftau, d6fww, d6fbb, d6fw, d6fbw, d6ftg,
            d6fwww, d6fphiQ3, d6fphiu1, d6fphid1, d6fphi1,
            d6fLLLL, d6fphiQ1, d6fphie1, one
        ) = torch.eye(21)[:, :, None]
        # d6fww/d6fbb assigned directly as basis vectors, matching the D6fww/D6fbb
        # names the datacards actually declare -- no d6fplus/d6fminus rotation needed.

        # These are not in the final results, not sure why
        d6fphi3 = 0.0
        d6fphi4 = 0.0
        
        d6brg = self.w_glgl(sm.mh, one, d6fg, d6fphi2, d6ftop, d6fphi4)
        d6brz = self.w_hzzs(sm.mh, one, d6fb, d6fw, d6fbb, d6fww, d6fbw, d6fphi2, d6fphi4) 
        d6brw = self.w_hwws(sm.mh, one, d6fw, d6fww, d6fphi2, d6fphi4) 
        d6brga = self.w_gaga(sm.mh, one, d6fphi2, d6fphi4, d6ftop, d6fbb, d6fww, d6fbw)
        d6brzga = self.w_zga(sm.mh, one, d6fw, d6fb, d6fbb, d6fww, d6fbw, d6fphi2, d6ftop, d6fphi4)
        d6brb = self.w_hbbbar(one, d6fphi2, d6fphi4, d6fbot)
        d6brtau = self.w_htata(one, d6fphi2, d6fphi4, d6ftau)
        d6brmu = self.w_hmumu(one, d6fphi2, d6fphi4, d6fmu)

        gamparttot = (
            sm.brsmw
            + sm.brsmz
            + sm.brsmb
            + sm.brsmc
            + sm.brsms
            + sm.brsmtau
            + sm.brsmmu
            + sm.brsmg
            + sm.brsmga
            + sm.brsmzga
        ) * sm.gammasmh

        gamd6w = sm.brsmw * sm.gammasmh * d6brw
        gamd6z = sm.brsmz * sm.gammasmh * d6brz
        gamd6b = sm.brsmb * sm.gammasmh * d6brb
        gamd6c = sm.brsmc * sm.gammasmh * d6brb
        gamd6s = sm.brsms * sm.gammasmh * d6brb
        gamd6tau = sm.brsmtau * sm.gammasmh * d6brtau
        gamd6mu = sm.brsmmu * sm.gammasmh * d6brmu
        gamd6g = sm.brsmg * sm.gammasmh * d6brg
        gamd6ga = sm.brsmga * sm.gammasmh * d6brga
        gamd6zga = sm.brsmzga * sm.gammasmh * d6brzga

        gammah = (
            (sm.gammasmh - gamparttot) * one.T * one
            + gamd6w
            + gamd6z
            + gamd6b
            + gamd6c
            + gamd6s
            + gamd6tau
            + gamd6mu
            + gamd6g
            + gamd6ga
            + gamd6zga
        )

        self.coeffs = torch.stack([
            gammah, d6brw, d6brz, d6brb, d6brtau, d6brg, d6brga, d6brzga, d6brmu
        ], dim=0).to(device)
    
        # leaving out brs, brc, brmu for now since they do not seem to be used
        self.gamma_prefactors = torch.tensor([
            sm.brsmw * sm.gammasmh,
            sm.brsmz * sm.gammasmh,
            sm.brsmb * sm.gammasmh,
            sm.brsmtau * sm.gammasmh,
            sm.brsmg * sm.gammasmh,
            sm.brsmga * sm.gammasmh,
            sm.brsmzga * sm.gammasmh,
            sm.brsmmu * sm.gammasmh,
        ], device=device)
        self.index_dict = {name: i for i, name in enumerate(
            ["brw", "brz", "brb", "brtau", "brg", "brga", "brzga", "brmu", "bri"]
        )}

    def get_smeft_matrix(self , sub_WCs, names):        
        pars = {name: i for i, name in enumerate(names)}
        smeft_matr = [[pars.get(sub_name, -1) for sub_name in name.split("x")] + [-1] * (1 - name.count("x")) for name in sub_WCs.keys()]
        return smeft_matr

    def zeta_p(x):
        zeta_p = 1.0 + np.sqrt(1.0 - x)
        return zeta_p

    def zeta_m(x):
        zeta_m = 1.0 - np.sqrt(1.0 - x)
        return zeta_m

    def zf(self, x):
        zi = 0 + 1.0j
        if x >= 1.0:
            zf_result = np.arcsin(np.sqrt(1.0 / x)) ** 2
        else:
            zf_result = (
                0.25 * (np.log(self.zeta_p(x) / self.zeta_m(x)) - zi * np.pi) ** 2
            )
        return zf_result

    def zg(self, x):
        zi = 0 + 1.0j
        if x >= 1.0:
            zg_result = np.sqrt(x - 1.0) * np.arcsin(1.0 / np.sqrt(x))
        else:
            zg_result = (
                0.5
                * np.sqrt(1.0 - x)
                * (np.log(self.zeta_p(x) / self.zeta_m(x)) - zi * np.pi)
            )
        return zg_result

    def zIfun1(self, a, b):
        zp1 = a * b / 2.0 / (a - b)
        zp2 = a**2 * b**2 / 2 / (a - b) ** 2 * (self.zf(a) - self.zf(b))
        zp3 = a**2 * b / (a - b) ** 2 * (self.zg(a) - self.zg(b))
        zIfun1_result = zp1 + zp2 + zp3
        return zIfun1_result

    def zIfun2(self, a, b):
        zIfun2_result = -a * b / 2.0 / (a - b) * (self.zf(a) - self.zf(b))
        return zIfun2_result

    def w_glgl(self, xmh, one, d6fg, d6fphi2, d6ftop, d6fphi4):
        taut = 4.0 * sm.xmt**2 / xmh**2

        zft = self.zf(taut)
        zf_tot = taut * (1.0 + (1.0 - taut) * zft)
        b_s = (1e-6 * d6fg) * sm.vev

        w = (
            -sm.vev * b_s
            + zf_tot
            * (
                one
                - sm.vev**2 * (1e-6 * d6fphi2) / 2.0
                - 1.0 / np.sqrt(2.0) * sm.vev**3 / sm.xmt * (1e-6 * d6ftop)
                - sm.vev**2 * (1e-6 * d6fphi4) / 4.0
            )
        )
        return w.T * w / zf_tot ** 2

    def w_hzzs_ff(self, xmh, gz0, gz1, gz2):
        ep = sm.xmz / xmh

        ep_sq = ep**2
        ep_cu = ep**3

        gz00 = gz0.T * gz0
        gz01 = gz0.T * gz1
        gz02 = gz0.T * gz2
        gz11 = gz1.T * gz1
        gz12 = gz1.T * gz2
        gz22 = gz2.T * gz2

        if ep >= 0.49 and ep <= 0.51:
            ep = 0.51
        if ep >= 0.5 and ep <= 1.0:
            return (
                - (1 - ep_sq) / (240.0 * ep_sq) * (
                    120 * gz00
                    - 780 * ep_sq * gz00
                    + 2820 * ep_sq**2 * gz00
                    - 360 * gz01
                    + 2120 * ep_sq * gz01
                    - 7240 * ep_sq**2 * gz01
                    - 760 * ep_cu**2 * gz01
                    + 276 * gz11
                    - 1519 * ep_sq * gz11
                    + 5061 * ep_sq**2 * gz11
                    - 669 * ep_cu**2 * gz11
                    - 89 * ep_sq**4 * gz11
                    + 21600 * ep_sq**2 * gz02
                    - 38880 * ep_cu**2 * gz02
                    - 32320 * ep_sq**2 * gz12
                    + 49760 * ep_cu**2 * gz12
                    + 3680 * ep_sq**4 * gz12
                    + 27200 * ep_sq**2 * gz22
                    - 128320 * ep_cu**2 * gz22
                    + 128000 * ep_sq**4 * gz22
                )
                + (
                    np.arccos((-1.0 + 3.0 * ep_sq) / (2.0 * ep_cu))
                    / (4.0 * np.sqrt(-1.0 + 4.0 * ep_sq))
                ) * (
                    6 * gz00
                    - 48 * ep_sq * gz00
                    + 120 * ep_sq**2 * gz00
                    - 16 * gz01
                    + 128 * ep_sq * gz01
                    - 304 * ep_sq**2 * gz01
                    - 96 * ep_cu**2 * gz01
                    + 11 * gz11
                    - 90 * ep_sq * gz11
                    + 216 * ep_sq**2 * gz11
                    + 88 * ep_cu**2 * gz11
                    - 144 * ep_sq * gz02
                    + 1152 * ep_sq**2 * gz02
                    - 2016 * ep_cu**2 * gz02
                    + 224 * ep_sq * gz12
                    - 1744 * ep_sq**2 * gz12
                    + 2816 * ep_cu**2 * gz12
                    + 576 * ep_sq**4 * gz12
                    - 160 * ep_sq * gz22
                    + 1760 * ep_sq**2 * gz22
                    - 6208 * ep_cu**2 * gz22
                    + 7776 * ep_sq**4 * gz22
                )
                - np.log(ep) / 4.0 * (
                    6 * gz00
                    - 36 * ep_sq * gz00
                    + 24 * ep_sq**2 * gz00
                    - 16 * gz01
                    + 96 * ep_sq * gz01
                    + 11 * gz11
                    - 68 * ep_sq * gz11
                    - 42 * ep_sq**2 * gz11
                    - 24 * ep_cu**2 * gz11
                    - 144 * ep_sq * gz02
                    + 864 * ep_sq**2 * gz02
                    - 288 * ep_cu**2 * gz02
                    + 224 * ep_sq * gz12
                    - 1296 * ep_sq**2 * gz12
                    - 96 * ep_cu**2 * gz12
                    - 160 * ep_sq * gz22
                    + 1440 * ep_sq**2 * gz22
                    - 4416 * ep_cu**2 * gz22
                    + 864 * ep_sq**4 * gz22
                )
            )
        else:
            return 0.0

    def w_hzzs(self, xmh, one, d6fb, d6fw, d6fbb, d6fww, d6fbw, d6fphi2, d6fphi4):
        gz0 = one + sm.vev**2 * 1e-6 * (d6fphi4 - d6fphi2) / 2.0
        gz1 = 0.5 * xmh**2 * (sm.sw2 * (1e-6 * d6fb) + sm.cw2 * (1e-6 * d6fw))
        gz2 = 0.5 * xmh**2 * (
            sm.sw2**2 * (1e-6 * d6fbb)
            + sm.cw2**2 * (1e-6 * d6fww)
            + sm.sw2 * sm.cw2 * (1e-6 * d6fbw)
        )
        ffaczzs = self.w_hzzs_ff(xmh, gz0, gz1, gz2)

        # Dividing by SM
        gz0 = torch.tensor([[1.0]])
        gz1 = torch.tensor([[0.0]])
        gz2 = torch.tensor([[0.0]])
        ffsm = self.w_hzzs_ff(xmh, gz0, gz1, gz2)

        return ffaczzs / ffsm

    def w_hwws_ff(self, xmh, g0, gw, gww):
        ep = sm.xmw / xmh

        ep_sq = ep**2
        ep_cu = ep**3

        g00 = g0.T * g0
        g01 = g0.T * gw
        g02 = g0.T * gww
        g11 = gw.T * gw
        g12 = gw.T * gww
        g22 = gww.T * gww

        if ep >= 0.49 and ep <= 0.51:
            ep = 0.51
        if ep >= 0.5 and ep <= 1.0:
            return (
                - abs(1 - ep_sq) / (24.0 * ep_sq) * (
                    24 * g00
                    - 156 * ep_sq * g00
                    + 564 * ep_sq**2 * g00
                    - 160 * ep_sq * g01
                    - 124 * ep_sq**2 * g01
                    - 52 * ep_cu**2 * g01
                    - 6 * ep_sq * g11
                    + 376 * ep_sq**2 * g11
                    - 137 * ep_cu**2 * g11
                    - 5 * ep_sq**4 * g11
                    + 2160 * ep_sq**2 * g02
                    - 3888 * ep_cu**2 * g02
                    - 1072 * ep_sq**2 * g12
                    + 440 * ep_cu**2 * g12
                    + 152 * ep_sq**4 * g12
                    + 1360 * ep_sq**2 * g22
                    - 6416 * ep_cu**2 * g22
                    + 6400 * ep_sq**4 * g22
                )
                + (
                    np.arccos((-1.0 + 3.0 * ep_sq) / (2.0 * ep_cu))
                    / (4.0 * np.sqrt(-1.0 + 4.0 * ep_sq))
                ) * (
                    12 * g00
                    - 96 * ep_sq * g00
                    + 240 * ep_sq**2 * g00
                    + 8 * g01
                    - 28 * ep_sq * g01
                    - 64 * ep_sq**2 * g01
                    - 96 * ep_cu**2 * g01
                    - 32 * ep_sq * g11
                    + 163 * ep_sq**2 * g11
                    - 32 * ep_cu**2 * g11
                    - 144 * ep_sq * g02
                    + 1152 * ep_sq**2 * g02
                    - 2016 * ep_cu**2 * g02
                    + 80 * ep_sq * g12
                    - 520 * ep_sq**2 * g12
                    + 512 * ep_cu**2 * g12
                    + 288 * ep_sq**4 * g12
                    - 80 * ep_sq * g22
                    + 880 * ep_sq**2 * g22
                    - 3104 * ep_cu**2 * g22
                    + 3888 * ep_sq**4 * g22
                )
                - np.log(ep) / 4.0 * (
                    12 * g00
                    - 72 * ep_sq * g00
                    + 48 * ep_sq**2 * g00
                    + 8 * g01
                    - 12 * ep_sq * g01
                    + 72 * ep_sq**2 * g01
                    - 32 * ep_sq * g11
                    + 27 * ep_sq**2 * g11
                    - 18 * ep_cu**2 * g11
                    - 144 * ep_sq * g02
                    + 864 * ep_sq**2 * g02
                    - 288 * ep_cu**2 * g02
                    + 80 * ep_sq * g12
                    - 360 * ep_sq**2 * g12
                    - 240 * ep_cu**2 * g12
                    - 80 * ep_sq * g22
                    + 720 * ep_sq**2 * g22
                    - 2208 * ep_cu**2 * g22
                    + 432 * ep_sq**4 * g22
                )
            )
        else:
            return 0.0

    def w_hwws(self, xmh, one, d6fw, d6fww, d6fphi2, d6fphi4):
        g0 = one + sm.vev**2 * 1e-6 * (d6fphi4 - d6fphi2) / 2.0
        gw = (1e-6 * d6fw) * xmh**2
        gww = (1e-6 * d6fww) * xmh**2
        ffacwws = self.w_hwws_ff(xmh, g0, gw, gww)

        # Dividing by SM
        g0 = torch.tensor([[1.0]])
        gw = torch.tensor([[0.0]])
        gww = torch.tensor([[0.0]])
        ffsm = self.w_hwws_ff(xmh, g0, gw, gww)

        return ffacwws / ffsm

    def w_gaga(self, xmh, one, d6fphi2, d6fphi4, d6ftop, d6fbb, d6fww, d6fbw):
        tauw = 4 * sm.xmw**2 / xmh**2
        taut = 4 * sm.xmt**2 / xmh**2
        zfw = self.zf(tauw)
        zft = self.zf(taut)
        zf1 = 2.0 + 3.0 * tauw + 3.0 * tauw * (2.0 - tauw) * zfw
        zf2 = -2.0 * taut * (1.0 + (1.0 - taut) * zft)

        zfsum = zf1 * (
            one
            - sm.vev**2 * (1e-6 * d6fphi2) / 2.0
            + sm.vev**2 * (1e-6 * d6fphi4) / 2.0
        ) + 4.0 / 3.0 * zf2 * (
            one
            - sm.vev**2 * (1e-6 * d6fphi2) / 2.0
            - 1.0 / np.sqrt(2.0) * sm.vev**3 / sm.xmt * (1e-6 * d6ftop)
            - sm.vev**2 * (1e-6 * d6fphi4) / 4.0
        )

        g_hgaga = (
            -sm.g
            * sm.xmw
            * sm.sw2
            / 2.0
            * ((1e-6 * d6fbb) + (1e-6 * d6fww) - (1e-6 * d6fbw))
        )

        # Dividing by SM
        zfsum_sm = zf1 + 4.0 / 3.0 * zf2
        w = g_hgaga + sm.alpha / (8.0 * np.pi * sm.vev) * zfsum
        return w.T * w / (
            sm.alpha / (8.0 * np.pi * sm.vev) * zfsum_sm
        ) ** 2

    def w_zga(self, xmh, one, d6fw, d6fb, d6fbb, d6fww, d6fbw, d6fphi2, d6ftop, d6fphi4):
        xz = 4 * sm.xmz**2 / xmh**2
        tau_t = 4 * sm.xmt**2 / xmh**2
        xlam_t = 4 * sm.xmt**2 / sm.xmz**2
        tau_w = 4 * sm.xmw**2 / xmh**2
        xlam_w = 4 * sm.xmw**2 / sm.xmz**2

        g_hzga1 = (
            sm.g
            * sm.xmw
            * np.sqrt(sm.sw2)
            * 1e-6 * (d6fw - d6fb) 
            / 2
            / np.sqrt(sm.cw2)
        )
        g_hzga2 = (
            sm.g
            * sm.xmw
            * np.sqrt(sm.sw2 / sm.cw2)
            * (
                sm.sw2 * 1e-6 * d6fbb
                - sm.cw2 * 1e-6 * d6fww
                + (sm.cw2 - sm.sw2) / 2 * 1e-6 * d6fbw
            )
        )

        xNc = 3.0
        et = 2.0 / 3.0
        t3 = 0.5

        zAt = (
            xNc
            * (-2)
            * et
            * (t3 - 2 * et * sm.sw2)
            / (np.sqrt(sm.sw2 * sm.cw2))
            * (self.zIfun1(tau_t, xlam_t) - self.zIfun2(tau_t, xlam_t))
        )
        zAw = -np.sqrt(sm.cw2 / sm.sw2) * (
            4 * (3 - sm.sw2 / sm.cw2) * self.zIfun2(tau_w, xlam_w)
            + ((1 + 2 / tau_w) * sm.sw2 / sm.cw2 - (5 + 2 / tau_w))
            * self.zIfun1(tau_w, xlam_w)
        )
        zA = zAt * (
            one
            - sm.vev**2 * (1e-6 * d6fphi2) / 2
            - 1 / np.sqrt(2) * sm.vev**3 / sm.xmt * (1e-6 * d6ftop)
            - sm.vev**2 * (1e-6 * d6fphi4) / 4
        ) + zAw * (
            one - sm.vev**2 * (1e-6 * d6fphi2) / 2 + sm.vev**2 * (1e-6 * d6fphi4) / 2
        )

        zA_sm = zAt + zAw
        w = (
            g_hzga1
            + 2 * g_hzga2
            + sm.alpha / (2 * np.sqrt(2) * np.pi * sm.vev) * zA
        )
        return w.T * w / (sm.alpha / (2 * np.sqrt(2) * np.pi * sm.vev) * zA_sm) ** 2

    def _w_fermion_pair(self, one, d6fphi2, d6fphi4, d6f_yukawa, mass):
        w = (
            one
            - sm.vev**2 * (1e-6 * d6fphi2) / 2.0
            - sm.vev**2 * (1e-6 * d6fphi4) / 4.0
            - 1.0 / np.sqrt(2.0) * sm.vev**3 / mass * (1e-6 * d6f_yukawa)
        )
        return w.T * w

    def w_hbbbar(self, one, d6fphi2, d6fphi4, d6fbot):
        return self._w_fermion_pair(one, d6fphi2, d6fphi4, d6fbot, sm.xmb)

    def w_htata(self, one, d6fphi2, d6fphi4, d6ftau):
        return self._w_fermion_pair(one, d6fphi2, d6fphi4, d6ftau, sm.xmtau)

    def w_hmumu(self, one, d6fphi2, d6fphi4, d6fmu):
        return self._w_fermion_pair(one, d6fphi2, d6fphi4, d6fmu, sm.xmmu)

    def decay_indices(self, decay_names: list[str]) -> list[int]:
        return [self.index_dict[name] if name in self.index_dict else -1 for name in decay_names]

    def compute(self, param):
        param_padded = F.pad(param, (0, 1), value=1.)
        results = F.bilinear(param_padded, param_padded, self.coeffs)
        gamma_tot = results[:, :1]
        gamma = results[:, 1:] * self.gamma_prefactors
        branching_ratios = F.pad(gamma / gamma_tot, (0, 1), value=0.)
        
        # In order: ggF, ttH, VBF, WH, ZH
        csgdelta = results[:, 5]
        cstthdelta = torch.ones_like(csgdelta)  
        csvbfdelta = sm.vbfwcontr * results[:, 1] + sm.vbfzcontr *results[:, 2]
        cswhdelta = results[:, 1]
        cszhdelta = results[:, 2]

        deltas = torch.stack([
            csgdelta, cstthdelta, csvbfdelta, cswhdelta, cszhdelta
        ], dim=1)

        return branching_ratios, deltas
