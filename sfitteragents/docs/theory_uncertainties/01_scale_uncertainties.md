# Renormalization and Factorization Scale Uncertainties

## 1. Physical Meaning

### Renormalization Scale ($\mu_R$)

Arises from absorbing ultraviolet divergences. The renormalized coupling $\alpha_s(\mu_R)$ runs according to the RGE:

$$\mu_R^2 \frac{d\alpha_s(\mu_R)}{d\mu_R^2} = \beta(\alpha_s) = -b_0 \alpha_s^2 - b_1 \alpha_s^3 - \cdots$$

where $b_0 = (33 - 2n_f)/(12\pi)$. Physical observables computed to all orders are $\mu_R$-independent (Callan-Symanzik equation). Any truncated prediction retains residual $\mu_R$ dependence proportional to the first omitted term.

### Factorization Scale ($\mu_F$)

Arises from separating long-distance (PDF) from short-distance (hard scattering) physics:

$$\sigma = \sum_{a,b} \int dx_1 \, dx_2 \, f_a(x_1, \mu_F^2) \, f_b(x_2, \mu_F^2) \, \hat{\sigma}_{ab}(Q^2, \mu_F^2, \mu_R^2)$$

The partonic cross-section contains $\ln(\mu_F^2/Q^2)$ terms that compensate the $\mu_F$ dependence of PDFs order by order. At finite order, a residual dependence remains.

### Reduction at Higher Orders

The residual scale dependence at N$^k$LO is formally $\mathcal{O}(\alpha_s^{n+k+1})$. Empirically:
- Higgs ggF: LO $\pm\sim100\%$ → NLO $\pm\sim20\%$ → NNLO $\pm\sim10\%$ → N$^3$LO $\pm\sim3\%$ (Anastasiou et al., JHEP 05 (2015) 058, [arXiv:1503.06056](https://arxiv.org/abs/1503.06056))
- $t\bar{t}$ total: NLO $\pm\sim15\%$ → NNLO $\pm\sim5\%$ (Czakon, Fiedler, Mitov, PRL 110 (2013) 252004, [arXiv:1303.6254](https://arxiv.org/abs/1303.6254))

---

## 2. Scale Variation Methods

### 2.1 Standard 7-Point Variation

Vary $\mu_R$ and $\mu_F$ around a central scale $\mu_0$ by factors of 2:

$$(\mu_R, \mu_F) \in \left\{ (\xi_R \mu_0, \xi_F \mu_0) \;\middle|\; \xi_R, \xi_F \in \{1/2, 1, 2\} \right\}$$

subject to:

$$\frac{1}{2} \leq \frac{\mu_R}{\mu_F} \leq 2$$

This excludes extreme combinations $(1/2, 2)$ and $(2, 1/2)$ that introduce large unphysical logarithms. The 7 points are:

$(1/2, 1/2)$, $(1/2, 1)$, $(1, 1/2)$, $(1, 1)$, $(1, 2)$, $(2, 1)$, $(2, 2)$

The uncertainty is the **envelope** (max/min deviation from central):

$$\Delta\Sigma^{+} = \max_{\text{7 pts}} \Sigma - \Sigma_{\text{central}}, \qquad \Delta\Sigma^{-} = \Sigma_{\text{central}} - \min_{\text{7 pts}} \Sigma$$

This is the standard in the LHC HXSWG reports ([arXiv:1610.07922](https://arxiv.org/abs/1610.07922)) and PDF4LHC recommendations (Butterworth et al., J. Phys. G 43 (2016) 023001, [arXiv:1510.03865](https://arxiv.org/abs/1510.03865)).

### 2.2 The 9-Point Variation

All $3 \times 3 = 9$ combinations without the $\mu_R/\mu_F$ constraint. More conservative; less commonly used.

### 2.3 Central Scale Choices

| Process | Central scale $\mu_0$ | Reference |
|---------|----------------------|-----------|
| Higgs (ggF) | $m_H/2$ | LHC HXSWG ([arXiv:1610.07922](https://arxiv.org/abs/1610.07922)) |
| $t\bar{t}$ (total) | $m_t$ | Natural hard scale |
| $t\bar{t}$ (differential) | $(m_{T,t} + m_{T,\bar{t}})/2$ or $H_T/4$ | Czakon et al., JHEP 04 (2017) 071, [arXiv:1606.03350](https://arxiv.org/abs/1606.03350); Schmal thesis Eq. 4.3 |
| Drell-Yan | $m_Z$ or $m_W$ | Invariant mass of lepton pair |
| Jet production | $p_T^{\text{jet}}$ or $\hat{H}_T/2$ | Transverse momentum or scalar sum |

### 2.4 Dynamic vs Fixed Scales

**Fixed scales** (e.g., $\mu_0 = m_t$): appropriate near threshold but lead to large logarithms in distribution tails where $Q \gg \mu_0$.

**Dynamic scales** (e.g., $\mu_0 = H_T/4$): evaluated event-by-event, essential for differential distributions spanning a wide energy range.

For $t\bar{t}$, the choice $\mu_0 = H_T/4$ vs $\mu_0 = m_t$ can shift the predicted $p_{T,t}$ spectrum by 10-20% in the tail ($p_{T,t} > 500$ GeV) even at NNLO (Czakon, Heymes, Mitov, JHEP 04 (2017) 071).

---

## 3. Limitations

### 3.1 Not a Statistical Uncertainty

Scale variation is a convention with no derivation from first principles. The factor-of-2 variation has no theorem guaranteeing the true result lies within the band. As stated in the PDG QCD review (Workman et al., PTEP 2022 (2022) 083C01): scale variation provides a rough estimate, not a confidence interval.

### 3.2 Known Underestimation Cases

- **Higgs ggF**: NLO scale band does not overlap with NNLO central value ($K_{\text{NLO}} \approx 1.7$). Driven by large $C_A = 3$ color factor (Harlander, Kilgore, PRL 88 (2002) 201801; Anastasiou, Melnikov, Nucl. Phys. B 646 (2002) 220).
- **Accidental cancellations**: Some processes have accidentally small NLO corrections, giving artificially narrow bands.
- **New channels opening**: When new partonic channels open at higher orders, the preceding scale variation cannot anticipate them.

### 3.3 Bayesian Alternatives

**Cacciari-Houdeau method** (JHEP 07 (2011) 138, [arXiv:1105.5152](https://arxiv.org/abs/1105.5152)): treats perturbative coefficients as random variables, derives posterior probability for the next term. Extended by Bonvini (EPJC 80 (2020) 989, [arXiv:2006.16293](https://arxiv.org/abs/2006.16293)) and Duhr, Huss, Mazeliauskas, Szafron (JHEP 09 (2021) 122, [arXiv:2106.04585](https://arxiv.org/abs/2106.04585)) into a theory covariance matrix framework.

Advantages: provides genuine probability distributions, allows correlation estimates. Not yet standard in experimental analyses.

---

## 4. Correlation Across Bins

### 4.1 Structure

Scale uncertainties are **highly correlated across bins** — a single scale variation shifts all bins simultaneously. This introduces both:
- **Normalization component**: all bins shift in same direction
- **Shape component**: different bins shift by different relative amounts

### 4.2 Shape vs Normalization Decomposition

For a distribution with bins $i$, the shape variation is:

$$\delta_i^{\text{shape}}(\xi_R, \xi_F) = \frac{\sigma_i(\xi_R, \xi_F)}{\sigma_{\text{tot}}(\xi_R, \xi_F)} - \frac{\sigma_i(1,1)}{\sigma_{\text{tot}}(1,1)}$$

### 4.3 Theory Covariance Matrix

Construct from scale variations:

$$S_{ij}^{\text{th}} = \frac{1}{N_{\text{var}}} \sum_{k=1}^{N_{\text{var}}} (\sigma_i^{(k)} - \bar{\sigma}_i)(\sigma_j^{(k)} - \bar{\sigma}_j)$$

Added to the experimental covariance in the $\chi^2$:

$$\chi^2 = (\vec{\sigma}^{\text{exp}} - \vec{\sigma}^{\text{th}})^T (C^{\text{exp}} + S^{\text{th}})^{-1} (\vec{\sigma}^{\text{exp}} - \vec{\sigma}^{\text{th}})$$

This approach was formalized for PDF fits (Ball et al., EPJC 79 (2019) 838, [arXiv:1906.10698](https://arxiv.org/abs/1906.10698)) and adopted in SMEFT fits (Hartland et al., JHEP 04 (2019) 100, [arXiv:1901.05965](https://arxiv.org/abs/1901.05965)).

### 4.4 Implementation in SFitter

Scale uncertainty as nuisance parameter(s):

$$\sigma_i^{\text{th}}(\vec{c}, \theta) = \sigma_i^{\text{central}}(\vec{c}) + \theta \cdot \delta_i^{\text{scale}}(\vec{c})$$

A single $\theta$ gives fully correlated normalization shifts; multiple nuisance parameters capture more complex patterns. The nuisance parameter is profiled or marginalized.

---

## 5. Practical Estimation

### 5.1 MadGraph Scale Variation Setup

In `run_card.dat`, enable systematics and configure scale variation:

```
# Enable systematics reweighting
True = use_syst

# Dynamic scale choice (event-by-event)
# 1 = fixed, 3 = HT/2, etc. — see MadGraph documentation
3 = dynamical_scale_choice

# If using fixed scales instead:
# 91.188 = fixed_ren_scale
# 91.188 = fixed_fac_scale

# Scale variation factors for reweighting
0.5 1 2 = rw_rscale    ! mu_R multipliers
0.5 1 2 = rw_fscale    ! mu_F multipliers

# Dynamic scale options:
# -1 = CKKW back-clustering (default)
#  0 = user-defined (edit setscales.f)
#  1 = sum of E_T
#  2 = HT = sum of sqrt(m^2 + pT^2)
#  3 = HT/2
#  4 = sqrt(s-hat)
# scalefact multiplies the chosen dynamic scale: mu = scalefact * mu_dyn
1.0 = scalefact
```

When `use_syst = True`, MadGraph stores the Bjorken-$x$ values, flavours, and scale information per event in the LHE file, enabling a posteriori reweighting without regeneration.

**LO vs NLO scale reweighting** (Mattelaer, EPJC 76 (2016) 674, [arXiv:1607.00763](https://arxiv.org/abs/1607.00763)):

- **At LO**: The `systematics` module runs as post-processing and reweights $\alpha_s^n(\mu_R)$ and PDFs $f(x, \mu_F)$. This is exact at LO because the matrix element depends on $\mu_R$ only through $\alpha_s$.
- **At NLO**: Use `rw_rscale`/`rw_fscale` (set in run_card). These are evaluated **during generation**, correctly reweighting all NLO contributions (Born, virtual, real-emission, counterterms) including explicit $\ln(\mu_R)$ and $\ln(\mu_F)$ terms. The `use_syst` post-processing at NLO is approximate (reweights only $\alpha_s$ and PDFs, missing virtual/counterterm log terms), but typically accurate to sub-percent level.

```
# NLO-specific run_card settings:
True = reweight_scale         ! store NLO scale variation weights
[1.0,2.0,0.5] = rw_rscale    ! mu_R factors (evaluated during generation)
[1.0,2.0,0.5] = rw_fscale    ! mu_F factors (evaluated during generation)
True = reweight_PDF           ! store PDF variation weights
```

**Changing the functional scale form**: The systematics module's `--dyn` flag can reweight between different functional forms (e.g., $H_T/2$ to $\sqrt{\hat{s}}$) by using stored per-event scale values. This is exact at LO but approximate beyond LO (reweights $\alpha_s$/PDFs but not scale-dependent matrix element terms). To rigorously compare functional forms at NLO, generate separate samples.

The systematics module can also be invoked after generation:

```bash
# Inside MadGraph console:
systematic <run_name> --mur=0.5,1,2 --muf=0.5,1,2

# Or command line:
python <MG5_dir>/bin/systematics <output_dir>/Events/<run_name>/events.lhe.gz \
    --mur=0.5,1,2 --muf=0.5,1,2 --together=scale
```

### 5.2 Extracting Per-Bin Scale Uncertainties

After running the systematics module, LHE events contain `<rwgt>` blocks with weights for each $(\mu_R, \mu_F)$ combination. For each bin of a histogram:

```python
import numpy as np

# 7-point scale variations (excluding extreme ratios)
scale_combos = [
    (0.5, 0.5), (0.5, 1.0), (1.0, 0.5),
    (1.0, 1.0),  # nominal
    (1.0, 2.0), (2.0, 1.0), (2.0, 2.0)
]

# histograms_scale[k][i] = cross-section in bin i for scale combo k
# Fill by looping over events, using the appropriate reweighted weight

# Per-bin envelope
nominal = histograms_scale[3]  # (1.0, 1.0)
scale_up = np.max(histograms_scale, axis=0) - nominal
scale_dn = nominal - np.min(histograms_scale, axis=0)

# Symmetrized uncertainty (for use in covariance matrix)
scale_unc = 0.5 * (scale_up + scale_dn)
```

### 5.3 Constructing the Scale Covariance Matrix

Since scale variation is a single coherent shift applied to all bins simultaneously:

```python
# For each scale combo k, compute the shift per bin
n_bins = len(nominal)
n_var = len(scale_combos)

shifts = np.zeros((n_var, n_bins))
for k in range(n_var):
    shifts[k] = histograms_scale[k] - nominal

# Three methods for the covariance matrix:

# Method 1: Sample covariance (captures correlation structure)
mean = np.mean(histograms_scale, axis=0)
deviations = histograms_scale - mean
cov_sample = deviations.T @ deviations / (n_var - 1)

# Method 2: Envelope, fully correlated (conservative, standard in ATLAS/CMS)
delta = 0.5 * (np.max(histograms_scale, axis=0) - np.min(histograms_scale, axis=0))
cov_envelope = np.outer(delta, delta)

# Method 3: Stewart-Tackmann outer product (handles asymmetric uncertainties)
# Reference: Stewart, Tackmann, PRD 85 (2012) 034011
delta_up = np.max(histograms_scale, axis=0) - nominal
delta_dn = nominal - np.min(histograms_scale, axis=0)
cov_st = np.maximum(np.outer(delta_up, delta_up),
                     np.outer(delta_dn, delta_dn))
```

**Which method to use:**
- `cov_envelope`: single nuisance parameter, fully correlated — appropriate for most SFitter analyses
- `cov_sample`: captures actual bin-bin correlation structure — preferred for profile likelihood fits
- `cov_st`: handles asymmetric uncertainties — preferred for exclusive jet bin analyses

**Critical**: the same scale variation must be applied to all bins simultaneously. Do not mix different scale choices across bins.

### 5.4 Using HighTea for NNLO Scale Variations

HighTea (Bonciani et al., EPJC 82 (2022) 200) provides NNLO predictions with scale variations via API:

```python
import requests

result = requests.post("https://hightea.hepforge.org/api/v1/compute", json={
    "process": "ttbar",
    "sqrts": 13000,
    "order": "NNLO",
    "pdf": "NNPDF40_nnlo_as_0118",
    "mt": 172.5,
    "muR": "HT/4",
    "muF": "HT/4",
    "observable": {"name": "m_tt", "bins": [345, 400, 500, 600, ...]},
    "scale_variations": True
}).json()
```

### 5.5 Using fastNLO Tables

```python
import fastnlo

fnlo = fastnlo.fastNLOLHAPDF("ttbar_mtt_NNLO.tab",
                              "NNPDF40_nnlo_as_0118", 0)

# Nominal
fnlo.SetScaleFactorsMuRMuF(1.0, 1.0)
fnlo.CalcCrossSection()
xs_nominal = fnlo.GetCrossSection()

# 7-point variation
results = {}
for xr, xf in scale_combos:
    fnlo.SetScaleFactorsMuRMuF(xr, xf)
    fnlo.CalcCrossSection()
    results[(xr, xf)] = fnlo.GetCrossSection()
```

### 5.6 K-Factor Computation

$$k_i = \frac{\sigma_i^{\text{NNLO}}}{\sigma_i^{\text{NLO}}}$$

Requirements: same PDF, $\alpha_s$, scale choice, binning, and $m_t$ in numerator and denominator. K-factor uncertainty from scale variation of the ratio:

$$\delta k_i = \frac{1}{2}\left(\max_j k_i^{(j)} - \min_j k_i^{(j)}\right)$$

This is typically much smaller than the individual NNLO or NLO scale uncertainties due to cancellation of correlated variations.
