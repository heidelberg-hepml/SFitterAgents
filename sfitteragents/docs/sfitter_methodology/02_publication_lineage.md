# SFitter Publication Lineage

Evolution of the SFitter SMEFT program from SUSY parameter fitting to global SMEFT analyses.

---

## Phase 1: SUSY Era (2004-2013)

### arXiv:hep-ph/0404282 — "SFITTER: SUSY parameter analysis at LHC and LC" (2004)
- First SFitter implementation for MSSM parameter determination
- Demonstrates LHC + linear collider complementarity

### arXiv:0709.3985 — "Measuring Supersymmetry" (2007)
**The foundational SFitter paper.**
- Introduces the **weighted Markov chain** MCMC technique
- Establishes the **RFit scheme** (flat theory uncertainties)
- Implements both profile likelihood and Bayesian marginalization
- Demonstrates reconstruction of MSSM Lagrangian from simulated LHC data
- Multi-modal exploration for discrete ambiguities

### arXiv:1309.6958 — "Constraining Supersymmetry with Planck" (2013)
- SFitter applied to MSSM with 13 free parameters
- Combined LHC + Planck + Xenon100 constraints
- Demonstrates SFitter's scalability to large parameter spaces

---

## Phase 2: Higgs EFT Era (2015-2018)

### arXiv:1505.05516 — "The Higgs Legacy of the LHC Run I" (2015)
**First SFitter SMEFT analysis.**
- Transition from SUSY to EFT/SMEFT
- ~10 Wilson coefficients in Higgs sector
- Dataset: ~60+ signal strengths from ATLAS + CMS Run I
- Demonstrates equivalence of coupling modifier and EFT approaches for rates
- Shows kinematic distributions break degeneracies that rates alone cannot
- Dimension-6 squared terms included (and shown to be important)
- Run I reach for new physics: 300-500 GeV

### arXiv:1511.08188 — "The Non-Linear Higgs Legacy" (2015)
- Extends linear (dim-6) results to non-linear EFT framework
- Demonstrates formal relationship between SMEFT and HEFT

### arXiv:1812.07587 — "The Gauge-Higgs Legacy of the LHC Run II" (2018)
- ~14-20 Wilson coefficients (expanded from Run I)
- Adds diboson differential distributions (WW, WZ high invariant mass tails)
- STXS framework for Higgs measurements
- CP-violating operators added
- Factor 2-5 improvement over Run I
- Demonstrates importance of high-energy tails for anomalous gauge couplings
- Identifies blind directions in Wilson coefficient space

---

## Phase 3: Top Sector SMEFT (2019-present)

### arXiv:1910.03606 — "O new physics, where art thou?" (2019)
**Foundational top-sector SMEFT analysis.**
- 22 Wilson coefficients (Table 2.2 in Schmal thesis)
- Comprehensive Run II top dataset: $t\bar{t}$ total + differential, single top, $t\bar{t}V$, $tZq$, top decay
- Four-fermion operators: 14 operators in three chirality classes (LL, RR, LR)
- NLO QCD via SMEFTatNLO, NNLO SM via fastNLO
- NNPDF3.1 NLO PDFs
- Theory uncertainties: scale, PDF, generator, top mass
- Key result: $C_{tG}/\Lambda^2 \in [-0.08, 0.07]$ TeV$^{-2}$
- Four-fermion operators constrained from high-$m_{t\bar{t}}$ tails
- DataPrep tool for systematic uncertainty preparation

### arXiv:2108.01094 — "From Models to SMEFT and Back?" (2021)
- SMEFT matched to UV-complete triplet model at one loop
- Demonstrates pattern of Wilson coefficients from specific UV models
- Theory uncertainties from matching procedure
- Shows complementarity between SMEFT and model-specific analyses

### arXiv:2208.08454 — "To Profile or To Marginalize" (2022)
**Critical methodological paper.**
- First Bayesian marginalization implementation in SFitter
- Higgs/Di-Boson/EWPO dataset: ~17 operators in HISZ basis
- Systematic comparison: profiling vs marginalization give different results with flat theory uncertainties
- Theory uncertainties 20-25% for top (dominant!) vs 5-10% for Higgs
- Key finding: RFit (flat) vs Gaussian theory uncertainties changes constraints significantly in top sector
- Updated dataset with new kinematic measurements

### arXiv:2312.12502 — "Staying on Top of SMEFT-Likelihood Analyses" (2023)
**The current state-of-the-art SFitter analysis. Schmal thesis paper.**
- **Combined fit**: 38 Wilson coefficients (22 top + ~17 Higgs/EW + BR_inv)
- Updated top dataset: new CMS $m_{t\bar{t}}$ (137 fb$^{-1}$, 15 bins to 3500 GeV)
- First use of published ATLAS likelihoods (pyhf/HistFactory) in SFitter
- MadGraph 3.5.0 + SMEFTatNLO, NNPDF4.0 NNLO, HighTea for NNLO k-factors
- Dynamic scale: $\mu = (m_T(t) + m_T(\bar{t}))/2$
- Interference terms found too noisy for newly implemented measurements — neglected
- Theory uncertainties shown to be the limiting factor in the top sector

---

## Phase 4: Next Generation (2024)

### arXiv:2411.00942 — "Profile Likelihoods on ML-Steroids" (2024)
- Neural importance sampling to accelerate profile likelihood evaluation
- Full SFitter SMEFT likelihood evaluated in 5 hours on a single GPU
- Same dataset and methodology as arXiv:2312.12502

### arXiv:2406.19076 — "Refinable modeling for unbinned SMEFT analyses" (2024)
- ML surrogates for unbinned per-event likelihood
- 10-50% sensitivity improvement over binned analyses
- Systematic uncertainty modeling via tree-boosting
- Path toward optimal SMEFT analyses

### arXiv:2403.02052 — "A Global View of the EDM Landscape" (2024)
- Extension to CP-violating sector (EDMs)
- Multi-scale EFT matching: SMEFT → LEFT → hadronic
- Combines low-energy precision (EDMs) with LHC collider data
- Hadronic matrix element uncertainties as dominant theory uncertainty

---

## Methodology Evolution Summary

| Aspect | 2007 | 2015 | 2019 | 2022 | 2023 | 2024 |
|--------|------|------|------|------|------|------|
| Physics | SUSY | Higgs EFT | Top SMEFT | Profile vs Margin | Combined | ML + EDMs |
| Operators | MSSM params | ~10 dim-6 | 22 top | 17 Higgs/EW | 38 combined | 38+ |
| PDF | — | — | NNPDF3.1 NLO | — | NNPDF4.0 NNLO | NNPDF4.0 |
| NNLO | — | — | fastNLO | — | HighTea | HighTea |
| MadGraph | — | — | SMEFTatNLO | — | v3.5.0 | v3.5.0 |
| Statistics | Profile + Bayes | Profile | Profile | Profile + Bayes | Profile + Bayes | ML-accelerated |
| Theory unc. | RFit (flat) | RFit | RFit | Flat vs Gauss compared | RFit | RFit |
