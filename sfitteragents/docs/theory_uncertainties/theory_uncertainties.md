# Theory Uncertainties in HEP Predictions

Reference material for estimating and implementing theory uncertainties in SMEFT fits.

## Contents

| File | Description |
|------|-------------|
| [01_scale_uncertainties.md](01_scale_uncertainties.md) | Renormalization and factorization scale uncertainties: physical meaning, 7-point variation, dynamic scales, correlation structure, limitations, Bayesian alternatives. **Practical**: MadGraph run_card setup, systematics module, per-bin envelope extraction, covariance matrix construction, HighTea/fastNLO usage, k-factor computation |
| [02_pdf_uncertainties.md](02_pdf_uncertainties.md) | Parton Distribution Function uncertainties: Hessian and MC replica methods, NNPDF/CT/MSHT, alpha_s, PDF-EFT interplay. **Practical**: LHAPDF Python API, MadGraph PDF reweighting, per-bin covariance construction (code), alpha_s variation recipe, PDF4LHC21 reduced set, cross-process correlations |
| [03_additional_uncertainties.md](03_additional_uncertainties.md) | Parton shower/matching, missing higher orders, parametric (m_t, m_W), EFT-specific (truncation, validity), MC statistics, combination methods. **Practical**: Pythia 8 ISR/FSR variations (config syntax), generator comparison setup, m_t shifts in MadGraph, MC stat estimation with N_eff, Barlow-Beeston, EFT truncation ratio diagnostic with iterative bin removal |

## Key References

1. Butterworth et al., "PDF4LHC recommendations," J. Phys. G 43 (2016) 023001, [arXiv:1510.03865](https://arxiv.org/abs/1510.03865)
2. de Florian et al., "Handbook of LHC Higgs Cross Sections: 4," CERN-2017-002, [arXiv:1610.07922](https://arxiv.org/abs/1610.07922)
3. Cacciari, Houdeau, "Meaningful characterisation of perturbative theoretical uncertainties," JHEP 07 (2011) 138, [arXiv:1105.5152](https://arxiv.org/abs/1105.5152)
4. Czakon, Fiedler, Mitov, "$t\bar{t}$ total cross section at NNLO," PRL 110 (2013) 252004, [arXiv:1303.6254](https://arxiv.org/abs/1303.6254)
5. Lafaye, Plehn, Rauch, Zerwas, "SFitter," EPJC 54 (2008) 617, [arXiv:0709.3985](https://arxiv.org/abs/0709.3985)
