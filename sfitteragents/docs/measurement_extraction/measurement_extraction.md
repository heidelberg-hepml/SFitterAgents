# Measurement Extraction Documentation

Reference material for extracting experimental measurement data (cross-sections, bin edges, uncertainty breakdowns, correlations) from published HEP papers and HEPData entries, in the form required by the SFitter global EFT fit framework.

## Contents

| File | Description |
|------|-------------|
| [01_data_retrieval.md](01_data_retrieval.md) | Locating the measurement: HEPData record, paper tables, sqrt(s)/luminosity/process metadata, absolute vs normalized distinction. Practical HEPData query workflow. |
| [02_uncertainty_decomposition.md](02_uncertainty_decomposition.md) | The Schmal two-step procedure for SFitter-style per-bin per-source uncertainty extraction. Total-cross-section breakdown + per-bin totals → per-bin per-source values via the $\omega_b$ scaling. When direct breakdowns are available vs. when the procedure must be applied. Correlation handling. |
| [03_figure_digitization.md](03_figure_digitization.md) | Fallback when values are only in figures (ratio panels, breakdown bar charts). When to attempt automated digitization, when to hand off to the user with WebPlotDigitizer / Engauge guidance, and how to flag digitized values. |
| [04_extraction_report.md](04_extraction_report.md) | Output JSON schema for the extraction report, per-modifier confidence levels (high/medium/low), and the validation checks the extraction-reviewer agent enforces. |

## Source Material

- The Schmal master thesis, Section 4.1, defines the two-step uncertainty decomposition that is the SFitter group's standard practice.
- Published SFitter analyses ([arXiv:1910.03606](https://arxiv.org/abs/1910.03606), [arXiv:2312.12502](https://arxiv.org/abs/2312.12502)) use this procedure throughout.
- The canonical list of SFitter modifier names that the extraction must target lives in `docs/sfitter/05_uncertainty_catalog.md`.
