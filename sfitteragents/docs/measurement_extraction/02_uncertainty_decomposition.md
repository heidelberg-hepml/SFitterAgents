# Uncertainty Decomposition

The standard SFitter procedure for producing **per-bin per-source** uncertainties from the complementary information that papers usually provide. Schmal master thesis Section 4.1.

---

## 1. The Problem

SFitter require uncertainties broken down by source AND by bin: `Jets` per bin, `bTagging` per bin, etc. Papers usually expose only two pieces of complementary information:

- **(A)** A breakdown of the **total** cross-section by source (paper Table 1 or equivalent). Lists each individual systematic with its percentage contribution to the inclusive measurement. Gives the **relative composition** of the total systematic.
- **(B)** Per-bin total uncertainties (HEPData). Usually the per-bin total systematic and statistical, **without** per-source breakdown.

Without a direct per-bin per-source table (which is the ideal but uncommon case — see §4 below), the agent must reconstruct the breakdown.

## 2. The Schmal Two-Step Procedure

Let $\Delta_j$ denote the contribution of source $j$ to the total systematic, from the paper's breakdown table (A). Let $\Delta_{{\rm tot},b}$ denote the total systematic in bin $b$, from HEPData (B).

The per-bin per-source uncertainty is:

$$\Delta_{b,j} \;=\; \omega_b \cdot \Delta_j$$

with the per-bin scaling factor:

$$\omega_b \;=\; \frac{\Delta_{{\rm tot},b}}{\sqrt{\sum_j \Delta_j^2}}$$

This distributes the per-bin total to the individual sources while preserving the relative composition from the breakdown table. It matches the per-bin total exactly:

$$\sqrt{\sum_j \Delta_{b,j}^2} \;=\; \sqrt{\sum_j \omega_b^2 \Delta_j^2} \;=\; \omega_b\sqrt{\sum_j \Delta_j^2} \;=\; \Delta_{{\rm tot},b}\quad\checkmark$$

The procedure assumes:
- The relative composition (the ratios $\Delta_j/\Delta_k$) is approximately bin-independent.
- All sources within a bin are uncorrelated with each other (quadrature combination).
- The per-bin total systematic from HEPData is the quadrature sum of the same sources listed in the paper's breakdown.

These assumptions are the SFitter standard and are used in arXiv:1910.03606 and arXiv:2312.12502.

## 3. Step-by-Step Recipe

1. From the paper's breakdown table (A), list each source $j$ and its absolute contribution $\Delta_j$ to the total cross-section. If the table gives percentages, convert: $\Delta_j = ({\rm pct}_j/100) \cdot \sigma_{\rm tot}$.
2. Group entries into the canonical SFitter modifier names early (e.g., paper's "JES + JER" → `Jets`; "electron + muon" → `Leptons`). Combine by quadrature within each group: $\Delta_{\rm Jets} = \sqrt{\Delta_{\rm JES}^2 + \Delta_{\rm JER}^2}$.
3. From HEPData (B), retrieve the per-bin total systematic $\Delta_{{\rm tot},b}$ for the observable being implemented.
4. Compute the normalization constant: $S = \sqrt{\sum_j \Delta_j^2}$. Sanity check: $S$ should agree with the paper's quoted total systematic on the inclusive measurement.
5. For each bin $b$, compute $\omega_b = \Delta_{{\rm tot},b}/S$, then $\Delta_{b,j} = \omega_b \cdot \Delta_j$ for each source $j$.
6. Convert to percentages of the per-bin measured value: $\delta_{b,j}^{\rm pct} = 100 \cdot \Delta_{b,j} / \sigma_b^{\rm meas}$. SFitter modifier `data` arrays store percentages.
7. Round-trip check: $\sqrt{\sum_j \Delta_{b,j}^2}$ should equal $\Delta_{{\rm tot},b}$ exactly. If not, an arithmetic error crept in.

## 4. When To Use Direct Breakdowns Instead

If the paper or HEPData provides a per-bin per-source breakdown directly:

- **Use it directly.** Do not re-derive via the procedure.
- Flag confidence as **high** in the extraction report.
- Cross-check: the quadrature sum of the per-source values per bin should match the per-bin total systematic from another HEPData entry (when both are exposed). Mismatch = a source is missing from either the direct breakdown or the total.

Many older measurements provide direct breakdowns only for the total cross-section, while HEPData exposes per-bin totals only. That is the case the Schmal procedure addresses.

## 5. When the Breakdown Is for the Total Only

If the paper provides a breakdown for the **total cross-section** but the observable being implemented is a **differential** (e.g., $m_{t\bar t}$ spectrum) without its own breakdown:

- The relative composition $\Delta_j$ from the total-cross-section table is still usable as a starting point. The ratios are typically similar bin-to-bin within the differential.
- Flag the per-bin per-source values as **derived** (confidence: medium) in the extraction report.
- Note explicitly which bins are expected to deviate from the relative composition assumption:
  - **Jet uncertainties** typically grow in high-$p_T$ / high-$m_{t\bar t}$ tails — flag tail bins as potential underestimates if `Jets` from a moderate-region breakdown is propagated to the tail
  - **Luminosity** is constant across bins (cancels in normalized distributions) — its per-bin entry is flat
  - **b-tagging** can shift with jet $p_T$ — high-$p_T$ regions may need a separate look
- Where the paper provides a separate breakdown for the same differential observable (e.g., in supplementary material), use that breakdown's $\Delta_j$ values for the procedure instead of the inclusive-table values.

## 6. Normalized Distributions

For a normalized distribution $(1/\sigma)\,d\sigma/dx$:

- The same procedure applies but the source set may be smaller (luminosity, and other normalization-only uncertainties, cancel in the ratio).
- Use the paper's breakdown table for the **normalized** observable if one is provided. If only the absolute-cross-section breakdown is available, drop the canceling sources explicitly and renormalize $S$ accordingly.
- After distribution, the resulting per-bin per-source values typically satisfy $\sum_b w_b \Delta_{b,j} \approx 0$ for sources that cancel in the normalization (where $w_b$ is the SM bin weight). Use this as a self-consistency check.

## 7. Correlation Handling

- Per-source values produced by the procedure are correlated **across bins within an observable** (since they share the relative composition $\Delta_j$). This is the SFitter standard treatment for systematic modifiers (`type: "syst"` in SFitter, same `name` correlates across bins).
- Statistical uncertainties (`type: "stat"`) are uncorrelated bin-to-bin — extract per-bin stat from HEPData directly, do not apply the decomposition procedure.
- If the paper or HEPData provides a **correlation matrix** for the per-bin total uncertainties, record it in the extraction report. SFitter can ingest it; the alternative is the diagonal assumption.
- Correlation **across measurements** of the same process — luminosity is always correlated across measurements at the same energy; theory uncertainties are typically correlated across measurements of the same process at the same energy. These correlations are encoded by matching the modifier `name` across observations in the SFitter datacard.

## 8. Edge Cases and Failure Modes

- **The paper's breakdown lists "Other" or "Sum of small effects"** — assign this to a generic `Theo` or `Mod` modifier rather than fabricating a specific source. Document in the extraction report.
- **The paper's listed sources exceed the canonical catalog** — combine into the most appropriate canonical group; document the merge explicitly.
- **$S \ne$ paper's reported total** — usually means a source is missing from either the breakdown or the quadrature sum. Resolve before propagating; otherwise the per-bin totals will not match HEPData by exactly the magnitude of the missing source.
- **Per-bin totals from HEPData and per-bin quadrature of the procedure disagree by more than a few percent** — round-trip arithmetic error, or HEPData's "total" excludes a source the paper's breakdown includes (e.g., theoretical uncertainties counted separately). Cross-check column definitions.
- **Negative-going systematics** — the procedure produces non-negative per-bin per-source values (since $\Delta_j$ and $\Delta_{{\rm tot},b}$ are magnitudes). Asymmetric (+/−) systematics from the paper should be symmetrized for SFitter, with the asymmetry documented.

## 9. Documenting the Procedure In the Extraction Report

For every modifier produced via the two-step procedure, record:

- The source the relative composition came from (paper Table X, supplementary, HEPData YY)
- The source the per-bin total came from
- Whether the inclusive-cross-section breakdown was used vs. an observable-specific breakdown
- Confidence: `high` if direct breakdown was used; `medium` if the procedure was applied with the same-observable breakdown; `medium` (with caveat) if the inclusive breakdown was propagated to a differential

The extraction-reviewer agent uses these source pointers to validate traceability. Missing pointers = automatic FLAG.
