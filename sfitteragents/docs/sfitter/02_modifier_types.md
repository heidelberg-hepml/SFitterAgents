# Modifier Types and Naming Conventions

## 1. Modifier Types

Four types of modifiers, classified by how they enter the likelihood:

### 1.1 `"pois"` — Poisson Statistical

For counting experiments. Typically set to `0.0` for unfolded measurements.

```json
{"name": "Pois", "energy": "13TeV", "label": "Pois", "type": "pois", "data": [0.0]}
```

### 1.2 `"stat"` — Statistical Uncertainties

Uncorrelated bin-to-bin. Values are **percentages** (fractional relative to the measured data).

| Name | Description |
|------|-------------|
| `stat` | Data statistical uncertainty |
| `MC` | Monte Carlo statistical uncertainty |
| `Trigger` | Trigger efficiency statistical component |
| `Mod` | Model/other statistical uncertainty |

```json
{"name": "stat", "energy": "13TeV", "label": "Stat", "type": "stat", "data": [0.261, 0.166, ...]}
```

### 1.3 `"syst"` — Systematic Uncertainties

Correlated across bins within a measurement. Modifiers with the **same `name`** across different observations are correlated. Values are **percentages**.

| Name | Description | Label |
|------|-------------|-------|
| `Luminosity` | Integrated luminosity uncertainty | `LHC` |
| `Jets` | Jet energy scale/resolution | `ATLAS`/`CMS` |
| `bTagging` | b-tagging efficiency | `ATLAS`/`CMS` |
| `Leptons` | Lepton reconstruction/ID | `ATLAS`/`CMS` |
| `partonShower` | Parton shower modeling | `ATLAS`/`CMS` |
| `Pileup` | Pileup reweighting | `ATLAS`/`CMS` |
| `ETmis` | Missing transverse energy | `ATLAS`/`CMS` |
| `Beam` | Beam uncertainties | `ATLAS`/`CMS` |
| `BkgTTBar` | $t\bar{t}$ background normalization | `ATLAS`/`CMS` |
| `BkgTTW` | $t\bar{t}W$ background | `ATLAS`/`CMS` |
| `BkgTTZ` | $t\bar{t}Z$ background | `ATLAS`/`CMS` |
| `BkgTW` | $tW$ background | `ATLAS`/`CMS` |
| `BkgSch` | $s$-channel background | `ATLAS`/`CMS` |
| `BkgTch` | $t$-channel background | `ATLAS`/`CMS` |
| `BkgWhel` | $W$ helicity background | `ATLAS`/`CMS` |
| `LightTagging` | Light-jet tagging | `ATLAS`/`CMS` |
| `TriggerEff` | Trigger efficiency systematic | `ATLAS`/`CMS` |
| `Tune` | Generator tune | `ATLAS`/`CMS` |
| `tTagging` | Top tagging | `ATLAS`/`CMS` |
| `tauTagging` | Tau tagging | `ATLAS`/`CMS` |

### 1.4 `"theo"` — Theoretical Uncertainties

Theory uncertainties on the SM prediction. Correlated across bins. Values are **percentages**.

| Name | Description | Typical size ($t\bar t$ $m_{t\bar t}$) |
|------|-------------|----------------------------------------|
| `PDF` / `PDFSim` | Parton distribution function uncertainty | ~1-3% |
| `ScaleSim` / `ScalesSim` | $\mu_R$, $\mu_F$ scale variation of the SM prediction template at its actual perturbative order | ~8-15% (LO), ~3-5% (NLO), ~1-3% (NNLO) |
| `Scales` / `ScalesT` | Scale uncertainty sourced from the measurement paper (observation-side, from the paper's reported theory uncertainty) | reported |
| `NNLOrew` / `ScalesNNLO` | **Uncertainty on the NNLO/NLO k-factor ratio** (only meaningful if the k-factor was actually applied to the template) | ~1-3% |
| `TopMass` | Top quark mass uncertainty | ~0.5-2% |
| `UnderlyingEvent` | Underlying event modeling | ~0.1-1% |
| `Matching` | ME-PS matching uncertainty | |
| `Scheme` | Computational scheme dependence | |
| `Theo` | Generic theoretical uncertainty | |

**Important distinctions:**

- `ScaleSim` vs `NNLOrew` are different things. `ScaleSim` is the scale
  uncertainty of the template at its perturbative order (LO template → ~10%,
  NNLO template → ~1-3%). `NNLOrew` is the uncertainty on the k-factor
  itself, which only has meaning if a k-factor was **applied** to the
  template (see `docs/eft/03_parameterization_methodology.md` Section 6.4).
- If an SM template is LO and no k-factor was applied, attaching only an
  NNLOrew modifier (or calling it "NNLO uncertainty") does not make the
  template NNLO. The missing correction becomes a fake BSM signal in the
  fit. Attach ScaleSim at the LO magnitude (~8-15%) to give the fit enough
  slack until a proper k-factor is applied.
- The "Sim" suffix signals the modifier is computed from the **prediction
  template** (e.g., MadGraph `use_syst True` scale variations), not from
  the measurement-side theory uncertainty quoted in the paper.

### 1.5 Where each type lives in the observation

The modifier *object* shape above is the same everywhere, but the canonical cards
(`Top_Full.json`, `Higgs_Full.json`) place modifiers by type:

- `pois` / `stat` / `syst` → inside **`observation.Meas.modifiers`** (measurement-side);
  background-side counterparts go in **`observation.Bkg.modifiers`**.
- `theo` → the **observation-level `observation.modifiers`** list.

The measured central values are in `observation.Meas.data` and the background in
`observation.Bkg.data` — there is no flat `data` array on the observation itself. See
`01_json_schema.md` for the full layout.

---

## 2. Label Conventions

The `label` field groups modifiers for correlation treatment:

| Label | Meaning |
|-------|---------|
| `Pois` | Poisson statistical |
| `Stat` | Statistical uncertainties |
| `LHC` | LHC-wide correlated (e.g., luminosity) |
| `ATLAS` | ATLAS-specific systematic |
| `CMS` | CMS-specific systematic |
| `Theo` | Theoretical uncertainty |

Modifiers with the same `name` and `label` across different observations are treated as correlated.

---

## 3. SFitter Uncertainty Index (from external documentation)

### Top Sector (indices 20-40)

| Index | Name | Category |
|-------|------|----------|
| 20 | Beam | Systematic |
| 21 | BkgSch | Background |
| 22 | BkgTTBar | Background |
| 23 | BkgTTW | Background |
| 24 | BkgTTZ | Background |
| 25 | BkgTW | Background |
| 26 | BkgTch | Background |
| 27 | BkgWhel | Background |
| 28 | ETmis | Systematic |
| 29 | Jets | Systematic |
| 30 | Leptons | Systematic |
| 31 | LightTagging | Systematic |
| 32 | Luminosity | Systematic |
| 33 | Pileup | Systematic |
| 34 | TriggerEff | Systematic |
| 35 | Tune | Systematic |
| 36 | bTagging | Systematic |
| 37 | dummy | (placeholder) |
| 38 | partonShower | Systematic |
| 39 | tTagging | Systematic |
| 40 | tauTagging | Systematic |

### Higgs Sector (indices 1-31)

The dual-index notation (e.g., `1/16`) reflects that each Higgs systematic has
two slots in the SFitter data card — one for each correlation block (typically
LHC-wide vs experiment-specific, or per energy).

| Index | Name |
|-------|------|
| 1/16 | Luminosity |
| 2/17 | Detector (Jets) |
| 3/18 | Lepton Reconstruction |
| 4/19 | Photon Reconstruction (PID) |
| 5/20 | bTagging |
| 6/21 | tauTagging |
| 7/22 | VBF jets tagging (everything VBF related) |
| 8/23 | Lepton Isolation |
| 9/24 | BkgZZ4l |
| 10/25 | BkgHtGG |
| 11/26 | BkgHtTT |
| 12/27 | BkgHtWW |
| 13/28 | BkgHtbb |
| 14/29 | WW production 8 TeV |
| 15/30 | WZ production 8 TeV |
| 31 | WZ production 7 TeV |

---

## 4. SFitter ID Encoding (Brief Reference)

Format: `ocfkkxe[_b]` — see [`06_id_naming_convention.md`](06_id_naming_convention.md)
for the complete reference with all channel-dependent codes, worked examples,
and a step-by-step ID construction algorithm. The brief table below covers
the most common cases only.

| Position | Meaning | Values |
|----------|---------|--------|
| `o` | Order | 1=LO, 2=NLO, 3=highest available (NNLO+) |
| `c` | Channel | 1=single top, 2=$t\bar{t}$, 3=top decay, 4=$t\bar{t}Z$, 5=$t\bar{t}W$, 6=flavour |
| `f` | Final state | Channel-dependent (see `06_id_naming_convention.md`) |
| `kk` | Kinematic variable | Channel-dependent, two chars zero-padded |
| `x` | Experiment | 1=CMS, 2=ATLAS, 3=averaged/experiment-irrelevant |
| `e` | Energy | 1=7 TeV, 2=8 TeV, 3=13 TeV, 4=low energy or 13.6 TeV |
| `_b` | Bin suffix | `_0` for single-bin measurements; omitted for distributions |

### Common $t\bar t$ final state codes (`f` for `c=2`)

| `f` | Meaning |
|-----|---------|
| 1 | lepton + jets |
| 2 | dilepton |
| 3 | all-jets |
| 4 | high-$p_T$ l+jets |
| 5 | $W$ helicity |
| 6 | irrelevant (total xsec/asymmetry) |
| 7 | high-$p_T$ jj |

### Common $t\bar t$ kinematic codes (`kk` for `c=2`)

| `kk` | Observable |
|------|-----------|
| 01 | $p_T^*$ (normalized) |
| 02 | $p_T$ (normalized) |
| 03 | $y_t$ (normalized) |
| 07 | $p_T^{t\bar{t}}$ (normalized) |
| 09 | $m_{t\bar{t}}$ (normalized) |
| 11 | total cross-section |
| 12 | $p_T(t_h)$ (unnormalized) |
| 13 | $p_T(t_h)$ (normalized) |
| 14 | asymmetry $A_C(m_{t\bar{t}})$ |
| 15 | total asymmetry |
| 16 | $\Delta\|y\|$ (normalized) |

---

## 5. Data Value Interpretation

**Important**: the `data` arrays in modifiers represent **percentage uncertainties** (relative to the measured value), not absolute uncertainties. The code converts them:

```python
# In ReadDataCard.syst_unc():
absolute_syst = modifier_data_percent / 100.0 * measurement_data
```

For `"theo"` type modifiers, the values are also percentages of the SM prediction.

For `"stat"` type, the values are percentages of the measured data.

For `"pois"` type, the values are absolute Poisson uncertainties (typically 0 for unfolded measurements).
