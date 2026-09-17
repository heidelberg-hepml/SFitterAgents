# Figure Digitization

When uncertainty values appear in paper figures (ratio panels, systematic-band bar charts, breakdown plots) but not in tables or HEPData.

---

## 1. When To Digitize

Digitization is a legitimate fallback used routinely in phenomenology. Resort to it when:

- A specific uncertainty source is shown only in a paper figure (e.g., a ratio panel with a labeled systematic band)
- HEPData and the paper's tables do not provide a per-source breakdown for the observable being implemented, and the [02_uncertainty_decomposition.md](02_uncertainty_decomposition.md) procedure would produce confidence-medium values that you'd like to validate or refine

Do **not** digitize when:

- The same value is available in a table or HEPData. Tables always win on precision.
- The figure is decorative (illustration only, no quantitative axis) or the relevant feature is too small to digitize reliably.

## 2. Automated Digitization Workflow

If the figure is included with the paper as a high-resolution image (PNG/PDF):

1. Save the figure to `/workspace/measurement_extraction/figures/<figureN>.png`.
2. Identify the axes: linear vs log, units, axis range. Note the x-axis bin centers (or edges) and the y-axis scale.
3. Use a digitization library (e.g., Python + `matplotlib.image`, OpenCV) to:
   - Load the image
   - Identify the axis frame (corner detection or manual coordinate calibration: provide 4 reference points with known data coordinates)
   - For each data series (uncertainty band, error bar, breakdown component), extract pixel coordinates and map to data coordinates via the calibration
4. Cross-check by digitizing one or two points whose values are known from the paper text or another table. Agreement to a few percent indicates the calibration is correct.
5. Flag every digitized value as **confidence: medium** in the extraction report. Record the figure number and the axis calibration parameters used.

## 3. When Automated Digitization Is Unreliable

The model often cannot reliably digitize without seeing the figure interactively. In that case, **delegate to the user**:

- Identify the figure number and exact panel.
- State precisely what to extract: which line/band/bar represents which uncertainty source, which bin edges to read, what the y-axis units are.
- Recommend a tool: **WebPlotDigitizer** (web-based, free, https://apps.automeris.io/wpd/) for most cases, or **Engauge Digitizer** (desktop, more control) for complex/log-axis figures.
- Provide a sample extraction template the user can fill in (e.g., a JSON skeleton with bin centers and source labels).
- Resume the extraction once the user pastes back the digitized numbers, flagging confidence per the user's reported precision.

## 4. Common Figure Types and How To Read Them

| Figure type | What to extract | Watch out for |
|---|---|---|
| **Ratio panel with systematic band** | Half-width of the band per bin (often shaded gray) = total systematic relative to the central prediction | The band is sometimes "data unc. + theory unc." combined — check the legend |
| **Stacked breakdown bar chart** (per bin) | Each stacked segment is one source's contribution | Be aware of whether the chart shows signed or unsigned values; SFitter wants unsigned |
| **Error bar on data points** | Vertical line span = stat uncertainty (often) | Some papers show stat+syst combined; check the legend |
| **Pull plot / nuisance parameter plot** | Used for likelihood fits, not directly useful for input extraction |  |

## 5. Sanity Checks On Digitized Values

After digitization:

- Sum digitized per-source values in quadrature; compare to the paper's reported per-bin total systematic (from HEPData or a table). Agreement to ~10% is acceptable; larger disagreement indicates a missed source or a calibration error.
- Compare the digitized values to the per-bin per-source values produced by the [02_uncertainty_decomposition.md](02_uncertainty_decomposition.md) procedure (if both are available). Order-of-magnitude agreement is expected. Large disagreement = one of the methods is wrong; investigate before shipping.
- Check that the digitized values follow physical trends — e.g., jet systematics typically grow toward kinematic edges; luminosity is flat across bins. A bin-dependence that contradicts the physical expectation is suspicious.

## 6. Reporting

For each digitized modifier in the extraction report:

```json
{
  "name": "<modifier_name>",
  "type": "syst",
  "values_percent": [...],
  "source": "Figure <N>, panel <X>, digitized from <ratio band / breakdown bar / error bar>",
  "confidence": "medium",
  "notes": "Digitized by <model or user>. Calibration cross-check: <comparison to known table value>."
}
```

The extraction-reviewer agent treats digitized values as inherently medium-confidence and will KEEP them when the source pointer is specific and the cross-check is documented; FLAG when either is missing.
