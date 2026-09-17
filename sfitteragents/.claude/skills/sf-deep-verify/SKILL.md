---
name: sf-deep-verify
description: Heavy verification cascade on the assembled EFT-reinterpretation deliverable — regime classification and review, adversarial concern verification routed by the sf-reviewer concerns, blind-spot triage with dispatched re-verifications, adversarial artifact/runtime probing, reconcile with synthesis verification, a re-verify cycle on any revision, and a closing failure-mode extraction pass that records recurring agent-system mistakes for future sessions. Use ONLY when the user explicitly asks for deep verification ("verify deeply", "go deep", "check carefully"). Do not auto-invoke.
---

# `/sf-deep-verify`

Seven stages. Stages 1-5 run on every invocation. Stage 6 fires only when Stage 5 applies a revision and loops back through Stages 2-4 on the revised deliverable until no further revision is needed. Stage 7 (failure-mode extraction) always fires after the cascade settles, before composing the answer.

This is the heavy verification cascade for the SFitter / EFT-reinterpretation (`sf-`) layer. It mirrors `mg-deep-verify`'s seven-stage shape — same dispatch discipline, same verdict vocabulary, same reconcile-and-re-verify logic — but is adapted at one load-bearing point.

## The key adaptation — re-verify against doc + artifact, not source

Where `mg-deep-verify` verifies by **source-walking MadGraph code**, `sf-deep-verify` verifies by **(a) checking each claim against the curated docs / methodology (`/sfitter_docs/...`), (b) recomputing the numbers (`ma-numerics-reviewer`), and (c) round-tripping or inspecting the actual produced artifacts** — the paper / HEPData values, the generated SMEFTatNLO matrix elements (`grep GC_` on `matrix*.f`), the κ-fit output (R²/residuals), and the assembled datacard (a `ReadDataCard` load).

The reinterpretation agents are doc-, data-, and tool-grounded, not code-grounded. The failure modes are silent: a missing k-factor, a contaminating four-fermion operator, a double-counted scale uncertainty, an absolute value where a percentage was expected — each produces a file that loads, fits, and returns a plausible-looking number that is biased. So "walk source adversarially for THIS input" becomes **"re-verify against the primary doc *and* the actual artifact for THIS input — recompute and round-trip, do not shortcut via cached results."** The load-bearing verification throughout this cascade is recompute + round-trip + doc-check, never a source-walk and never a cached lesson.

## Dispatch discipline

Every Agent dispatch you make within this skill — Stage 1 (the regime-review dispatch), Stage 2 (the per-concern verifier dispatches), Stage 3, Stage 6, Stage 7, the synthesis-verification step in Stage 5, and any other dispatch the cascade triggers — must include this line **verbatim** in the dispatch prompt:

> **Deep-verify dispatch: wiki and Recent lessons as orientation only; for THIS input re-verify against the primary doc/methodology AND the actual artifact (the paper/HEPData numbers, the generated matrix elements, the fit output, the datacard) — recompute and round-trip; do not shortcut via cached results.**

This overrides the global `ma-wiki-as-evidence` rule for the dispatched agent. The cascade is doing the verification; the dispatched agent must not shortcut via cached wiki content or cached lessons. Each stage's dispatch instructions below repeat the cue at the point of action — do not omit it.

**You apply the same self-discipline.** When you are running this cascade, your own lead-memory's Recent lessons and playbook references are orientation only — usable to route and prioritise, not citable as verified evidence in the synthesis. Re-verify against doc + artifact via agent dispatches (carrying the line above) for THIS input.

When Stage 4 invokes `/mg-probe`, attach the same line to the `ma-probe` dispatch the skill makes on your behalf. The `/mg-probe` skill is callable outside the cascade (where this discipline does not apply); the sf-deep-verify line is your channel for opting that dispatch into adversarial mode.

## Stage 1 — Regime classification and review

Carry forward the EFT / reinterpretation regime the lead produced when routing this task (per *Classify the regime before routing* in lead-discipline). If none was recorded, dispatch `ma-physics-consultant` to classify fresh. The classification names: which operators are in play and the truncation (linear, `NP=1` / interference-only, vs squared, `NP^2=2`); the observable's normalized-vs-absolute and fiducial-vs-total status (owned by `sf-measurement-extractor` — this decides which uncertainties cancel and whether a uniform k-factor or scale shift is a no-op); and the perturbative order the data demands of the SM baseline.

Then review it adversarially: dispatch `ma-physics-reviewer` to challenge the EFT framing for THIS input (is the truncation right, do the named operators actually contribute, is the power-counting sound), and `sf-reviewer` to challenge the reinterpretation framing (is the observable classified right, which concerns does this deliverable's purpose make load-bearing). Each dispatch prompt ends with the **sf-deep-verify line**. A NEEDS REVISION corrects the classification before any later stage builds on it; a WARNING flows into Stage 5 reconcile. The review comes first because every later stage depends on the regime: Stage 2 uses it to focus the concern verification, Stage 3 to focus the blind-spot scan, and Stage 4's probe expectations are derived from it.

## Stage 2 — Concern verification (adversarial), routed by the sf-reviewer concerns

`mg-deep-verify` Stage 2 atomizes the spec into per-claim verdicts and routes by `kind`. Here the spine is instead the **eight physics/assembly `sf-reviewer` concerns** (§1–§8; documentation, §9, is gated at assembly-time and phase-close — not re-verified here) — extraction traceability, uncertainty-decomposition integrity, normalization-classification consistency, SM-baseline perturbative order, scan contamination, κ-fit quality, theory double-counting, datacard assembly integrity. Instead of atomic-claim source-walking, dispatch one verifier per implicated concern, in parallel, each carrying the **sf-deep-verify line** and instructed to re-verify against doc + artifact (not memory). State explicitly in each dispatch that the load-bearing verification is **recompute + round-trip + doc-check, not a source-walk.**

| Concern (sf-reviewer §) | Verifier(s) | Re-verify by |
|---|---|---|
| Extraction traceability / decomposition round-trip / normalization (§1, §2, §3) | the extractor + decomposer — `sf-measurement-extractor`, `sf-systematics-decomposer` | re-confirm each source pointer against the actual paper / HEPData record; recompute the Schmal round-trip (`√(Σ Δ_b,j²)` vs HEPData per-bin total; `S` vs paper quoted total); re-confirm normalized/fiducial propagation |
| SM-baseline order + k-factor (§4) | `sf-order-corrector` | recompute the integrated σ from the datacard and compare to the literature NNLO; confirm the NNLO k-factor is **applied per-bin**, not absorbed as a "ScalesNNLO" uncertainty |
| Scan contamination (§5) | an artifact check via the Stage-4 probe / `sf-scan-sanitizer` | `grep GC_` on the actual `matrix*.f`, confirming only the intended operator's couplings (and pure QCD) are active — not by assertion |
| κ-fit quality (§6) | `sf-kappa-extractor` + `ma-numerics-reviewer` | recompute the polynomial fit; R² > 0.999, residuals consistent with MC fluctuation (no systematic pattern), `a₀` consistent with the independent SM prediction; interference S/N honoured |
| Theory double-counting (§7) | the theory estimators — `sf-scale-uncertainty-estimator`, `sf-pdf-uncertainty-estimator`, `sf-parametric-uncertainty-estimator` | confirm each template (prediction-side) source sits on exactly one side, not double-counted against an observation-side modifier covering the same source |
| Datacard assembly integrity (§8) | `sf-datacard-schema-reviewer` (schema/parse) + `sf-reviewer` (semantic) | schema/parse: load the assembled JSON with `ReadDataCard` (must succeed), array lengths, ID pairing, %-vs-absolute, the 7-char ID; semantic: the assembled values trace to their upstream sources — observation = the extraction report, prediction = `sf-sm-template` at the settled order, D6 = `sf-parameterize`'s κ·σ_SM with the operator set complete |

Route only the concerns the deliverable implicates — a κ table with no datacard does not yet exercise §8; an absolute observable does not exercise the normalization-cancellation half of §3. **Batch by verifier, not by concern:** one dispatch per verifier covers all the concern-items routed to it; verifiers fire in parallel.

**Verifier dispatch shape.** Dispatch each verifier with its concern-item list and the instruction: *"Re-verify each item against the primary doc AND the actual artifact for THIS input — recompute the number, round-trip the round-trip, load the load — do not rely on the assembled value or a cached result. For each item: APPROVED (doc + artifact settle it; state the check) / NEEDS REVISION (the item is violated or its load-bearing evidence is silent; cite the discriminating check) / WARNING (you cannot adjudicate from your slice — a methodological convention with more than one defensible form, or an input you cannot verify here; name what must resolve it)."* Reviewers (`ma-numerics-reviewer`, `ma-physics-reviewer`) receive their layer-specific items with out-of-slice content marked as premises — slice-boundary discipline applies.

Each verifier returns **APPROVED / NEEDS REVISION / WARNING** per item. Every dispatch in Stage 2 ends with the **sf-deep-verify line** verbatim.

## Stage 3 — Blind-spot scan + dispatched re-verifications

Dispatch `ma-blind-spot-auditor` with: the assembled deliverable, the question, Stage 1's regime classification, and a per-agent summary of Stage 2 returns (one paragraph each: what was re-verified against which doc + artifact, what was concluded). Dispatch prompt ends with the **sf-deep-verify line**.

The auditor is a **triage scanner, not a verifier.** It returns a structured list — each item names an unverified region, the recommended agent, and a one-sentence rationale. In this layer the unverified regions are doc/data/tool-shaped: a modifier whose source pointer was never checked against the paper, a bin that was never round-tripped, an operator that was never confirmed zeroed in `matrix*.f`, a theory source potentially double-counted across the two sides, an ID character never decoded. No re-verifications, no facts, no judgement.

For each flagged blind spot, dispatch the recommended `sf-` agent with the auditor's pointer and the question. It re-verifies against doc + artifact for this input per its card discipline (re-confirm the pointer in the paper, recompute the round-trip, `grep` the matrix element, load the card), returns its findings, and updates its wiki if durable.

The auditor pass is **unconditional** — always dispatch it. Empty flag-list is a valid outcome. Findings from the dispatched agents enter Stage 5 alongside the original trail; they are not re-routed through Stage 2 (Stage 5's synthesis verification and Stage 6's re-verify cycle catch problems that emerge during reconcile).

## Stage 4 — Artifact / runtime probe (adversarial, expectation-driven)

Two kinds of artifact, two probe channels.

**MadGraph artifacts → `/mg-probe`.** Invoke the `/mg-probe` skill for the matrix-element and integrated-σ checks, with the assembled commands, the question, the agent returns, and an expectation list. The list must carry at least one **target-derived** expectation — what a *correct* setup for the question produces, computed from Stage 1's regime independently of the assembled spec. Examples:
- *"The integrated σ from the SM template is within X% of the literature NNLO (e.g. `t t̄` @13 TeV ≈ 832 pb); a factor-1.5–2 gap means the NNLO k-factor was missed."* (target-derived)
- *"`matrix1.f` contains only the intended operator's `GC_` couplings and pure QCD — no four-fermion `GC_` from the DIM64F* blocks leaked in."* (target-derived)
- *"A small-statistics validation `launch` of the scan point survives without a multi-channel crash."* (spec-derived sanity)

The `/mg-probe` skill carries the expectation discipline, the dispatch shape, and the boundary rules (probe ≠ doc/source overrule; absence of deviation ≠ correctness). Attach the **sf-deep-verify line** to the `ma-probe` dispatch.

**Non-MadGraph artifacts → inline checks.** Two checks the probe skill does not cover, run inline:
- **κ-fit residuals** — recompute the polynomial fit from the scan output and check the residual pattern (R² > 0.999, no systematic structure, `a₀` consistent with the independent SM prediction). Routes through `sf-kappa-extractor` + `ma-numerics-reviewer` if not already settled in Stage 2.
- **Datacard load** — load the assembled JSON with `ReadDataCard`; it **must succeed**. A load failure, a length-mismatch error, or a missing-ID error is a finding.

Findings from both channels flow into Stage 5 alongside the streams from Stages 2-3.

## Stage 5 — Reconcile

Findings from four streams:

- **Stage 1** — regime classification (which operators/truncation, normalization, perturbative order, and which concerns the physics makes load-bearing).
- **Stage 2** — per-concern verdicts (each concern-item labelled APPROVED / NEEDS REVISION / WARNING by its routed verifier).
- **Stage 3** — dispatched-agent findings (from blind-spot follow-up re-verifications).
- **Stage 4** — probe deviations (per supplied expectation, per probe-derived expectation) + the inline κ-fit and `ReadDataCard` results.

Cross-reference the regime classification against the agent trail. A regime-implicated agent not in the trail is itself a finding (a routing failure caught in deep mode); engage the missing agent — e.g. a normalized observable whose luminosity-cancellation was never checked, or an operator named in Stage 1 never confirmed zeroed.

Walk every finding. Each gets one verdict:

- **revise** — change the deliverable value (re-engage the owning agent in revise-mode). Default action on NEEDS REVISION.
- **re-engage** — dispatch the owning agent for resolution.
- **dismiss** — with an explicit one-sentence reason.

**A WARNING is never resolved by your own adjudication.** A WARNING flags an open question a verifier could not decide — a methodological convention with more than one defensible form (which truncation, which side the scale uncertainty attaches to), an ambiguity in what the user asked for, or a load-bearing input that cannot be verified here. You may not settle it by applying the verifier's suggested alternative, and you may not dismiss it as your own call. Route it: **re-engage** the agent that owns the question, or — when the WARNING concerns what the user asked for — re-read the user's request and resolve against that. Only the owning agent's resolution, or the user's explicit request, turns a WARNING into a revise or an APPROVED-equivalent.

No "noted-but-shipped" action. Caveats live in `sf-reinterpret`'s reconciliation step. Every NEEDS REVISION not revised carries a written dismissal reason.

### Synthesis verification (before applying a substantive revision)

Discriminate:

- **Trivial** (skip verification): a single verifier's specific fix; an arithmetic correction; a value change a single agent explicitly authored. The "synthesis" is verdict routing.
- **Substantive** (verify): the revision combines findings from multiple streams; a truncation or operator-set change; a value change with non-trivial physics implications (a k-factor that shifts every bin, a normalization reclassification); the conclusion is your interpretation rather than any single stream's verdict.

For substantive syntheses, dispatch the layer-reviewer for the synthesis's layer — `ma-physics-reviewer` for an EFT-framing synthesis, `ma-numerics-reviewer` for a recomputation synthesis, `sf-reviewer` for a reinterpretation-concern synthesis. The dispatch carries each underlying finding as a marked premise, the synthesis as the claim to verify, the explicit ask *"Verify the synthesis, or propose an alternative that preserves the original deliverable,"* and the **sf-deep-verify line** verbatim.

If APPROVED: apply the revision; proceed to Stage 6.
If NEEDS REVISION / WARNING / alternative proposed: do not apply; re-enter Stage 5 with the new finding; re-triage.

### Wiki updates

When during reconcile you notice an agent's wiki claim is contradicted by a Stage 2 / 3 finding for this input, the only mechanism is **`Agent` dispatch to the owning agent** with an update-mode prompt (per `lead-discipline.md` "Content boundary"). It invokes `ma-wiki-write` itself on its own subtree — you do not write or edit an agent's pages directly, ever. For lead-side findings (a dispatch-level surprise), invoke `ma-wiki-write` on `/agent_wikis/lead/` per your wiki discipline; Stage 7's failure-mode extraction is the structured channel for behavioural-mistake candidates.

## Stage 6 — Re-verify on revision (conditional)

**Fires whenever Stage 5 applied a revision.** A revised deliverable is unverified — the streams that produced findings verified a deliverable that no longer exists. Before composing the answer, re-enter the cascade with carry-forward:

| Stream | Re-run? | Reason |
|---|---|---|
| Stage 1 — regime | NO | The regime is a property of the input (measurement + operators + truncation), not of the deliverable. |
| Stage 2 — concerns | PARTIAL | Re-check only the concerns the revision touched; verdicts on unchanged concerns carry forward. (A k-factor revision re-fires §4 and §8; an extraction-pointer fix re-fires §1-3 and §8.) |
| Stage 3 — blind-spot | YES | New deliverable → new unverified regions; the auditor triages the actual revised artifact. |
| Stage 4 — probe | YES | New numbers → new matrix elements, fit output, datacard; re-grep, re-fit, re-load. |

Re-enter Stage 5 with the merged findings (carried-forward verdicts + new findings); re-triage. If Stage 5 applies another revision, Stage 6 fires again — there is no cap. The carry-forward is what makes re-verification affordable.

### When the cycle does not converge

If a revised deliverable keeps producing new revisions across rounds without settling, the issue is not at the parameter level — it is an observable-classification, operator-set, or methodology problem that `sf-deep-verify`'s internal cycle cannot fix. **Escape upward, not by accepting a caveat.** Hand back to the conductor (`sf-reinterpret`, or the owning sub-skill — `sf-extract` / `sf-sm-template` / `sf-parameterize` / `sf-datacard` — at its spec-construction level) with: the persistent finding, the revisions tried, and an explicit ask to re-engage at the construction level. The escape is structural, not a deadline.

## Stage 7 — Failure-mode extraction (always fires)

After Stage 6 has fired all its cycles (or after Stage 5 if Stage 6 did not fire), and **before composing the answer**, dispatch `ma-failure-mode-extractor` with the cascade trail (regime, agent trail summary, per-concern verdicts from Stage 2, blind-spot findings, probe deviations + inline κ-fit/`ReadDataCard` results, Stage 5 reconcile decisions, Stage 6 cycles if any). Dispatch prompt ends with the **sf-deep-verify line**. The extractor returns a structured list of candidates — agent-system mistakes the cascade surfaced. One occurrence is enough; no recurrence gate.

A candidate names: the owner (a memory-carrying agent, or `lead`), the behavioural mistake, the trigger condition, the correct behaviour, the cascade evidence, and a recommendation (ADD a new page / UPDATE an existing page / DEFER).

For each candidate:

- **Owner is a memory-carrying agent** (a doer / worker / advisor) → dispatch it in update-mode with the candidate fields; it invokes `ma-wiki-write` to write a page in its own subtree with a description naming the recurring mistake (single-writer-per-page; the lead never writes an agent's page).
- **Owner is the lead** → the lead invokes `ma-wiki-write` itself on `lead/` with a description naming the dispatch-level mistake.
- **A reviewer is never the owner.** Reviewers are memoryless by design (adversarial freshness — no wiki, no slate). A mistake a reviewer *surfaced* is recorded against the **doer whose behaviour must change**; a reviewer's own *coverage gap* — a check it missed or a criterion it misapplied — is recorded as a **lead-side coverage note** the lead compensates for on the next dispatch, never in a reviewer subtree.
- **DEFER** → record nothing; the candidate was not durable enough.

The extraction step does not change the deliverable, does not produce caveats, and is independent of whether the cascade closed cleanly. A clean cascade typically produces zero candidates; a cascade with revisions produces 0-2. Over-recording is the failure mode of this stage itself — discipline against it lives in the extractor's card.

This stage is the wiki-side counterpart to the deliverable-side reconciliation: Stage 5 fixes the answer; Stage 7 records the lesson so future sessions of the same agent do not need the same fix.

## After sf-deep-verify

Hand back to `sf-reinterpret`'s reconciliation step (or to the user directly if `sf-deep-verify` was invoked post-shipping) with the verified deliverable, the verified findings, and any caveats from dismissed-with-reason findings. Caveats are surfaced; defects shipped without resolution are not.
