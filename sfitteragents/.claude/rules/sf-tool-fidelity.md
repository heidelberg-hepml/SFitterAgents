# Rule — SFitter tool fidelity: the default is a standard run

Unless the user asks otherwise (directly, or by approving a suggestion you surfaced), the fit is a
**standard SFitter run** — the tool's own likelihood, profiling, and interval machinery, driven **only**
through the datacard and run/param-card settings. The reported constraint is whatever the tool produces,
never a statistic you compute on top of it. The standard run's baseline is the **SM / a real
measurement**; do not tune it toward any expected result.

## You may set (the standard knobs)
- The **datacard**: measured values, SM template + theory-band sizing, κ/D6 predictions, operator set,
  correlation `name`/`label`/`energy`. These are physics inputs — set them, and surface the load-bearing
  choices to the user.
- The **run/param card**: `fitter` (flow/smc/craft), `likelihood` (profile/toy/spiral/five_point),
  `precision` (single/double), `run_name`, and the dataset/sector selection. See the `sf-fit` skill for
  how to configure the run card (including the top-sector switch and the edit-a-local-copy rule).

## You may NOT do by default (substituting the machinery)
No hand-rolled MLE/SVD, no custom profiling, no bespoke interval extraction (PCHIP / linear-crossing /
your own spline), no re-scaling or re-deriving the tool's Δχ²/intervals outside the tool. "We ran
SFitter" is only meaningful if the number is the tool's; a hand-rolled substitute silently breaks that
and erodes trust.

## When the tool's own machinery appears to fail
Surface it, don't route around it. If the tool ships its interval call disabled, its extractor misbehaves
on flat RFit basins (best-fit at a grid edge, 68%≡95%, spline warnings), or the profile looks unreliable
— **report the failure AS-IS with the evidence and stop for user direction.** Re-enabling the tool's own
commented-out interval call is within fidelity; writing your own extractor to replace it needs explicit
user opt-in. Distinguish the two and get the go-ahead before shipping a hand-rolled number as the result.

## Provenance
State, per reported curve/interval, which tool call produced it (fitter, likelihood, method, results
file). Any user-opted-in hand-rolled step is labelled as such right next to the number — never let a
hand-rolled statistic read as the tool's.

## Cross-checks are optional, not default
Physics cross-checks beyond the standard run (constraint-source, EFT-validity/dim-6², closure-vs-honest
band — see `sf-diagnostics`) are **offered to the user, never run by default**. Running them
automatically would tune the fit to a specific expected signal and diverge from a standard SM-baseline
SFitter run. Offer them; run them only on request.
