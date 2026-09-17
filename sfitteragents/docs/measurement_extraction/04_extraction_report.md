# Extraction Report

Output format for the measurement-extractor agent. The extraction-reviewer agent verdicts (KEEP / FLAG / REJECT) operate on this format.

---

## 1. Top-Level Schema

```json
{
  "measurement": {
    "process": "pp -> tt~",
    "observable": "m_tt",
    "sqrt_s_TeV": 13,
    "luminosity_invfb": 137,
    "reference": "arXiv:XXXX.XXXXX",
    "hepdata_record": "ins<inspire_id>",
    "is_normalized": true,
    "is_fiducial": false
  },
  "bins": [
    {
      "bin_low": 345,
      "bin_high": 400,
      "value": 0.00123,
      "stat_unc": 0.00005,
      "syst_unc_total": 0.00008
    }
  ],
  "modifiers": [
    {
      "name": "<canonical SFitter name>",
      "type": "pois|stat|syst|theo",
      "values_percent": [...],
      "source": "<paper Table N | HEPData Table M | Figure F | derived via Schmal procedure>",
      "confidence": "high|medium|low",
      "notes": "<grouping/digitization/extrapolation notes>"
    }
  ],
  "uncertainty_ordering": ["Jets", "bTagging", "Leptons", "Luminosity", "..."],
  "correlation_matrix": null
}
```

The `bins` array carries the central values and per-bin totals; the `modifiers` array carries the per-source per-bin uncertainty values to feed into the SFitter datacard's modifier list.

## 2. Field Rules

| Field | Rule |
|---|---|
| `measurement.is_normalized` | `true` if the values are $(1/\sigma)\,d\sigma/dx$; `false` if absolute $d\sigma/dx$ or total cross-section |
| `measurement.is_fiducial` | `true` if measured in a fiducial volume (lepton/jet cuts applied) without extrapolation to full phase space |
| `bins[].value` | Per-bin measured value (cross-section or normalized cross-section) |
| `bins[].stat_unc` / `bins[].syst_unc_total` | Per-bin absolute uncertainties (units match `value`); used for cross-checks, not for the SFitter modifier `data` arrays |
| `modifiers[].values_percent` | Per-bin percentage of measured value; this IS what SFitter modifiers consume (after the SFitter ordering / catalog naming is applied) |
| `modifiers[].source` | Specific source pointer required; "the paper" is insufficient and will be flagged by the reviewer |
| `uncertainty_ordering` | Order of modifier names matters for SFitter — modifiers at the same index across observations are correlated |

## 3. Confidence Levels

The reviewer agent uses these labels to gate which extractions can proceed to the config-builder.

| Level | Criterion | Reviewer disposition |
|---|---|---|
| **`high`** | Directly from a paper table, HEPData entry, or unambiguous text quote, with a specific source pointer (table number / row / HEPData table ID) | KEEP unless the source pointer is incorrect |
| **`medium`** | Derived via the [02_uncertainty_decomposition.md](02_uncertainty_decomposition.md) procedure when only the total-cross-section breakdown is available, or digitized from a figure with a cross-check, or paper text mentions the value without a clean table reference | KEEP if the derivation/digitization steps are documented; FLAG if not |
| **`low`** | Estimated from typical experimental values, inferred from similar (but distinct) measurements, or extrapolated beyond the original measurement's phase space | REJECT by default; the reviewer requires explicit user override |

Confidence is per-modifier, not per-measurement. A single extraction often mixes high (HEPData per-bin stat), high (a specific paper-table source), and medium (sources derived via decomposition).

## 4. The `source` Field — What Makes It Specific Enough

Examples that pass the reviewer:

- `"HEPData record ins1234567, Table 5, column 'syst total'"`
- `"Paper Table 3, row 'Jet energy scale' + row 'Jet energy resolution', combined in quadrature"`
- `"Derived via Schmal two-step procedure (docs/measurement_extraction/02_uncertainty_decomposition.md). Relative composition from paper Table 1; per-bin totals from HEPData Table 5"`
- `"Figure 7, lower panel, gray systematic band; digitized by user with WebPlotDigitizer"`

Examples that get flagged or rejected:

- `"From the paper"` — too vague
- `"Standard value"` — not traceable
- `"From a similar ATLAS measurement"` — not the actual source
- `"Estimated"` — no source

## 5. Validation Checks (Mandatory Before Sign-Off)

The extractor must run these before producing the report; the extraction-reviewer will re-run them.

1. **Quadrature cross-check on totals**: per bin, $\sqrt{\sum_j \Delta_{b,j}^2}$ across all systematic modifiers should equal `bins[b].syst_unc_total` from HEPData within ~1%. Larger discrepancy indicates a missing source or a quadrature ordering error.
2. **Inclusive sum cross-check**: $\sum_b \sigma_b \cdot {\rm bin\_width}_b$ should equal the paper's quoted total cross-section (for absolute distributions) or $\approx 1$ (for normalized). A factor-of-two-or-more discrepancy usually means a units error (e.g., pb vs fb).
3. **Bin edge contiguity**: `bins[i].bin_high == bins[i+1].bin_low` for all $i$. Gaps or overlaps are extraction errors.
4. **No duplicated or missing modifiers**: every modifier name appears exactly once; the always-required set (`Pois`, `stat`, `Luminosity`) is present.
5. **Percentage range**: every entry in `modifiers[].values_percent` is $\ge 0$ and (typically) $< 100$. Values > 100 % usually indicate an absolute-vs-percentage encoding error; flag and re-check.
6. **Normalization consistency** (normalized distributions only): luminosity-derived uncertainties are absent or vastly reduced.
7. **Figure vs table cross-check** when both are available: compare to within a few percent; the source closer to a primary table (paper, then HEPData) wins on discrepancy.

## 6. Per-Modifier Output Sample

A complete modifier entry as the extractor produces it:

```json
{
  "name": "Jets",
  "type": "syst",
  "values_percent": [2.08, 0.81, 1.17, 1.45, 2.03, 2.78, 3.41, 4.12, 5.66],
  "source": "Derived via Schmal procedure. Relative composition: paper Table 3 'Jet energy scale' (1.21%) + 'Jet energy resolution' (0.67%) quadrature-combined = 1.38%. Per-bin totals: HEPData Table 5 'total systematic'.",
  "confidence": "medium",
  "notes": "Tail bin (bin 8, 5.66%) larger than inclusive: expected, jet uncertainties grow with pT. Cross-check OK: sum-in-quadrature of all syst modifiers matches HEPData per-bin total to <0.5%."
}
```

The `notes` field is where the extractor explains anything that would otherwise look like a discrepancy — making the reviewer's job a check, not an investigation.

## 7. Hand-Off to Config-Builder

When the extraction report is approved (all entries KEEP or KEEP-with-caveat), it feeds directly into the config-builder agent. The config-builder converts:

- `measurement` metadata → observation `name` and `ID` (using the SFitter ID encoding from `docs/sfitter/06_id_naming_convention.md`)
- `bins[].value` → observation `data` array
- `bins[].bin_high - bins[].bin_low` → observation `bin_widths`
- `modifiers[]` → observation `modifiers` array (with the canonical SFitter `name`, `type`, `label`, and `data` fields per `docs/sfitter/01_json_schema.md`)

Mismatches between the extraction report's modifier names and the SFitter canonical catalog (e.g., `JES_+_JER` instead of `Jets`) must be resolved at extraction time, not at config-builder time — the config-builder should not be making canonical-name decisions.
