# SFitter Output for a Reinterpreted Measurement

## Goal

The agent should produce a **single JSON file** containing one observation entry (the newly reinterpreted measurement) with its paired prediction, in the SFitter format. The user will manually concatenate this into the full dataset JSON.

---

## 1. What the Agent Needs to Produce

A JSON file with this structure:

```json
{
  "observations": [
    {
      "name": "<measurement_name>",
      "ID": "<sfitter_id>",
      "bin_widths": [<bin widths>],
      "Meas": {
        "data": [<measured values per bin>],
        "modifiers": [
          {"name": "Pois", "energy": "13TeV", "label": "Pois", "type": "pois", "data": [0.0, ...]},
          {"name": "stat", "energy": "13TeV", "label": "Stat", "type": "stat", "data": [<% per bin>]},
          {"name": "MC", "energy": "13TeV", "label": "Stat", "type": "stat", "data": [<% per bin>]},
          {"name": "Luminosity", "energy": "13TeV", "label": "LHC", "type": "syst", "data": [<% per bin>]},
          {"name": "Jets", "energy": "13TeV", "label": "<experiment>", "type": "syst", "data": [<% per bin>]},
          ...
        ]
      },
      "Bkg": { "data": [<background per bin>], "modifiers": [] },
      "modifiers": [
        {"name": "PDFSim", "energy": "13TeV", "label": "Theo", "type": "theo", "data": [<% per bin>]},
        {"name": "ScalesT", "energy": "13TeV", "label": "Theo", "type": "theo", "data": [<% per bin>]}
      ]
    }
  ],
  "predictions": [
    {
      "name": "<measurement_name>",
      "ID": "<sfitter_id>",
      "data": [<SM prediction per bin>],
      "modifiers": [
        {"name": "D6tg", "data": [<absolute contribution per bin>]},
        {"name": "D6tgxD6tg", "data": [<absolute contribution per bin>]},
        {"name": "D6tgxD6qq18", "data": [<absolute contribution per bin>]},
        ...
      ]
    }
  ]
}
```

Measured values live in `Meas.data`, background in `Bkg.data`; the measurement-side
uncertainties (`pois`/`stat`/`syst`) go in `Meas.modifiers`, theory uncertainties (`theo`)
in the observation-level `modifiers`. `version` is optional. Prediction modifiers use bare
operator names (linear), self-products `D6opxD6op` (quadratic), and `D6op1xD6op2` (cross).

---

## 2. Mapping from Agent Workflow to JSON Fields

| JSON field | Source in agent workflow | Phase |
|------------|------------------------|-------|
| `observations.Meas.data` | Measured values from paper/HEPData | Phase 1 (Measurement Extraction) |
| `observations.Bkg.data` | Background central values per bin | Phase 1 / Phase 3 |
| `observations.bin_widths` | Bin edges from paper/HEPData | Phase 1 |
| `observations.ID` | Assigned using SFitter encoding convention | Phase 1 |
| Modifiers type `"stat"` | Statistical uncertainties from paper | Phase 1 |
| Modifiers type `"syst"` | Systematic uncertainties from paper, grouped into SFitter categories | Phase 1 |
| Modifiers type `"theo"` | Theory uncertainties from scale/PDF variation | Phase 3 (SM Prediction) |
| Modifiers type `"pois"` | Typically `[0.0, ...]` for unfolded measurements | Phase 1 |
| `predictions.data` | SM prediction per bin (NLO/NNLO) | Phase 3 |
| `predictions.modifiers` (`D6op`, `D6opxD6op`) | Linear + quadratic from WC scans | Phase 4 (Single-Operator) |
| `predictions.modifiers` (`D6op1xD6op2`) | Cross/interference coefficients from pair scans | Phase 5 (Interference) |

Note: `pois`/`stat`/`syst` modifiers live in `observations.Meas.modifiers` (background-side
ones in `observations.Bkg.modifiers`); `theo` modifiers live in the observation-level
`observations.modifiers`.

---

## 3. Key Formatting Requirements

### 3.1 Uncertainty Values Are Percentages

All `stat`, `syst`, and `theo` modifier `data` values are **percentages** (not fractions, not absolute). The SFitter code converts internally:

```python
absolute_uncertainty = percentage / 100.0 * measured_value
```

### 3.2 Prediction Modifiers Are Absolute

Wilson coefficient contributions — the bare-name linear term `D6op`, the self-product quadratic `D6opxD6op`, and the cross term `D6op1xD6op2` — are **absolute values** (same units as the cross-section), not percentages and not normalized $\kappa$ coefficients.

### 3.3 Array Lengths Must Match

All `data` arrays within one observation (measurements + all modifiers) must have the same length = number of bins.

### 3.4 Operator Naming Must Match Existing Convention

Use `D6` prefix: `D6tg`, `D6qq18`, `D6qq11`, `D6qq38`, etc. New operators must follow the same pattern. Check `sfitter/data/Top_Full.json` for the complete list of operator names in use.

### 3.5 Modifier Names Must Match for Correlation

Systematic modifiers with the same `name` across different observations are correlated in the fit. Use the exact names from the SFitter uncertainty index (e.g., `"Jets"`, not `"JES"` or `"JetEnergy"`).

---

## 4. Example Output

For a new CMS $t\bar{t}$ differential cross-section in $p_T(t_h)$ at 13 TeV with 3 operators ($C_{tG}$, $C_{Qq}^{1,8}$, $C_{Qq}^{1,1}$) and 3 bins:

```json
{
  "observations": [
    {
      "name": "ttbar_CMS_diffxs_13_pTth_lj",
      "ID": "2211223",
      "bin_widths": [100, 150, 300],
      "Meas": {
        "data": [0.00234, 0.00156, 0.00045],
        "modifiers": [
          {"name": "Pois", "energy": "13TeV", "label": "Pois", "type": "pois", "data": [0.0, 0.0, 0.0]},
          {"name": "stat", "energy": "13TeV", "label": "Stat", "type": "stat", "data": [1.2, 2.1, 5.3]},
          {"name": "MC", "energy": "13TeV", "label": "Stat", "type": "stat", "data": [0.8, 1.5, 3.2]},
          {"name": "Luminosity", "energy": "13TeV", "label": "LHC", "type": "syst", "data": [2.1, 2.1, 2.1]},
          {"name": "Jets", "energy": "13TeV", "label": "CMS", "type": "syst", "data": [1.5, 2.3, 4.1]},
          {"name": "bTagging", "energy": "13TeV", "label": "CMS", "type": "syst", "data": [0.9, 1.1, 1.3]}
        ]
      },
      "Bkg": { "data": [0.0, 0.0, 0.0], "modifiers": [] },
      "modifiers": [
        {"name": "PDFSim", "energy": "13TeV", "label": "Theo", "type": "theo", "data": [0.25, 0.31, 0.42]},
        {"name": "ScalesT", "energy": "13TeV", "label": "Theo", "type": "theo", "data": [8.5, 9.2, 12.1]}
      ]
    }
  ],
  "predictions": [
    {
      "name": "ttbar_CMS_diffxs_13_pTth_lj",
      "ID": "2211223",
      "data": [0.00241, 0.00162, 0.00048],
      "modifiers": [
        {"name": "D6tg", "data": [1.2e-04, 8.5e-05, 3.1e-05]},
        {"name": "D6tgxD6tg", "data": [1.8e-05, 1.3e-05, 5.2e-06]},
        {"name": "D6qq18", "data": [3.5e-06, 2.8e-06, 1.5e-06]},
        {"name": "D6qq18xD6qq18", "data": [1.1e-06, 9.2e-07, 5.8e-07]},
        {"name": "D6qq11", "data": [-5.1e-07, 1.2e-07, 3.4e-07]},
        {"name": "D6qq11xD6qq11", "data": [7.2e-06, 6.1e-06, 3.9e-06]},
        {"name": "D6tgxD6qq18", "data": [2.6e-07, 1.8e-07, 8.5e-08]},
        {"name": "D6tgxD6qq11", "data": [-1.1e-07, 5.0e-08, 2.2e-08]},
        {"name": "D6qq18xD6qq11", "data": [-1.3e-08, 3.5e-07, 7.0e-07]}
      ]
    }
  ]
}
```
