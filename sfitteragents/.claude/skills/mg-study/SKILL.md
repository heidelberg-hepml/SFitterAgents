---
name: mg-study
description: Warm-up by phased source scan — study a topic of MadGraph (`/mg-study NLO`, `/mg-study decays`) or, bare, each consultant's core area, ahead of any task. Dispatches the relevant consultants to scan their slice in four phases (explore → physics → gaps → cautions), caching facts-with-provenance and flagging probe-candidates; cheap probes confirm comprehension inline, expensive ones are proposed for confirmation. Refines per-slice routing in the agent descriptions and cross-slice seams in the lead wiki. User-invoked warm-up between tasks; not auto-invoked, does not answer physics questions (that is `/mg-setup`).
---

# `/mg-study [topic]`

`/mg-study` is a **warm-up** skill: it scans MadGraph source ahead of any task and caches what it finds, so the agent enters later work already knowing its way around — instead of accumulating knowledge only as a byproduct of answering questions. Invoke it deliberately between tasks. It is not auto-invoked.

`/mg-study NLO`, `/mg-study decays`, `/mg-study the EFT machinery` — study a topic. Bare `/mg-study` — each consultant studies its own core area.

## Orchestration

Same shape as `/ma-wiki-lint`: dispatch the relevant consultants in parallel, each into its own `consultants/<agent-name>/` subtree; run the lead's own pass on `lead/`; aggregate.

- **Topic given** — dispatch the consultants that own the topic (NLO → `nlo-syntax`, `amcatnlo`, `nlo-export`, `madloop`, `fks`, `nlo-model`; decays → `chain-decay`, `madwidth`, `madspin-interface`, `bw-window`). Route by slice ownership as for any dispatch.
- **No topic** — dispatch each consultant to study its own core source areas (the ones its card lists under "Source code areas").

## Per-consultant dispatch — four phases

Each consultant, dispatched on its own subtree, first **reads its existing pages** (always gap-aware: add what is missing, extend what is thin, correct what source now contradicts; never duplicate). Then it works the area through four phases, by reading source:

1. **Explore** — locate the relevant files and functions; record paths and structure.
2. **Physics** — extract what the code computes and the physics/algorithm it encodes. Understanding, not paraphrase.
3. **Gaps** — record what cannot be settled from source alone.
4. **Cautions** — flag source-visible hazards: a default that assumes a regime, a silent fallback, a code path that drops a contribution. A caution is a pointer ("watch out for X here"), not a claim about the runtime outcome.

### What each phase records

- **Facts** — input-independent and statically verifiable: files scanned, verbatim content, file:line citations, what the code computes as readable from source, and cautions grounded in a visible default. Cache at confidence. A study page is a cited source record of your slice, not advice.
- **Probe-candidates** — any *runtime* prediction or open question a phase raises (a comprehension prediction "this should produce …"; a gap "can't tell from source whether …"; a caution's runtime consequence "this may silently give …"). A runtime claim is **never** cached as fact from reading alone.

Do **not** author implications (regime-specific recommendations, "for input X use Y"): they need a real input and are `/mg-setup` work, not scan output.

### Probing during the scan

A probe is always tied to a **named candidate** — a prediction (phase 2), a gap (phase 3), or a caution's runtime consequence (phase 4). If you cannot say in one line what the probe would tell you, do not run it — that rules out aimless launching, not probing a gap you have named. Cheap vs. expensive is the threshold `/mg-probe` already defines on its card: quick parse-time checks and small-statistics local launches are cheap and run inline; anything its card treats as a long-running launch is **expensive** — do **not** run it yourself, list it in your return, one line each (what it would tell you). **Any probe result you did not predict becomes a new gap or caution.** Cache confirmed facts; write any unconfirmed runtime claim as **hypothesis**, or leave it as a caution.

Return a **description-level summary of what you now hold** (page slugs + one line each) plus your list of expensive probe-candidates.

## Lead pass — routing and the probe gate

After the consultants return:

1. **Routing.** Fold what you learned about who-owns-what into the two routing homes (per `lead-discipline.md`): refine the `description` of each consultant you dispatched this pass (the per-slice routing surface — `description` field only, never the body, ≤ ~800 chars, supersede in place), and write or update a per-seam `lead/` page for any cross-slice seam, multi-slice fan-out, or dispatch ordering you found. Dispatch behaviour, not MadGraph facts (those stay in the consultant subtrees). Do not build a single combined routing-index.
2. **Expensive-probe confirmation.** Collect the expensive probe-candidates the consultants flagged. Propose the batch to the user (one line each); run only the approved ones by re-dispatching the owning consultant with `/mg-probe` and a physics-anchored expectation, then fold the confirmed facts back in. When no user is present, apply your token budget in place of asking. Cheap source work and cheap probes proceed on invocation; expensive runs wait for a go-ahead.

## Final phase — verify write locations

A consultant's slate is read only from `/output/.claude/agent-memory/<agent-name>/MEMORY.md`; a slate written under the wiki (`/agent_wikis/`) is never loaded, so its content is silently inert. After aggregating, the lead audits the writes:

1. `find /agent_wikis -name MEMORY.md ! -empty` returns nothing. A hit is a consultant that wrote its slate relative to its wiki subtree instead of the project-root path.
2. Each consultant dispatched this run has a non-empty slate at `/output/.claude/agent-memory/<agent-name>/MEMORY.md`.
3. Consultant pages sit under `/agent_wikis/consultants/<agent-name>/`, lead pages under `/agent_wikis/lead/`.

For any populated slate found under `/agent_wikis`: move it to the project-root path when that copy is missing, otherwise delete the stray; then re-dispatch the owning consultant to write its slate to the project-root path. Report what was checked and corrected.

## Boundaries

- **Facts and cautions, not implications.**
- **Single-writer-per-page.** Each consultant writes only its own subtree; you write only `lead/`.
- **Gap-aware always.** Existing pages are read before writing; study extends and corrects, never duplicates.
- **Warm-up, not task work.** `/mg-study` primes knowledge between tasks; it does not answer a user's physics question — that is `/mg-setup`.
