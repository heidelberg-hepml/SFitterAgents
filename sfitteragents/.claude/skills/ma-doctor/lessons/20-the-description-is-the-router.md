# 20 — The description is the router

> A card's description is the lead's routing key *and* a standing token cost paid on every request. The same field carries both pressures at once.

Under progressive disclosure only a card's name and description are loaded at decision time, so
description quality directly determines whether the right specialist gets picked. The discipline
is two-sided: over-list the synonyms and intents that should reach it ("better to over-list than
under-list"), *and* keep its boundary distinct from siblings so one request doesn't fire two
agents. But that same description is injected into the system prompt on every single request,
dispatched or not — so it must also earn its standing tokens. A long roster is itself a cost:
more entries means more tokens every turn and higher odds of a wrong pick.

**In a harness like this.** The agent card descriptions are the lead's routing keys *and* an
unconditional standing cost paid every request. The actionable form is description discipline:
tight, high-value-per-token, self-disambiguating descriptions (rich-but-disjoint). This licenses
tightening *what each description says*, not speculatively thinning the roster — a cut specialist
surfaces as a first-use failure that is hard to detect.

## Where the books say it

- **Agent Skills** — ch6/ch2/ch5/ch7. The `description` *is* the router: over-list synonyms, but tighten trigger conditions and reduce overlap — don't let one keyword trigger two skills.
- **Codex Complete Guide** — §08. Description quality directly determines whether a skill is triggered correctly — it is the routing surface, not documentation.
- **OpenClaw: The Complete Guide** — §19/§21/§30. Descriptions of all skills are injected into the system prompt every request, so each additional skill lengthens that prompt and eats context window — the standing token cost.
- **Obsidian AI: The Complete Guide** — §05 P4. The per-page form: a 30-80-char `summary` lets the agent judge relevance without reading the full text.
- **Hermes Agent** — §09/§11. A long roster is itself a cost — the more tools on offer, the likelier the model picks the wrong one.
- **Claude Code Source-Code Analysis** — token-frugality section. Minimal always-on roster — the always-on agent descriptions are the main always-on cost; the levers that hold regardless are shorter descriptions and fewer always-on agents.
