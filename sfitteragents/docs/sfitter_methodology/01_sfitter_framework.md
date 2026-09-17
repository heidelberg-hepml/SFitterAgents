# SFitter Core Framework

Sources: arXiv:0709.3985 (original), arXiv:2208.08454 (profiling vs marginalization), arXiv:2312.12502 (Schmal thesis / combined fit), Schmal master thesis (schmal_m.pdf).

---

## 1. The RFit Scheme — Flat Theory Uncertainties

The defining feature of SFitter's uncertainty treatment is the **RFit scheme**: theory uncertainties are modeled as **flat (uniform) distributions**, not Gaussians.

**Rationale** (arXiv:0709.3985, Section 3): Theory uncertainties (e.g., scale variation, missing higher orders) represent a range within which the true value could lie with equal probability. Unlike experimental statistical uncertainties, they do not follow a Gaussian distribution — there is no "central value" and no reason to believe values near the center are more likely than values near the edges.

**Mathematical form** (Schmal thesis Eq. 3.7):

$$\mathcal{L}(\mu, \sigma | x) = \mathcal{F}(x | \mu, \sigma) = \frac{1}{2\sigma} \Theta[x - (\mu - \sigma)] \Theta[(\mu + \sigma) - x]$$

This is a box function of width $2\sigma$ centered at $\mu$.

**Consequence for the likelihood**: When a measurement with Gaussian experimental uncertainty $\sigma_{\text{exp}}$ has a theory prediction with flat theory uncertainty $\sigma_{\text{theo}}$, the resulting likelihood is the convolution:

$$\mathcal{L}_{\text{combined}} = \text{Gauss}(\sigma_{\text{exp}}) \otimes \text{Flat}(\sigma_{\text{theo}})$$

This produces a likelihood that is **flat near the best-fit point** (within the theory uncertainty range) and falls off Gaussianly in the tails. The profile likelihood then has a flat "plateau" of width $\sim 2\sigma_{\text{theo}}$, which can significantly widen the confidence intervals compared to a purely Gaussian treatment.

**Impact** (arXiv:2208.08454): The choice of flat vs Gaussian for theory uncertainties matters enormously in the top sector, where theory uncertainties are 20-25% of the total cross-section (dominant over the ~5% experimental systematics). In the Higgs sector, where theory uncertainties are 5-10%, the impact is smaller.

**This is a key distinction from other SMEFT fitting groups** (e.g., SMEFiT, fitmaker/HEPfit) which typically treat all uncertainties as Gaussian.

---

## 2. Three Uncertainty Distributions

SFitter uses three different probability distributions for the three uncertainty categories (Schmal thesis Eq. 3.5-3.7, Table 3.1):

| Category | Distribution | Type code (SFitter) | Correlation |
|----------|-------------|------------------------|-------------|
| **Systematic** (experimental) | Gaussian $\mathcal{N}(x | \mu, \sigma)$ | `syst` | Correlated across bins ($\rho = 0.99$ within experiment) |
| **Statistical** | Poisson $\text{Pois}(d | p)$ | `stat` / `pois` | Uncorrelated (bin-by-bin) |
| **Theory** | Flat $\mathcal{F}(x | \mu, \sigma)$ | `theo` | Correlated across bins of same process |

The exclusive likelihood for a single measurement (Schmal thesis Eq. 3.6):

$$\mathcal{L}_{\text{excl}} = \text{Pois}(d | p(\alpha_n, \theta_i, b)) \cdot \text{Pois}(b_{CR} | bk) \cdot \prod_i \mathcal{C}(\theta_i, \sigma_i)$$

where $\mathcal{C}$ is the constraint on nuisance parameters (Gaussian for systematics, flat for theory).

---

## 3. Profiling vs Marginalization

SFitter implements both frequentist (profiling) and Bayesian (marginalization) approaches (arXiv:2208.08454):

### Profile Likelihood (default, frequentist)

For each point in Wilson coefficient space $\vec{C}$, maximize the likelihood over all nuisance parameters $\vec{\theta}$:

$$\mathcal{L}_{\text{prof}}(\vec{C}) = \max_{\vec{\theta}} \mathcal{L}(\vec{C}, \vec{\theta})$$

With flat theory uncertainties, this gives a flat plateau in the profile likelihood where the theory uncertainty can absorb the deviation.

### Bayesian Marginalization

Integrate over nuisance parameters with priors:

$$\mathcal{L}_{\text{marg}}(\vec{C}) = \int d\vec{\theta} \, \mathcal{L}(\vec{C}, \vec{\theta}) \, \pi(\vec{\theta})$$

With flat priors on theory nuisance parameters and Gaussian priors on systematic nuisance parameters.

### Key Finding (arXiv:2208.08454)

- When theory uncertainties are **Gaussian**: profiling and marginalization give **similar** results
- When theory uncertainties are **flat** (RFit): results **differ significantly** — profiling gives wider confidence intervals due to the flat plateau effect
- The choice matters most in the top sector where theory uncertainties dominate

---

## 4. Weighted Markov Chain Monte Carlo

SFitter uses a custom weighted MCMC algorithm (arXiv:0709.3985) to explore the Wilson coefficient parameter space:

- **Proposal function**: Gaussian with adaptive step size, targeting 30-50% acceptance rate
- **Multi-modal handling**: Combination of grid scans and MCMC to find all local minima
- **Burn-in**: First 10% of chain discarded
- **Convergence**: Monitored via Gelman-Rubin diagnostics and visual inspection of trace plots

Results are presented as:
1. **1D profile likelihoods**: $\Delta\chi^2 = 1$ for 68% CL, $\Delta\chi^2 = 3.84$ for 95% CL
2. **2D contours**: $\Delta\chi^2 = 2.30$ (68% CL), $\Delta\chi^2 = 5.99$ (95% CL)
3. **Individual bounds**: one-operator-at-a-time (all others fixed to SM)
4. **Marginalized bounds**: profiled over all other operators (always weaker)

---

## 5. Correlation Treatment

### Systematic Uncertainties (arXiv:2312.12502, Section 3.2)

Within a single experiment, systematic uncertainties of the same type are correlated with $\rho = 0.99$ (not 1.0, to avoid singular covariance matrices). The correlation is encoded positionally: uncertainties at the same position in different measurements are treated as correlated.

### Covariance Matrix

$$C_{ij} = \frac{\sum_{\text{syst}} \sigma_{i,\text{syst}} \cdot \sigma_{j,\text{syst}} \cdot \rho_{i,j,\text{syst}}}{\sigma_{i,\text{exp}} \cdot \sigma_{j,\text{exp}}}$$

### Cross-Measurement Correlations

- **Same experiment, same systematic type**: correlated ($\rho = 0.99$)
- **Different experiments**: uncorrelated (e.g., ATLAS Jets ≠ CMS Jets)
- **LHC-wide**: luminosity is correlated across experiments at same energy
- **Theory uncertainties**: correlated across measurements of the same process at the same energy

### Published Likelihoods (arXiv:2312.12502, Section 3.3)

When ATLAS/CMS publish full HistFactory likelihoods (pyhf format), SFitter can use them directly. The 100-200+ nuisance parameters are grouped into SFitter categories by name matching (e.g., `BTag_B`, `BTag_C`, `BTag_light` → `bTagging`). This grouping is validated by comparing reproduced uncertainties against published values (Table 5.1 in Schmal thesis).

---

## 6. DataPrep Tool

The DataPrep tool (mentioned in arXiv:1910.03606) prepares SFitter input files:

1. **Ordering**: Ensures systematic uncertainties are in the correct positional order for correlation encoding
2. **Averaging**: When multiple measurements of the same observable exist (e.g., $t\bar{t}$ total cross-section from ATLAS $l$+jets and ATLAS dilepton), DataPrep averages them weighted by constraining power
3. **Correlation**: Links theory uncertainties across measurements of the same process at the same energy
4. **Format**: Produces the SFitter data card format:

```
MEASUREMENT_NAME_i = sigma_meas,i ± Delta_syst,i ± Delta_stat,i ± Delta_hat,i
```

---

## 7. Dimension-6 Squared Terms

SFitter **always includes** the quadratic ($C^2/\Lambda^4$) terms from squaring dimension-6 amplitudes (arXiv:1505.05516, arXiv:1910.03606). This is a deliberate choice, distinct from some other groups that drop them for EFT consistency:

**Arguments for inclusion** (used by SFitter):
- Ensures positive-definite cross-sections
- Quadratic terms dominate for some operators where linear interference is helicity-suppressed
- Prevents flat directions in the fit
- The quadratic dependence is an exact consequence of the amplitude structure ($|\mathcal{A}|^2$ is quadratic in $C$)

**Caveat**: Quadratic dim-6 terms are formally the same order as dim-8 interference terms, which are neglected. This inconsistency is acknowledged but accepted for practical reasons.

---

## 8. EFT Validity Considerations

The SFitter group monitors EFT validity via (arXiv:1812.07587, arXiv:1910.03606):

- **Energy-growing effects**: Dim-6 contributions grow as $\hat{s}/\Lambda^2$ in distribution tails. High-$m_{t\bar{t}}$ bins are most sensitive but also most at risk of EFT breakdown.
- **Bin removal**: Bins where quadratic terms dominate over linear may be removed (e.g., highest $p_T(t_h)$ bins in arXiv:2312.12502)
- **Consistency check**: Compare individual (one-at-a-time) vs marginalized bounds — large differences indicate that the data cannot independently constrain all operators

---

## 9. The `sfitter` Implementation

The code that runs the fit is the **`sfitter`** package: it **extends the original SFitter
implementation with GPU support and importance sampling** — which is why the fit is a GPU job rather
than a local one. It implements the same three-distribution likelihood:

- `"pois"` modifiers → Poisson distribution
- `"stat"` modifiers → contributes to Poisson/Gaussian statistical term
- `"syst"` modifiers → Gaussian with $\rho = 0.99$ correlation
- `"theo"` modifiers → **Flat** (RFit) distribution

The systematic formula in the `sfitter` package's `ReadDataCard` (from `datacard.py`) combines measurement and background systematics:

$$\delta_{\text{syst}} = \sqrt{(m \cdot d)^2 + (b \cdot d_{\text{bkg}})^2 - 2 \times 0.99 \times (m \cdot d)(b \cdot d_{\text{bkg}})}$$

where the 0.99 factor encodes the near-total correlation between measurement and background systematic effects.
