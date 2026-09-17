# Reinterpretation pipeline and SFitter handles

## The tool
The framework this agent works in is **SFitter** (arXiv:0709.3985, 2208.08454, 2312.12502) — the name
used for the agent, its `sf-` layer, and the deliverable. Its implementation is the **`sfitter`**
Python package (the `sfitter` CLI; modules `datacard.py` / `ReadDataCard`, the fitters), which the
handles below point at.

## Pipeline
The EFT-reinterpretation pipeline — turning an experimental measurement into an SFitter datacard with kappa-parameterized predictions. Stages (each is an sf- workflow skill):

1. **Measurement extraction** — measured values, bin edges, per-bin per-source uncertainties, metadata (`sf-extract`).
2. **SM-prediction template** — the SM baseline at the correct perturbative order + the theory-uncertainty budget the fit sits on (`sf-sm-template`).
3. **EFT parameterization** — SMEFTatNLO Wilson-coefficient scans -> kappa_1/kappa_2 per bin + interference (`sf-parameterize`).
4. **Datacard assembly** — the SFitter JSON observation+prediction entry, validated against `ReadDataCard` (`sf-datacard`).

The overarching conductor is the `sf-reinterpret` skill; deep verification is `sf-deep-verify`. Every prediction is produced by running MadGraph through the inherited `mg-*` pipeline (`rules/mg-pipeline.md`), and all compute-heavy runs go through the `cluster-submission` skill.

Across all four stages the analysis maintains a paper-grade provenance record under `/output/documentation/` **as the work happens** — see `rules/sf-documentation.md` (the contract) and the `sf-document` skill (the procedure).

## Documentation library — `$SFITTER_DOCS`
`/sfitter_docs` is the curated documentation library for this layer. The `sf-*` agents treat it as their primary source (the analogue of `$MADGRAPH_INSTALL` source for the `ma-`/`mg-` slices). Sub-trees: `eft/`, `sfitter/`, `measurement_extraction/`, `sfitter_methodology/`, `theory_uncertainties/`. Cite as `/sfitter_docs/<area>/<file>.md`.

## SFitter install — `$SFITTER_INSTALL`
The SFitter fitting tool (its `ReadDataCard`, the fitters) is installed in the container. Resolve it for the current environment:

```bash
echo "${SFITTER_INSTALL:-/opt/sfitter}"
ls -d /opt/sfitter /opt/envs/MAD/lib/python*/site-packages/sfitter 2>/dev/null | head -1
```

Use `$SFITTER_INSTALL/...` in citations; expand at the shell when reading a file. The assembled datacard JSON is consumed by SFitter's `ReadDataCard`; running the fit itself is a GPU job submitted via `cluster-submission`.
