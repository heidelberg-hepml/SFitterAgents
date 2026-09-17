# SFitter Documentation

Reference material for the SFitter JSON data format used in global SMEFT fits.

## Contents

| File | Description |
|------|-------------|
| [01_json_schema.md](01_json_schema.md) | Complete JSON schema: observations, predictions, modifiers. Field-by-field reference with examples from actual data files |
| [02_modifier_types.md](02_modifier_types.md) | All modifier types (pois, stat, syst, theo), naming conventions, SFitter uncertainty categories, ID encoding |
| [03_predictions_format.md](03_predictions_format.md) | Wilson coefficient predictions: linear, quadratic, and interference terms. Operator naming conventions |
| [04_integration_plan.md](04_integration_plan.md) | What the agent delivers for one measurement: the observation + prediction JSON entry, where each field comes from, formatting requirements, and a worked example |
| [05_uncertainty_catalog.md](05_uncertainty_catalog.md) | Complete catalog of all 66 SFitter-recognized uncertainties by type, with extraction priority and processing formulas |
| [06_id_naming_convention.md](06_id_naming_convention.md) | The `ocfkkxe[_b]` ID encoding scheme for SFitter observations: position-by-position lookup tables, channel-dependent `f` and `kk` codes, worked examples from real datasets, ID construction algorithm, validation rules |

## Source Material

- `$SFITTER_INSTALL` — the SFitter codebase, i.e. the `sfitter` package (`/opt/sfitter` in the container)
- `$SFITTER_INSTALL/data/` — Example JSON data files. **Canonical (source of truth):** `Top_Full.json` (top sector), `Higgs_Full.json` (Higgs sector). `new_likelihood.json` is a **deprecated** older dialect (flat observation `data`, `_lin`/`_quad`/`_interf` names) that `ReadDataCard` no longer accepts — do not use it as a template.
- The original SFitter naming convention and uncertainty index documentation
  has been fully mirrored into the files above. The agent system
  does NOT depend on any external documentation directory at runtime — every
  piece of information needed to construct or validate an SFitter JSON
  is contained in this `docs/sfitter/` directory.
