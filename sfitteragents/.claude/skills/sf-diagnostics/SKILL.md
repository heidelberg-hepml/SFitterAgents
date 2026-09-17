---
name: sf-diagnostics
description: OPTIONAL physics cross-checks on a completed SFitter fit — run ONLY when the user asks for one, or offer them after a standard fit. Covers the constraint-source check (which observable/bins carry the Δχ²), the EFT-validity / dim-6² check (R=|Q·C²|/|L·C| per bin), and the closure-vs-honest theory-band cross-check. These are diagnostics on top of the standard run, NOT part of it — never run them by default (that would tune the fit to an expected signal and diverge from a standard SM-baseline SFitter run). Use when the user says "check what drives the constraint", "is the EFT valid here", "how much of the width is the theory band", or accepts an offered cross-check.
---

# `/sf-diagnostics`

Optional cross-checks on a finished fit. These sharpen interpretation but are **not** the standard
deliverable.

## Guardrail — offered, never default

A standard SFitter run (`sf-fit`, `rules/sf-tool-fidelity.md`) baselines on the **SM / a real
measurement** and does not assume any injected signal. These diagnostics are **offered to the user** or
run **on explicit request** — never automatically. Running them by default would tune the analysis toward
a specific expected result (overfitting to one benchmark) rather than reporting what a standard run finds.
When you finish a standard fit you MAY list these as available cross-checks; do not perform them unless
asked.

## The cross-checks

**1. Constraint-source check** — decompose the fit's Δχ² by observable/bin: which measurements actually
carry the constraint? Flag a constraint driven by a **near-null observable** (e.g. a charge asymmetry
A_C ≈ 10⁻³ sitting on a large *relative* theory band), or by one or two extreme bins. A constraint that
rests on a near-null or a single out-of-window bin is fragile and worth surfacing to the user — but report
it as a diagnostic, not as grounds to silently drop data.

**2. EFT-validity / dim-6² check** — per bin, compute the truncation ratio **R = |Q·C²| / |L·C|**
(quadratic vs linear contribution at the fitted C). Where R > 1 the dim-6² term dominates and the linear
EFT expansion is breaking down — typically the high-energy tails. Report which bins breach validity and
by how much; offer (do not force) a re-fit with those bins removed so the user can compare. Note the
`sf-methodology-consultant` slice: SFitter always includes dim-6², and high-tail bins are
candidates for removal (`/sfitter_docs/sfitter_methodology/01` §8).

**3. Closure-vs-honest theory-band cross-check** — the standard fit uses the **honest** theory band
(e.g. the full LO scale/PDF envelope), which is correct for a real (higher-order) measurement. On request,
re-run with a **closure-diagnostic** band (sized at the template's own MC-statistical precision, valid
only when the data and template share the exact same order/PDF — i.e. a synthetic closure) and surface
the honest-vs-closure width/centre difference. Keep honest-LO the default and quoted result; present
closure only as a diagnostic of how much interval width is the band choice. Report both AS-IS.

## Reporting

Each cross-check is labelled a **diagnostic**, kept separate from the standard fit's reported constraint,
and carries its own caveat (a near-null-driven constraint is fragile; an R>1 fit is over-extrapolated; a
closure band is not the physical band for a real measurement). The standard-run numbers remain the ones to
quote unless the user decides otherwise.
