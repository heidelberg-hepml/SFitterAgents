---
name: sf-fit
description: Use when the deliverable is running the SFitter fit on an assembled datacard and reading off the constraint — "run the fit", "fit this datacard", "give me the intervals / likelihood profile", "what does SFitter say for operator X". Owns the step AFTER the datacard: configure the run/param card (including the top-sector switch and the edit-a-local-copy rule), run the tool's own standard fit, and extract the tool's own intervals on the correct Wilks scale. Enforces `rules/sf-tool-fidelity.md` (no hand-rolled statistics by default) and OFFERS the optional cross-checks in `sf-diagnostics` rather than running them. Skip for building the datacard (that is `sf-datacard`) or a pure factual lookup.
---

# `/sf-fit`

The fit step — turning a validated SFitter datacard into the tool's own reported constraint. This
closes the gap after `sf-datacard`: `sf-reinterpret` produces the datacard, and this skill runs the
**standard SFitter fit** and reads off the intervals. Governed by `rules/sf-tool-fidelity.md`: the
default is the tool's own likelihood, profiling, and interval machinery, driven only through the datacard
and run-card settings — never a statistic hand-computed on top of it. Compute-heavy fits are a GPU job
submitted via `cluster-submission`.

## 1. Configure the run/param card

The SFitter run card selects the **fitter** (`flow`/`smc`/`craft`), the **likelihood**
(`profile`/`toy`/`spiral`/`five_point`), the **precision** (`single`/`double`), the `run_name`, and the
**dataset/sector**. Recommendations for a tt̄ SMEFT reinterpretation are the sfitter-methodology
consultant's slice (dispatch `sf-methodology-consultant`); a common default is
`fitter=flow, likelihood=profile, precision=double` with the `profile` likelihood pointed at the
datacard JSON.

**Sector gate (do not skip).** The run card's `sector` key selects the operator basis, and the
shipped example cards come in both flavours (`top_fit.yaml`, `higgs_fit.yaml`). For a tt̄ /
top-sector reinterpretation the dataset/operator/sector selection must be the **top sector** — a
Higgs-configured card silently fits the wrong thing. Verify the
current setting and the exact fields to change against source (`$SFITTER_INSTALL` + the run-card
spec) — a config claim is a source claim (`rules/ma-truth-sources.md`); do not assume the field names.

**EDIT ONLY A LOCAL COPY — NEVER THE INSTALLED CARD.** Copy the run card out of `$SFITTER_INSTALL`
into the fit's job directory under `$CLUSTER_RUNS` (below), edit the copy, and point the run at the copy.
Mutating the shipped card under `$SFITTER_INSTALL` corrupts the tool for every future run and every other
session on the image. State in your deliverable which local copy you used.

## 2. Run the standard fit + read the tool's own intervals

**How the tool runs.** The entry point is `python -m sfitter run <run card>` (`fit` / `plot
<yyyymmdd_hhmmss>_<run_name>` repeat the fit or the plots of an existing run). Each run is written to
`output/<yyyymmdd_hhmmss>_<run_name>/` (`results.pkl`, plots, `log.txt`) next to the `sfitter` package
it was imported from, and that `output/` directory must already exist. A job sees only `$CLUSTER_RUNS`
and the image, and `datacard:` in the run card is resolved from the working directory. So run a copy of
the tool inside the job directory:

```bash
JOB=$CLUSTER_RUNS/<jobname>
mkdir -p $JOB && cp -r $SFITTER_INSTALL $JOB/sfitter && mkdir -p $JOB/sfitter/output
# copy the datacard and the edited run card into $JOB; set `datacard:` to the absolute path of the copy
# job-script body (a GPU partition, via cluster-submission):
cd $JOB/sfitter && $CLUSTER_EXEC python -m sfitter run $JOB/<run card>.yaml --verbose
```

Run the fit through the tool this way (via `cluster-submission` when it is GPU/heavy). Then read the constraint
from the tool's **own** output — `profile_1d` (frequentist profile) and, when asked, `marginal_1d`
(Bayesian marginal) — and the tool's **own** `confidence_interval` for the 68/95% intervals. Per
`rules/sf-tool-fidelity.md`: **do not hand-roll** the profiling or the interval extraction. If the tool
ships its interval call disabled, re-enabling the tool's own routine is within fidelity; writing your own
extractor is a user-opt-in deviation — if the native extractor misbehaves (flat-basin spline overshoot,
best-fit at a grid edge, 68%≡95%, spline warnings), report it AS-IS with the evidence and stop for
direction.

## 3. Wilks scale — read the 1-parameter interval correctly

`log_likelihood_top` returns **−χ²** and the flow stores `profile_1d = exp(−χ²)` — a **squared** density
(the `/2` variant is commented out in source; verify at `$SFITTER_INSTALL`). So the tool's own
`−2·ln(profile_1d)` is **2× the 1-parameter Wilks Δχ²**, and the correct frequentist scale is
**`Δχ² = −ln(profile_1d/max)`** (68% at Δχ²=1, 95% at 3.84). Reading `−2ln` as Wilks makes the interval
**~√2 too narrow**. This is the sfitter-methodology consultant's slice — confirm the convention against
source before quoting a σ.

## 4. Provenance and offered cross-checks

- **Provenance.** For every reported curve/interval, state which tool call produced it (fitter,
  likelihood, method, results file), and label any user-opted-in hand-rolled step right next to the number.
- **Offer, don't run, the cross-checks.** After a clean standard fit you MAY offer the optional
  diagnostics in `sf-diagnostics` (constraint-source, EFT-validity/dim-6², closure-vs-honest band). Run
  them only when the user asks — the standard run sits on the SM and does not assume an injected signal;
  running the cross-checks by default would tune the fit to an expected result.

## 5. Document (hard gate)

The fit is not shipped until `/output/documentation/fit/` is current per `rules/sf-documentation.md` and
the `sf-document` skill: an exact copy of the fit code invoked in `code/`; the exact invocation
documented in `fit.md`; any change to the fit code noted, justified, and its modified copy saved (keep
both, with the diff — the tool-fidelity rule already requires you edit only a local copy, so that copy
is the artifact); `results/` holds the fit outputs, intervals, and plots; and any ephemeral python that
produced a kept result crystallized to a saved script (debugging throwaways need not be). The reported
constraint is not shippable without this bucket.
