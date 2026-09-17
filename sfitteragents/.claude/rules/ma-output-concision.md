# Output concision — return what's load-bearing, nothing else

Your return is read once by the lead and then lives in the conversation forever, costing cache-reads on every subsequent turn. Write only what carries the finding.

- **State the finding.** Don't restate the dispatch context or recap your slice.
- **Cite, don't narrate.** `<path>:<line>: <one-line claim>` beats *"I walked banner.py and observed that around line 4305 the bwcutoff is registered with default 15, which I confirmed by reading the surrounding context where the registration pattern matches…"*
- **Implications: 1-3 sentences.** Name the recommendation and its key caveat. Skip motivation, alternatives-considered, and meta-commentary about your confidence.
- **No filler.** No "I hope this helps," no "let me know if you need more detail," no preamble or close.
- **No padding between bullets.** A bulleted list is the structure; the bullets are the content.

The two-section return contract (`## Source-walked facts` / `## Implications`) and the slice-rejection contract (`## Rejected (out-of-slice)`) are unchanged — this rule governs how much you write inside each section, not the section structure itself.

This rule applies to subagent returns to the lead. The lead's final answer to the user follows the `mg-setup` reconciliation format and is not bound by this rule.
