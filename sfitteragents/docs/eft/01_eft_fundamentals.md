# EFT Fundamentals and SMEFT

## 1. Effective Field Theory Basics

### 1.1 Separation of Scales

An Effective Field Theory exploits a hierarchy of energy scales. If the energy $E$ probed in experiments is much smaller than the scale $\Lambda$ of new heavy degrees of freedom ($E \ll \Lambda$), then the effects of the heavy physics can be parameterized as a series in $E/\Lambda$.

One "integrates out" heavy particles (masses $M \sim \Lambda$) from the full theory. Their effects are encoded in modified couplings and new higher-dimensional interactions among the remaining light fields.

### 1.2 The EFT Lagrangian and Power Counting

A generic EFT Lagrangian in 4D spacetime:

$$\mathcal{L}_{\text{EFT}} = \mathcal{L}_{\text{ren}} + \sum_{d > 4} \sum_i \frac{C_i^{(d)}}{\Lambda^{d-4}} \mathcal{O}_i^{(d)}$$

where:
- $\mathcal{L}_{\text{ren}}$: renormalizable part (operators of mass dimension $\leq 4$)
- $\mathcal{O}_i^{(d)}$: local operators of mass dimension $d$, built from light fields and respecting the symmetries of the low-energy theory
- $C_i^{(d)}$: dimensionless **Wilson coefficients** encoding UV physics effects
- $\Lambda$: **cutoff scale**, the characteristic mass scale of the integrated-out heavy physics

Operators of dimension $d$ contribute to amplitudes at order $(E/\Lambda)^{d-4}$. Higher-dimensional operators are progressively suppressed.

### 1.3 Matching

**Matching** determines the Wilson coefficients from a specific UV-complete theory. At a scale $\mu \sim \Lambda$, one computes the same observables in both the full theory and the EFT and demands equality:

$$\mathcal{A}_{\text{full}}(p, M, g) \bigg|_{p \ll M} = \mathcal{A}_{\text{EFT}}(p, C_i, \Lambda)$$

Matching can be performed at tree level or loop level. Tools: `matchmakereft`, `matchete`, `CoDEx`.

### 1.4 Validity Regime

The EFT is valid when:
- $E \ll \Lambda$ (the expansion parameter $E/\Lambda$ is small)
- Truncation at a finite dimension $d$ is justified
- Perturbative unitarity is not violated

At the LHC, individual events can probe $\sqrt{\hat{s}}$ approaching $\Lambda$, where the EFT may break down. This must be assessed case-by-case.

---

## 2. The Standard Model Effective Field Theory (SMEFT)

### 2.1 Definition

SMEFT extends the SM with higher-dimensional operators under three assumptions:
1. Gauge symmetry is $SU(3)_C \times SU(2)_L \times U(1)_Y$
2. Electroweak symmetry breaking is realized linearly (Higgs is an $SU(2)_L$ doublet)
3. The particle content below $\Lambda$ is exactly that of the SM

The SMEFT Lagrangian:

$$\mathcal{L}_{\text{SMEFT}} = \mathcal{L}_{\text{SM}} + \sum_{d=5}^{\infty} \sum_i \frac{C_i^{(d)}}{\Lambda^{d-4}} \mathcal{O}_i^{(d)}$$

In practice, truncated at dimension 6:

$$\mathcal{L}_{\text{SMEFT}} \approx \mathcal{L}_{\text{SM}} + \frac{1}{\Lambda} \sum_i C_i^{(5)} \mathcal{O}_i^{(5)} + \frac{1}{\Lambda^2} \sum_i C_i^{(6)} \mathcal{O}_i^{(6)}$$

### 2.2 Dimension 5: The Weinberg Operator

There is exactly **one** independent operator at dimension 5 (up to flavor indices):

$$\mathcal{O}_W = c_W \frac{(\bar{l}_p l_p)(\phi^\dagger \phi)}{\Lambda}$$

After EWSB, this generates Majorana neutrino masses $m_\nu \sim C^{(5)} v^2 / \Lambda$. It violates lepton number by $\Delta L = 2$.

### 2.3 Dimension 6: The Warsaw Basis

The complete non-redundant set of dimension-6 operators was established by Grzadkowski, Iskrzynski, Misiak, and Rosiek (JHEP 1010, 2010, 085; [arXiv:1008.4884](https://arxiv.org/abs/1008.4884)) — the **Warsaw basis**.

**Operator count:** In the general case with 3 generations and no flavor symmetry, there are **2499** independent baryon-number-conserving dimension-6 operators.

The Warsaw basis organizes operators into eight classes:

| Class | Schematic | Example |
|-------|-----------|---------|
| $X^3$ | Three field strengths | $\mathcal{O}_G = f^{ABC} G_\mu^{A\nu} G_\nu^{B\rho} G_\rho^{C\mu}$ |
| $H^6$ | Six Higgs fields | $\mathcal{O}_H = (H^\dagger H)^3$ |
| $H^4 D^2$ | Four Higgs, two derivatives | $\mathcal{O}_{H\Box} = (H^\dagger H) \Box (H^\dagger H)$ |
| $X^2 H^2$ | Two field strengths, two Higgs | $\mathcal{O}_{HG} = H^\dagger H \, G_{\mu\nu}^A G^{A\mu\nu}$ |
| $\psi^2 H^3$ | Yukawa-like | $\mathcal{O}_{eH} = (H^\dagger H)(\bar{L} e H)$ |
| $\psi^2 X H$ | Dipole operators | $\mathcal{O}_{eW} = (\bar{L} \sigma^{\mu\nu} e) \tau^I H W_{\mu\nu}^I$ |
| $\psi^2 H^2 D$ | Fermion-Higgs currents | $\mathcal{O}_{Hl}^{(1)} = (H^\dagger i \overleftrightarrow{D}_\mu H)(\bar{L} \gamma^\mu L)$ |
| $\psi^4$ | Four-fermion | $\mathcal{O}_{ll} = (\bar{L} \gamma_\mu L)(\bar{L} \gamma^\mu L)$ |

### 2.4 Why Truncate at Dimension 6

1. **Power suppression**: Dimension-8 operators are $\mathcal{O}(1/\Lambda^4)$ vs $\mathcal{O}(1/\Lambda^2)$ for dimension 6
2. **Experimental precision**: Most LHC measurements have $\mathcal{O}(10\%)$ uncertainties, sensitive to $1/\Lambda^2$ but typically not $1/\Lambda^4$
3. **Practical complexity**: Dimension 8 contains tens of thousands of operators
4. **SFitter convention**: Truncation at the Lagrangian level, removing dimension-8 contributions entirely

**Caveat**: There exist processes where dimension-6 contributions vanish by selection rules and dimension-8 provides the leading BSM effect.

### 2.5 Linear vs Quadratic Contributions to Observables

The amplitude with a dimension-6 operator insertion:

$$\mathcal{A} = \mathcal{A}_{\text{SM}} + \frac{C}{\Lambda^2} \mathcal{A}_{\text{BSM}}$$

The cross-section $\sigma \propto |\mathcal{A}|^2$ becomes:

$$\sigma = \sigma_{\text{SM}} + \frac{C}{\Lambda^2} \sigma_{\text{int}} + \frac{C^2}{\Lambda^4} \sigma_{\text{BSM}^2}$$

where:
- $\sigma_{\text{int}} \propto 2\,\text{Re}(\mathcal{A}_{\text{SM}}^* \mathcal{A}_{\text{BSM}})$: **linear** (interference) term, $\mathcal{O}(1/\Lambda^2)$
- $\sigma_{\text{BSM}^2} \propto |\mathcal{A}_{\text{BSM}}|^2$: **quadratic** term, $\mathcal{O}(1/\Lambda^4)$

The quadratic term is formally the same order as dimension-8 interference with the SM. A strict EFT expansion would drop it, but in practice **both terms are kept** because:
- The quadratic term ensures physical (positive) cross-sections
- For some operators, linear interference is helicity-suppressed and the quadratic term dominates
- Quadratic terms prevent flat directions in fits

With multiple operators, cross-terms appear:

$$\sigma \supset \frac{C_i C_j}{\Lambda^4} \sigma_{\text{interf},ij}$$

These **operator interference terms** are crucial for global fits.

### 2.6 Interference Subtleties

Interference between dimension-6 operators and the SM can be suppressed when:
- **Helicity selection rules** prevent it (e.g., in $gg \to HH$ via chromomagnetic dipole)
- **The SM amplitude is loop-suppressed** while the SMEFT amplitude is tree-level
- **CP structure**: CP-odd operators do not interfere with CP-even SM amplitudes in CP-symmetric observables

---

## 3. Operator Bases

### 3.1 Warsaw Basis (Standard)

**Reference**: Grzadkowski et al., JHEP 1010 (2010) 085, [arXiv:1008.4884](https://arxiv.org/abs/1008.4884)

- Complete and non-redundant (EOM, IBP, Fierz redundancies eliminated)
- Universally adopted by the LHC EFT Working Group, SMEFiT, fitmaker
- Standard for tool chains: SMEFTatNLO, SMEFTsim, WCxf, DsixTools
- Uses EOM to eliminate operators with derivatives on field strengths

### 3.2 SILH Basis

**Reference**: Giudice, Grojean, Pomarol, Rattazzi, JHEP 0706 (2007) 045, [arXiv:hep-ph/0703164](https://arxiv.org/abs/hep-ph/0703164)

- Power counting motivated by composite Higgs models
- Keeps operators involving $D^\mu(H^\dagger H)$ rather than using EOM to replace with fermion currents
- Contains redundant operators w.r.t. Warsaw basis
- Useful for theoretical analysis of composite Higgs, but Warsaw preferred for phenomenology

### 3.3 HISZ Basis

**Reference**: Hagiwara, Ishihara, Szalapski, Zeppenfeld, Phys. Rev. D48 (1993) 2182

- Predates complete SMEFT classification, focuses on bosonic sector (anomalous gauge couplings)
- Not complete for full dimension-6 SMEFT
- Appears in legacy LEP analyses, superseded by Warsaw for modern work
- Translation dictionaries exist to convert to Warsaw basis

### 3.4 Basis Translation

All complete bases span the same physical space. The `WCxf` (Wilson Coefficient Exchange Format) standard and the `wilson` Python package provide automated translation.

---

## 4. UFO Models for MadGraph

### 4.1 SMEFTatNLO

**Reference**: Degrande, Durieux, Maltoni et al., [arXiv:2008.11743](https://arxiv.org/abs/2008.11743), [arXiv:2104.02723](https://arxiv.org/abs/2104.02723)

- Warsaw basis operators affecting top, Higgs, and EW processes
- **NLO QCD** accuracy (includes UV counterterms and $R_2$ rational terms)
- Supports general and restricted flavor scenarios
- Multiple EW input schemes

### 4.2 SMEFTsim

**Reference**: Brivio, [arXiv:1709.09735](https://arxiv.org/abs/1709.09735), [arXiv:2012.11343](https://arxiv.org/abs/2012.11343)

- Complete set of 2499 baryon-number-conserving dim-6 Warsaw basis operators
- **LO only**
- Multiple input schemes and flavor assumptions (`general`, `top`, `topU3l`, `U35`)
- Supports linear and quadratic contributions via `NP` order parameter

### 4.3 dim6top

**Reference**: Aguilar-Saavedra et al., [arXiv:1802.07237](https://arxiv.org/abs/1802.07237)

- Focused on top quark interactions only
- **LO only**
- Conventions sometimes differ from Warsaw basis
- Widely used in ATLAS/CMS top SMEFT analyses; `SMEFTatNLO` preferred for new work

### 4.4 Comparison

| Feature | SMEFTatNLO | SMEFTsim | dim6top |
|---------|-----------|----------|---------|
| Basis | Warsaw | Warsaw | Warsaw-like |
| QCD precision | NLO | LO | LO |
| Operator scope | Top/Higgs/EW | Complete (2499) | Top sector |
| Flavor options | General + restricted | Multiple | Top-focused |
| Maintained | Yes | Yes | Limited |

---

## 5. Wilson Coefficient Conventions

### 5.1 Standard Convention ($C_i / \Lambda^2$)

$$\mathcal{L} \supset \frac{C_i}{\Lambda^2} \mathcal{O}_i$$

$C_i$ is dimensionless; $\Lambda$ is a fixed reference scale (often 1 TeV). Bounds are quoted on $C_i/\Lambda^2$ in TeV$^{-2}$.

### 5.2 Rescaled Conventions

Some authors use:
- $\hat{C}_i = C_i v^2 / \Lambda^2$ (dimensionless, gives fractional deviation from SM)
- SILH-motivated: $c_H / (2f^2)$ with composite Higgs decay constant $f$

### 5.3 WCxf Standard

The Wilson Coefficient Exchange Format unambiguously specifies:
- Basis (e.g., `Warsaw`)
- EFT (e.g., `SMEFT`)
- Renormalization scale $\mu$
- Normalization convention

### 5.4 RG Running

Wilson coefficients **run** with energy scale via renormalization group equations. The SMEFT anomalous dimension matrix is known at one loop. Running mixes operators: a UV model generating one operator at $\mu = \Lambda$ will generally generate many at $\mu = m_Z$.

### 5.5 Key Points for Implementation

1. **Always specify the basis** (Warsaw is default)
2. **Always specify the scale** $\mu$ at which coefficients are evaluated
3. **Always specify the convention** ($C_i/\Lambda^2$ in TeV$^{-2}$ vs other)
4. **State whether quadratic terms are included**
5. **EW input scheme matters** (different schemes absorb different SMEFT shifts)
6. **Flavor assumptions must be stated**
