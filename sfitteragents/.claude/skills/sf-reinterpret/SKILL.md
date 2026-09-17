---
name: sf-reinterpret
description: Use when the deliverable is reinterpreting an experimental measurement as a SMEFT/EFT constraint — the end-to-end pipeline from a measurement to a validated SFitter datacard with κ-parameterized predictions. The default path for "reinterpret this measurement", "parameterize operator X on measurement Y", "build an SFitter datacard from this paper". Sequences the sf- sub-skills; invoke a sub-skill directly for a single phase. Skip for a pure factual lookup.
---

# `/sf-reinterpret`

The overarching reinterpretation workflow — the conductor over the finer `sf-` sub-skills that turn an experimental measurement into a validated SFitter datacard with κ-parameterized predictions. Each phase delegates to a sub-skill that carries its own phase detail (agent roster, internal steps, gates); this skill does not restate them — it names the sequence, the gates between phases, and the interactive guidance. The orchestration disciplines it leans on are always-loaded, not restated here: dual-spec, regime classification — for this layer, EFT power-counting plus observable classification — reconcile-by-re-engaging, and revise-before-caveat live in `lead-discipline.md`; "a clean run is not evidence" lives in `rules/ma-outcome-not-evidence.md`. Compute-heavy MadGraph runs (the SM template and the WC scan) go through `mg-setup` to build and `cluster-submission` to run; this skill conducts, the sub-skills own their phases.

## Interactive framing

This workflow is user-facing and iterative. At the start of a new reinterpretation, briefly introduce the pipeline and ask the user **where to begin** and **which observable(s)** they want parameterized. The user may skip phases, supply their own files at any point (an extraction report, an SM template, a κ table), or iterate on any phase. On **resume**, check `/output` and `/workspace` for artifacts from prior phases — a reviewed extraction report, a validated SM template, a κ/D6 table, a partial datacard — to determine where work left off; do not re-run a phase whose artifact already exists unless the user asks to iterate on it.

## The pipeline

1. **Measurement extraction** — invoke `sf-extract`. Produces a reviewer-approved, structured extraction report (per-bin values, decomposed uncertainties, canonical modifier names). REQUIRED first gate: **confirm the target observable(s) with the user before extracting** — a paper carries several, and extracting the wrong one is a total loss. Hands off the report to `sf-sm-template` and `sf-datacard`.

2. **SM prediction template** — invoke `sf-sm-template`. Produces the SM prediction per bin at the correct perturbative order plus the theory-uncertainty budget — the baseline the EFT fit sits on. Compute-heavy: the prediction is a MadGraph NLO build via `mg-setup`, run via `cluster-submission`. Hands off the template to `sf-parameterize` and `sf-datacard`.

3. **EFT parameterization** — invoke `sf-parameterize`. Opens with operator selection, then the SMEFTatNLO Wilson-coefficient scan campaign, and produces the κ₁/κ₂ + interference tables. Compute-heavy: the scan is submitted via `cluster-submission`. Hands off the κ/D6 tables to `sf-datacard`.

4. **Datacard assembly** — invoke `sf-datacard`. Assembles one paired observation + prediction from the extraction report and the κ/D6 tables into the SFitter JSON, validated until it loads with `ReadDataCard`, written to `/output`. The terminal artifact of the pipeline.

## Deep verification

The heavy verification cascade is **not** automatic. When the user asks for deep verification ("verify deeply", "go deep", "check carefully") — or before shipping a high-stakes datacard — invoke `sf-deep-verify`.

## Documentation

Every reinterpretation maintains a paper-grade provenance record under `/output/documentation/` **as the work happens** (always-loaded `rules/sf-documentation.md` is the contract; the `sf-document` skill is the procedure). This conductor owns the top-level `documentation/README.md` — create it at the start of a reinterpretation (analysis identity + phase index + reproduce-recipe skeleton) and update it as each phase closes. Each sub-skill owns its own bucket (`extraction/`, `sm_template/`, `parameterization/`, `datacard/`, `fit/`).

## Between phases

Summarize the completed phase's result and ask the user how to proceed — **continue / skip / iterate / explain**. Per reconcile-by-re-engaging, a problem surfaced in a later phase is re-engaged at its owning phase with the finding as an explicit premise, not caveated around. **A phase is not complete — and the pipeline does not advance — until its documentation bucket is current** per `rules/sf-documentation.md` and the `sf-document` skill.

Running the actual SFitter fit (a GPU job) is **not** part of this datacard pipeline — it is the lead's job downstream of the datacard, via the `sf-fit` skill (run/param-card setup → the tool's own standard fit → the tool's own intervals) and `cluster-submission`. The fit is a **standard SFitter run by default** — the tool's own likelihood, profiling, and intervals, driven only through the datacard and run-card knobs; substituting hand-rolled statistics for the tool's machinery is a user-opt-in deviation, not the default (`rules/sf-tool-fidelity.md`).
