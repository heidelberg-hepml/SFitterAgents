# MadGraph pipeline and install root

## Pipeline
Chain of transformations with load-bearing cross-stage interactions:

1. **Model loading** — `import model` (+ restriction).
2. **Process specification** — `generate / add process` (chain decays, coupling orders, filters, polarization).
3. **Diagram generation** — Feynman diagrams + matrix-element representation.
4. **Code output** — `output <dir>` → process directory.
5. **Card configuration** — `<PROC_DIR>/Cards/run_card.dat`, `param_card.dat`.
6. **Integration / event generation** — `launch` → phase space + LHE output.
7. **Downstream tools** — optional MadSpin / Pythia8 / Delphes / MadAnalysis5 / Rivet.

Orthogonal axes (NLO, matching, EFT, physics) cut across stages.

## Install root
`$MADGRAPH_INSTALL` is the named handle for the MadGraph install root used across this preset's agent cards, rules, skills, and wiki citations. To resolve it for the current environment, run one of:

```bash
echo "${MADGRAPH_INSTALL:-$(command -v mg5_aMC | xargs -r dirname | xargs -r dirname)}"
ls -d /opt/MG5_aMC /opt/mg5* /opt/MadGraph* ~/MG5_aMC* 2>/dev/null | head -1
```

In the apptainer image this typically resolves to `/opt/MG5_aMC`; other environments may differ. Use `$MADGRAPH_INSTALL/...` in citations; expand at the shell when actually reading a file.
