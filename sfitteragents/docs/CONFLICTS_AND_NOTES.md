# Conflicts, Ambiguities, and Notes

Known conflicts between the sources, conventions to keep straight, and pitfalls of the tools.

---

## 1. HISZ vs Warsaw Basis in Combined Fit

**Conflict**: The Top sector uses the **Warsaw basis** (arXiv:1910.03606), while the Higgs/Di-Boson/EWPO sector uses the **HISZ basis** (arXiv:2208.08454). The combined fit (arXiv:2312.12502) requires basis translation.

**Sources**: Schmal thesis Section 2.2.2 and Section 5.3; arXiv:2312.12502 Eq. 5.4.

**Key translation**: $C_{\phi G} = -\frac{\alpha_s}{8\pi} f_{GG}$

**Impact for agents**: The agent uses Warsaw basis naming throughout (matching SMEFTatNLO). When interfacing with Higgs-sector SFitter inputs, basis translation may be needed.

---

## 2. Theory Uncertainty Treatment: Flat vs Gaussian

**Not a conflict** (deliberate choice), but a critical distinction to document:

- **SFitter**: Theory uncertainties (`"theo"` type) are treated as **flat** (uniform) distributions (RFit scheme). Source: arXiv:0709.3985, arXiv:2208.08454.
- **Other fitting groups** (SMEFiT, fitmaker, HEPfit): typically treat all uncertainties as **Gaussian**.
- **Our documentation** (in `docs/theory_uncertainties/03_additional_uncertainties.md`, Section 6.3) mentions both flat and Gaussian options but does not strongly state which SFitter uses.

**Impact**: Agents need to know that `"theo"` modifiers in SFitter JSON are interpreted as flat distributions, not Gaussian. This affects how theory uncertainty values should be set — they represent the **half-width of a uniform distribution**, not a standard deviation.

**See**: `docs/sfitter_methodology/01_sfitter_framework.md`.

---

## 3. Interference Terms: Neglect Decision

**Note** (not a conflict): The Schmal thesis (arXiv:2312.12502) found that interference terms between operator pairs are often too noisy to extract reliably, even with MadGraph accuracy set to 0.01% and multi-day computation times. The decision was made to **neglect interference for newly implemented measurements**.

**Sources**: Schmal thesis Section 4.2 (SMEFT interference), Figure 4.6.

**Impact for agents**: Attempt interference extraction, but expect to recommend neglecting interference for most pairs: in the Schmal thesis even 3-day MadGraph runs at 0.01% accuracy were insufficient for some pairs (e.g., $C_{td}^1$ and $C_{Qd}^1$). The interference noise finding is consistent across arXiv:1910.03606 and arXiv:2312.12502.

---

## 4. PDF Set Evolution

**Note**: The SFitter group switched from **NNPDF3.1 NLO** (used in arXiv:1910.03606) to **NNPDF4.0 NNLO** (used in arXiv:2312.12502) because NNPDF3.1 caused positivity issues in distribution tails with SMEFT contributions.

**Impact**: The agent should use **NNPDF4.0 NNLO** (`NNPDF40_nnlo_as_0118`) for all new predictions.

---

## 5. $O_G$ (Triple Gluon Operator) Exclusion

**Note**: $O_G = f^{ABC} G_\mu^{A\nu} G_\nu^{B\rho} G_\rho^{C\mu}$ is **not included** in the SFitter top-sector fit (arXiv:1910.03606). Its contributions to $t\bar{t}$ production are set to zero because multi-jet measurements provide much stronger constraints.

**Impact**: The operator catalog (docs/eft/02_operator_catalog.md) lists $O_G$ as a pure gauge operator. Agents should not attempt to parameterize $O_G$ effects on $t\bar{t}$ measurements — it should be excluded from the WC scan for top-pair production.

---

## 6. Scale Choice Discrepancy

**Minor discrepancy**: Two different dynamic scale choices are mentioned for $t\bar{t}$:
- Schmal thesis Eq. 4.3: $\mu_R = \mu_F = \frac{1}{2}(m_T(t) + m_T(\bar{t}))$
- NNLO predictions (HighTea): $H_T/4$ is commonly used

These are different functional forms but give similar numerical values near threshold. The discrepancy is $\mathcal{O}(10\%)$ and is within the scale variation uncertainty band.

**Impact**: For consistency, the agent should use the same scale choice for NLO SMEFT predictions as for the SM baseline. The Schmal thesis uses $(m_T(t) + m_T(\bar{t}))/2$ for MadGraph NLO and HighTea for NNLO k-factors.

**See**: docs/theory_uncertainties/01_scale_uncertainties.md and docs/sfitter_methodology/03_dataset_and_operators.md.

---

## 7. SMEFTatNLO Default-Nonzero Wilson Coefficients (Operator Contamination)

**Severity**: Critical.

**Issue**: SMEFTatNLO's default `param_card.dat` contains **nonzero values**
for many Wilson coefficients. Scanning a single operator (e.g., $C_{tG}$)
without explicitly zeroing the defaults lets them contribute to the matrix
element alongside the scanned operator, contaminating extracted
$\kappa_1$/$\kappa_2$ values.

**Which operators leak** (SMEFTatNLO has **five** DIM6 blocks, not three):
- `DIM6` block (bosonic + Yukawa): 8 default-nonzero entries → **safe** under
  `QED=0` (the QED filter strips them during code generation)
- `DIM62F` block (two-fermion): 19 default-nonzero entries → **safe** under
  `QED=0`
- `DIM64F` block (four-quark): 6 default-nonzero entries (codes 17, 19, 20,
  21, 23, 25) → **NOT safe**, must be manually zeroed. Four-fermion operators
  don't need EW insertions, so the `QED=0` filter leaves them alone. Codes
  17, 19, 20, 21, 25 all produce contaminating contributions via $d\bar d$,
  $s\bar s$, or $b\bar b$ initial states.
- `DIM64F2L` block (two-quark + two-lepton): all default-nonzero → **safe for
  hadronic processes at LO** (vertex structure requires external leptons which
  $pp \to t\bar t$ does not have), but **NOT safe** for any process with
  explicit leptons (Drell-Yan, $t\bar t \ell\ell$, etc.) or NLO EW corrections.
- `DIM64F4L` block (four-lepton): all default-nonzero → **trivially safe**
  for any process without external leptons (no quark legs at all).

For pure-hadronic $pp \to t\bar t$ at LO, the DIM64F2L and DIM64F4L blocks
do not contaminate (the matrix element `grep GC_` shows no DIM64F2L-derived
couplings). However, they MUST be zeroed for any process that includes leptons
in the matrix element.

**Empirical verification method**: Inspect the generated Fortran matrix elements
at `<proc_dir>/SubProcesses/P*/matrix*.f` and cross-reference coupling names
(`GC_N`) with `<proc_dir>/Source/MODEL/coupl.inc`. Only couplings derived from
the scanned operator (plus pure QCD) should appear.

**Recommended fix**: Use the **defensive zeroing pattern** — explicitly zero
every DIM64F code in every `.mg5` script, then enable only the scanned
operator(s). Optionally also zero DIM6/DIM62F for protection against future
changes that might drop `QED=0`.

**Reference documentation**: Full details, code templates, and the matrix
element verification procedure are in
[docs/eft/04_smeftatnlo_pitfalls.md](eft/04_smeftatnlo_pitfalls.md).

**Agent prompt**: `sf-scan-sanitizer` mandates
the parameter audit + defensive zeroing + post-generation matrix element
inspection for every SMEFTatNLO scan.

**Related**: The same file also documents the SMEFTatNLO vs LHC-TOPWG
convention mismatch for $c_{tG}$ (factor of $g_s$).

---

## 8. NNLO K-Factor Must Be Applied, Not Just Acknowledged

**Severity**: Critical.

**Issue**: When the SM prediction baseline is computed at LO or NLO MadGraph
but the published measurement is at NNLO precision, attaching a "NNLOrew" or
"ScalesNNLO" theory uncertainty modifier is **not** the same as applying the
NNLO k-factor. The uncertainty modifier accounts for variations *around* a
correctly-applied k-factor; it does not perform the correction itself.

If the k-factor is missing, the SM baseline is at the wrong perturbative order
relative to the data, and any per-bin shape mismatch between LO/NLO and NNLO
is silently absorbed into the Wilson coefficients during the fit. This produces
fake BSM preferences that look like genuine signals but are really
SM-modeling residuals.

**Quick sanity check**: compare the integrated cross-section implied by the
SM prediction in the data card against the published NNLO value for the
process. For $t\bar t$ at 13 TeV the literature NNLO value is ~832 pb. If
the data card's SM prediction integrates to ~480 pb (LO) or ~700 pb (NLO),
the k-factor was not applied.

**Symptoms in the fit output**:
- A normalized differential fit prefers a non-zero Wilson coefficient on a
  shape mode that matches the known NNLO/NLO-EW correction shape
- Adding the inclusive cross-section to the same fit produces a 2σ+ tension
  with the differential
- Whitened residuals show systematic structure (negative near threshold,
  positive in bulk, negative in tail) consistent with missing higher-order
  shape corrections

**Reference**: Full details and the correct procedure (NLO MadGraph → HighTea
k-factor per bin → apply, not assign uncertainty) are in
[docs/eft/03_parameterization_methodology.md](eft/03_parameterization_methodology.md)
Section 6.4.

### 8b. Uniform k-factor + missing ScaleSim

**Severity**: Critical. Two subtleties through which Entry 8 recurs even when
the integrated cross-section check passes:

1. **Uniform k-factor on a normalized differential.** A k-factor
   $k_{SM} = \sigma^{\rm NNLO}_{\rm incl} / \sigma^{\rm LO}_{\rm incl}$
   applied uniformly is correct for the inclusive piece, but if the
   distribution being fit is **normalized**, a uniform k cancels in the
   ratio and the differential template stays uncorrected.

2. **No ScaleSim on the template.** If MadGraph runs with `use_syst False`,
   per-bin scale variations are never generated and the prediction gets no
   `ScaleSim` modifier. `NNLOrew` and `ScalesT` are not substitutes — they
   are the k-factor-ratio uncertainty and the measurement-side theory
   uncertainty, typically an order of magnitude smaller than the LO
   template uncertainty that should be attached.

**Lessons**:

- For normalized differentials, a uniform k-factor is equivalent to no
  k-factor — the §6.4 integrated-cross-section sanity check cannot see
  this because the inclusive matches literature even while the differential
  template is uncorrected. The check must be "per-bin k-factor present
  and bin-dependent," not just "integrated cross-section matches."
- Missing template scale uncertainty is a **separate** failure mode from
  the missing k-factor. A fit can have a perfectly-applied k-factor and
  still be overconfident if ScaleSim is absent. See §6.5.
- Comparing against `Top_Full.json` or another canonical reference with
  well-attested ScaleSim values is an effective cross-check. A shift
  $\Delta C \gtrsim 1$ between configurations differing only in ScaleSim
  attachment is a bug signal, not a methodological difference.

**Reference**: `docs/eft/03_parameterization_methodology.md` Section 6.5
documents the ScaleSim requirement in detail.

---

## 9. Warnings (Less Severe, Worth Knowing)

These are not critical bugs, but failure modes worth knowing. Treat as advisory.

### 9a. Normalized-only fits are weak for total-cross-section operators

Operators whose dominant effect is an overall rescaling of the cross-section
(notably $C_{tG}$, but also several four-fermion operators) are intrinsically
poorly constrained when the only fit observable is a normalized differential
distribution like $1/\sigma \cdot d\sigma/dx$. The overall rescaling cancels
in the ratio, leaving only a small (typically a few percent) per-bin shape
change to constrain the operator.

In principle this is not a problem for SFitter, which combines multiple
measurements naturally — adding the inclusive cross-section as a separate
observation breaks the degeneracy. **However**, if a fit produces a Wilson
coefficient bound that is much wider than the published literature value, or
that prefers a value far from zero with weak chi² evidence, check whether the
relevant inclusive measurement is present in the data card. Missing inclusive
constraints on cross-section-rescaling operators is the most common cause of
this failure mode.

### 9b. SFitter dead-zone $\chi^2$ can mask poor fits

SFitter's RFit implementation produces a flat chi² "dead zone" around the
best-fit point with width proportional to the theory uncertainty. This is
correct behavior (it reflects the flat-prior treatment of theory uncertainties,
arXiv:0709.3985), but it has a side effect: a fit can have a very low
$\chi^2/{\rm dof}$ inside the dead zone while still being a poor description
of the data — the residuals are simply being absorbed into the theory
nuisance parameters.

**Recommendation**: As a sanity check, after any SFitter fit, also compute
the chi² without the dead-zone (e.g., a standard Gaussian-likelihood version
with the same covariance matrix). If the two differ by more than ~2x in
$\chi^2/{\rm dof}$, the dead-zone is masking residual structure that may
indicate either real BSM physics, missing higher-order corrections in the SM
prediction, or under-estimated experimental uncertainties.

### 9c. Inter-observation tension is a useful diagnostic

When two measurements that should constrain the same operator pull in opposite
directions, the simpler/cleaner measurement is usually the one to trust. In
practice this often means: **inclusive cross-section over normalized
differential** (the inclusive carries fewer modeling assumptions and is less
sensitive to shape modeling). A 2σ+ tension between the two for a single
operator is a strong hint that something is wrong with the differential
prediction (typically: missing higher-order corrections, wrong scale choice,
or unmodeled experimental systematics).

This is itself a valuable diagnostic — when running multi-observation fits,
report the per-observation chi² contributions at the combined best-fit point
alongside the combined result, so any tension is immediately visible.

---

## 10. Datacard Dialect: `Top_Full.json`/`Higgs_Full.json` Supersede `new_likelihood.json`

**Severity**: Critical (silent). A datacard authored to the older dialect either
fails to load or loads into the **wrong operator basis** with no error raised.

**Confirmed source of truth** (official): the installed parser
`sfitter/likelihood/datacard.py` (`ReadDataCard`) + `predictions.py`
(`get_smeft_matrix`), and the reference cards **`Top_Full.json`** (top) and
**`Higgs_Full.json`** (Higgs). These **supersede** all docs and the older
`new_likelihood.json` example.

**Two dialects existed.** An earlier format (Dialect A, `new_likelihood.json`) used a **flat observation `data`** array and prediction
modifier names with `_lin`/`_quad`/`{OP1}xD6{OP2}_interf` suffixes. The parser
and the canonical cards were rewritten to **Dialect B**: observations nest **`Meas`/`Bkg`** (`{data, modifiers}` each), and
prediction modifiers use **bare names + `x`-products** — `D6op` (linear),
`D6opxD6op` (quadratic), `D6op1xD6op2` (cross). The parser recovers the operator
structure by splitting the modifier name on the literal `x`
(`predictions.py:get_smeft_matrix`).

**Empirical failure modes** (against the installed `ReadDataCard`):
- A **flat-data** observation (Dialect A) → `KeyError: 'Meas'` at construction.
  It will not load at all.
- A `Meas`/`Bkg` card that keeps `_lin`/`_quad`/`_interf` **names** → loads, but
  every suffixed token fails to match an operator and is dropped to index `-1`;
  `_quad` (no `x`) is even mis-read as linear. The EFT terms silently collapse —
  a meaningless fit, no error. (`Top_Full.json` also contains a latent typo
  `D6qq18x6qt8` — a dropped `D` — illustrating the split-on-`x` fragility.)

**Operator basis is chosen by the run card, not the datacard.** The run card's
`sector` key (`top` — the default when absent — or `higgs`) selects which
operator list in `ProfileLikelihood` (`full_likelihood.py`) the fit varies; an
optional `parameter_names` list restricts it to a subset of that sector's basis
(operators left out are fixed at zero). After the `x`-split, any modifier token
not in the active list is dropped to index `-1`. So even a perfectly-formed
`Top_Full.json` mis-parameterizes under `sector: higgs`, and a D6 token missing
from a restricted `parameter_names` silently drops out.

**Impact for agents**: produce only Dialect B; match `Top_Full.json` /
`Higgs_Full.json`; never match `new_likelihood.json`; always confirm the
round-trip with `ReadDataCard`. For a top-sector fit, confirm the run card
selects `sector: top` (and that any `parameter_names` covers every D6 operator
the card carries).
