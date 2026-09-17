# SFitter Predictions Format

> **Canonical reference:** `Top_Full.json` (top sector) and `Higgs_Full.json` (Higgs sector),
> as accepted by the installed `ReadDataCard` / `predictions.get_smeft_matrix`. The earlier
> `new_likelihood.json` naming (`_lin`/`_quad`/`_interf` suffixes) is **deprecated** — the
> installed parser does not interpret those suffixes.

## 1. Structure

Each prediction object is paired with an observation by matching `ID`:

```json
{
  "name": "ttbar_ATLAS_diffxs_13_mtt_lj",
  "ID": "2210923",
  "data": [0.003291, 0.004605, 0.002628, ...],
  "modifiers": [
    {"name": "D6tg",         "data": [...]},
    {"name": "D6tgxD6tg",    "data": [...]},
    {"name": "D6qq18",       "data": [...]},
    {"name": "D6qq18xD6qq18","data": [...]},
    {"name": "D6tgxD6qq18",  "data": [...]},
    ...
  ]
}
```

### Fields

| Field | Description |
|-------|-------------|
| `data` | SM prediction per bin ($\sigma_{\text{SM},b}$) — same binning as the paired observation |
| `modifiers` | Wilson coefficient contributions: linear, quadratic, and cross (interference) terms |

---

## 2. Wilson Coefficient Naming Convention

The modifier name encodes **which Wilson coefficient(s) the term multiplies**, using the
literal `x` as the product operator. There are **no `_lin`/`_quad`/`_interf` suffixes**.

### Operator Names

| JSON name | Warsaw basis | Description |
|-----------|-------------|-------------|
| `D6tg` | $C_{tG}$ | Chromomagnetic dipole |
| `D6qq18` | $C_{Qq}^{1,8}$ | Four-fermion (LL, octet, SU(2) singlet) |
| `D6qq11` | $C_{Qq}^{1,1}$ | Four-fermion (LL, singlet, SU(2) singlet) |
| `D6qq38` | $C_{Qq}^{3,8}$ | Four-fermion (LL, octet, SU(2) triplet) |
| `D6qq31` | $C_{Qq}^{3,1}$ | Four-fermion (LL, singlet, SU(2) triplet) |
| `D6qt8` | $C_{tq}^{8}$ | Four-fermion (LR, octet: light doublet × top singlet) |
| `D6qt1` | $C_{tq}^{1}$ | Four-fermion (LR, singlet: light doublet × top singlet) |
| `D6ut8` | $C_{tu}^{8}$ | Four-fermion (RR, octet) |
| `D6ut1` | $C_{tu}^{1}$ | Four-fermion (RR, singlet) |
| `D6qu8` | $C_{Qu}^{8}$ | Four-fermion (LR, octet: heavy doublet × light up singlet) |
| `D6qu1` | $C_{Qu}^{1}$ | Four-fermion (LR, singlet: heavy doublet × light up singlet) |
| `D6dt8` | $C_{td}^{8}$ | Four-fermion (RR, octet) |
| `D6dt1` | $C_{td}^{1}$ | Four-fermion (RR, singlet) |
| `D6qd8` | $C_{Qd}^{8}$ | Four-fermion (LR, octet: heavy doublet × light down singlet) |
| `D6qd1` | $C_{Qd}^{1}$ | Four-fermion (LR, singlet: heavy doublet × light down singlet) |
| `D6tw` | $C_{tW}$ | Electroweak dipole |
| `D6bw` | $C_{bW}$ | Electroweak dipole |
| `D6phiq3` | $C_{\varphi Q}^{(3)}$ | Top–Higgs current (triplet) |
| `D6tz` | $C_{tZ}$ | Neutral electroweak dipole |
| `D6phiqm` | $C_{\varphi Q}^{(-)}=C_{\varphi Q}^{(1)}-C_{\varphi Q}^{(3)}$ | Top–Higgs current |
| `D6phit` | $C_{\varphi t}$ | Right-handed top–Higgs current |
| `D6phiphi` | $C_{\varphi tb}$ | Right-handed $Wtb$ current |

These are the 22 names of the top-sector fit basis (`_TOP_PARAMETER_NAMES` in
`sfitter/likelihood/full_likelihood.py`), the same tokens `Top_Full.json` uses. The `D6` prefix
stands for "dimension 6". Casing is load-bearing: every name is lower case (`D6qu1`, never
`D6Qu1`).

### Term Encoding

| Term | Modifier name | Scales as |
|------|---------------|-----------|
| Linear (SM–BSM interference) for operator `D6op` | `D6op` (bare) | $C_i / \Lambda^2$ |
| Quadratic (BSM squared) for operator `D6op` | `D6opxD6op` (self-product) | $C_i^2 / \Lambda^4$ |
| Cross-operator interference of `D6op1`,`D6op2` | `D6op1xD6op2` | $C_i C_j / \Lambda^4$ |

### Examples

```
D6tg          → linear term of C_tG
D6tgxD6tg     → quadratic (C_tG²) term
D6tgxD6qq18   → cross term between C_tG and C_Qq^{1,8}
D6tgxD6qq11   → cross term between C_tG and C_Qq^{1,1}
D6qq18xD6qq11 → cross term between C_Qq^{1,8} and C_Qq^{1,1}
```

**How the parser reads it.** `predictions.get_smeft_matrix` splits each modifier name on
the literal `x` and looks up each token in the fit's operator list: `D6tg` → linear in
$C_{tG}$; `D6tgxD6tg` → quadratic; `D6tgxD6qq18` → the $C_{tG}C_{Qq}^{1,8}$ cross term. A
token that is not a registered operator is silently dropped (mapped to index `-1`) — so the
bare operator names must match the fit's active operator list exactly (see §6).

---

## 3. Physics: How Predictions Are Used

The total prediction for bin $b$ with Wilson coefficients $\vec{C}$ active:

$$\sigma_{\text{pred},b}(\vec{C}) = \sigma_{\text{SM},b} + \sum_i C_i\,[\texttt{D6op}_i]_b + \sum_i C_i^2\,[\texttt{D6op}_i\texttt{xD6op}_i]_b + \sum_{i<j} C_i C_j\,[\texttt{D6op}_i\texttt{xD6op}_j]_b$$

where $[\texttt{name}]_b$ is the `data[b]` of the modifier with that name.

Or equivalently, in the normalized form used by SFitter:

$$\sigma_{\text{pred},b} = \sigma_{\text{SM},b} \left[1 + \sum_i \kappa_{1,i,b} C_i + \sum_i \kappa_{2,i,b} C_i^2 + \sum_{i<j} \kappa_{\text{int},ij,b} C_i C_j\right]$$

The `data` array in the prediction is $\sigma_{\text{SM},b}$, and the modifier `data` arrays
are the **absolute** contributions (the bare-name term, the self-product term, the
cross term), not the normalized $\kappa$ coefficients.

To convert:

$$\kappa_{1,i,b} = \frac{[\texttt{D6op}_i]_b}{\sigma_{\text{SM},b}}, \qquad \kappa_{2,i,b} = \frac{[\texttt{D6op}_i\texttt{xD6op}_i]_b}{\sigma_{\text{SM},b}}$$

---

## 4. Example: Complete Observation + Prediction Pair

From `Top_Full.json`, an ATLAS $t\bar{t}$ measurement at 13 TeV (illustrative values):

**Observation:** measured central values in `Meas.data`, background in `Bkg.data`, the
measurement-side uncertainties in `Meas.modifiers` (stat/syst/pois), and the theory
uncertainties in the observation-level `modifiers` (theo). See `01_json_schema.md`.

**Prediction:**
- SM: 818.635 pb → `data`
- $C_{tG}$ linear: +225.776 pb per unit $C_{tG}$ → `D6tg`
- $C_{tG}$ quadratic: +34.605 pb per unit $C_{tG}^2$ → `D6tgxD6tg`
- $C_{Qq}^{1,8}$ linear: +7.478 pb per unit $C_{Qq}^{1,8}$ → `D6qq18`
- etc.

So at $C_{tG} = 1$: $\sigma_{\text{pred}} = 818.635 + 225.776 + 34.605 = 1079.0$ pb.

---

## 5. Checklist for Producing a New Prediction Entry

When the agent produces a new measurement for SFitter:

1. **SM prediction** per bin → `predictions.data[]`
2. **Linear contribution** per operator per bin → `D6{op}` modifier (bare name)
3. **Quadratic contribution** per operator per bin → `D6{op}xD6{op}` modifier (self-product)
4. **Cross/interference terms** per operator pair per bin → `D6{op1}xD6{op2}` modifier
5. **Operator naming**: use the `D6` prefix convention matching existing entries; preserve casing
6. **Bin count**: must match the prediction `data` array length (= observation `Meas.data` length)
7. **ID**: must match the paired observation's `ID`

---

## 6. The Operator Basis Is Set by the Run Card

The operators the fit actually varies (the POIs) are **not** read from the datacard. The run
card's `sector` key (`top`, the default when absent, or `higgs`) selects one of the operator
lists in `ProfileLikelihood` (`full_likelihood.py`); an optional `parameter_names` list
restricts the fit to a subset of that sector's basis (operators left out are fixed at zero).
After the `x`-split, any token not in the active list is silently dropped (index `-1`), so:

- A top-sector card (`D6tg`, `D6qq18`, …) requires `sector: top`, or every operator
  collapses to `-1`.
- The bare operator names in the card must exactly match the names in the active list.

See `CONFLICTS_AND_NOTES.md` §10.
