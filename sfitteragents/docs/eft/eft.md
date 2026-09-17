# EFT Documentation

Curated reference material for SMEFT parameterization workflows.

## Contents

| File | Description |
|------|-------------|
| [01_eft_fundamentals.md](01_eft_fundamentals.md) | EFT basics: separation of scales, power counting, matching, SMEFT Lagrangian, Warsaw basis, dimension-6 truncation, linear vs quadratic contributions, operator bases, UFO models, Wilson coefficient conventions |
| [02_operator_catalog.md](02_operator_catalog.md) | Complete dimension-6 Warsaw basis operator catalog organized by sector: top, Higgs/EW, four-fermion. Includes definitions, CP properties, process mappings, and flavor symmetry assumptions |
| [03_parameterization_methodology.md](03_parameterization_methodology.md) | EFT fitting methodology: kappa parameterization, normalized distributions, extracting coefficients from simulations, interference terms, uncertainty treatment, k-factors, SFitter workflow |
| [04_smeftatnlo_pitfalls.md](04_smeftatnlo_pitfalls.md) | **SMEFTatNLO parameter card hygiene**: the default-nonzero operator trap (DIM64F contamination), the QED=0 filter mechanism, defensive zeroing pattern, matrix-element verification, convention mismatch with LHC-TOPWG, truncation residuals |

## Key References

1. Grzadkowski, Iskrzynski, Misiak, Rosiek, "Dimension-Six Terms in the Standard Model Lagrangian," JHEP 1010 (2010) 085, [arXiv:1008.4884](https://arxiv.org/abs/1008.4884) — Warsaw basis definition
2. Degrande, Durieux, Maltoni et al., [arXiv:2008.11743](https://arxiv.org/abs/2008.11743), [arXiv:2104.02723](https://arxiv.org/abs/2104.02723) — SMEFTatNLO UFO model
3. Brivio, [arXiv:1709.09735](https://arxiv.org/abs/1709.09735), [arXiv:2012.11343](https://arxiv.org/abs/2012.11343) — SMEFTsim UFO model
4. Aguilar-Saavedra et al., [arXiv:1802.07237](https://arxiv.org/abs/1802.07237) — dim6top UFO model
5. Giudice, Grojean, Pomarol, Rattazzi, JHEP 0706 (2007) 045, [arXiv:hep-ph/0703164](https://arxiv.org/abs/hep-ph/0703164) — SILH basis
