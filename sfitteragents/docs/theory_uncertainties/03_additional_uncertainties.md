# Additional Theory Uncertainties

Beyond scale variation and PDFs: parton shower, parametric, EFT-specific, MC statistical, and combination methods.

---

## 1. Parton Shower and Matching Uncertainties

### 1.1 NLO Matching Schemes

Two dominant frameworks:

- **MC@NLO** (Frixione, Webber, JHEP 0206 (2002) 029): subtraction terms derived from the shower; events can carry negative weights
- **POWHEG** (Nason, JHEP 0411 (2004) 040; Frixione, Nason, Oleari, JHEP 0711 (2007) 070): hardest emission from exact NLO matrix element, positive weights, introduces $h_{\text{damp}}$ separation scale

The difference between Powheg and MadGraph5_aMC@NLO (Alwall et al., JHEP 1407 (2014) 079) predictions provides a matching uncertainty. For $t\bar{t}$, this is $\mathcal{O}(5\text{-}10\%)$ in differential distribution tails (ATLAS, EPJC 78 (2018) 186).

### 1.2 Shower Algorithms

- **Pythia 8** (Sjostrand et al., Comput. Phys. Commun. 191 (2015) 159): $p_T$-ordered dipole shower
- **Herwig 7** (Bellm et al., EPJC 76 (2016) 196): angular-ordered + dipole shower options

Key differences in: wide-angle soft radiation, jet substructure (10-20% differences), $t\bar{t}$ gap fraction.

### 1.3 ISR/FSR Scale Variations

Vary the shower renormalization scale by factors of $\{0.5, 2.0\}$ independently for ISR and FSR. In Pythia 8: `TimeShower:renormMultFac` and `SpaceShower:renormMultFac`.

Automated uncertainty framework: Mrenna, Skands, Phys. Rev. D 94 (2016) 074005, [arXiv:1605.08352](https://arxiv.org/abs/1605.08352).

### 1.4 Impact on SMEFT Fits

SMEFT operator effects manifest in distribution tails (high $p_T$, high $m_{t\bar{t}}$) — precisely where shower/matching uncertainties are largest. However, for unfolded parton-level measurements, shower effects are removed from the data, and the theory prediction needs only the hard process (no showering required).

---

## 2. Missing Higher-Order Uncertainties

### 2.1 Beyond Scale Variation

Standard scale variation:
- Probes only logarithmic structure ($\ln(\mu/Q)$ terms), misses finite rational terms
- Has no probabilistic interpretation
- Can underestimate true uncertainty (see below)

### 2.2 Cacciari-Houdeau Bayesian Method

Reference: JHEP 07 (2011) 138, [arXiv:1105.5152](https://arxiv.org/abs/1105.5152).

Given expansion $\Sigma = \sum_{n=0}^{N} c_n \alpha_s^n$, assume prior $|c_n| \leq \bar{c}$ and derive posterior for $c_{N+1}$. Extended by Bonvini (EPJC 80 (2020) 989) and Duhr et al. (JHEP 09 (2021) 122) into theory covariance matrix framework.

### 2.3 Known Underestimation Cases

- **Higgs ggF**: NLO band does not cover NNLO. $K_{\text{NLO}} \approx 1.7$ driven by $C_A = 3$ (Harlander, Kilgore, PRL 88 (2002) 201801; Anastasiou, Melnikov, Nucl. Phys. B 646 (2002) 220)
- **Diboson tails**: NNLO corrections can exceed NLO band in high invariant mass regions (Grazzini, Kallweit, Rathlev, JHEP 1509 (2015) 100)
- **New channels opening**: e.g., $gg \to WW$ at NNLO not anticipated by NLO scale variation

---

## 3. Parametric Uncertainties

### 3.1 Top Quark Mass

Current: $m_t = 172.52 \pm 0.33$ GeV (world combination). Pole mass has additional $\mathcal{O}(\Lambda_{\text{QCD}}) \sim 0.2\text{-}0.5$ GeV renormalon ambiguity (Beneke, Phys. Lett. B 434 (1998) 115).

Impact on $t\bar{t}$:

$$\frac{\delta\sigma_{t\bar{t}}}{\sigma_{t\bar{t}}} \approx -4 \frac{\delta m_t}{m_t} \approx 0.7\% \text{ for } \delta m_t = 0.3 \text{ GeV}$$

Comparable to NNLO scale uncertainty. Differential distributions near threshold ($m_{t\bar{t}} \approx 2m_t$) are extremely sensitive.

### 3.2 Other Parameters

| Parameter | Value | Impact |
|-----------|-------|--------|
| $m_b$ ($\overline{\text{MS}}$) | $4.18 \pm 0.03$ GeV | $b\bar{b}H$: $\delta\sigma/\sigma \approx 2\delta m_b/m_b \approx 1.4\%$ |
| $m_W$ | $80.3692 \pm 0.0133$ GeV | EW predictions, $\sin^2\theta_W$ |
| $\alpha_s(M_Z)$ | $0.1180 \pm 0.0009$ | $gg \to H$: $\delta\sigma/\sigma \approx 2\delta\alpha_s/\alpha_s \approx 1.5\%$ at LO |

### 3.3 Practical Treatment

Shift each parameter by $\pm 1\sigma$:

$$\delta\Sigma_{\text{param}} = \frac{\Sigma(p + \delta p) - \Sigma(p - \delta p)}{2}$$

Independent parametric uncertainties added in quadrature. In SFitter, treated as nuisance parameters with Gaussian constraints.

---

## 4. EFT-Specific Theory Uncertainties

### 4.1 SMEFT Truncation

Neglecting dimension-8 operators introduces truncation uncertainty. At $\mathcal{O}(1/\Lambda^4)$, dimension-6 squared and dimension-8 interference both contribute:

$$\sigma \supset \frac{C_i^2}{\Lambda^4}\sigma_{\text{quad}} + \frac{C_k^{(8)}}{\Lambda^4}\sigma_{\text{dim8,int}}$$

**Estimation approaches:**
1. Compare linear-only vs linear+quadratic fits (Ethier et al., JHEP 2101 (2021) 128, [arXiv:2011.02075](https://arxiv.org/abs/2011.02075))
2. Naive dimensional analysis to bound dim-8 effects
3. Explicit dim-8 computations where available (Murphy, JHEP 2010 (2020) 174; Li et al., JHEP 2104 (2021) 152)

### 4.2 Mixed QCD-EFT Corrections

SMEFT contributions at LO but SM at NNLO creates a mismatch. NLO QCD corrections to dim-6 operators have been computed for:
- $t\bar{t}$: Degrande et al., Phys. Rev. D 103 (2021) 096024
- Higgs: Dawson, Giardino, Phys. Rev. D 97 (2018) 093003

QCD $K$-factors for SMEFT contributions can differ from SM $K$-factors — simply rescaling LO SMEFT by SM $K$-factor introduces error.

### 4.3 EFT Validity

The SMEFT expansion requires $E \ll \Lambda$. Warning signs:
- Dim-6 squared terms dominating over interference
- Best-fit $\Lambda$ comparable to energy reach
- Unitarity violation at high energies

Diagnostic: check $R = |\sigma^{(6,\text{sq})}| / |\sigma^{(6,\text{int})}|$ per bin. When $R \gtrsim 1$, EFT is breaking down. See Contino et al., JHEP 1607 (2016) 144, [arXiv:1604.06444](https://arxiv.org/abs/1604.06444).

### 4.4 Theory Uncertainty on Kappa Coefficients

The kappa coefficients themselves carry uncertainty from:
1. Perturbative order at which they are computed (LO vs NLO for SMEFT)
2. PDF dependence (can differ from SM prediction)
3. Residual scale dependence

These propagate into extracted Wilson coefficients.

---

## 5. Monte Carlo Statistical Uncertainty

### 5.1 Origin

Finite number of generated events $N$ gives statistical fluctuations per bin:

$$\delta\sigma_{\text{bin}}^{\text{MC}} = \sigma_{\text{bin}} / \sqrt{N_{\text{eff,bin}}}$$

For weighted events (common at NLO):

$$N_{\text{eff}} = \frac{(\sum_i w_i)^2}{\sum_i w_i^2}$$

Can be much smaller than $N$ when weights have large variance (especially MC@NLO with negative weights).

### 5.2 Treatment

Add as uncorrelated uncertainty per bin (Barlow-Beeston method, Comput. Phys. Commun. 77 (1993) 219):

$$\chi^2 = \sum_{\text{bins}} \frac{(\text{data} - \text{theory})^2}{\sigma_{\text{exp}}^2 + \sigma_{\text{MC}}^2}$$

Distinct from experimental MC stat uncertainty (from finite simulated samples used in unfolding).

### 5.3 Mitigation

- Increase generated events until $\sigma_{\text{MC}} \ll \sigma_{\text{exp}}$
- Reduce negative weight fractions (Frederix et al., JHEP 2009 (2020) 038)
- Use reweighting instead of regeneration where possible

---

## 6. Combining Theory Uncertainties

### 6.1 Correlation Structure

| Source | Across bins | Across processes | Treatment |
|--------|------------|-----------------|-----------|
| Scale ($\mu_R, \mu_F$) | Correlated | Uncorrelated between processes | Nuisance parameter(s) per process |
| PDF | Correlated | Correlated (same PDFs) | Hessian eigenvectors or replicas |
| $\alpha_s$ | Correlated | Correlated | Single nuisance parameter |
| Shower/matching | Correlated | Partially correlated | Discrete systematic |
| Parametric ($m_t$, etc.) | Correlated | Correlated for same parameter | Nuisance parameter per parameter |
| MC statistical | Uncorrelated | Uncorrelated | One per bin (Barlow-Beeston) |
| EFT truncation | Correlated (grows with $E$) | Correlated | Process/bin-dependent |

### 6.2 Envelope vs Quadrature

**Scale variation**: use **envelope** (7-point max/min). The 7 points are not statistically independent — quadrature would underestimate.

**Combining different sources**: add in **quadrature** (independent physical origins):

$$\delta\sigma_{\text{total}}^{\text{th}} = \sqrt{(\delta\sigma_{\text{scale}})^2 + (\delta\sigma_{\text{PDF}})^2 + (\delta\sigma_{\alpha_s})^2 + (\delta\sigma_{\text{param}})^2 + \cdots}$$

### 6.3 Flat vs Gaussian Priors

- **Scale variation**: no probabilistic interpretation. Model as flat (Rfit, Hocker et al., EPJC 21 (2001) 225) or Gaussian. Flat is more conservative; choice affects extracted WC confidence intervals.
- **PDF, parametric**: well-defined statistical interpretation → Gaussian nuisance parameters.

### 6.4 SFitter Implementation

Theory nuisance parameters in the likelihood:

$$-2\ln L = \sum_i \frac{(d_i - t_i(\vec{C}, \vec{\theta}))^2}{\sigma_{\text{exp},i}^2} + \sum_k \theta_k^2$$

with:

$$t_i(\vec{C}, \vec{\theta}) = t_i^{(0)}(\vec{C}) + \sum_k \theta_k \cdot \delta t_{i,k}$$

Supports profiling (minimize over $\theta$) and marginalization (integrate over $\theta$).

---

## 7. Typical Sizes

| Source | Inclusive | Differential tails |
|--------|----------|-------------------|
| Scale (NLO) | 5-15% | 10-30% |
| Scale (NNLO) | 1-5% | 3-10% |
| PDF (68% CL) | 2-5% | 5-15% |
| $\alpha_s$ | 1-3% | 2-5% |
| Shower/matching | 2-10% | 10-30% |
| $m_t$ ($\pm 0.3$ GeV) | $<1\%$ | 1-5% |
| EFT truncation | Process-dependent | Grows as $(E/\Lambda)^2$ |
| MC statistical | Sample-dependent | Worse in tails |

---

## 8. Practical Estimation Recipes

### 8.1 Pythia 8 Shower Variations

Configure ISR/FSR scale variations in the Pythia 8 settings:

```
# Pythia 8.2
TimeShower:renormMultFac = 0.5   # or 2.0 (FSR alpha_s scale)
SpaceShower:renormMultFac = 0.5  # or 2.0 (ISR alpha_s scale)

# Pythia 8.3+
fsr:muRfac = 0.5   # or 2.0
isr:muRfac = 0.5   # or 2.0
```

**Automated uncertainty weights** (Mrenna, Skands, PRD 94 (2016) 074005):

```
UncertaintyBands:doVariations = on
UncertaintyBands:List = {
  fsr:muRfac=0.5 isr:muRfac=0.5,
  fsr:muRfac=0.5 isr:muRfac=2.0,
  fsr:muRfac=2.0 isr:muRfac=0.5,
  fsr:muRfac=2.0 isr:muRfac=2.0,
  fsr:muRfac=0.5,
  fsr:muRfac=2.0,
  isr:muRfac=0.5,
  isr:muRfac=2.0
}
```

This computes variation weights on-the-fly via Sudakov reweighting, without regenerating events. Take the **envelope** across all variations per bin.

**Limitation**: Reweighting cannot capture differences between shower algorithms (Pythia vs Herwig) — only parametric variations within one algorithm.

### 8.2 Generator Comparison Setup

For $t\bar{t}$, the standard comparison set:

1. **Powheg + Pythia 8** (POWHEG matching)
2. **MadGraph5_aMC@NLO + Pythia 8** (MC@NLO matching)
3. **MadGraph5_aMC@NLO + Herwig 7** (alternative shower)

Requirements: same PDF set, $m_t$, $\alpha_s(M_Z)$, EW parameters, and fiducial cuts across all generators. Take the envelope per bin.

For Powheg, the $h_{\text{damp}}$ parameter controls matching of the hardest emission. CMS default: $h_{\text{damp}} = 1.379 \times m_t$.

### 8.3 Top Mass Variation

In MadGraph `param_card.dat`:

```
Block mass
  6 1.725000e+02 # MT
```

Or via launch command:

```
launch
  set mt 173.5    # up variation (+1 GeV)
  set mt 171.5    # down variation (-1 GeV)
```

Generate three samples (nominal, up, down), shower identically, apply same analysis:

```python
# Per-bin uncertainty, rescaled to experimental precision
delta_mt_gen = 1.0  # GeV (generation shift)
delta_mt_exp = 0.33  # GeV (experimental uncertainty)

mt_unc_per_bin = 0.5 * (sigma_up - sigma_dn) * (delta_mt_exp / delta_mt_gen)
```

Use $\pm 1.0$ GeV shifts ($\sim 3\sigma$ of experimental uncertainty) to ensure clear signal above MC noise. Verify linearity by generating at intermediate mass values.

### 8.4 MC Statistical Uncertainty

Per bin with weighted events:

```python
import numpy as np

# For each bin, accumulate weights and weights-squared
sum_w = np.zeros(n_bins)     # sum of weights
sum_w2 = np.zeros(n_bins)    # sum of weights squared

for event in events:
    bin_idx = find_bin(event.observable)
    sum_w[bin_idx] += event.weight
    sum_w2[bin_idx] += event.weight**2

# Statistical uncertainty
mc_stat_unc = np.sqrt(sum_w2)

# Effective number of events
n_eff = sum_w**2 / sum_w2
```

**Rule of thumb**: MC stat should be $< 1/3$ of experimental stat uncertainty per bin. If $N_{\text{eff},i} < 9 \times N_{\text{data},i}$, increase MC statistics or merge bins.

For NLO generators with negative weights (MC@NLO): effective statistics reduced by factor $(1 - 2f_-)^2$ where $f_-$ is the negative weight fraction (typically 10-25% for $t\bar{t}$).

**Barlow-Beeston treatment** in pyhf:

```json
{"name": "mc_stat", "type": "staterror", "data": [delta_1, delta_2, ...]}
```

### 8.5 EFT Truncation Diagnostics

**Ratio test** — for each bin $i$ and operator $j$, at the best-fit WC value:

$$R_{ij} = \frac{|\sigma_{\text{quad},ij}(c_j^{\text{best fit}})|}{|\sigma_{\text{int},ij}(c_j^{\text{best fit}})|}$$

- $R \ll 1$: EFT well-behaved, linear approximation valid
- $R \sim 1$: EFT questionable for this bin
- $R > 1$: EFT breaking down — consider removing bin from fit

**Linear vs quadratic comparison**: run the fit twice (linear-only and linear+quadratic). If 95% CL intervals differ by more than ~30%, truncation effects are significant.

**Iterative bin removal**:
1. Quadratic fit → get $c_j^{\text{best}}$
2. Compute $R_{ij}$ → remove bins with $R > 1$
3. Re-fit → updated $c_j^{\text{best}}$
4. Recompute $R$ → check convergence (typically 2-3 iterations)

**Energy clipping**: alternatively, impose $p_T < p_T^{\text{max}}$ or $m_{t\bar{t}} < m_{\text{max}}$ such that $R < 1$ in all retained bins. Conservative but operator-independent.
