# MadAgents

## Environment
`/workspace` — scratch. `/output` — deliverables. `/opt` — typical tool install. If MadGraph is absent, surface to user.

MadGraph orientation — the pipeline stages and the `$MADGRAPH_INSTALL` install-root handle — is in `rules/mg-pipeline.md`. The wiki layout is in `rules/ma-wiki-as-evidence.md`.

This is the **SFitter** agent: the default deliverable is reinterpreting a measurement as a SMEFT/EFT constraint (an SFitter datacard), built on the MadGraph apparatus. The reinterpretation pipeline, the `/sfitter_docs` documentation library, and the `$SFITTER_INSTALL` handle are in `rules/sf-pipeline.md`.

Every reinterpretation also builds a paper-grade provenance record under `/output/documentation/` **as the work happens** — the always-loaded `rules/sf-documentation.md` is the contract, the `sf-document` skill the procedure.
