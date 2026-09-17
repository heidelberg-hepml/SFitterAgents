# Truth sources — verify per input

When your card or the lead's appended prompt names a primary truth source (MadGraph source code, first-principles physics, runtime artefacts, authoritative literature — depends on your role), that source is the **only** evidence for your claims. Memory is not a truth source. Pretrained recall is at best a hypothesis; verify it against the source before treating it as evidence.

- **Verify against your truth source for THIS input every time** — by walking / deriving / probing, OR by adopting a scope-matching cached finding per `ma-wiki-as-evidence`. Don't describe the canonical case and assume it applies.
- **Don't pattern-match from analogous cases.** Different inputs have different answers; verify.

## What counts as source

MadGraph's behaviour is determined by code + config files together. Both are source. The Python and Fortran files under `$MADGRAPH_INSTALL/` are source; so are the config and data files MadGraph reads — model `restrict_*.dat`, UFO `parameters.py` / `couplings.py` / `vertices.py`, generated `param_card.dat` / `run_card.dat`, generated-tree files (`configs.inc`, `decayBW.inc`, `matrix1_orig.f`, etc.). The principle: anything MadGraph reads to determine behaviour for this input is source. Examples are illustrative, not exhaustive.

A claim about config-file content is a source claim. Answering from recall about what a restriction file "usually" does, or what defaults a model "typically" carries, is not verification — read the file.
