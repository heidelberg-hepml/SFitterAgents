---
name: sf-parameterize
description: Use when the deliverable is a SMEFT Wilson-coefficient scan campaign and the κ-parameterization extracted from it — "parameterize operator X on this observable", "run a WC scan and extract κ₁/κ₂", "give me the D6 lin/quad contributions for the datacard", "add interference between these operators". The phased scaffold from operator selection through scan design, the mandatory hygiene gate, the cluster-submitted runs, κ-extraction, interference, and hand-off to the datacard. Skip for a pure source-mechanics lookup (dispatch the relevant agent directly) or a single factual question (e.g. "what's the SFitter name for C_tG").
---

# `/sf-parameterize`

The parameterization workflow — the phased sequence for running a SMEFT Wilson-coefficient scan campaign and extracting the κ-parameterization SFitter consumes. The orchestration disciplines it leans on are always-loaded, not restated here: dual-spec, regime classification, slice-boundary premises, whole-spec reconciliation, revise-before-caveat, and the conflict-by-re-engaging rule live in `lead-discipline.md`; "a clean run is not evidence" lives in `rules/ma-outcome-not-evidence.md`; compute-heavy submission discipline lives in `cluster-submission`. This skill is the parameterization-specific scaffold over them.

The campaign builds on the inherited MadGraph layer: every scan run is **built with `/mg-setup`** (the process line, model, EFT orders, run-card) and **submitted via `/cluster-submission`** — SMEFTatNLO scans are compute-heavy and never run locally. This skill orchestrates the EFT-specific agents on top.

A scan that parses, runs, and fits cleanly can still ship silently-biased κ. The gates below are where a wrong-but-runnable campaign deviates from a correct one; name them, do not skip them on a clean run.

## Phase 1 — Operator selection

Agree the operator set and the truncation before anything runs. Dispatch in parallel:

- `ma-physics-consultant` — which operators physically contribute to this process, and whether the intended WC range is inside EFT validity.
- `ma-eft-consultant` — the UFO model (SMEFTatNLO for the top sector), the `restrict_*.dat` selection, and the NP-truncation **mechanics**: linear (`NP=1`, the Λ⁻² interference) vs squared (`NP^2=2`, the Λ⁻⁴ BSM-squared).
- `sf-convention-translator` — the Warsaw → SFitter `D6*` naming (`D6tg`, `D6qq18`, …), the alternative-Warsaw aliases (map to canonical before assigning a prefix), and the SMEFTatNLO↔LHC-TOPWG `c_tG` `g_s` rescaling that the target fitter's convention may demand.

Output of the phase: the operator set, the pair list (if interference is wanted), and the truncation choice (linear-only vs linear+quadratic). Reconcile a physics-vs-EFT-validity conflict by re-engaging, not by adopting the better-cited side.

## Phase 2 — Scan design

Dispatch `sf-scan-designer` for the campaign shape: the symmetric scan grid skipping 0 (e.g. `C ∈ {-10,-7.5,-5,-2.5,2.5,5,7.5,10}`), per-operator independent runs (one output dir each), the separate Λ⁻² / Λ⁻⁴ output requests, the `.mg5` skeleton (process line, run-card knobs, scan-value placement) with a placeholder for the hygiene block, and the polynomial-fit-vs-direct-decomposition route choice. The `NP=`/`NP^2==` syntax that realizes the separation is `ma-eft-consultant`'s; the consultant specifies *which separation it needs*. Whether the range stays EFT-valid is `ma-physics-consultant`'s (Phase 1).

## Phase 3 — Scan hygiene (MANDATORY gate)

Dispatch `sf-scan-sanitizer`. Two parts, both required:

- **Defensive zeroing.** Enumerate every code in every `DIM6*` block from the model's `restrict_default.dat` for THIS version and set each to `0.0` in the `.mg5`, activating only the scanned operator(s) after the block. The `QED=0` filter strips DIM6/DIM62F but does **NOT** touch the four-fermion `DIM64F` block — the primary contamination risk. The codes are version-specific; do not trust a memorized list. For a joint interference run, both operators stay active and the rest are zeroed.
- **Matrix-element contamination check** — run it as a probe (the `/mg-probe` pattern) or delegate the file-opening to `sf-reviewer`. After generation, `grep GC_` on the compiled `matrix*.f` and map each `GC_N` via `coupl.inc`; only couplings from the scanned operator (and pure QCD) may appear. Any other `GC_N` is contamination — fix the zeroing and regenerate.

**Gate — contamination-free:** a contaminated scan still runs and still fits, and silently biases the extracted κ by 2–10% (worse in tails) from operators you never meant to activate. This is the per-`ma-outcome-not-evidence` failure mode — a clean run is not evidence the scan is clean. Do not proceed to Phase 4 until the matrix elements are confirmed clean for this generation.

## Phase 4 — Run the scans

Build each run with the inherited `/mg-setup` (model, process, EFT orders, run-card) and **submit via `/cluster-submission`** — SMEFTatNLO event generation across a scan grid is compute-heavy, never local. The hard rule from `cluster-submission` binds: the dispatch must explicitly direct the worker to write a job script under `$CLUSTER_RUNS/<jobname>/`, submit with `sbatch`, wait for completion, and capture exit status and outputs. Per-operator runs are independent — parallelize them. Wait for completion before treating output as authoritative; a low-statistics local run is not a substitute.

## Phase 5 — Extract κ₁/κ₂

Dispatch `sf-kappa-extractor`: per bin, fit `σ_lin(C)=m_b·C` and `σ_quad(C)=a_b·C²` (residuals after the SM subtraction), then `κ₁,b = m_b/σ_SM,b`, `κ₂,b = a_b/σ_SM,b`. For a **normalized differential**, also fit the integrated cross-section over the same grid for the total kappas and apply the Taylor handling (`a_norm = κ₁,b − κ₁,t`, `c_norm = …`); flag operators that act as an overall rescaling (weakly constrained when normalized). Convert to the SFitter **absolute** contributions (`lin = κ₁·σ_SM`, `quad = κ₂·σ_SM`); the bare-`D6op` / self-product-`D6opxD6op` / cross-`D6op1xD6op2` naming and any `g_s` rescaling on those numbers are `sf-convention-translator`'s.

**Gate — fit quality:** `R² > 0.999` on both the linear and quadratic per-bin fits; residuals consistent with per-bin MC stats with **no systematic structure vs C**; the free-fit `a₀` agrees with the independent SM run within MC noise. A lower R² or structured residual means insufficient statistics, non-polynomial behavior, or contamination — investigate, do not paper over. Whether a structured residual is real higher-order physics rather than a fit defect is `ma-physics-consultant`'s call; `sf-kappa-extractor` flags the structure.

## Phase 6 — Interference

For each operator pair, dispatch `sf-kappa-extractor`. From the joint-run Λ⁻⁴ output, subtract the individual quadratics (`σ_cross = σ_Λ⁻⁴,both − C_i²·σ_quad,i − C_j²·σ_quad,j`, the single-op quadratics being Phase-5 inputs), then `κ₂^(ij) = σ_cross/(σ_SM·C_i·C_j)` per bin — the convention already absorbs the factor of 2.

**Gate — interference S/N:** report `reliable:false` with a note rather than ship noise when `|κ₂^(ij)| / √(κ₂^(ii)·κ₂^(jj)) ≤ 0.1` (interference is a difference of large numbers, so MC noise is severe; the Schmal thesis found `C_td¹ × C_Qd¹` to be one such case). Before giving up on a borderline pair, try the mitigations: more statistics, reference `(C_i,C_j)` that maximize interference vs the quadratics, or the direct-decomposition route. The pair count is `N(N-1)/2` — scan only the physically-motivated pairs (`ma-physics-consultant` on which pairs interfere).

## Phase 7 — Hand off

The κ tables and absolute D6 contributions feed `sf-datacard` as the prediction modifiers (`D6op`, `D6opxD6op`, `D6op1xD6op2` arrays placed into the datacard `modifiers` block). The SM baseline these contributions are normalized against — at the correct perturbative order, per-bin NNLO k-factor applied, with its own template uncertainties — comes from `sf-sm-template` (owner `sf-order-corrector` for the k-factor decision). Confirm the baseline used in Phase 5's `σ_SM` matches the one `sf-datacard` will ship; a mismatch silently rescales every κ.

## Gates and failure modes (summary)

| Gate | Phase | Failure if skipped |
|---|---|---|
| Defensive zeroing done | 3 | Default-nonzero operators enter the amplitude |
| Matrix-element contamination-free (`grep GC_`) | 3 | Silent 2–10% κ bias from leaked couplings |
| Fit quality `R² > 0.999`, no structured residual, `a₀` ↔ SM | 5 | Bad κ from low stats, non-polynomial behavior, or baseline inconsistency |
| Interference S/N > 0.1 | 6 | Noise-dominated `κ₂^(ij)` shipped as signal |
| Baseline matches `sf-datacard`'s | 7 | Every κ silently rescaled by a wrong σ_SM |

Reconcile and present per the whole-spec reconciliation and revise-before-caveat disciplines: confirm the cross-slice invariants (the convention the contributions carry matches the target fitter; the baseline is consistent end-to-end) by dispatch to the owning agents, not by eyeball.

## Family

Sibling workflows in the `sf-` layer: `sf-reinterpret` (the end-to-end orchestration this is one stage of), `sf-extract` (measurement extraction), `sf-sm-template` (the SM baseline), `sf-datacard` (the prediction/observation datacard assembly this hands off to), and `sf-deep-verify` (the deep-verification cascade). Inherited skills used directly: `mg-setup` (build), `cluster-submission` (submit), `mg-probe` (the runtime contamination check).

## Document

Before this phase is complete, update `/output/documentation/parameterization/` per `rules/sf-documentation.md` and the `sf-document` skill: `runcards/` + `code/` hold every scan runcard and driver; **every scan run that feeds the final κ table is listed in `parameterization.md` with its version**; `validation/` holds the coefficient-extraction plots (κ-fit R², residual structure); and the md records the reasoning for each choice (operator set, truncation, hygiene). **Copy the exact cluster runcards in** — `$CLUSTER_RUNS` is scratch. The phase is not done until this bucket is current.
