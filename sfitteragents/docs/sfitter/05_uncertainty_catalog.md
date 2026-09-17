# SFitter Uncertainty Catalog

Complete catalog of all 66 unique modifiers (uncertainties) found across all SFitter JSON data files. This is the authoritative reference for which uncertainties the measurement-extractor agent should attempt to find.

---

## 1. Poisson (type: `"pois"`)

| Name | Label | Description |
|------|-------|-------------|
| `Pois` | `Pois` | Poisson statistical fluctuations. Set to 0.0 for unfolded measurements. Always required. |

---

## 2. Statistical (type: `"stat"`)

Uncorrelated bin-to-bin. Values are **percentages** of the measured data.

| Name | Label | Dataset | Description |
|------|-------|---------|-------------|
| `stat` | `Stat` | Top + Higgs | Data statistical uncertainty |
| `MC` | `Stat` | Top | Monte Carlo statistical uncertainty |
| `Trigger` | `Stat` | Top | Trigger efficiency statistical component |
| `Mod` | `Stat` | Top | Model/other statistical uncertainty |
| `LightTagging` | `Stat` | Top | Light-jet tagging statistical component |
| `bFragmentation` | `Stat` | Top | b-quark fragmentation statistical component |
| `Others` | `Stat` | Top | Other/miscellaneous statistical uncertainties |

---

## 3. Systematic (type: `"syst"`)

Correlated across bins. Same `name` across observations = correlated. Values are **percentages**.

### 3.1 Detector / Reconstruction

| Name | Label | Dataset | Description |
|------|-------|---------|-------------|
| `Jets` | experiment | Top | Jet energy scale + resolution (combined) |
| `JES` | experiment | Top | Jet energy scale (separate, CMS convention) |
| `JER` | experiment | Top | Jet energy resolution (separate, CMS convention) |
| `Leptons` | experiment | Top | Lepton reconstruction and identification |
| `Lepton_Rec` | experiment | Higgs | Lepton reconstruction (Higgs convention) |
| `Lepton_Iso` | experiment | Higgs | Lepton isolation (Higgs convention) |
| `Photon_Rec` | experiment | Higgs | Photon reconstruction / PID |
| `Detector` | experiment | Higgs | Generic detector systematic (Higgs convention) |
| `ETmis` | experiment | Top | Missing transverse energy |
| `Pileup` | experiment | Top | Pileup reweighting |
| `Beam` | experiment | Top | Beam energy / beam conditions |

### 3.2 Tagging

| Name | Label | Dataset | Description |
|------|-------|---------|-------------|
| `bTagging` | experiment | Top + Higgs | b-jet tagging efficiency |
| `tTagging` | experiment | Top | Top-jet tagging |
| `tauTagging` | experiment | Top + Higgs | Tau tagging |
| `WBFtagjs` | experiment | Higgs | VBF jet tagging |

### 3.3 Backgrounds

| Name | Label | Dataset | Description |
|------|-------|---------|-------------|
| `BkgTTBar` | experiment | Top | $t\bar{t}$ background normalization |
| `BkgTTW` | experiment | Top | $t\bar{t}W$ background |
| `BkgTTZ` | experiment | Top | $t\bar{t}Z$ background |
| `BkgTW` | experiment | Top | $tW$ background |
| `BkgTch` | experiment | Top | $t$-channel single top background |
| `BkgSch` | experiment | Top | $s$-channel single top background |
| `BkgWhel` | experiment | Top | $W$ helicity background |
| `BkgTTA` | experiment | Top | $t\bar{t}$ + associated background |
| `BgEPZZ4l` | experiment | Higgs | $ZZ \to 4\ell$ background |

### 3.4 Modeling / Generator

| Name | Label | Dataset | Description |
|------|-------|---------|-------------|
| `partonShower` | experiment | Top | Parton shower modeling |
| `PSscale` | experiment | Top | Parton shower scale (CMS convention) |
| `ISR` | experiment | Top | Initial-state radiation variation |
| `FSR` | experiment | Top | Final-state radiation variation |
| `Tune` | experiment | Top | Generator tune |
| `Luminosity` | `LHC` | Top + Higgs | Integrated luminosity (LHC-wide correlated) |

---

## 4. Theoretical (type: `"theo"`)

Theory uncertainties on the SM prediction. Correlated across bins. Values are **percentages** of the prediction.

### 4.1 QCD / Perturbative

| Name | Label | Dataset | Description |
|------|-------|---------|-------------|
| `ScalesT` | `Theo` | Top | Renormalization + factorization scale variation (primary) |
| `Scales` | `Theo` | Top | Scale variation (alternative naming, older measurements) |
| `ScalesSim` | `Theo` | Top | Scale variation on simulation (separate component) |
| `ScaleSim` | `Theo` | Top | Scale variation on simulation (variant naming) |

### 4.2 PDF / $\alpha_s$

| Name | Label | Dataset | Description |
|------|-------|---------|-------------|
| `PDF` | `Theo` | Top | PDF uncertainty (from data/measurement side) |
| `PDFSim` | `Theo` | Top | PDF uncertainty (from simulation/prediction side) |
| `hatPDFNLO` | `Theo` | Top | NLO PDF hat-scheme uncertainty |

### 4.3 Parametric / Physics

| Name | Label | Dataset | Description |
|------|-------|---------|-------------|
| `TopMass` | `Theo` | Top | Top quark mass uncertainty |
| `UnderlyingEvent` | `Theo` | Top | Underlying event modeling |
| `Matching` | `Theo` | Top | Matrix element / parton shower matching |
| `NLOMatching` | `Theo` | Top | NLO-specific matching uncertainty |
| `Scheme` | `Theo` | Top | Computational scheme dependence |
| `ColorReconnection` | `Theo` | Top | Color reconnection modeling |
| `Extrapolation` | `Theo` | Top | Extrapolation uncertainty (fiducial → full phase space) |

### 4.4 Generic / Higgs

| Name | Label | Dataset | Description |
|------|-------|---------|-------------|
| `Theo` | — | Top + Higgs | Generic theoretical uncertainty placeholder |
| `Theo1`–`Theo13` | — | Higgs | Higgs-specific theoretical uncertainties (indexed) |

---

## 5. Processing in SFitter Code

From `datacard.py`, each type is processed differently:

| Type | Method | Formula | Notes |
|------|--------|---------|-------|
| `pois` | `poiss_unc()` | Raw value extraction | Direct pass-through |
| `stat` | `stat_unc()` | `data[i] * obs_data` or `data[i] * obs_bkg` | Percentage × measured value |
| `theo` | `theo_unc()` | `data[i] * (obs_data - obs_bkg)` | Percentage × signal prediction |
| `syst` | `syst_unc()` | See formula below | Combines meas + bkg with correlation |

**Systematic formula** (combines measurement and background systematic contributions):

$$\delta_{\text{syst}} = \sqrt{(m \cdot d)^2 + (b \cdot d_{\text{bkg}})^2 - 2 \times 0.99 \times (m \cdot d)(b \cdot d_{\text{bkg}})}$$

where $m$ = modifier percentage/100, $d$ = observation data, $b$ = background modifier percentage/100, $d_{\text{bkg}}$ = background data. The 0.99 factor assumes 99% correlation between measurement and background systematic effects.

---

## 6. Correlation Rules

1. Modifiers with the **same `name`** across different observations are treated as **correlated**
2. The `label` field groups modifiers for organizational purposes:
   - `LHC` = correlated across all LHC experiments (e.g., luminosity)
   - `ATLAS` / `CMS` = correlated within one experiment
   - `Theo` = theory uncertainties (correlated across measurements of the same process)
   - `Stat` = statistical (uncorrelated)
3. The `energy` field distinguishes uncertainties at different collision energies

---

## 7. Priority for Extraction

When extracting from a new measurement, attempt to find these in order of importance:

**Always required:**
- `Pois` (set to 0 for unfolded)
- `stat` (data statistics)
- `Luminosity`

**High priority (usually available):**
- `Jets` or `JES`+`JER`
- `bTagging`
- `Leptons`
- `MC` (MC statistics)
- `ScalesT` (scale variation)
- `PDFSim` (PDF uncertainty)

**Medium priority (often available):**
- `partonShower`
- `Pileup`
- `ETmis`
- `TopMass`
- `UnderlyingEvent`
- Background normalizations (`BkgTTBar`, etc.)

**Lower priority (process-specific):**
- `Matching`, `NLOMatching`
- `ColorReconnection`
- `Extrapolation`
- `Scheme`
- `ISR`, `FSR` (if not combined into `partonShower`)
