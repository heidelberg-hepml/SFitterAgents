# EFT Parameterization Methodology

How to extract SMEFT operator effects from simulations and package them for global fits with SFitter.

---

## 1. Observable Parameterization

### 1.1 Cross-Section Dependence on Wilson Coefficients

At dimension 6, the cross-section depends on Wilson coefficients as:

$$\sigma_{\text{SMEFT}} = \sigma_{\text{SM}} + \frac{C_i}{\Lambda^2}\sigma_{\text{lin},i} + \frac{C_i^2}{\Lambda^4}\sigma_{\text{quad},i} + \frac{C_i C_j}{\Lambda^4}\sigma_{\text{interf},ij}$$

SFitter parameterizes this per bin as:

$$\sigma_{\text{SMEFT}} = \left[1 + \kappa_1 C + \kappa_2 C^2\right] \sigma_{\text{SM}}$$

where:
- $\kappa_1 = \sigma_{\text{lin}} / (\Lambda^2 \sigma_{\text{SM}})$: **linear coefficient** from SM-BSM interference, $\mathcal{O}(\Lambda^{-2})$
- $\kappa_2 = \sigma_{\text{quad}} / (\Lambda^4 \sigma_{\text{SM}})$: **quadratic coefficient** from BSM amplitude squared, $\mathcal{O}(\Lambda^{-4})$

### 1.2 Physical Meaning

The **linear term** arises from $2\,\text{Re}(\mathcal{A}_{\text{SM}}^* \cdot \mathcal{A}_{\text{BSM}})$ and captures how much the operator interferes with the SM process. It is the leading BSM effect.

The **quadratic term** arises from $|\mathcal{A}_{\text{BSM}}|^2$ and is always positive. It ensures physical cross-sections and is numerically dominant for some operators where the linear interference is helicity-suppressed.

The parameterization is **exactly quadratic** in $C$ because the amplitude is $\mathcal{A} = \mathcal{A}_{\text{SM}} + (C/\Lambda^2)\mathcal{A}_6$, and $|\mathcal{A}|^2$ is quadratic in $C$.

---

## 2. Normalized Distributions

### 2.1 The Normalization Problem

For normalized measurements ($1/\sigma \, d\sigma/dx$), the normalization itself depends on the Wilson coefficients.

Per-bin cross-section:

$$\sigma_b = \sigma_b^{\text{SM}} \left[1 + \kappa_{1,b}\, C + \kappa_{2,b}\, C^2\right]$$

Total cross-section:

$$\sigma_{\text{tot}} = \sigma_{\text{tot}}^{\text{SM}} \left[1 + \kappa_{1,t}\, C + \kappa_{2,t}\, C^2\right]$$

where $\kappa_{1,t} = \sum_b w_b \kappa_{1,b}$ with weights $w_b = \sigma_b^{\text{SM}}/\sigma_{\text{tot}}^{\text{SM}}$.

### 2.2 Taylor Expansion

The normalized SMEFT-to-SM ratio:

$$\frac{\sigma_{\text{norm}}}{\sigma_{\text{norm,SM}}} = \frac{1 + \kappa_{1,b}\, C + \kappa_{2,b}\, C^2}{1 + \kappa_{1,t}\, C + \kappa_{2,t}\, C^2}$$

Expanding to second order:

$$\frac{\sigma_{\text{norm}}}{\sigma_{\text{norm,SM}}} \approx 1 + a_{\text{norm}}\, C + c_{\text{norm}}\, C^2 + \mathcal{O}(C^3)$$

with:

$$a_{\text{norm}} = \kappa_{1,b} - \kappa_{1,t}$$

$$c_{\text{norm}} = \kappa_{2,b} - \kappa_{2,t} + \kappa_{1,t}^2 - \kappa_{1,b}\kappa_{1,t}$$

**Key consequences:**
- If all bins have the same $\kappa_1$, the linear term $a_{\text{norm}}$ vanishes — normalized distributions are only sensitive to **shape differences**
- One bin is always redundant ($\sum_b w_b \cdot a_{\text{norm},b} = 0$ by construction)
- Operators like $O_{tG}$ that contribute uniformly across bins are better constrained by absolute cross-sections than normalized distributions

---

## 3. Extracting Kappa Coefficients from Simulations

### 3.1 MadGraph Simulation Strategy

Using MadGraph with the SMEFTatNLO UFO model:

1. **SM baseline**: Generate the process at NLO with all WCs set to zero
2. **WC scan**: For each operator $C_i$, generate at multiple values (e.g., $C \in \{-10, -7.5, -5, -2.5, 2.5, 5, 7.5, 10\}$)
3. **Contribution separation**: MadGraph separates contributions by $\Lambda$ scaling:
   - Linear ($\Lambda^{-2}$): SM-BSM interference
   - Quadratic ($\Lambda^{-4}$): BSM amplitude squared

### 3.2 Polynomial Fitting

When fitting cross-sections at multiple WC values:

$$\sigma(C) = a_0 + a_1 C + a_2 C^2$$

Then: $\kappa_1 = a_1 / a_0$, $\kappa_2 = a_2 / a_0$

This is done **per bin** of each differential distribution.

### 3.3 Validation Checks

- **$R^2$ of fit**: Should be $> 0.999$. Poor $R^2$ indicates insufficient MC statistics or non-polynomial behavior
- **Residuals**: Should be consistent with MC statistical fluctuations and show no systematic pattern
- **$a_0$ consistency**: Compare with independent SM prediction
- **WC range**: Must be physically reasonable — too large risks EFT validity concerns

### 3.4 Direct Decomposition (Alternative)

MadGraph with SMEFTatNLO can output the three components separately via reweighting:
- $\sigma^{\text{SM}}$ (NP=0)
- $\sigma^{\text{int}}_i$ (interference, $\propto C_i$)
- $\sigma^{\text{BSM}}_{ij}$ (quadratic, $\propto C_i C_j$)

This avoids numerical fitting when available and is exact.

---

## 4. Interference Terms Between Operators

### 4.1 Cross-Operator Dependence

With multiple operators:

$$\sigma = \sigma_{\text{SM}} \left[1 + \sum_i \kappa_1^{(i)} C_i + \sum_{i \leq j} \kappa_2^{(ij)} C_i C_j\right]$$

The off-diagonal $\kappa_2^{(ij)}$ ($i \neq j$) come from $2\,\text{Re}(\mathcal{A}_{\text{BSM}}^{(i)*} \cdot \mathcal{A}_{\text{BSM}}^{(j)})$.

### 4.2 Extraction Method

1. Run with only operator $i$: extract $\kappa_1^{(i)}$, $\kappa_2^{(ii)}$
2. Run with only operator $j$: extract $\kappa_1^{(j)}$, $\kappa_2^{(jj)}$
3. Run with both active at reference values $C_i, C_j$
4. Subtract known individual contributions:

$$\sigma_{\text{interf}} = \sigma(C_i, C_j) - \sigma_{\text{SM}} - \sigma_{\text{SM}}(\kappa_1^{(i)} C_i + \kappa_2^{(ii)} C_i^2) - \sigma_{\text{SM}}(\kappa_1^{(j)} C_j + \kappa_2^{(jj)} C_j^2)$$

$$\kappa_2^{(ij)} = \frac{\sigma_{\text{interf}}}{\sigma_{\text{SM}} \cdot C_i \cdot C_j}$$

### 4.3 Practical Challenges

- **Interference is often small**: Off-diagonal terms frequently much smaller than diagonal $\kappa_2^{(ii)}$ because different operators affect different diagram topologies or helicity structures
- **Noise**: Extracted as difference of large numbers, so MC noise can be severe
- **MadGraph limitation**: The $\Lambda^{-4}$ output contains both quadratic and interference terms simultaneously — individual quadratic contributions must be subtracted
- **When to neglect**: A practical threshold is $|\kappa_2^{(ij)}| / \sqrt{\kappa_2^{(ii)} \kappa_2^{(jj)}} < 0.1$
- **Pair count**: For $N$ operators, there are $N(N-1)/2$ off-diagonal terms — computationally expensive for large operator sets

### 4.4 Noise Mitigation Strategies

- Increase MadGraph statistics (can require very long computation times)
- Optimize the fixed WC value to maximize interference relative to quadratic contributions
- Use the reweighting decomposition when available in MadGraph
- Accept that some interference terms are not reliably extractable (as found in the Schmal thesis for certain operator pairs like $C_{td}^1$ and $C_{Qd}^1$)

---

## 5. Uncertainty Treatment in Fits

### 5.1 Categories

#### Statistical Uncertainties
- **Uncorrelated** across bins and measurements
- Scale as $1/\sqrt{N}$ with luminosity
- Each bin has independent statistical uncertainty

#### Systematic Uncertainties (Experimental)
**Correlated across bins** within a measurement, often correlated across measurements.

| Category | Components | Correlation |
|----------|-----------|-------------|
| Jet energy scale (JES) | Flavor, pileup, $\eta$-intercalibration | Across bins and jet processes |
| Jet energy resolution (JER) | Smearing | Across bins |
| b-tagging | Efficiency for b, c, light jets | Across bins and b-jet processes |
| Lepton ID/isolation | Electron, muon efficiencies | Across bins |
| Luminosity | Overall normalization | Fully correlated (cancels in normalized distributions) |
| Pileup | Reweighting | Across bins |
| Backgrounds | Modeling of background processes | Process-specific |

#### Theory Uncertainties
- **Scale variation**: Vary $\mu_R$, $\mu_F$ by factors of $1/2$ and $2$ (7-point variation), take envelope
- **PDF uncertainties**: Hessian eigenvector sets (CT18, MSHT20) or MC replicas (NNPDF)
- **Generator differences**: Compare Powheg vs MadGraph, Pythia vs Herwig
- All correlated across bins; the correlation structure is non-trivial

### 5.2 Uncertainty Grouping for SFitter

Individual systematic sources are grouped into SFitter categories. For a normalized distribution, the total systematic per bin is distributed according to relative contributions:

$$\omega_b = \frac{\Delta_{\text{tot},b}}{\sqrt{\sum_j \Delta_j^2}}$$

where $\Delta_{\text{tot},b}$ is the total systematic in bin $b$ and $\Delta_j$ are the individual source contributions.

**The ordering of uncertainties matters**: uncertainties at the same position in different measurements are treated as correlated in SFitter.

### 5.3 SFitter Data Format

Measurements are encoded as:

```
MEASUREMENT_NAME_i = sigma_meas,i ± Delta_syst,i ± Delta_stat,i ± Delta_hat,i
```

The uncertainty columns follow a fixed ordering convention so that correlated systematics align across measurements.

### 5.4 Nuisance Parameter Treatment

SFitter introduces nuisance parameters $\theta_k$ for each correlated uncertainty source:

$$\mu_b(\vec{C}, \vec{\theta}) = \mu_b^{\text{SMEFT}}(\vec{C}) + \sum_k \theta_k \cdot \Delta_{b,k}$$

The $\chi^2$ includes a penalty:

$$\chi^2 = \sum_b \frac{(\mu_b - d_b)^2}{\sigma_{\text{stat},b}^2} + \sum_k \theta_k^2$$

Nuisance parameters are either **profiled** (minimized over) or **marginalized** (integrated over, Bayesian).

---

## 6. K-Factors and Higher-Order Corrections

### 6.1 Definition

$$k = \frac{\sigma_{\text{NNLO}}}{\sigma_{\text{NLO}}}$$

Can be inclusive (single number) or differential (per-bin $k_b$). Differential k-factors capture shape changes from higher-order corrections.

### 6.2 Mixed-Order Strategy

- **SM prediction**: NNLO QCD (via HighTea, MATRIX, MCFM, or fastNLO tables)
- **SMEFT corrections**: NLO QCD (via MadGraph + SMEFTatNLO)
- **Combined prediction**:

$$\sigma_{\text{pred}} = \sigma_{\text{SM}}^{\text{NNLO}} \left[1 + \kappa_1^{\text{NLO}} C + \kappa_2^{\text{NLO}} C^2\right]$$

This assumes the NNLO/NLO ratio is similar for SM and SMEFT contributions. This is generally a good approximation because higher-order QCD radiation is largely independent of the short-distance EFT vertex. *(⚠ This holds only for operators that **preserve** the SM QCD order — not for the top-sector dipole/four-fermion set. See the NLO-isolation caveat immediately below.)*

### SMEFT order in practice — the NLO-isolation trap and the LO+k fallback

The κ-at-NLO prescription above is the published SFitter default (arXiv:2312.12502),
**but it structurally fails for operators whose insertion changes the QCD order relative to the SM
Born** — the top-sector norm: the chromomagnetic dipole `ctG` (extra $g_s$ → QCD=1 per insertion)
and the four-fermion octets (`ctq8`, `cQq8`, `cQu8`, `cQd8`, `ctu8`, `ctd8`, …; QCD=0 vs the SM's
QCD=2). For these, isolating the interference ($\Lambda^{-2}$) and quadratic ($\Lambda^{-4}$)
pieces at NLO — which the κ parameterization requires — cannot be done cleanly:

1. **`NP^2==N` isolation is forbidden at NLO.** MadGraph accepts only `<=` squared-order
   constraints at NLO (`amcatnlo_interface.py`); the negative selector `NP^2<=-1` passes the gate
   but is *cumulative*, not isolating. No squared-order form both runs at NLO and isolates a single
   order. (`NP^2==` works only at **LO**.)
2. **The single-run `NP^2<=N [QCD]` route mixes Born orders** (SM Born at QCD=2/NP=0 alongside the
   EFT-interference Born at a different QCD power) → the "Born diagrams do not factorize" warning —
   a *real correctness hazard*, because mixed-Born-order makes the real radiation inconsistent with
   the virtuals.
3. **It dies at fixed-order integration with a pole miscancellation** (structural ~9% MadFKS-vs-OLP
   mismatch on the NP=2 split-order: `POLES MISCANCELLATION … TOO MANY FAILURES`). Crucially, a
   **setup `check_poles` can PASS while the full integration fails** — it tests one FKS
   configuration at RAMBO points, so it is not sufficient evidence. The tolerance knobs
   (`IRPoleCheckThreshold`, `PrecisionVirtualAtRunTime=-1`) **mask** the wrong subtraction; they do
   not fix it.

**Gate — probe before committing an NLO scan.** If any operator in the scan changes the QCD order
vs the SM Born and NLO is under consideration, run a **short fixed-order *integration* pole probe**
on one operator (the dominant, e.g. `ctG`) + SM *first* (a miscancellation surfaces in seconds),
and only then recommend NLO. Never present an NLO-vs-LO decision that rests on a "the warning is
benign / nothing branches on it" reading — that is a statement about code flow, not physics
correctness.

**Fallback when the probe fails — LO κ × the SM higher-order k-factor** (the recognized "K-factor
approximation"). At LO the linear/quadratic separation is clean and exact for *all* operators
including `ctG` (`NP^2==` is available at LO), with no order-mixing and no pole miscancellation. The
SM template already carries $\sigma_{\text{SM}}^{\text{NLO}} \times$ the NNLO k-factor, so:

$$\sigma_{\text{pred}} = \sigma_{\text{SM}}^{\text{NNLO}} \left[1 + \kappa_1^{\text{LO}} C + \kappa_2^{\text{LO}} C^2\right]$$

**Caveat — an approximation, not free.** LO κ misses the genuine NLO-EFT corrections (~10–40%,
operator- and interference/quadratic-dependent, and possibly **large or negative** where an LO
suppression lifts at NLO). Do **not** assume the SM k-factor proxies the EFT k-factor: SMEFTatNLO
(arXiv:2008.11743) measured EFT k-factors that vary operator-to-operator and between interference
and quadratic, ranging 1–2 and even negative (e.g. $O_W$); the approximation degrades for large $C$
and in BSM-sensitive tails. Surface the LO-vs-NLO choice to the user with this evidence — do not
silently pick.

### 6.3 Tools

- **HighTea**: Web API for NNLO predictions using precomputed event databases
- **fastNLO / APPLgrid / PineAPPL**: Interpolation grids for fast NLO/NNLO re-evaluation with different PDFs/scales
- **MCFM, MATRIX**: Dedicated NNLO calculators
- **MadGraph + SMEFTatNLO**: NLO SMEFT predictions with automatic linear/quadratic decomposition

### 6.4 Critical Warning: K-Factor Application Is a Separate Step

A subtle and dangerous failure mode: producing the LO (or NLO) MadGraph SM
prediction, attaching an "NNLO uncertainty" modifier to it, but **never actually
multiplying by the k-factor**. The result is that the SM baseline used in the
fit is at the wrong perturbative order, and any per-bin shape mismatch between
the LO/NLO SM prediction and the (typically NNLO-precision) measured data will
be absorbed into the Wilson coefficients as a fake BSM signal.

Symptoms of this failure mode:
- Comparing $\sigma_{\text{SM}}^{\text{tot}}$ from the fit's prediction file
  against the literature NNLO value: for $t\bar t$ at 13 TeV, NNLO is ~832 pb;
  if the fit's SM prediction reports ~480 pb (LO) or ~700 pb (NLO), the
  k-factor was not applied
- A normalized differential fit prefers a non-zero Wilson coefficient on a
  shape mode that happens to look like the known NNLO/NLO-EW correction shape
- The same operator gives wildly different best-fit values from inclusive vs
  differential measurements (the inclusive is less sensitive to shape
  mis-modeling and tends to give the "true" answer; the differential is
  contaminated by the missing higher-order shape physics)
- Whitened residuals after the fit have systematic structure (e.g., negative
  near threshold, positive in the bulk, negative in the tail) that matches
  the expected pattern of missing NNLO corrections

The correct procedure for the SM prediction is:

1. Run MadGraph at NLO with SMEFTatNLO → get $\sigma_b^{\text{NLO}}$ per bin
2. Obtain the **per-bin** NNLO/NLO k-factor $k_b$ from HighTea (or MATRIX, fastNLO)
   using **the same scale choice, PDF, and binning** as the NLO MadGraph run.
   A single uniform $k$ applied to every bin of a **normalized** differential
   $(1/\sigma)\,d\sigma/dx$ cancels in the ratio and produces no shape
   correction — it is a no-op on the fit. The k-factor must be bin-dependent
   to be useful for normalized observables.
3. **Apply** the k-factor: $\sigma_b^{\text{SM,used}} = k_b \cdot \sigma_b^{\text{NLO}}$
4. Use $\sigma_b^{\text{SM,used}}$ as the baseline in the parameterization
   $\sigma_{\text{SMEFT},b} = \sigma_b^{\text{SM,used}} (1 + \kappa_{1,b} C + \kappa_{2,b} C^2)$
5. The k-factor uncertainty (scale variation of the NNLO/NLO ratio, generator
   differences, etc.) is then a separate "NNLOrew" or "ScalesNNLO" modifier on
   top of the corrected baseline — **not** a stand-in for the correction itself.
   Typical magnitude is ~1-3% per bin; if your "NNLOrew" values look like
   ~10-40%, you are describing the k-factor itself, not its uncertainty, and
   the central value has not been corrected.

A quick sanity check before any fit: compute the integrated cross-section
implied by the SM prediction in the data card, and compare against the
published NNLO value for the process. They should agree within a few percent.
A factor-of-1.5–2 disagreement means the k-factor was missed.

### 6.5 Template Scale Uncertainty on the SM Prediction

Independent of whether a k-factor was applied, the SM prediction template
itself has a scale/PDF uncertainty that must be attached to the prediction
as its own modifier. This is a separate question from k-factor application
and a separate modifier from NNLOrew:

| Modifier | What it represents | Typical magnitude ($t\bar t$ $m_{t\bar t}$) |
|----------|--------------------|---------------------------------------------|
| **ScaleSim** / **ScalesSim** | $\mu_R$, $\mu_F$ scale variation of the SM template at its actual perturbative order | ~8-15% per bin (LO), ~3-5% per bin (NLO), ~1-3% per bin (NNLO) |
| **PDFSim** | PDF set variation / error-set envelope of the SM template | ~1-3% per bin |
| **NNLOrew** | Uncertainty on the NNLO/NLO k-factor ratio (only if a k-factor was applied) | ~1-3% per bin |
| **ScalesT** | Scale uncertainty of the measured data's unfolding / theory-modeling source (observation-side) | reported by the measurement |

The "Sim" suffix signals that the modifier lives on the **prediction (Sim)**
side, not the measurement side. Canonical reference datasets like
`Top_Full.json` attach ScaleSim on the observation side to cover the same
LO-template scale uncertainty; either attachment is acceptable as long as
the uncertainty is present somewhere and propagated correctly.

**Why this matters:** without ScaleSim (or an equivalent), the fit treats
the SM template as perfectly known. Any residual shape mismatch between the
template and the data — whether from missing higher-order corrections,
imperfect k-factor reweighting, or genuine physics — is absorbed into the
Wilson coefficients as a fake BSM preference. The symptom looks identical
to the §6.4 missing-k-factor failure mode, and the two failures can compound.

**How to extract ScaleSim / PDFSim:**

1. **MadGraph with `use_syst True`**: generates per-event scale- and
   PDF-variation weights. Post-process the MadGraph output to extract the
   per-bin envelope of the 7-point ($\mu_R$, $\mu_F \in \{0.5, 1, 2\}$ with
   $|\ln(\mu_R/\mu_F)| \le \ln 2$) variations for ScaleSim, and the PDF
   error-set envelope for PDFSim. **Required**: do NOT run with
   `use_syst False` if the run will feed an SFitter config — the scale
   information is lost and cannot be reconstructed after the fact without
   rerunning MadGraph.
2. **HighTea / fastNLO / MATRIX**: if these tables were used for the
   k-factor, they provide bin-level NNLO scale uncertainties directly.
3. **Literature envelope (fallback)**: if neither of the above is
   available, a flat per-bin envelope drawn from the published theory
   uncertainty on the same observable is acceptable with a clear note in
   the extraction report. This is strictly a stopgap; a re-run with
   `use_syst True` is preferred.

**Sanity cross-check**: compare the sum of template modifiers
($\sqrt{\text{ScaleSim}^2 + \text{PDFSim}^2}$ per bin) against the total
theory uncertainty quoted in the measurement paper on the SM prediction.
Agreement to within a factor of 2 is expected; large disagreement indicates
either a missing modifier or a magnitude error.

The §6.4 check and the §6.5 check are independent; both must pass.

---

## 7. Complete Workflow Summary

```
Phase 1: Extract measurement data + uncertainties
         Source: Paper, HEPData
         Output: Measured values per bin, uncertainty breakdown by source

Phase 2: Select operators
         Source: Physics knowledge, expected sensitivity
         Output: List of Wilson coefficients to scan

Phase 3: SM prediction
         Tool: MadGraph (NLO) + k-factors (NNLO via HighTea)
         Output: sigma_SM per bin, theory uncertainties

Phase 4: Single-operator scan
         Tool: MadGraph + SMEFTatNLO at multiple WC values
         Output: kappa_1, kappa_2 per bin per operator

Phase 5: Interference (optional)
         Tool: MadGraph with operator pairs
         Output: kappa_2^{ij} per bin per pair (or decision to neglect)

Phase 6: Config file
         Assembly: Data + uncertainties + SM prediction + kappa tables
         Format: SFitter convention
```
