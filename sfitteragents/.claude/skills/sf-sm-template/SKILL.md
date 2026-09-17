---
name: sf-sm-template
description: Use when the deliverable is the SM-prediction template an EFT fit sits on — the Standard-Model baseline for an observable at the correct perturbative order, with theory uncertainties attached, ready to feed the κ parameterization and the datacard `theo` block. Fires on "SM prediction", "SM baseline", "compute the SM template", "what's the prediction for these bins", "NNLO k-factor", "ScaleSim/PDFSim on the prediction", or the Phase-3 step of a reinterpretation. Frames the prediction target, runs the SM prediction as a MadGraph NLO build, gates the perturbative order, sizes the theory-uncertainty budget, and validates against data before hand-off. Skip for a pure factual lookup (dispatch the relevant agent directly) or when an already-validated template exists.
---

# `/sf-sm-template`

The workflow that produces the **SM prediction template** for an observable — the Standard-Model baseline at the correct perturbative order, with theory uncertainties attached. This is the object an EFT fit sits on: the κ parameterization multiplies into it ($\sigma_{{\rm SMEFT},b}=\sigma_b^{\rm SM}(1+\kappa_{1,b}C+\kappa_{2,b}C^2)$) and the datacard's `theo` modifiers carry its uncertainty. Get this wrong and the bias does not announce itself — it absorbs into a Wilson coefficient as fake BSM.

The orchestration disciplines this workflow leans on are always-loaded, not restated here: dual-spec, regime classification, slice-boundary premises, whole-spec reconciliation, revise-before-caveat, and "a clean run is not evidence" live in `lead-discipline.md`. This skill is the SM-template-specific scaffold over them. Two inherited skills do load-bearing work inside it: **`mg-setup`** builds the MadGraph run, and **`cluster-submission`** executes the compute-heavy ones. Reference them — do not restate.

This workflow is Phase 3 of the reinterpretation family (`sf-reinterpret` overarching; `sf-extract` before it, `sf-parameterize` and `sf-datacard` after). It consumes the extraction's observable classification and produces the κ baseline + `theo` block those siblings consume.

## Phase 1 — Frame the prediction target

Capture what the template must predict (dual-spec discipline), verbatim where the user gave it: the **process**, the **perturbative order** the measurement is at (NLO? NNLO?), **which bins** (edges, observable), and **normalized vs absolute**. The normalized-vs-absolute classification is **not** yours to assert — it is owned by `sf-measurement-extractor` (from the extraction). Dispatch it (or read its extraction return) before proceeding: the answer decides whether the k-factor must be per-bin (Phase 3) and whether luminosity belongs in the budget (Phase 4). If the target is too vague to act on (order unstated, bins unstated), surface and ask.

## Phase 2 — Run the SM prediction (a MadGraph NLO build)

The SM prediction *is* a MadGraph run, almost always at NLO. Build it via the inherited **`mg-setup`** skill — frame the physics-spec, classify the regime, dispatch the `ma-` consultants `mg-setup` names (process line → `ma-process-syntax-consultant`; NLO bracket syntax → `ma-nlo-syntax-consultant` + `ma-amcatnlo-consultant` + `ma-nlo-model-consultant`; the central scale and PDF set → `ma-scales-pdf-consultant`; cuts/binning → `ma-kinematic-cuts-consultant`), then reconcile. Two SM-template-specific build requirements to carry into the `mg-setup` framing:

- **`use_syst True`** — the run must store per-event scale and PDF variation weights, or ScaleSim/PDFSim cannot be reconstructed without rerunning (Phase 4 depends on this; `ma-systematics-consultant` / `ma-scales-pdf-consultant` own the mechanics).
- **Central scale appropriate to the observable** — a dynamic scale for a differential spanning a wide range, not a fixed scale that grows large logs in the tail (`ma-scales-pdf-consultant` owns the choice).

**Submit the run via `cluster-submission`, NOT locally.** An NLO event-generation run with systematics weights is compute-heavy by definition — it matches every "when to submit" criterion. When you delegate the run, the dispatch must explicitly direct the worker to submit (job script under `$CLUSTER_RUNS/<jobname>/`, `sbatch`, wait for completion, capture exit status, read outputs from `$CLUSTER_RUNS/`). If a worker returns NLO cross-sections with no job ID / no `$CLUSTER_RUNS` entry / no `exit_status`, push back and require the cluster run. A low-statistics local probe is not the high-statistics prediction the fit needs.

## Phase 3 — Perturbative-order gate (hard gate)

Dispatch **`sf-order-corrector`**: it owns "is the baseline at the right order". Two hard gates, both must pass before the template can ship:

- **The NNLO k-factor must be APPLIED, not absorbed.** If the measurement is at NNLO and MadGraph ran at NLO, the per-bin ratio is *multiplied* into the baseline ($\sigma_b^{\rm SM,used}=k_b\,\sigma_b^{\rm NLO}$), with $k_b$ from HighTea/MATRIX/fastNLO at the **same scale, PDF, $\alpha_s$, $m_t$, binning** as the NLO run. A "ScalesNNLO"/"NNLOrew" modifier is a *separate* object (the uncertainty *on* the ratio, ~1–3%), never a stand-in for applying it. **For a normalized differential the k-factor must be per-bin** — a uniform scalar $k$ cancels in $(1/\sigma)\,d\sigma/dx$ and silently no-ops on the fit.
- **Integrated-σ vs literature NNLO sanity check.** Integrate the SM prediction and compare to the published NNLO total for the process ($pp\to t\bar t$ 13 TeV $\approx 832$ pb). A result near LO ($\sim480$ pb) or bare NLO ($\sim700$ pb) flags a missed k-factor. Confirm the literature value against its citation for THIS process and energy — do not ship the 832-pb row from recall.

These are gates: the workflow does not advance to Phase 4 until `sf-order-corrector` confirms both. (Scale-form mechanics → `ma-scales-pdf-consultant`; first-principles physics of the NNLO shape → `ma-physics-consultant`; an independent integral recompute → `ma-numerics-consultant`.)

## Phase 4 — Theory-uncertainty budget

The template carries its own theory uncertainty — independent of whether a k-factor was applied. Without it the fit treats the template as perfectly known and absorbs every residual shape mismatch into the Wilson coefficients. Size the budget at the magnitude appropriate to the **actual** perturbative order of the baseline (an NNLO-corrected baseline gets NNLO-sized scale uncertainty, not NLO). Dispatch the per-source estimators:

- **`sf-scale-uncertainty-estimator`** — ScaleSim: the 7-point $\mu_R/\mu_F$ **envelope** (not quadrature), per bin, at the right order (~8–15% LO, ~3–5% NLO, ~1–3% NNLO for $t\bar t$). RFit/flat-prior assignment.
- **`sf-pdf-uncertainty-estimator`** — PDFSim: PDF + $\alpha_s$ error-set envelope (Hessian vs MC-replica per set), ~2–5% inclusive / 5–15% tail. Gaussian assignment.
- **`sf-parametric-uncertainty-estimator`** — $m_t$ (and other parametrics), parton-shower/matching (particle-level only), MC-statistical, EFT-truncation, and the NNLOrew magnitude (~1–3%); it sizes each and assigns its prior, and flags which of its sources are N/A for this measurement class (shower is removed by unfolding at parton level).

**Then assemble the budget — the lead's cross-slice reconciliation, not one estimator's:**

- **Which to include** — scale, PDF+$\alpha_s$, and MC-stat always; $m_t$ and shower for particle-level; $m_t$ but **not** shower for parton-level unfolded (removed by unfolding); EFT-truncation only for the EFT-specific budget. Drop any source an estimator flagged N/A.
- **Combine** — across-source **quadrature** (independent origins): $\delta_b^{\rm theo}=\sqrt{\delta_{\rm scale}^2+\delta_{\rm PDF}^2+\delta_{\alpha_s}^2+\delta_{m_t}^2+\delta_{\rm shower}^2+\delta_{\rm MC}^2}$, each source carrying the prior its estimator assigned (scale flat/RFit; PDF/$\alpha_s$/parametric/MC-stat Gaussian).
- **No double-counting against the observation side** — the measurement's reported theory uncertainty already sits on the observation entry; the same physical source must not appear on both sides. Dispatch **`sf-systematics-decomposer`** (it owns the observation-side budget) and confirm each source sits on exactly one side: shower removed by unfolding is not on a parton-level template; the paper's observation-side `ScalesT` is a *measurement* uncertainty distinct from your template's ScaleSim; template MC-stat is a different sample from the unfolding MC-stat.
- **Carry each source's caveat** — a lower-bound, stopgap-literature-envelope, or applicability flag an estimator raised (a ggF scale envelope flagged a lower bound; a documented literature envelope used as a stopgap) travels **with** its source into the combined budget and the hand-off. The quadrature must not silently launder a flagged lower bound into a hard uncertainty.

## Phase 5 — Validate and hand off

Two checks before shipping, by dispatch (whole-spec reconciliation — a cross-slice invariant is not a lead eyeball):

- **SM-vs-data validation.** Compare the completed template to the measured data as a sanity step — agreement within the combined (data + theory) uncertainty is expected; a systematic shape disagreement that is *not* the EFT signal you are about to fit means the template, the k-factor, or the budget is still wrong (re-open the relevant phase per revise-before-caveat). Per `ma-outcome-not-evidence`, a template that "runs and produces numbers" is not a validated template.
- **Cross-check $\sqrt{{\rm ScaleSim}^2+{\rm PDFSim}^2}$** per bin against the paper's quoted theory uncertainty on the SM prediction — agreement within a factor of ~2 is expected; a large gap means a missing modifier or a magnitude error (re-engage the owning Phase-4 estimator).

Then hand off: the template + its theory modifiers feed **`sf-parameterize`** (the κ baseline the WC scan multiplies into) and **`sf-datacard`** (the `theo` block of the observation/prediction entry). Ship per revise-before-caveat — revise within the user's commitments before caveating; surface every load-bearing choice (scale choice, k-factor source, which sources entered the budget) rather than shipping it silently.

## Gates and required deliverables

Hard gates (Phase 3, both owned by `sf-order-corrector`, both must pass before Phase 4):

1. NNLO k-factor **applied** (multiplied into the baseline), **per-bin** for normalized differentials — a uniform $k$ on a normalized template is flagged as insufficient.
2. Integrated SM σ within range of the published NNLO literature total for the process/energy.

Required deliverables of the workflow:

- **SM prediction per bin** at the correct perturbative order, with the central scale and PDF set named.
- **k-factors applied, listed explicitly per bin** (a single uniform $k$ on a normalized differential is called out as a no-op, not a correction).
- **ScaleSim and PDFSim per bin**, each with its **magnitude and source** (MadGraph `use_syst` weights, HighTea/MATRIX/fastNLO tables, or a documented literature envelope as a flagged stopgap), at the magnitude appropriate to the baseline's actual order; plus NNLOrew if a k-factor was applied.
- **SM-vs-data validation** result and the no-double-counting confirmation against the observation side.

## Document

Before this phase is complete, update `/output/documentation/sm_template/` per `rules/sf-documentation.md` and the `sf-document` skill: `runcards/` holds every run_card / param_card / `.mg5` that fed the template; `code/` holds the driver, k-factor, and theory-budget scripts; `validation/` holds the SM-vs-own-simulation validation plot; and `sm_template.md` records the reasoning for each choice (perturbative order, per-bin NNLO k-factor, central scale, PDF). **Copy the exact cluster runcards and driver in** — `$CLUSTER_RUNS` is scratch, not durable. The phase is not done until this bucket is current.
