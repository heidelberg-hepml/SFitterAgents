---
name: sf-document
description: Use at the close of every reinterpretation phase — and before shipping a datacard or fit — to record that phase's provenance into `/output/documentation/<bucket>/`. The procedure behind the always-loaded `rules/sf-documentation.md`: the five-bucket layout, the step-log template (decision log, code manifest, validation), the per-step content checklists, the `README.md` structure, and the pre-ship reproducibility audit. The rule says you must document as you go; this skill says how, and what each bucket must contain to be paper-grade. Invoke whenever a phase produced a kept result and its bucket needs writing or updating. Skip only for a phase that produced nothing the analysis keeps.
---

# `/sf-document`

The procedure for the documentation regime. `rules/sf-documentation.md` (always loaded) is the contract —
the invariants, the adoption gate, the success criterion; this skill is the *how*: the layout, the
templates, and what each bucket must contain to be paper-grade. It authors nothing about the physics — it
records what the pipeline actually did, as it did it. Success is **information completeness**: the union of
these files carries everything a paper on the analysis would need, reconstructable without the
conversation, the cluster scratch, or agent memory.

## The tree — `/output/documentation/`

Five buckets, one per pipeline sub-skill. Every bucket has the invariant two parts — a `code/` subdir and
one canonical `<bucket>.md` log — plus the named data subdirs its checklist below demands.

```
/output/documentation/
  README.md                          # overarching, terse index (see "README" below)
  extraction/       {code/, raw/, processed/, extraction.md}
  sm_template/      {code/, runcards/, validation/, sm_template.md}
  parameterization/ {code/, runcards/, validation/, parameterization.md}
  datacard/         {code/, validation/, datacard.json, datacard.md}
  fit/              {code/, results/, fit.md}
```

**Cluster artifacts.** Heavy runs execute in `$CLUSTER_RUNS/<job>/`, which is per-session, gitignored, and
not durable. **Copy** the exact runcards, driver, and job script that produced a kept result into the
bucket — do not reference the cluster dir.

## The step-log template — every `<bucket>.md`

- `## Purpose` — what this phase produced, one paragraph.
- `## Decision log` — chronological, append-only. One entry per decision or code change:
  *`<wall-clock timestamp> · <ordinal / cluster-job-id>` · the decision · who (**agent** | **user**) ·
  reasoning · source/evidence (doc cite, paper table, probe result)*. Include timestamps always (a reader
  may ignore them; they cost nothing). `FAILED:` and `SUPERSEDED:` entries stay in place, never deleted.
- `## Code manifest` — one row per file in `code/`: *filename · what it does · exact invocation command ·
  where it ran (local | cluster job `<id>`)*. **Every kept result maps to a row here** — this is where the
  adoption gate is checked.
- `## Inputs / Outputs` — data provenance: raw sources (URL / DOI / HEPData id), processed products, the
  artifacts handed to the next phase.
- `## Validation` — the plots / checks this phase's checklist requires.
- `## Result` — the numbers / artifacts passed downstream.

## Per-step content checklists (the "done" definition for each bucket)

- **extraction** — every uncertainty **choice** logged, and the **source** of every included uncertainty
  term named; `raw/` holds the original downloaded data (HEPData tarball, tables) untouched; `processed/`
  **references** the canonical `sf-extract` extraction report (single source, not a copy); `code/` holds
  every extraction / digitization script.
- **sm_template** — every run_card / param_card / `.mg5` saved to `runcards/`; `code/` holds the driver +
  k-factor + theory-budget scripts; the reasoning for each choice (perturbative order, per-bin NNLO
  k-factor, central scale, PDF) in the log; the SM-vs-own-simulation validation plot in `validation/`.
- **parameterization** — every scan runcard + driver saved (`runcards/`, `code/`); **every scan run that
  feeds the final κ table listed in the md, with its version**; the reasoning for each choice (operator
  set, truncation, hygiene); coefficient-extraction validation plots (κ-fit R², residual structure) in
  `validation/`.
- **datacard** — the assembly choices logged (modifier→canonical-name mapping, theory-band sizing, ID
  encoding); the shipped `datacard.json` copied in; the `ReadDataCard` load log in `validation/`.
- **fit** — an exact copy of the fit code invoked in `code/`; the exact invocation documented; any change
  to the fit code noted, justified, and its modified copy saved (keep both, with the diff); `results/`
  holds the fit outputs / intervals / plots; any ephemeral python that produced a kept result crystallized
  to a saved script (debugging throwaways need not be).

## README — the overarching index

`README.md` is a **terse index + reproduce-recipe, not a prose narrative** — the completeness lives in the
union of the bucket files; the README is navigation. It carries: the analysis identity (measurement,
observable(s), operator set); one line per phase linking its bucket log; the **end-to-end reproduce recipe**
(which files to run, in which order, on what); and the paper-readiness checklist (every per-step bucket
checklist above satisfied). The `sf-reinterpret` conductor owns and updates it; each sub-skill owns its own
bucket.

## Pre-ship audit (the hard gate)

Before a datacard or fit is declared done, confirm: every bucket present and current; every code-manifest
row resolves to a file in `code/`; **no kept result without a re-runnable script behind it** (the adoption
gate); every uncertainty term sourced; failed / superseded paths recorded, not erased. `sf-reviewer`'s
documentation concern is the independent reviewable check.
