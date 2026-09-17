# Current SFitter Dataset and Operator Set

As of the combined fit in arXiv:2312.12502 (2023). This is the target configuration for the agent.

---

## 1. Tool Versions

| Tool | Version | Notes |
|------|---------|-------|
| MadGraph5_aMC@NLO | v3.5.0 | NLO QCD with SMEFTatNLO UFO model |
| PDF set | NNPDF4.0 NNLO | `NNPDF40_nnlo_as_0118`, 100 replicas |
| NNLO SM predictions | HighTea API | Replaces earlier fastNLO tables |
| $\alpha_s(M_Z)$ | 0.118 | Consistent with NNPDF4.0 |
| Pythia / Herwig | Not used | Data is unfolded to parton level |

**Note on NNPDF3.1 → NNPDF4.0**: The switch was motivated by positivity issues in NNPDF3.1 that caused inconsistent SMEFT contributions in distribution tails (arXiv:2312.12502).

---

## 2. Top Sector Operators (22)

From Table 2.2 of Schmal thesis / arXiv:1910.03606. Warsaw basis with $U(2)_q \times U(2)_u \times U(2)_d$ flavor symmetry.

### Four-Fermion (LL) — 4 operators

| Operator | Color | $SU(2)$ | Shaded (contributes to $t\bar{t}$) |
|----------|-------|---------|------|
| $O_{Qq}^{3,8}$ | octet | triplet | Yes |
| $O_{Qq}^{1,8}$ | octet | singlet | Yes |
| $O_{Qq}^{3,1}$ | singlet | triplet | Yes |
| $O_{Qq}^{1,1}$ | singlet | singlet | Yes |

### Four-Fermion (RR) — 4 operators

| Operator | Color | Shaded |
|----------|-------|--------|
| $O_{tu}^{8}$ | octet | Yes |
| $O_{tu}^{1}$ | singlet | Yes |
| $O_{td}^{8}$ | octet | Yes |
| $O_{td}^{1}$ | singlet | Yes |

### Four-Fermion (LR/RL) — 6 operators

| Operator | Color | Shaded |
|----------|-------|--------|
| $O_{Qu}^{8}$ | octet | Yes |
| $O_{Qu}^{1}$ | singlet | Yes |
| $O_{Qd}^{8}$ | octet | Yes |
| $O_{Qd}^{1}$ | singlet | Yes |
| $O_{tq}^{8}$ | octet | Yes |
| $O_{tq}^{1}$ | singlet | Yes |

### Higgs-Fermion Current — 5 operators

| Operator | Key processes |
|----------|---------------|
| $O_{\phi Q}^{(3)}$ | Single top, $t\bar{t}Z$, $t\bar{t}W$ |
| $O_{\phi Q}^{(1)}$ | $t\bar{t}Z$, $tZq$, EWPO ($R_b$) |
| $O_{\phi t}$ | $t\bar{t}Z$, $tZq$ |
| $O_{\phi tb}$ | Single top (RH $Wtb$) |
| $O_{t\phi}$ | $t\bar{t}H$, top Yukawa |

Derived combinations: $C_{\phi Q}^{-} = C_{\phi Q}^{(1)} - C_{\phi Q}^{(3)}$, $C_{tZ} = -s_W C_{tW} + c_W C_{tB}$

### Dipole — 3 operators

| Operator | Key processes |
|----------|---------------|
| $O_{tG}$ | $t\bar{t}$ (dominant via ggF, ~90% of production) |
| $O_{tW}$ | $Wtb$ vertex, single top, $W$ helicity |
| $O_{tB}$ | $t\bar{t}Z$, $t\bar{t}\gamma$ |

**Note**: $O_G$ (triple gluon) is **excluded** — contributions to $t\bar{t}$ set to zero as multi-jet constraints are much stronger (arXiv:1910.03606).

---

## 3. Higgs / Di-Boson / EWPO Operators (~17)

From arXiv:2208.08454. Uses **HISZ basis** (not Warsaw) for historical reasons.

| Operator | Type |
|----------|------|
| $O_{GG}$ ($f_{GG}$) | Higgs-gluon |
| $O_{WW}$, $O_{BB}$, $O_{BW}$ | Higgs-gauge |
| $O_B$, $O_W$, $O_{3W}$ | Gauge self-coupling |
| $O_{\phi 1}$, $O_{\phi 2}$ | Higgs self-coupling / kinetic |
| $O_{e\phi,22}$, $O_{e\phi,33}$ | Lepton Yukawa (muon, tau) |
| $O_{d\phi,33}$ | Bottom Yukawa |
| $O_{u\phi,33}$ | Top Yukawa (overlaps with $O_{t\phi}$) |
| $O_{4L}$ | Four-lepton |
| $O_{\phi e}^{(1)}$, $O_{\phi u}^{(1)}$, $O_{\phi d}^{(1)}$, $O_{\phi Q}^{(1,3)}$ | Fermion currents |
| $BR_{\text{inv}}$ | Higgs invisible BR (free parameter) |

**Basis translation**: For the combined fit, HISZ operators are converted to Warsaw basis. Key relation: $C_{\phi G} = -\frac{\alpha_s}{8\pi} f_{GG}$.

---

## 4. Top Sector Measurements

### $t\bar{t}$ Total Cross-Sections

| Measurement | $\sqrt{s}$ | $\mathcal{L}$ | Experiment | Channel |
|-------------|-----------|----------------|------------|---------|
| $\sigma_{t\bar{t}}$ | 8 TeV | 20.2 fb$^{-1}$ | ATLAS | $e\mu$ |
| $\sigma_{t\bar{t}}$ | 8 TeV | 2.3 fb$^{-1}$ | CMS | $l$+jets |
| $\sigma_{t\bar{t}}$ | 13 TeV | 36 fb$^{-1}$ | ATLAS | $l$+jets (published likelihood) |
| $\sigma_{t\bar{t}}$ | 13 TeV | 36 fb$^{-1}$ | ATLAS | $e\mu$ |
| $\sigma_{t\bar{t}}$ | 13 TeV | 35.9 fb$^{-1}$ | CMS | $l$+jets |
| $\sigma_{t\bar{t}}$ | 13 TeV | 35.9 fb$^{-1}$ | CMS | dilepton |

### $t\bar{t}$ Differential Distributions

| Observable | $\sqrt{s}$ | $\mathcal{L}$ | Experiment | Bins | Notes |
|-----------|-----------|----------------|------------|------|-------|
| $m_{t\bar{t}}$ (norm.) | 13 TeV | 137 fb$^{-1}$ | CMS | 15 | Up to 3500 GeV, **new in arXiv:2312.12502** |
| $p_T(t_h)$ (norm.) | 13 TeV | 137 fb$^{-1}$ | CMS | Variable | Hadronically-decaying top |

### Associated Production

| Process | $\sqrt{s}$ | Experiment |
|---------|-----------|------------|
| $t\bar{t}Z$ | 13 TeV | ATLAS (published likelihood, **new**) |
| $t\bar{t}Z$ | 13 TeV | CMS |
| $t\bar{t}W$ | 13 TeV | ATLAS, CMS |
| $tZq$ | 13 TeV | ATLAS, CMS |

### Single Top

| Channel | $\sqrt{s}$ | Experiment |
|---------|-----------|------------|
| $t$-channel | 8, 13 TeV | ATLAS, CMS |
| $s$-channel | 8, 13 TeV | ATLAS, CMS |
| $tW$ | 13 TeV | ATLAS, CMS |

### Top Decay

| Observable | Description |
|-----------|-------------|
| $F_L$, $F_0$ | $W$ helicity fractions in $t \to Wb$ |
| $A_C$ | Charge asymmetry at 7, 8 TeV |

---

## 5. Scale Choices

| Process | Central scale $\mu_0$ | Reference |
|---------|----------------------|-----------|
| $t\bar{t}$ | $\mu_R = \mu_F = \frac{1}{2}(m_T(t) + m_T(\bar{t}))$ | Schmal thesis Eq. 4.3 |
| $t\bar{t}$ (NNLO via HighTea) | $H_T/4$ | arXiv:2312.12502 |

Scale variation: $\mu_R, \mu_F$ by factor 2 (7-point). Envelope taken as theory uncertainty.

---

## 6. Theory Uncertainty Categories (Top Sector)

From Table 8.1 in Schmal thesis / arXiv:1910.03606:

### Theory type (`theo`)

| Name | Description |
|------|-------------|
| ScalesT | Renormalization + factorization scale variation |
| Scales | Scale variation (alternative naming) |
| ScalesSim / ScaleSim | Scale variation on simulation |
| PDF | PDF uncertainty (data side) |
| PDFSim | PDF uncertainty (simulation side) |
| TopMass | Top quark mass variation |
| UnderlyingEvent | Underlying event modeling |
| Matching | ME-PS matching |
| NLOMatching | NLO matching uncertainty |
| Scheme | Computational scheme |
| ColorReconnection | Color reconnection |
| Extrapolation | Fiducial → full phase space |
| hatPDFNLO | NLO PDF hat-scheme |

### Systematic type (`syst`)

| Name | Description |
|------|-------------|
| Jets | JES + JER combined |
| bTagging | b-jet tagging efficiency |
| Leptons | Lepton reconstruction + ID |
| Luminosity | Integrated luminosity |
| Pileup | Pileup reweighting |
| ETmis | Missing transverse energy |
| Beam | Beam energy |
| partonShower | Parton shower modeling |
| PSscale | Parton shower scale |
| ISR / FSR | Initial/final state radiation |
| Tune | Generator tune |
| tTagging | Top-jet tagging |
| tauTagging | Tau tagging |
| BkgTTBar, BkgTTW, BkgTTZ, BkgTW, BkgSch, BkgTch, BkgWhel | Background normalizations |

### Statistical type (`stat`)

| Name | Description |
|------|-------------|
| stat | Data statistics |
| MC | Monte Carlo statistics |
| Trigger | Trigger efficiency |
| Mod | Model statistical |
| LightTagging | Light-jet tagging |
| bFragmentation | b-fragmentation |
| Others | Miscellaneous |
