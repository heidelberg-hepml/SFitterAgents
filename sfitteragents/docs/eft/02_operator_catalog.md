# Dimension-6 SMEFT Operator Catalog (Warsaw Basis)

Reference: Grzadkowski, Iskrzynski, Misiak, Rosiek, JHEP 1010 (2010) 085, [arXiv:1008.4884](https://arxiv.org/abs/1008.4884).

Notation: $\varphi$ = Higgs doublet, $\tilde{\varphi} = i\sigma_2 \varphi^*$, $Q$ = LH quark doublet, $t_R, b_R$ = RH top/bottom singlets, $G_{\mu\nu}^A$ = gluon field strength, $W_{\mu\nu}^I$ = $SU(2)_L$ field strength, $B_{\mu\nu}$ = $U(1)_Y$ field strength, $T^A$ = $SU(3)_C$ generators, $\tau^I$ = $SU(2)_L$ generators.

---

## 1. Top Sector Operators

Under $U(2)_q \times U(2)_u \times U(2)_d$ flavor symmetry (first two generations degenerate, third generation distinguished), approximately 20-25 independent operators dominate top quark physics.

### 1.1 Chromomagnetic Dipole

| Operator | Definition | CP | Key processes (tree level) | Best sensitivity |
|----------|-----------|-----|---------------------------|-----------------|
| $O_{tG}$ | $(\bar{Q}\sigma^{\mu\nu} T^A t)\tilde{\varphi}\, G_{\mu\nu}^A + \text{h.c.}$ | Even (Re) / Odd (Im) | $gg \to t\bar{t}$, $t\bar{t}+\text{jets}$, $t\bar{t}H$, $t\bar{t}Z$, $t\bar{t}W$ | $t\bar{t}$ total and differential cross-sections |

- Modifies the $g$-$t$-$\bar{t}$ vertex by adding a chromomagnetic moment
- Enters $t\bar{t}$ production at tree level (both $q\bar{q}$ and $gg$ channels)
- Mainly sensitive to ggF processes (~90% of $t\bar{t}$ at LHC)
- Also contributes to $gg \to H$ at one loop
- Im($C_{tG}$) is CP-odd, generates asymmetries

### 1.2 Electroweak Dipole

| Operator | Definition | CP | Key processes (tree level) | Best sensitivity |
|----------|-----------|-----|---------------------------|-----------------|
| $O_{tW}$ | $(\bar{Q}\sigma^{\mu\nu} \tau^I t)\tilde{\varphi}\, W_{\mu\nu}^I + \text{h.c.}$ | Even (Re) / Odd (Im) | Single top, $t\bar{t}W$, $t\bar{t}Z$, $tZq$ | $W$ helicity fractions in $t \to Wb$, single top |
| $O_{tB}$ | $(\bar{Q}\sigma^{\mu\nu} t)\tilde{\varphi}\, B_{\mu\nu} + \text{h.c.}$ | Even (Re) / Odd (Im) | $t\bar{t}Z$, $t\bar{t}\gamma$, $tZq$, $t\gamma q$ | $t\bar{t}\gamma$, $t\bar{t}Z$ differential |

**Derived mass-eigenstate combinations:**

$$C_{tZ} = -s_W C_{tW} + c_W C_{tB}, \qquad C_{t\gamma} = c_W C_{tW} + s_W C_{tB}$$

- $O_{tW}$ modifies the $Wtb$ vertex (adds right-handed tensor coupling)
- $O_{tB}$ only appears in neutral-current top processes
- Both enter $h \to \gamma\gamma$ and $h \to Z\gamma$ at one loop

### 1.3 Higgs-Fermion Current Operators

| Operator | Definition | CP | Key processes (tree level) | Best sensitivity |
|----------|-----------|-----|---------------------------|-----------------|
| $O_{\varphi Q}^{(1)}$ | $(\varphi^\dagger i \overleftrightarrow{D}_\mu \varphi)(\bar{Q}\gamma^\mu Q)$ | Even | $t\bar{t}Z$, $tZq$, $t\bar{t}H$ | $Z$-pole observables ($R_b$, $A_{FB}^b$), $t\bar{t}Z$ |
| $O_{\varphi Q}^{(3)}$ | $(\varphi^\dagger i \overleftrightarrow{D}_\mu^I \varphi)(\bar{Q}\tau^I\gamma^\mu Q)$ | Even | Single top (all), $t\bar{t}Z$, $t\bar{t}W$, $tZq$ | Single top cross-sections, $W$ helicity, $R_b$ |
| $O_{\varphi t}$ | $(\varphi^\dagger i \overleftrightarrow{D}_\mu \varphi)(\bar{t}\gamma^\mu t)$ | Even | $t\bar{t}Z$, $tZq$ | $t\bar{t}Z$ differential, $tZq$ |
| $O_{\varphi tb}$ | $(\tilde{\varphi}^\dagger i D_\mu \varphi)(\bar{t}\gamma^\mu b) + \text{h.c.}$ | Even (Re) / Odd (Im) | Single top, $t\bar{t}W$ (RH $Wtb$) | Single top polarization, $W$ helicity |
| $O_{t\varphi}$ | $(\varphi^\dagger \varphi)(\bar{Q} t \tilde{\varphi}) + \text{h.c.}$ | Even (Re) / Odd (Im) | $t\bar{t}H$, $tHq$, $tHW$ | $t\bar{t}H$ cross-section, Higgs signal strengths |

**Key basis relations** (used in SFitter):

$$C_{\varphi Q}^{-} = C_{\varphi Q}^{(1)} - C_{\varphi Q}^{(3)}, \qquad C_{\varphi Q}^{+} = C_{\varphi Q}^{(1)} + C_{\varphi Q}^{(3)}$$

Coupling modifications:

$$\delta g_{Zt_L} \propto C_{\varphi Q}^{(1)} + C_{\varphi Q}^{(3)}, \quad \delta g_{Zb_L} \propto C_{\varphi Q}^{(1)} - C_{\varphi Q}^{(3)}, \quad \delta g_{Wt_Lb_L} \propto C_{\varphi Q}^{(3)}$$
$$\delta g_{Zt_R} \propto C_{\varphi t}, \quad \delta g_{Wt_Rb_R} \propto C_{\varphi tb}$$

### 1.4 Four-Fermion Operators (Two Heavy, Two Light)

Notation: superscript $I \in \{1,3\}$ = $SU(2)$ singlet/triplet, $C \in \{1,8\}$ = $SU(3)$ color singlet/octet.

#### $(LL)(LL)$ type

| Operator | Definition | Chirality | Color | Key processes |
|----------|-----------|-----------|-------|---------------|
| $O_{Qq}^{1,1}$ | $(\bar{Q}\gamma_\mu Q)(\bar{q}\gamma^\mu q)$ | $LL$ | singlet | $q\bar{q} \to t\bar{t}$ |
| $O_{Qq}^{3,1}$ | $(\bar{Q}\gamma_\mu \tau^I Q)(\bar{q}\gamma^\mu \tau^I q)$ | $LL$ | singlet | $q\bar{q} \to t\bar{t}$, single top ($s$-ch) |
| $O_{Qq}^{1,8}$ | $(\bar{Q}\gamma_\mu T^A Q)(\bar{q}\gamma^\mu T^A q)$ | $LL$ | octet | $q\bar{q} \to t\bar{t}$ |
| $O_{Qq}^{3,8}$ | $(\bar{Q}\gamma_\mu \tau^I T^A Q)(\bar{q}\gamma^\mu \tau^I T^A q)$ | $LL$ | octet | $q\bar{q} \to t\bar{t}$, single top ($s$-ch) |

#### $(RR)(RR)$ type

| Operator | Definition | Chirality | Color | Key processes |
|----------|-----------|-----------|-------|---------------|
| $O_{tu}^{1}$ | $(\bar{t}\gamma_\mu t)(\bar{u}\gamma^\mu u)$ | $RR$ | singlet | $q\bar{q} \to t\bar{t}$ (via $u\bar{u}$) |
| $O_{tu}^{8}$ | $(\bar{t}\gamma_\mu T^A t)(\bar{u}\gamma^\mu T^A u)$ | $RR$ | octet | $q\bar{q} \to t\bar{t}$ (via $u\bar{u}$) |
| $O_{td}^{1}$ | $(\bar{t}\gamma_\mu t)(\bar{d}\gamma^\mu d)$ | $RR$ | singlet | $q\bar{q} \to t\bar{t}$ (via $d\bar{d}$) |
| $O_{td}^{8}$ | $(\bar{t}\gamma_\mu T^A t)(\bar{d}\gamma^\mu T^A d)$ | $RR$ | octet | $q\bar{q} \to t\bar{t}$ (via $d\bar{d}$) |

#### $(LL)(RR)$ and $(RL)$ mixed chirality

| Operator | Definition | Chirality | Color | Key processes |
|----------|-----------|-----------|-------|---------------|
| $O_{Qu}^{1}$ | $(\bar{Q}\gamma_\mu Q)(\bar{u}\gamma^\mu u)$ | $LR$ | singlet | $q\bar{q} \to t\bar{t}$ |
| $O_{Qu}^{8}$ | $(\bar{Q}\gamma_\mu T^A Q)(\bar{u}\gamma^\mu T^A u)$ | $LR$ | octet | $q\bar{q} \to t\bar{t}$ |
| $O_{Qd}^{1}$ | $(\bar{Q}\gamma_\mu Q)(\bar{d}\gamma^\mu d)$ | $LR$ | singlet | $q\bar{q} \to t\bar{t}$ |
| $O_{Qd}^{8}$ | $(\bar{Q}\gamma_\mu T^A Q)(\bar{d}\gamma^\mu T^A d)$ | $LR$ | octet | $q\bar{q} \to t\bar{t}$ |
| $O_{tq}^{1}$ | $(\bar{t}\gamma_\mu t)(\bar{q}\gamma^\mu q)$ | $RL$ | singlet | $q\bar{q} \to t\bar{t}$ |
| $O_{tq}^{8}$ | $(\bar{t}\gamma_\mu T^A t)(\bar{q}\gamma^\mu T^A q)$ | $RL$ | octet | $q\bar{q} \to t\bar{t}$ |

**Key properties of four-fermion operators:**
- All 14 enter $q\bar{q} \to t\bar{t}$ at tree level
- Best constrained from high-$m_{t\bar{t}}$ tails (where $q\bar{q}$ fraction increases and contributions grow as $\hat{s}/\Lambda^2$)
- Charge asymmetry $A_C$ is $q\bar{q}$-initiated by definition, providing additional discrimination
- $SU(2)$-triplet operators ($O_{Qq}^{3,*}$) also contribute to single top
- All listed operators are CP-even (vector currents)

---

## 2. Higgs / Electroweak Bosonic Sector

### 2.1 Pure Gauge

| Operator | Definition | CP | Key processes |
|----------|-----------|-----|---------------|
| $O_{G}$ | $f^{ABC} G_\mu^{A\nu} G_\nu^{B\rho} G_\rho^{C\mu}$ | Even | Multi-jet (3-gluon vertex) |
| $O_{\tilde{G}}$ | $f^{ABC} \tilde{G}_\mu^{A\nu} G_\nu^{B\rho} G_\rho^{C\mu}$ | **Odd** | CP-violating multi-jet |
| $O_{W}$ | $\epsilon^{IJK} W_\mu^{I\nu} W_\nu^{J\rho} W_\rho^{K\mu}$ | Even | $WW$, $WZ$, VBF, triboson |
| $O_{\tilde{W}}$ | $\epsilon^{IJK} \tilde{W}_\mu^{I\nu} W_\nu^{J\rho} W_\rho^{K\mu}$ | **Odd** | CP-odd diboson angular observables |

### 2.2 Higgs-Gauge

| Operator | Definition | CP | Key processes |
|----------|-----------|-----|---------------|
| $O_{\varphi G}$ | $(\varphi^\dagger \varphi) G_{\mu\nu}^A G^{A\mu\nu}$ | Even | $gg \to H$ (direct coupling), $H+\text{jet}$ |
| $O_{\varphi \tilde{G}}$ | $(\varphi^\dagger \varphi) \tilde{G}_{\mu\nu}^A G^{A\mu\nu}$ | **Odd** | CP-odd $gg \to H$ |
| $O_{\varphi W}$ | $(\varphi^\dagger \varphi) W_{\mu\nu}^I W^{I\mu\nu}$ | Even | $H \to WW^*$, VBF, $VH$ |
| $O_{\varphi B}$ | $(\varphi^\dagger \varphi) B_{\mu\nu} B^{\mu\nu}$ | Even | $H \to \gamma\gamma$, $H \to Z\gamma$ |
| $O_{\varphi WB}$ | $(\varphi^\dagger \tau^I \varphi) W_{\mu\nu}^I B^{\mu\nu}$ | Even | $H \to \gamma\gamma$, TGC, EWPO ($S$-parameter) |
| $O_{\varphi \tilde{W}}$, $O_{\varphi \tilde{B}}$, $O_{\varphi \tilde{W}B}$ | CP-odd counterparts | **Odd** | CP-sensitive Higgs/gauge observables |

### 2.3 Higgs Self-Interaction

| Operator | Definition | CP | Key processes |
|----------|-----------|-----|---------------|
| $O_{\varphi}$ | $(\varphi^\dagger \varphi)^3$ | Even | Di-Higgs ($gg \to HH$), modifies trilinear $\lambda_3$ |
| $O_{\varphi \Box}$ | $(\varphi^\dagger \varphi) \Box (\varphi^\dagger \varphi)$ | Even | Universal Higgs coupling rescaling |
| $O_{\varphi D}$ | $(\varphi^\dagger D_\mu \varphi)^* (\varphi^\dagger D^\mu \varphi)$ | Even | $T$-parameter, $\rho$-parameter, $M_W$ |

### 2.4 Higgs-Fermion (Light Generations & Leptons)

| Operator | Definition | CP | Key processes |
|----------|-----------|-----|---------------|
| $O_{\varphi l}^{(1)}$ | $(\varphi^\dagger i \overleftrightarrow{D}_\mu \varphi)(\bar{L}\gamma^\mu L)$ | Even | $Z \to \ell\ell$, EWPO |
| $O_{\varphi l}^{(3)}$ | $(\varphi^\dagger i \overleftrightarrow{D}_\mu^I \varphi)(\bar{L}\tau^I\gamma^\mu L)$ | Even | $W \to \ell\nu$, $Z \to \ell\ell$, $M_W$ |
| $O_{\varphi e}$ | $(\varphi^\dagger i \overleftrightarrow{D}_\mu \varphi)(\bar{e}\gamma^\mu e)$ | Even | $Z \to e^+e^-$, $\sin^2\theta_{\text{eff}}$ |
| $O_{\varphi u}$ | $(\varphi^\dagger i \overleftrightarrow{D}_\mu \varphi)(\bar{u}\gamma^\mu u)$ | Even | $Z \to q\bar{q}$ (light quarks) |
| $O_{\varphi d}$ | $(\varphi^\dagger i \overleftrightarrow{D}_\mu \varphi)(\bar{d}\gamma^\mu d)$ | Even | $Z \to q\bar{q}$ (light quarks) |
| $O_{b\varphi}$ | $(\varphi^\dagger \varphi)(\bar{Q} b \varphi) + \text{h.c.}$ | Even/Odd | $H \to b\bar{b}$ |
| $O_{\tau\varphi}$ | $(\varphi^\dagger \varphi)(\bar{L} \tau \varphi) + \text{h.c.}$ | Even/Odd | $H \to \tau\tau$ |

---

## 3. Process-Operator Summary

### 3.1 Top-Quark Processes

| Process | Tree-level operators |
|---------|---------------------|
| $t\bar{t}$ (inclusive & differential) | $O_{tG}$, all 14 four-fermion ops |
| Single top $t$-channel | $O_{\varphi Q}^{(3)}$, $O_{tW}$, $O_{\varphi tb}$, $O_{Qq}^{3,1}$, $O_{Qq}^{3,8}$ |
| Single top $s$-channel | $O_{\varphi Q}^{(3)}$, $O_{tW}$, $O_{Qq}^{3,1}$, $O_{Qq}^{3,8}$ |
| $tW$ associated | $O_{\varphi Q}^{(3)}$, $O_{tW}$, $O_{tG}$ |
| $t\bar{t}Z$ | $O_{\varphi Q}^{(1)}$, $O_{\varphi Q}^{(3)}$, $O_{\varphi t}$, $O_{tW}$, $O_{tB}$, $O_{tG}$, 4F ops |
| $t\bar{t}W$ | $O_{\varphi Q}^{(3)}$, $O_{tW}$, $O_{tG}$, $O_{\varphi tb}$, 4F ops |
| $t\bar{t}\gamma$ | $O_{tW}$, $O_{tB}$, $O_{tG}$, 4F ops |
| $t\bar{t}H$ | $O_{t\varphi}$, $O_{tG}$, $O_{\varphi Q}^{(1)}$, $O_{\varphi Q}^{(3)}$, $O_{\varphi t}$, 4F ops |
| $tZq$ | $O_{\varphi Q}^{(1)}$, $O_{\varphi Q}^{(3)}$, $O_{\varphi t}$, $O_{tW}$, $O_{tB}$ |
| $t$ decay ($t \to Wb$) | $O_{tW}$, $O_{\varphi Q}^{(3)}$, $O_{\varphi tb}$ |

### 3.2 Higgs Processes

| Process | Key operators |
|---------|--------------|
| $gg \to H$ | $O_{\varphi G}$; loop: $O_{tG}$, $O_{t\varphi}$, $O_{b\varphi}$ |
| VBF | $O_{\varphi W}$, $O_{\varphi B}$, $O_{\varphi WB}$, $O_{\varphi \Box}$, $O_{\varphi D}$ |
| $WH$, $ZH$ | $O_{\varphi W}$, $O_{\varphi B}$, $O_{\varphi WB}$, $O_{\varphi \Box}$, $O_{\varphi D}$, $O_{\varphi l}^{(1,3)}$ |
| $H \to \gamma\gamma$ | $O_{\varphi W}$, $O_{\varphi B}$, $O_{\varphi WB}$; loop: $O_{tW}$, $O_{tB}$ |
| $H \to WW^*/ZZ^*$ | $O_{\varphi W}$, $O_{\varphi B}$, $O_{\varphi WB}$, $O_{\varphi \Box}$, $O_{\varphi D}$ |
| $H \to b\bar{b}$ | $O_{b\varphi}$, $O_{\varphi \Box}$ |
| $HH$ (di-Higgs) | $O_{\varphi}$, $O_{\varphi \Box}$, $O_{\varphi G}$, $O_{t\varphi}$, $O_{tG}$ |

### 3.3 Diboson Processes

| Process | Key operators |
|---------|--------------|
| $pp \to WW$ | $O_{W}$, $O_{\varphi W}$, $O_{\varphi WB}$, $O_{\varphi D}$ |
| $pp \to WZ$ | $O_{W}$, $O_{\varphi W}$, $O_{\varphi WB}$, $O_{\varphi D}$ |
| $pp \to W\gamma$ / $Z\gamma$ | $O_{W}$, $O_{\varphi WB}$, $O_{\varphi B}$ |

---

## 4. Flavor Symmetry Assumptions

| Assumption | Description | Typical operator count |
|------------|-------------|----------------------|
| $U(3)^5$ | All generations identical | ~50 |
| $U(2)_q \times U(2)_u \times U(2)_d$ | First two generations degenerate, third distinguished | ~40 (top+Higgs+EWPO) |
| MFV | All flavor violation $\propto$ SM Yukawas | Further reduced |
| General (3 gen) | No flavor symmetry | 2499 |

---

## 5. CP Properties

| CP-Even | CP-Odd |
|---------|--------|
| Re($C_{tG}$), Re($C_{tW}$), Re($C_{tB}$) | Im($C_{tG}$), Im($C_{tW}$), Im($C_{tB}$) |
| $C_{\varphi Q}^{(1,3)}$, $C_{\varphi t}$ (Hermitian currents) | Im($C_{\varphi tb}$), Im($C_{t\varphi}$) |
| $O_G$, $O_W$ | $O_{\tilde{G}}$, $O_{\tilde{W}}$ |
| $O_{\varphi G}$, $O_{\varphi W}$, $O_{\varphi B}$, $O_{\varphi WB}$ | $O_{\varphi\tilde{G}}$, $O_{\varphi\tilde{W}}$, $O_{\varphi\tilde{B}}$, $O_{\varphi\tilde{W}B}$ |
| All four-fermion ops (vector $\times$ vector) | Scalar/tensor four-fermion ops |

CP-odd operators generate: forward-backward asymmetries, azimuthal asymmetries in $t\bar{t}V$, electric dipole moments (EDMs) providing very strong indirect constraints.

---

## 6. Common Alternative Naming Conventions

| This document | Alternative notations |
|---------------|----------------------|
| $O_{\varphi Q}^{(1)}$ | $O_{Hq}^{(1)}$, $\mathcal{O}_{\varphi q}^{(1)}$ |
| $O_{\varphi Q}^{(3)}$ | $O_{Hq}^{(3)}$, $\mathcal{O}_{\varphi q}^{(3)}$ |
| $O_{\varphi t}$ | $O_{Hu}^{33}$, $\mathcal{O}_{\varphi u}^{33}$ |
| $O_{t\varphi}$ | $O_{u\varphi}^{33}$, $\mathcal{O}_{tH}$, $O_{y_t}$ |
| $O_{tG}$ | $O_{uG}^{33}$, $\mathcal{O}_{tG}$ |
| $O_{tW}$ | $O_{uW}^{33}$, $\mathcal{O}_{tW}$ |
| $O_{tB}$ | $O_{uB}^{33}$, $\mathcal{O}_{tB}$ |
