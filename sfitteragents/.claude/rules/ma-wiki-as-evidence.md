# Wiki and MEMORY.md as evidence

## Wiki layout
Persistent notes tree at `/agent_wikis/`:

```
/agent_wikis/
  consultants/<agent-name>/   # each consultant owns + writes its own; one subdir per agent
  lead/                        # private to the orchestrator; flat (no subdirs)
```

Subtree naming is **literal** — `<agent-name>` is the consultant's exact agent filename (without `.md`), suffix and all (e.g. `consultants/ma-bw-window-consultant/`, not `consultants/bw-window/`). Each consultant's own card states which subtree it owns. Single-writer-per-page is preserved; no consultant reads another consultant's subtree. Use `$MADGRAPH_INSTALL/...` in wiki citations rather than hardcoded install paths. Wiki linting (`/ma-wiki-lint`) is **user-invoked only** — do not auto-invoke at session start or end.

## Adopting wiki content as evidence
Your wiki's source-derived content is evidence for the input it explicitly covers. If a page's scope matches your input, adopt its findings — you do not need to re-walk source. Verify one cited file:line still resolves as a sanity check.

Your auto-loaded MEMORY.md's "Recent lessons" are evidence the same way: a lesson whose trigger matches your input applies.

Do NOT extrapolate. A page or lesson about configuration X is evidence for X, not for similar-X. If your input doesn't match the scope, walk source.

If your dispatch explicitly instructs adversarial verification (e.g. "mg-deep-verify dispatch: wiki and Recent lessons as orientation only"), comply — the cascade is doing the verification, not the cache. Your MEMORY.md's "Slice" and "Core operating principles" sections stay active (they're meta-discipline, not claims); the "Wiki page index" stays as navigation. Only the "Recent lessons" demote to orientation-only alongside the wiki bodies.
