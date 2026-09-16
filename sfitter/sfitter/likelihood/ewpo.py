import torch
import torch.nn.functional as F
from . import sm

class EWPO:
    def __init__(self, device = torch.device):
        # Most of this is directly copied from SFitter for now, can put this into sm.py later
        self.qu =  2./3.
        self.qd = -1./3.
        self.qe = -1.

        self.gLu = 1./2. - self.qu * sm.sw2
        self.gRu = -self.qu * sm.sw2
        self.gLd = -1./2. - self.qd * sm.sw2
        self.gRd = -self.qd * sm.sw2
        self.gLnu = 1./2.
        self.gRnu = 0.
        self.gLe = -1./2. - self.qe*sm.sw2
        self.gRe = -self.qe * sm.sw2
        
        # EWPO_SM
        self.GamZ_sm    = 2.4945
        self.sigh0_sm   = 41.488
        self.Rl_sm      = 20.752
        self.AFBl_sm    = .0163
        self.AlLEP_sm   = .1476
        self.AlSLD_sm   = self.AlLEP_sm
        self.Rb_sm      = .21578
        self.Rc_sm      = .17224
        self.AFBb_sm    = .1035
        self.AFBc_sm    = .0740
        self.Ab_sm      = .93466
        self.Ac_sm      = .6682
        self.shiftMW_sm = 80.367
        self.GamW_sm    = 2.0892
        self.BRWlnu_sm  = .1087

        # Define the experimental values for the EWPOs
        self.data = torch.tensor([2.4952, 41.54, 20.767, .0171, .1465, .1513, .21692, .1721, .0992, .0707, .923, .67, 80.379, 2.085, .1086], device=device)

        self.err_gauss = torch.tensor([.0023, .037, .025, .0010, .0033, .0021, .00066, .0030, .0016, .0035, .020, .027, 0.012, 0.042, 0.0009], device=device)

        self.err_theo = torch.tensor([0.0009, 0.008, 0.010, 0.00007, 0.0003, 0.0003, 0.00002, 0.00003, 0.0002, 0.0002, 0.000061, 0.0001, 0.006, 0.001, 0.000065], device=device)

        
        # Correlations taken from the fortran code
        corr = torch.zeros((15, 15), device = device)
        """
        corr[0,0] = 1.1010787732927034
        corr[1,0] = 0.33933820872851794
        corr[2,0] = -0.06701235691381727
        corr[3,0] = -0.009091957559422987
        corr[0,1] = 0.33933820872851794
        corr[1,1] = 1.1395125870958867
        corr[2,1] = -0.2109897050367873
        corr[3,1] = -0.019670513630820965
        corr[0,2] = -0.06701235691381727
        corr[1,2] = -0.21098970503678727
        corr[2,2] = 1.042229748557718
        corr[3,2] = 0.059831841220194394
        corr[0,3] = -0.009091957559422985
        corr[1,3] = -0.019670513630820962
        corr[2,3] = 0.05983184122019439
        corr[3,3] = 1.0034958820627942
        corr[4,4] = 1.
        corr[5,5] = 1.
        corr[6,6] = 1.056724272260261
        corr[7,6] = 0.18075913960417764
        corr[8,6] = 0.1074934271838703
        corr[9,6] = -0.0871483315498916
        corr[10,6] = 0.07319199364537304
        corr[11,6] = -0.03706354282499387
        corr[6,7] = 0.18075913960417764
        corr[7,7] = 1.038211442722387
        corr[8,7] = -0.02019003221813814
        corr[9,7] = -0.012651838969267791
        corr[10,7] = -0.03263902603651426
        corr[11,7] = 0.05936058772414478
        corr[6,8] = 0.1074934271838703
        corr[7,8] = -0.020190032218138133
        corr[8,8] = 1.0396118813741015
        corr[9,8] = -0.16445734554894548
        corr[10,8] = -0.05590909837903124
        corr[11,8] = -0.003178963190532863
        corr[6,9] = -0.08714833154989161
        corr[7,9] = -0.01265183896926779
        corr[8,9] = -0.16445734554894548
        corr[9,9] = 1.0329414801710872
        corr[10,9] = 0.028469041686571966
        corr[11,9] = -0.04007785741303736
        corr[6,10] = 0.07319199364537306
        corr[7,10] = -0.03263902603651426
        corr[8,10] = -0.055909098379031255
        corr[9,10] = 0.02846904168657197
        corr[10,10] = 1.0240774100502565
        corr[11,10] = -0.11811420709720657
        corr[6,11] = -0.03706354282499386
        corr[7,11] = 0.05936058772414477
        corr[8,11] = -0.0031789631905328607
        corr[9,11] = -0.04007785741303736
        corr[10,11] = -0.11811420709720656
        corr[11,11] = 1.0196716436855682
        corr[12,12] = 1.
        corr[13,13] = 1.
        corr[14,14] = 1.
        """
        # Correlations from datacard, these are probably the ones used in the end right?
        
        corr[0,0] = 1            
        corr[0,1] = -0.297
        corr[0,2] = 0.004
        corr[0,3] = 0.003
        corr[1,0] = -0.297
        corr[1,1] = 1
        corr[1,2] = 0.183
        corr[1,3] = 0.006
        corr[2,0] = 0.004
        corr[2,1] = 0.183
        corr[2,2] = 1
        corr[2,3] = -0.056
        corr[3,0] = 0.003
        corr[3,1] = 0.006
        corr[3,2] = -0.056
        corr[3,3] = 1
        corr[4,4] = 1
        corr[5,5] = 1
        corr[6,6] = 1
        corr[6,7] = -0.18
        corr[6,8] = -0.1
        corr[6,9] = 0.07
        corr[6,10] = -0.08
        corr[6,11] = 0.04
        corr[7,6] = -0.18
        corr[7,7] = 1
        corr[7,8] = 0.04
        corr[7,10] = 0.04
        corr[7,11] = -0.06
        corr[8,6] = -0.1
        corr[8,7] = 0.04
        corr[8,8] = 1
        corr[8,9] = 0.15
        corr[8,10] = 0.06
        corr[8,11] = 0.01
        corr[9,6] = 0.07
        corr[9,8] = 0.15
        corr[9,9] = 1
        corr[9,10] = -0.02
        corr[9,11] = 0.04
        corr[10,6] = -0.08
        corr[10,7] = 0.04
        corr[10,8] = 0.06
        corr[10,9] = -0.02
        corr[10,10] = 1
        corr[10,11] = 0.11
        corr[11,6] = 0.04
        corr[11,7] = -0.06
        corr[11,8] = 0.01
        corr[11,9] = 0.04
        corr[11,10] = 0.11
        corr[11,11,] = 1
        corr[12,12] = 1
        corr[13,13] = 1
        corr[14,14] = 1
        
        self.corr = corr

        # d6fww/d6fbb (positions 7,8, matching predictions.py and the datacard
        # naming) are unpacked for positional alignment with param's 21 columns
        # but unused below -- EWPO has no dependence on these operators.
        (
            d6fg, d6fb, d6fphi2, d6fmu, d6ftop, d6fbot,
            d6ftau, d6fww, d6fbb, d6fw, d6fbw, d6ftg,
            d6fwww, d6fphiQ3, d6fphiu1, d6fphid1, d6fphi1,
            d6fLLLL, d6fphiQ1, d6fphie1, one
        ) = torch.eye(21)[:,]

        d6fg = d6fg*10
        d6fb = d6fb*10
        d6ftg = d6ftg*10
        d6fmu = d6fmu/100
        d6ftop = d6ftop*10
        d6fphiQ3 = d6fphiQ3/10
        d6fphiu1 = d6fphiu1/10
        d6fphid1 = d6fphid1/10
        d6fphi1 = d6fphi1/10
        d6fLLLL = d6fLLLL/100
        d6fphiQ1 = d6fphiQ1/10
        d6fphie1 = d6fphie1/10

        dS, dT, dU, dGf, dMW = self.STUGfMW(d6fbw, d6fphi1, d6fLLLL)
        dgLu, dgLd, dgLnu, dgLe, dgRu, dgRd, dgRnu, dgRe = self.dgLR(dS, dT, dGf, d6fphiQ1, d6fphiQ3, d6fphiu1, d6fphid1, d6fphie1)
        dgWLud_til, dgWLenu_til, dgWRud_til, dgWRenu_til, dgWLud, dgWLenu, dgWRud, dgWRenu = self.dgWLR(dGf, dMW, d6fphiQ3)

        dGamZ = self.dGamZ(dgLe, dgRe, dgLu, dgRu, dgLd, dgRd, dgLnu)

        GamZ = self.GamZ(one, dGamZ)
        sigh0 = self.sigh0(one, dGamZ, dgLe, dgRe, dgLu, dgRu, dgLd, dgRd)
        Rl = self.Rl(one, dgLe, dgRe, dgLu, dgRu, dgLd, dgRd)
        AFBl = self.AFBL(one, dgLe, dgRe)
        AlLEP = self.AlLEP(one, dgLe, dgRe)
        AlSLD = self.AlSLD(one, dgLe, dgRe)
        Rb = self.Rb(one, dgLd, dgRd, dgLu, dgRu)
        Rc = self.Rc(one, dgLu, dgLd, dgRu, dgRd)
        AFBb = self.AFBb(one, dgLd, dgRd, dgLe, dgRe)
        AFBc = self.AFBc(one, dgLe, dgRe, dgLu, dgRu)
        Ab = self.Ab(one, dgLd, dgRd)
        Ac = self.Ac(one, dgLu, dgRu)
        shiftMW = self.shiftMW(one, dMW)
        GamW = self.GamW(one, dgWLud, dgWLenu, dMW)
        BRWlnu = self.BRWlnu(one, dgWLud, dgWLenu)

        self.ewpo_coeffs = torch.stack([GamZ, sigh0, Rl, AFBl, AlLEP, AlSLD, Rb, Rc, AFBb, AFBc, Ab, Ac, shiftMW, GamW, BRWlnu], dim=0).to(device)


    def dg_til(self, d6fphiQ1, d6fphiQ3, d6fphiu1, d6fphid1, d6fphie1):
        dgLu_til  = -sm.vev**2 / 8 * (1e-6 * (4 * d6fphiQ1 - d6fphiQ3))
        dgLd_til  = -sm.vev**2 / 8 * (1e-6 * (4 * d6fphiQ1 + d6fphiQ3))
        dgLnu_til = 0.  # no fphiL1, fphiL3 for universal couplings
        dgLe_til  = 0.
        dgRu_til = -sm.vev**2 / 2 * (1e-6 * d6fphiu1)
        dgRd_til = -sm.vev**2 / 2 * (1e-6 * d6fphid1)
        dgRnu_til = 0.
        dgRe_til = -sm.vev**2 /2 * (1e-6 * d6fphie1)

        return dgLu_til, dgLd_til, dgLnu_til, dgLe_til, dgRu_til, dgRd_til, dgRnu_til, dgRe_til

    def STUGfMW(self, d6fbw, d6fphi1, d6fLLLL):
        dS = - sm.alpha * 4 * 3.14159 * sm.vev**2 * (1e-6 * d6fbw)
        dT = -0.5 * sm.vev**2 * (1e-6 * d6fphi1)
        dU = torch.zeros_like(dT)
        dGf = -2 * (1e-6 * d6fLLLL) * sm.vev**2 + 0 # last 0 is where fphiL1,3 would go
        dMW = 0.5 * sm.cw2 / (sm.cw2 - sm.sw2) * dT - 0.25 / (sm.cw2 - sm.sw2) * dS + 0.125 / sm.sw2 * dU - 0.5 * sm.sw2 / (sm.cw2 - sm.sw2) * dGf

        return dS, dT, dU, dGf, dMW

    def dgi(self, dS, dT, dGf):
        dg1 = 0.5 * (dT - dGf)                             #here dT is alpha*dt, dGf is dGf/Gf 
        dg2 = sm.sw2 / (sm.cw2 - sm.sw2) * (sm.cw2 * (dT - dGf) - 0.25 / sm.sw2 * dS)   # here dT is alpha*dT, dS is alpha*dS, dGf is dGf/Gf 
        return dg1, dg2

    def dgLR(self, dS, dT, dGf, d6fphiQ1, d6fphiQ3, d6fphiu1, d6fphid1, d6fphie1):
        dg1, dg2 = self.dgi(dS, dT, dGf)
        dgLu_til, dgLd_til, dgLnu_til, dgLe_til, dgRu_til, dgRd_til, dgRnu_til, dgRe_til = self.dg_til(d6fphiQ1, d6fphiQ3, d6fphiu1, d6fphid1, d6fphie1)

        dgLu = self.gLu * dg1 + self.qu * dg2 + dgLu_til
        dgLd = self.gLd * dg1 + self.qd * dg2 + dgLd_til
        dgLnu = self.gLnu * dg1 + 0 * dg2 + dgLnu_til
        dgLe = self.gLe * dg1 + self.qe * dg2 + dgLe_til
        
        dgRu = self.gRu * dg1 + self.qu * dg2 + dgRu_til
        dgRd = self.gRd * dg1 + self.qd * dg2 + dgRd_til
        dgRnu = self.gRnu * dg1 + 0 * dg2 + dgRnu_til
        dgRe = self.gRe * dg1 + self.qe * dg2 + dgRe_til

        return dgLu, dgLd, dgLnu, dgLe, dgRu, dgRd, dgRnu, dgRe

    def dgWLR(self, dGf, dMW, d6fphiQ3):
        dgw = dMW - 1/2 * dGf

        dgWLud_til = sm.vev**2 / 4 * (1e-6 * d6fphiQ3)
        dgWLenu_til = 0.                #not including fphiud1
        dgWRud_til = 0.                 #not including fphiL3, vev**2/4.*fphiL3
        dgWRenu_til = 0.

        dgWLud = dgw + dgWLud_til
        dgWLenu = dgw + dgWLenu_til
        dgWRud = dgWRud_til
        dgWRenu = dgWRenu_til

        return dgWLud_til, dgWLenu_til, dgWRud_til, dgWRenu_til, dgWLud, dgWLenu, dgWRud, dgWRenu


    def GamZ(self, one, dGamZ):
        GamZ = self.GamZ_sm * (one + dGamZ)
        return GamZ

    def sigh0(self, one, dGamZ, dgLe, dgRe, dgLu, dgRu, dgLd, dgRd):
        sigh0 = self.sigh0_sm * (one + 2. * (self.gLe * dgLe + self.gRe * dgRe) / (self.gLe**2 + self.gRe**2) + 2. * (2. * (self.gLu * dgLu + self.gRu * dgRu) + 3. * (self.gLd * dgLd + self.gRd * dgRd)) / (2. * (self.gLu**2 + self.gRu**2) + 3. * (self.gLd**2 + self.gRd**2)) - 2. * dGamZ)
        return sigh0

    def Rl(self, one, dgLe, dgRe, dgLu, dgRu, dgLd, dgRd):
        Rl = self.Rl_sm * (one - 2 * (self.gLe * dgLe+ self.gRe * dgRe) / (self.gLe**2 + self.gRe**2) + 2. * (2. * (self.gLu * dgLu + self.gRu * dgRu) + 3 * (self.gLd * dgLd + self.gRd * dgRd)) / (2. * (self.gLu**2 + self.gRu**2) + 3. * (self.gLd**2 + self.gRd**2)))
        return Rl

    def AFBL(self, one, dgLe, dgRe):
        AFBL =self.AFBl_sm * (one + 8. * self.gLe * self.gRe / (self.gLe**4 - self.gRe**4) * (self.gRe * dgLe - self.gLe * dgRe))
        return AFBL

    def AlLEP(self, one, dgLe, dgRe):
        AlLEP = self.AlLEP_sm * (one + 4. * self.gLe * self.gRe / (self.gLe**4 - self.gRe**4) * (dgLe * self.gRe - dgRe * self.gLe))
        return AlLEP

    def AlSLD(self, one, dgLe, dgRe):
        AlSLD = self.AlSLD_sm * (one + 4. * self.gLe * self.gRe / (self.gLe**4 - self.gRe**4) * (dgLe * self.gRe - dgRe * self.gLe)) 
        return AlSLD

    def Rb(self, one, dgLd, dgRd, dgLu, dgRu):
        Rb = self.Rb_sm * (one + 2. * (self.gLd * dgLd + self.gRd*dgRd) / (self.gLd**2 + self.gRd**2) - 2. * (2. * (self.gLu * dgLu + self.gRu * dgRu) + 3. * (self.gLd * dgLd + self.gRd * dgRd)) / (2. * (self.gLu**2 + self.gRu**2) + 3. * (self.gLd**2 + self.gRd**2)))
        return Rb

    def Rc(self, one, dgLu, dgLd, dgRu, dgRd):
        Rc = self.Rc_sm * (one + 2. * (self.gLu * dgLu + self.gRu * dgRu) / (self.gLu**2 + self.gRu**2) -2. * (2. * (self.gLu * dgLu + self.gRu * dgRu) + 3. *(self.gLd * dgLd + self.gRd * dgRd)) / (2. * (self.gLu**2 + self.gRu**2) + 3. *(self.gLd**2 + self.gRd**2)))
        return Rc
    
    def AFBb(self, one, dgLd, dgRd, dgLe, dgRe):
        AFBb = self.AFBb_sm * (one + 4. * self.gLe * self.gRe / (self.gLe**4 - self.gRe**4) * (self.gRe * dgLe - self.gLe * dgRe) + 4. * self.gLd * self.gRd / (self.gLd**4 - self.gRd**4) * (self.gRd * dgLd - self.gLd * dgRd))
        return AFBb
    
    def AFBc(self, one, dgLe, dgRe, dgLu, dgRu):
        AFBc = self.AFBc_sm * (one + 4. * self.gLe * self.gRe / (self.gLe**4 - self.gRe**4) * (self.gRe * dgLe - self.gLe * dgRe) + 4. * self.gLu * self.gRu / (self.gLu**4 - self.gRu**4) * (self.gRu * dgLu - self.gLu * dgRu))
        return AFBc
    
    def Ab(self, one, dgLd, dgRd):
        Ab = self.Ab_sm * (one + 4. * self.gLd * self.gRd / (self.gLd**4 - self.gRd**4) * (self.gRd * dgLd - self.gLd * dgRd))
        return Ab
    
    def Ac(self, one, dgLu, dgRu):
        Ac = self.Ac_sm * (one + 4. * self.gLu * self.gRu / (self.gLu**4 - self.gRu**4) * (self.gRu * dgLu - self.gLu * dgRu))
        return Ac
    
    def shiftMW(self, one, dMW):
        shiftMW = self.shiftMW_sm * (one + dMW) #recall dMW from subroutine is actually dMW/MW
        return shiftMW
    
    def GamW(self, one, dgWLud, dgWLenu, dMW):
        GamW = self.GamW_sm * (one + 4./3. * dgWLud + 2./3. * dgWLenu + dMW)
        return GamW
    
    def BRWlnu(self, one, dgWLud, dgWLenu):
        BRWlnu = self.BRWlnu_sm * (one - 4./3. * dgWLud + 4./3. * dgWLenu)
        return BRWlnu

    def dGamZ(self, dgLe, dgRe, dgLu, dgRu, dgLd, dgRd, dgLnu):
        dGamZ = 2. * (3. * (self.gLe * dgLe + self.gRe * dgRe) + 3. * (self.gLnu * dgLnu) + 6. * (self.gLu * dgLu + self.gRu * dgRu) + 9. * (self.gLd * dgLd + self.gRd * dgRd)) / (3. * (self.gLe**2 + self.gRe**2) + 3. * (self.gLnu**2) + 6. * (self.gLu**2 + self.gRu**2) + 9. * (self.gLd**2 + self.gRd**2))
        return dGamZ

    def compute_chi2(self, param):
        param_padded = F.pad(param, (0, 1), value=1.)
        pred = F.linear(param_padded, self.ewpo_coeffs)

        x0 = abs(self.data - pred)

        chi_gauss = torch.where(
            (x0 < self.err_theo) | (self.err_gauss == 0.), 0., (x0 - self.err_theo) / self.err_gauss.clip(min=1e-30)
        )
        
        # With corr
        #chi2 = torch.matmul(chi_gauss, torch.matmul(self.corr, chi_gauss.T))
        #chi2 = torch.dot(chi_gauss, torch.mv(self.inv_corr, chi_gauss))

        # Without corr
        chi2 = chi_gauss.square().sum(dim=-1)
        return chi2 
