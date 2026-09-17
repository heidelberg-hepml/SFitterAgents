# Data Retrieval

How to locate the measurement data and metadata from a paper or arXiv entry.

---

## 1. Sources, in Order of Preference

1. **HEPData record** — primary source. Machine-readable YAML / JSON / CSV with bin edges, central values, statistical uncertainty per bin, and (usually) total systematic per bin. URL pattern: `https://www.hepdata.net/record/ins<inspire_id>` or `/record/<hepdata_id>`.
2. **Paper main tables** — typically a "results" table (total cross-section + breakdown) and an uncertainty-breakdown table. HEPData has the data; the paper has the source decomposition that HEPData usually doesn't carry.
3. **Paper supplementary material / auxiliary tables** — sometimes contains per-bin per-source breakdowns when the main paper does not.
4. **Paper figures** — fallback when neither HEPData nor tables expose the needed source breakdown. See [03_figure_digitization.md](03_figure_digitization.md).

Always look at both the HEPData record AND the paper. HEPData has the precise per-bin numbers but rarely the systematic decomposition; the paper has the decomposition but usually only for the total or with limited binning.

## 2. Required Metadata

For each measurement, record:

| Field | Source |
|---|---|
| Process | Paper abstract / data section (e.g., `pp → tt~`, `pp → ttZ`) |
| Observable | Paper figure caption / table header (e.g., `m_tt`, `pT(t_h)`, `total cross-section`) |
| $\sqrt{s}$ | Paper data section (7, 8, 13, or 13.6 TeV) |
| Luminosity | Paper data section (in fb$^{-1}$) |
| Absolute vs normalized | Paper figure caption — look for $1/\sigma\,d\sigma/dx$ vs $d\sigma/dx$ |
| Fiducial vs total phase space | Paper unfolding section |
| Reference | arXiv ID, journal ref, HEPData record ID |

The absolute-vs-normalized distinction matters: a normalized differential needs different SM-prediction handling (per-bin k-factor required, uniform k-factor is a no-op — see the `sm-baseline-perturbative-order` skill) and the luminosity uncertainty cancels in the ratio.

## 3. HEPData Workflow

Typical pattern using `WebFetch`:

1. Find the HEPData record from the paper's INSPIRE entry or the journal page. The HEPData URL is usually `https://www.hepdata.net/record/ins<inspire_id>`.
2. Fetch the table index — HEPData record landing pages list tables with names like "Table 1", "Figure 5", "Differential cross-section as a function of $m_{t\bar t}$".
3. For each relevant table, download the YAML or JSON via the table's API URL (`?format=yaml` or `?format=json` query parameter).
4. Parse: HEPData files have `independent_variables` (bin edges or labels) and `dependent_variables` (values + per-point uncertainties). The uncertainty structure within `dependent_variables` carries the breakdown HEPData chose to expose — often `stat` and `sys` only, sometimes more granular.

## 4. Bins and Edges

Read bin edges directly from HEPData when available. From the paper figure axes is a last resort and should be flagged as medium-confidence.

Record:
- `bin_low` and `bin_high` per bin
- The observable being binned and its units
- Bin width per bin (SFitter datacards expose `bin_widths` explicitly)
- Whether bins are contiguous (gap = potential issue) and whether the full kinematic range is covered

## 5. Absolute vs Normalized — Validation Checks

For a normalized differential:
- $\sum_b \sigma_b \cdot {\rm bin\_width}_b \approx 1$ (integrates to 1 to within rounding)
- Luminosity uncertainty is absent or vastly reduced compared to the absolute version of the same measurement
- The y-axis label / figure caption explicitly says $1/\sigma\,d\sigma/dx$ or "normalized"

For an absolute differential:
- $\sum_b \sigma_b \cdot {\rm bin\_width}_b \approx \sigma_{\rm tot}$ (matches the inclusive cross-section quoted in the paper, within uncertainties)
- Luminosity uncertainty is present and at the experiment-wide level (~1.5–2.5%)

A mismatch in either direction usually means the wrong table was retrieved (normalized when you wanted absolute, or vice versa) or a bin-width vs bin-content confusion.

## 6. What Each Source Typically Contains

| Source | Has | Lacks |
|---|---|---|
| HEPData record | Per-bin central values, statistical uncertainty, often total systematic, sometimes correlation matrices, bin edges | Per-source systematic breakdown (usually) |
| Paper main table | Total cross-section with full source breakdown, integrated luminosity, $\sqrt{s}$, unfolding choices | Per-bin values for differentials |
| Paper aux tables | Sometimes per-bin per-source breakdowns (rare but ideal) | Variable across papers |
| Paper figures | Visual breakdown bands, ratio panels — extractable but lower confidence | Numerical precision |

The two-step decomposition in [02_uncertainty_decomposition.md](02_uncertainty_decomposition.md) is the bridge between these complementary sources — it lets you combine the paper's total-cross-section source breakdown with HEPData's per-bin totals to produce per-bin per-source uncertainties.

## 7. Cross-Reference With the Modifier Catalog

Before searching the paper, consult `docs/sfitter/05_uncertainty_catalog.md` for the canonical name of each uncertainty source. Map paper terminology to canonical names early — e.g., a paper's "Jet energy scale (JES)" + "Jet energy resolution (JER)" combines (in quadrature) to the SFitter `Jets` modifier; "Electron ID" + "Muon ID" combines to `Leptons`. Mapping at extraction time is much cleaner than later, in the config-builder stage.
