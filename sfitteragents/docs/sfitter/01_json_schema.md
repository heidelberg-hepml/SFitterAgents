# SFitter JSON Schema

The SFitter data format stores experimental observations, their uncertainties, and theoretical SMEFT predictions in a single JSON file. Each file represents a dataset (e.g., "Top sector", "Higgs sector") containing multiple measurements.

> **Canonical source of truth.** This schema describes the format accepted by the
> **installed** `ReadDataCard` (`sfitter/likelihood/datacard.py`) and matches the
> shipped reference cards **`Top_Full.json`** (top sector) and **`Higgs_Full.json`**
> (Higgs sector). These two cards supersede everything else. The older
> `new_likelihood.json` uses a **deprecated** earlier dialect (flat observation `data`,
> `_lin`/`_quad`/`_interf` modifier names) that the installed parser does **not** accept —
> it raises `KeyError: 'Meas'`. Do not use it as a template. When in doubt, match
> `Top_Full.json`/`Higgs_Full.json` and confirm the round-trip with `ReadDataCard`.

## Top-Level Structure

```json
{
  "observations": [ ... ],   // Array of observation objects
  "predictions": [ ... ]     // Array of prediction objects (paired with observations)
  // "version": "1.0.0"      // OPTIONAL — present in Higgs_Full.json, absent in Top_Full.json
}
```

Observations and predictions are paired by matching `ID` fields. `version` is optional —
do not require it (`Top_Full.json` has none).

---

## Observation Object

Each observation represents one measurement (total cross-section, or a differential distribution with multiple bins). The measured values and the background live in **nested `Meas` and `Bkg` objects** — there is **no flat `data` array on the observation itself**.

```json
{
  "name": "ttbar_ATLAS_diffxs_13_mtt_lj",
  "ID": "2210923",
  "bin_widths": [75, 80, 100, 120, 160, 160, 230, 250, 500],
  "Meas": {
    "data": [0.00297128, 0.00386455, 0.00220051, ...],
    "modifiers": [
      {"name": "Pois", "energy": "13TeV", "label": "Pois", "type": "pois", "data": [0.0, ...]},
      {"name": "stat", "energy": "13TeV", "label": "Stat", "type": "stat", "data": [0.261, ...]},
      {"name": "MC",   "energy": "13TeV", "label": "Stat", "type": "stat", "data": [0.219, ...]},
      {"name": "Luminosity", "energy": "13TeV", "label": "LHC",   "type": "syst", "data": [2.1, ...]},
      {"name": "Jets", "energy": "13TeV", "label": "ATLAS", "type": "syst", "data": [2.08, ...]},
      {"name": "BkgTTBar", "energy": "13TeV", "label": "ATLAS", "type": "syst", "data": [1.1, ...]}
    ]
  },
  "Bkg": {
    "data": [0.0, ...],
    "modifiers": []
  },
  "modifiers": [
    {"name": "PDF",     "energy": "13TeV", "label": "Theo", "type": "theo", "data": [1.2, ...]},
    {"name": "ScalesT", "energy": "13TeV", "label": "Theo", "type": "theo", "data": [11.5, ...]}
  ]
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Human-readable measurement name (e.g., `ttbar_ATLAS_diffxs_13_mtt_lj`) |
| `ID` | string | Yes | Unique SFitter-style identifier (e.g., `"2210923"`, see ID encoding below) |
| `bin_widths` | array[float] | Yes | Width of each bin (for differential distributions; `[1.0]` for total cross-sections) |
| `Meas` | object | Yes | `{ "data": [...], "modifiers": [...] }` — the measured central values + the measurement-side uncertainty modifiers |
| `Bkg` | object | Yes | `{ "data": [...], "modifiers": [...] }` — the background central values + background-side modifiers (`modifiers` may be empty) |
| `modifiers` | array[object] | Yes | The observation-level modifier list — holds the **`theo`** (theory-on-SM) modifiers |
| `Luminosity` | array[float] | No | Higgs-sector cards only (e.g. `[4.5]`) |
| `Decay` | array[string] | No | Higgs-sector cards only (e.g. `["brw"]`) — selects the Higgs decay path |

`ReadDataCard` reads `observation['Meas']['data']`, `observation['Bkg']['data']`,
`observation['Meas']['modifiers']`, `observation['Bkg']['modifiers']`, and
`observation['modifiers']` (the theo list). A flat-data observation (`data` directly on the
observation, no `Meas`) raises `KeyError: 'Meas'` at construction.

For total cross-sections: `Meas.data`, `Bkg.data`, and `bin_widths` are single-element arrays.
For differential distributions: arrays have length = number of bins.

### Modifier Object

The modifier object shape is the same wherever it appears (inside `Meas.modifiers`,
`Bkg.modifiers`, or the observation-level `modifiers`):

```json
{
  "name": "Jets",           // Uncertainty source name
  "energy": "13TeV",        // Collision energy (optional)
  "label": "ATLAS",         // Category label for correlation grouping (optional)
  "type": "syst",           // One of: "pois", "stat", "syst", "theo"
  "data": [2.08, 0.81, ...] // Per-bin uncertainty values
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Name of the uncertainty source |
| `type` | string | `"pois"` / `"stat"` / `"syst"` / `"theo"` |
| `energy` | string | Collision energy (e.g., `"13TeV"`) |
| `label` | string | Correlation group label (e.g., `"ATLAS"`, `"LHC"`, `"Theo"`, `"Stat"`) |
| `data` | array[float] | Per-bin values. Interpretation depends on type (see modifier_types.md) |

**Where each modifier type lives** (see `02_modifier_types.md` §1.5):
`pois` / `stat` / `syst` go inside `Meas.modifiers` (and the background-side ones inside
`Bkg.modifiers`); `theo` goes in the **observation-level** `modifiers` list.

**Data array length** must match the length of `Meas.data` (= `bin_widths`).

---

## Prediction Object

Each prediction is paired with an observation by matching `ID`. The prediction is flat:
its `data` is the per-bin SM cross-section and its `modifiers` are the Wilson-coefficient
contributions.

```json
{
  "name": "ttbar_ATLAS_diffxs_13_mtt_lj",
  "ID": "2210923",
  "data": [0.003291, 0.004605, 0.002628, ...],
  "modifiers": [
    {"name": "D6tg",        "data": [0.001281, 0.001500, ...]},
    {"name": "D6tgxD6tg",   "data": [0.000192, 0.000239, ...]},
    {"name": "D6qq18",      "data": [2.568e-05, 3.699e-05, ...]},
    {"name": "D6qq18xD6qq18","data": [9.528e-07, 2.208e-06, ...]},
    {"name": "D6tgxD6qq18", "data": [2.624e-06, 4.713e-06, ...]},
    ...
  ]
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Measurement name (matches observation) |
| `ID` | string | Identifier (matches observation's `ID`) |
| `data` | array[float] | SM prediction per bin (same binning as observation) |
| `modifiers` | array[object] | Wilson coefficient contributions (linear, quadratic, cross) |

### Prediction Modifier (Wilson Coefficient Term)

```json
{"name": "D6tg", "data": [0.001281, 0.001500, ...]}
```

**Naming convention** — the modifier name encodes which Wilson coefficient(s) the term
multiplies; there are **no `_lin`/`_quad`/`_interf` suffixes**:

| Term | Modifier name | Scales as |
|------|---------------|-----------|
| Linear (SM–BSM interference) for operator `D6op` | **`D6op`** (bare) | $C_i/\Lambda^2$ |
| Quadratic (BSM²) for operator `D6op` | **`D6opxD6op`** (self-product) | $C_i^2/\Lambda^4$ |
| Cross / operator-interference of `D6op1`,`D6op2` | **`D6op1xD6op2`** | $C_i C_j/\Lambda^4$ |

The parser derives the operator structure by **splitting the modifier name on the literal
`x`** (`predictions.py:get_smeft_matrix`) and matching each token against the fit's operator
list. Casing is load-bearing: the top-sector names are all lower case (`D6qu1`, never `D6Qu1`).

The prediction with Wilson coefficients active is:

$$\sigma_{\text{pred},b}(\vec C) = \sigma_{\text{SM},b} + \sum_i C_i\,[\,\texttt{D6op}_i\,]_b + \sum_i C_i^2\,[\,\texttt{D6op}_i\texttt{xD6op}_i\,]_b + \sum_{i<j} C_i C_j\,[\,\texttt{D6op}_i\texttt{xD6op}_j\,]_b$$

where $[\texttt{name}]_b$ is that modifier's `data[b]`.

> **Operator basis is set by the run card, not this file.** The set of operators the fit
> actually varies is chosen by the run card's `sector` key (`top`, the default, or `higgs`;
> operator lists in `ProfileLikelihood`, `full_likelihood.py`), optionally restricted by a
> `parameter_names` list — it is **not** read from the datacard. Tokens (after the `x`-split)
> that are not in the active list are silently dropped (mapped to index `-1`). A top-sector
> fit therefore requires `sector: top`. See `CONFLICTS_AND_NOTES.md` §10.

---

## Example: Total Cross-Section

```json
{
  "name": "ttbar_ATLAS_totalxs_13",
  "ID": "2261133",
  "bin_widths": [1.0],
  "Meas": {
    "data": [816.318],
    "modifiers": [
      {"name": "Pois", "energy": "13TeV", "label": "Pois", "type": "pois", "data": [0.0]},
      {"name": "stat", "energy": "13TeV", "label": "Stat", "type": "stat", "data": [0.318572]},
      {"name": "MC",   "energy": "13TeV", "label": "Stat", "type": "stat", "data": [0.276735]},
      {"name": "Luminosity", "energy": "13TeV", "label": "LHC",   "type": "syst", "data": [0.472078]},
      {"name": "Jets", "energy": "13TeV", "label": "ATLAS", "type": "syst", "data": [0.430159]},
      {"name": "bTagging", "energy": "13TeV", "label": "ATLAS", "type": "syst", "data": [0.427177]},
      {"name": "Leptons",  "energy": "13TeV", "label": "ATLAS", "type": "syst", "data": [0.900325]},
      {"name": "Beam",     "energy": "13TeV", "label": "ATLAS", "type": "syst", "data": [0.166527]}
    ]
  },
  "Bkg": { "data": [0.0], "modifiers": [] },
  "modifiers": [
    {"name": "PDF",     "energy": "13TeV", "label": "Theo", "type": "theo", "data": [0.45]},
    {"name": "ScalesT", "energy": "13TeV", "label": "Theo", "type": "theo", "data": [10.0]}
  ]
}
```

## Example: Differential Distribution

See the ATLAS $t\bar{t}$ $m_{t\bar{t}}$ distribution in `Top_Full.json` (a multi-bin
differential with nested `Meas`/`Bkg` and bare/`x`-product prediction modifiers), and
`Higgs_Full.json` for the Higgs-sector path (with `Luminosity`/`Decay` and `cs*` prediction
modifiers).
