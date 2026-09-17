# A run's outcome is not evidence

A MadGraph run's surface outcome — that it ran and gave a number, or that it balked — is not, by itself, evidence. Evidence is the substance: the physics observable a result implies, or the source and alternatives behind a claimed limitation. This binds whoever handles the result — a consultant evaluating its own slice's output, and the lead reconciling the whole spec.

## A clean run is not evidence of correct physics

A clean exit, an output directory, a finite cross-section prove only that MadGraph found *something* to compute — never that it computed the thing the physics asked for. MadGraph validates syntax, model-consistency, and numerics; it does not validate intent.

Before offering a result as evidence, name the observable that would distinguish a right setup from a wrong one, and check it:

- the cross-section against a *consistent* baseline — a collapse of orders of magnitude, or degeneracy across configs that should differ;
- a partial width or branching ratio — BR ≤ 1; a microscopic partial width or BR ≈ 0 is the silent-fail fingerprint of a zeroed coupling;
- the diagram topology — is the generated amplitude the requested observable, or does it carry a contaminating topology or a silently-dropped sub-decay;
- order / sign parity for an EFT polynomial piece.

Each agent checks the invariant *its own* result implies; these are illustrations, not a closed list.

The shortcut this forbids: **"it ran / it generated / it gave a σ, so it is right."** A successful run is the start of verification, not the end of it. Naming the check is cheap; dispatch the expensive confirmation (a probe, an owning-slice walk) only when the result is load-bearing.

## A dead-end is not evidence of impossibility

"It got rejected" or "I cannot see how" is not "it cannot be done." Apparent inability to deliver is a fact to investigate, not a verdict to accept: search for the model, plugin, syntax, UFO, or PDF set that unblocks it, and verify candidates against source. Declare "this cannot be done" only with evidence — a reproduced rejection, or an alternatives search that came up empty.

The shortcut this forbids: **"my first approach failed, so it is unsupported."**
