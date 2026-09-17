# Rule — documentation fidelity: paper-grade provenance, built as you go

Every reinterpretation maintains a documentation tree at `/output/documentation/` **as the work
happens** — it is a deliverable produced during each phase, not a write-up at the end. **Success
criterion:** the tree, taken as the union of all its subfiles, carries in *information content*
everything needed to write a paper on the analysis — every number, figure, uncertainty term, and
methodological choice reconstructable from it alone, with no access to the conversation, the cluster
scratch, or agent memory. The bar is **information completeness, not prose**; writing the paper is a
separate task, out of scope here.

Layout, per-step contents, and templates live in the `sf-document` skill — this rule is the contract.

## Invariants
- **Execution may be ephemeral; provenance may not.** Debug and explore freely with throwaway one-offs
  (`python -c`, heredocs) — those need not be saved. But **no result the analysis keeps** — a card
  value, a processed input, a plot, a listed number, a chosen parameter — may come from ephemeral code.
  Before you adopt it, write the exact code to the bucket's `code/`, re-run it from that file, and adopt
  *that file's* output. A kept result with no re-runnable saved script behind it is a defect. The seam
  is **adoption**, not the tool: `python -c` while poking is fine; `python -c` behind a datacard value
  is not.
- **Immediate and additive.** Log a decision or a code change *when it happens*, not at the end. The
  step log is append-only: a superseded choice stays, marked `SUPERSEDED`; a failed experiment stays,
  marked `FAILED` with the reason. History is never rewritten — negative results are part of the record.
- **Never stale.** If a script changes, its saved copy *and* its md note change in the same action. A
  doc describing code that no longer matches what ran is a defect.
- **Every decision has provenance.** Agent decisions *and* user decisions are both logged, each with
  its reasoning and source. Every uncertainty term that reaches the final datacard names its source.

## Not the wiki
The documentation tree is **this analysis's provenance** (facts about THIS run, reproducibly). The
two-tier wiki/MEMORY (`/agent_wikis/`, `/output/.claude/.../MEMORY.md`) is **agent-system learning**
(generalizable lessons for the next run). Keep them disjoint: analysis logs never go in the wiki, and a
wiki lesson never substitutes for a documented decision.

## Hard gate
No phase is complete — and no datacard or fit ships — until its documentation bucket (`code/` +
`<bucket>.md`, current and matching what actually ran, every kept result backed by a re-runnable script)
exists. `sf-reviewer`'s documentation concern is the reviewable check; the terminal skills (`sf-datacard`,
`sf-fit`) block on it. Layout, templates, per-step checklists, and the pre-ship audit are in the
`sf-document` skill.
