# SFitterAgents

SFitter is a tool for **reinterpreting experimental measurements as SMEFT
constraints**. Given a published measurement, it builds a fit-ready datacard with
parameterized Wilson-coefficient predictions and runs the SFitter likelihood to
turn the measurement into limits on effective operators.

The prediction templates it fits are produced with MadGraph (via SMEFTatNLO), and
the setup/automation is driven by the companion **MadAgents** project:

- MadAgents: <https://github.com/MadGraphTeam/MadAgents>
- SFitterAgents: <https://arxiv.org/pdf/2607.22813>