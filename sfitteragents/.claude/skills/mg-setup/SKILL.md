---
name: mg-setup
description: Set up MG5_aMC for a physics request end-to-end — the default path for any task that builds or configures a MadGraph process or run. Use whenever the deliverable is an MG5 setup: the process line, model, parameters, cuts, scales, LO/NLO mode, decay chains, EFT orders, and so on. Frames the request, classifies the physics regime (which surface keywords routinely under-specify), builds the candidate via consultant dispatches, and reconciles against the physics-spec. Skip only for a pure source-mechanics lookup (dispatch the consultant directly) or a quick factual answer.
---

# `/mg-setup`

The setup workflow — the four-step sequence for building a MadGraph configuration. The orchestration disciplines it leans on are always-loaded, not restated here: dual-spec, regime classification, slice-boundary premises, whole-spec reconciliation, and revise-before-caveat live in `lead-discipline.md`; "a clean run is not evidence" lives in `rules/ma-outcome-not-evidence.md`. This skill is the setup-specific scaffold over them.

**Step 1 — Frame the physics-spec.** Capture the user's prompt verbatim (dual-spec discipline). If too vague to act, surface and ask.

**Step 2 — Classify the regime.** Classify the physics regime (regime-classification discipline) and route to the slices each regime implicates — sub-threshold parent → `ma-bw-window-consultant`; NLO bracket syntax → `nlo-syntax` + `amcatnlo` + `nlo-model`; EFT operators → `ma-eft-consultant`; and so on.

**Step 3 — Build the candidate.** Translate physics-spec + regime classification into a candidate MadGraph configuration. Dispatch the slices the regime named plus any others your reading requires; consultants author within slice, you conduct, iterate as returns reveal what's next.

The simulation-spec is what the configured artifacts *do*, not what you meant them to do, and this is exactly where the two silently diverge. A model name does not fix its vertices, a restriction card silently prunes couplings, a chain drops a sub-decay the parentheses never bound — each artifact is opaque until its owning slice reads it. So build every load-bearing choice on what the artifact actually carries, read by its owner, in **both directions**: a contribution the physics needs can be silently absent (a dead process, a removed coupling), and one you never intended silently present (a contaminating topology, an extra coupling). On a don't-run setup both are invisible until something is read.

The build is not done until each load-bearing choice is grounded in what its artifact does — never its name — and the candidate is coherent across stages.

**Step 4 — Reconcile and present.** Two checks before shipping:

- **Per-requirement.** Verify each requirement in the physics-spec is satisfied by the assembled simulation-spec, given everything else now in it.
- **Whole-spec.** Confirm the emergent cross-slice invariants the assembled spec implies (whole-spec reconciliation discipline) — by dispatch to the owning slices, not by eyeball.

Then ship per the revise-before-caveat discipline.
