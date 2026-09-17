# SMEFTatNLO Pitfalls and Parameter Card Hygiene

Practical issues encountered when using SMEFTatNLO for Wilson coefficient scans, and the defensive patterns that prevent them.

---

## 1. The Default-Nonzero Operator Trap

### What the bug looks like

When scanning a single operator (say, $C_{tG}$) with SMEFTatNLO, the naive
workflow is:

1. Write an `.mg5` script that sets the scanned operator to a value and leaves
   everything else "at default".
2. Generate and run the process.
3. Extract the linear/quadratic contributions.

**This is wrong.** SMEFTatNLO's default `param_card.dat` contains **nonzero
values** for many Wilson coefficients that were never meant to be active in
your scan. Unless you explicitly zero them, they contribute to the amplitude
alongside the operator you intended to vary, contaminating the extracted
$\kappa_1$ and $\kappa_2$ by 2–10% (larger in distribution tails).

The contamination is bounded by the $d\bar d / s\bar s / b\bar b$ initial-state
PDF fraction — small enough to not be "obviously wrong", large enough to
systematically bias any downstream SMEFT fit. Default-nonzero DIM64F couplings
do enter the compiled matrix elements this way; §4 shows how to check.

---

## 2. Which Operators Leak

SMEFTatNLO has **five** Wilson coefficient blocks in its `param_card.dat`:

| Block | Contains | Default-nonzero | Safe for $pp \to t\bar t$? |
|-------|----------|-----------------|---------------------------|
| `DIM6` | Bosonic + Yukawa-type dim-6 operators | ~8 | Yes (via QED=0 filter) |
| `DIM62F` | Two-fermion dim-6 operators (including $O_{tG}$, $O_{tW}$, $O_{tB}$, $O_{\phi Q}^{(1,3)}$, $O_{\phi t}$, etc.) | ~19 | Yes (via QED=0 filter) |
| `DIM64F` | Four-fermion dim-6 operators (all quarks) | ~25 | **NO — manual zeroing required** |
| `DIM64F2L` | Two-quark + two-lepton four-fermion operators | All default-nonzero | Yes at LO (vertex structure) |
| `DIM64F4L` | Four-lepton operators | All default-nonzero | Yes trivially (no quarks) |

**The QED=0 filter saves you from most of them.** When the process card
specifies `QED=0`, MadGraph's code generator drops every vertex that carries
QED coupling power. Since virtually every operator in `DIM6` and `DIM62F`
involves a Higgs/Z/W/γ insertion, their couplings are stripped before any
matrix element is written.

**The vertex structure saves you from the two lepton-containing blocks** at
LO for $pp \to t\bar t$, but this protection is process-specific — see below.

### DIM6 block — No action needed (under QED=0)

All 8 default-nonzero entries are EW/Higgs operators. They're killed by the
QED=0 filter. $O_G$ (triple gluon) is dead in SMEFTatNLO regardless (it's
not implemented in the 2-to-2 matrix element generation path).

### DIM62F block — No action needed (under QED=0)

All 19 default-nonzero entries need a Higgs/Z/W/γ insertion. They're killed
by the QED=0 filter. The **only** DIM62F-derived coupling that appears in the
$pp \to t\bar t$ matrix element is $c_{tG}$ itself (as intended).

### DIM64F block — **Manual zeroing required**

Four-fermion operators don't need electroweak insertions — they're pure QCD
four-fermion contact interactions. The QED=0 filter does not touch them.

The following DIM64F codes are **default-nonzero** in SMEFTatNLO and **must
be explicitly zeroed** before any $pp \to t\bar t$ scan:

| Code | Operator | Default value | Leaks via |
|------|----------|---------------|-----------|
| 17 | $c_{td}^{(1)}$ | 0.242 | $d\bar d$, $s\bar s \to t\bar t$ |
| 19 | $c_{QQ}^{(8)}$ | 0.902 | $b\bar b \to t\bar t$ |
| 20 | $c_{QQ}^{(1)}$ | 0.721 | $b\bar b \to t\bar t$ |
| 21 | $c_{Qt}^{(1)}$ | 0.541 | $b\bar b \to t\bar t$ |
| 23 | $c_{tt}^{(1)}$ | 0.956 | No $t\bar t$ diagram (4-top), but zero for safety |
| 25 | $c_{Qt}^{(8)}$ | 0.551 | $b\bar b \to t\bar t$ |

Note that code 23 is a four-top operator with no initial-state legs, so
MadGraph excludes it automatically from the $2 \to 2$ amplitude — but zeroing
it anyway is cheap and defensively clarifies intent.

### DIM64F2L block — Safe at LO for hadronic processes, **process-dependent**

SMEFTatNLO also includes a `DIM64F2L` block containing two-quark + two-lepton
four-fermion operators ($c_{qlM}^{(1)}$, $c_{tl}^{(1)}$, $c_{Qe}^{(1)}$, etc.).
**All entries in this block are default-nonzero** in the SMEFTatNLO parameter
card.

**Why they don't contaminate $pp \to t\bar t$ at LO**: the vertex structure
of these operators is two quarks plus two leptons. A $pp \to t\bar t$ tree-level
amplitude needs two incoming quarks (or two incoming gluons) and two outgoing
tops — no leptons. There is no way to insert a two-quark-two-lepton vertex
into this amplitude at tree level without producing external leptons, which
the process `p p > t t~` does not allow.

**When they DO matter**:
- At NLO, lepton loops can introduce these operators via vertex corrections.
  For an NLO QCD scan this is not a concern, but NLO EW corrections would
  pick them up.
- Any process with explicit leptons in the final state — e.g.,
  $pp \to t\bar t \ell^+ \ell^-$, $pp \to \ell^+ \ell^-$ (Drell-Yan),
  $pp \to W^+ W^- \to \ell^+ \nu \ell^- \bar\nu$ — will be contaminated by
  these defaults unless they are zeroed.
- Semi-leptonic top decay observables: if the process includes the top decay
  chain $t \to W b \to \ell\nu b$ explicitly in the matrix element, these
  operators enter.

**Defensive recommendation**: zero DIM64F2L in every scan script, even for
pure-hadronic processes. Same reasoning as the DIM64F 4-top operator: cost
is negligible, protection is universal, and it catches the bug if someone
later reuses the script for a leptonic process.

### DIM64F4L block — Safe trivially (pure leptonic)

The `DIM64F4L` block contains pure four-lepton operators (e.g., $c_{LL}$,
$c_{ee}$, $c_{Le}$). **All entries are default-nonzero.**

These can never contribute to $pp \to t\bar t$ at any order — they involve
no quarks at all. They are only relevant for lepton-collider processes
($e^+e^- \to \ell^+ \ell^-$) or NLO EW corrections to leptonic processes.

**Defensive recommendation**: zero DIM64F4L for completeness and consistency.
The cost is a handful of extra lines.

---

## 3. The Defensive Pattern

**Always use the defensive pattern**: explicitly zero every operator in the
UFO model except the one(s) being scanned.

### Why defensive > minimal

- **Cost**: ~30 extra lines in each `.mg5` script — negligible runtime cost
- **Self-documenting**: anyone reading the script sees exactly which operators
  are active
- **Robust against process card changes**: if `QED=0` is later removed or
  changed (e.g., adding EW corrections), the DIM6/DIM62F contamination would
  suddenly become active. Explicit zeroing prevents this class of bug entirely.
- **Robust against UFO model updates**: if a future SMEFTatNLO release adds
  new default-nonzero operators, the explicit zeros catch them automatically.
- **Audit trail**: the list of zeros in the script is a direct reference for
  what "SM baseline plus one operator" means in your scan.

### Template for a single-operator scan

For scanning $C_{tG}$ (interference run, DIM62F code 10):

```mg5
import model SMEFTatNLO-LO
define p = g u c d s u~ c~ d~ s~ b b~
generate p p > t t~ NP^2==1 QED=0
output /output/scans/ctG/int_output

launch /output/scans/ctG/int_output
  set run_card nevents 2000000
  set run_card ebeam1 6500
  set run_card ebeam2 6500

  # === DEFENSIVE ZEROING ===
  # Zero all DIM64F four-fermion operators (QED=0 filter does not touch them)
  set param_card DIM64F 1  0.0
  set param_card DIM64F 2  0.0
  set param_card DIM64F 3  0.0
  set param_card DIM64F 4  0.0
  set param_card DIM64F 5  0.0
  set param_card DIM64F 6  0.0
  set param_card DIM64F 7  0.0
  set param_card DIM64F 8  0.0
  set param_card DIM64F 9  0.0
  set param_card DIM64F 10 0.0
  set param_card DIM64F 11 0.0
  set param_card DIM64F 12 0.0
  set param_card DIM64F 13 0.0
  set param_card DIM64F 14 0.0
  set param_card DIM64F 15 0.0
  set param_card DIM64F 16 0.0
  set param_card DIM64F 17 0.0   # c_td^(1) — default 0.242
  set param_card DIM64F 18 0.0
  set param_card DIM64F 19 0.0   # c_QQ^(8) — default 0.902
  set param_card DIM64F 20 0.0   # c_QQ^(1) — default 0.721
  set param_card DIM64F 21 0.0   # c_Qt^(1) — default 0.541
  set param_card DIM64F 22 0.0
  set param_card DIM64F 23 0.0   # c_tt^(1) — default 0.956 (4-top, filtered anyway)
  set param_card DIM64F 24 0.0
  set param_card DIM64F 25 0.0   # c_Qt^(8) — default 0.551

  # Zero all DIM64F2L two-quark + two-lepton operators (safe at LO for hadronic
  # processes but contaminates anything with leptons; zero for safety/portability)
  set param_card DIM64F2L 1  0.0
  set param_card DIM64F2L 2  0.0
  # ... (complete list — one line per code in the DIM64F2L block)

  # Zero all DIM64F4L four-lepton operators (irrelevant for pp > tt~ but
  # zero for completeness and to catch accidental reuse on leptonic processes)
  set param_card DIM64F4L 1  0.0
  # ... (complete list — one line per code in the DIM64F4L block)

  # Optional but recommended: also zero DIM6 and DIM62F for protection
  # against future process-card changes that might drop QED=0.
  # (Currently these are all killed by QED=0, but explicit is safer.)
  # set param_card DIM6   1  0.0
  # ... (complete list)
  # set param_card DIM62F 1  0.0
  # ... (complete list, except the scanned operator)

  # === ACTIVE OPERATOR ===
  set param_card DIM62F 10 1.0   # c_tG (the scanned operator)

  done
```

For each WC scan value, only the last `set param_card DIM62F 10 ...` line
changes. Everything else stays identical.

**Note on complete enumeration**: The exact list of codes in each block is
determined by the SMEFTatNLO version you are using. Before writing a scan
script, inspect the model's default `param_card.dat` (typically found at
`<MG5_DIR>/models/SMEFTatNLO/restrict_default.dat` or
`<MG5_DIR>/models/SMEFTatNLO/parameters.py`) and enumerate every code in
every `DIM6*` block. The defensive pattern requires zeroing *all* of them,
not just the subset listed in this document.

---

## 4. Verifying Contamination Absence

After generating a process with SMEFTatNLO, you can verify that no unintended
operators entered the matrix element by inspecting the generated Fortran:

```bash
# List all couplings used in the matrix element
grep -h '^ *JAMP\|^ *AMP' <proc_dir>/SubProcesses/P*/matrix*.f | \
  grep -oE 'GC_[0-9]+' | sort -u

# Map each GC_N to its operator via coupl.inc
grep 'GC_' <proc_dir>/Source/MODEL/coupl.inc
```

Each `GC_N` symbol corresponds to a specific vertex. For a clean single-operator
scan, only couplings derived from your scanned operator (and pure QCD) should
appear.

---

## 5. Other SMEFTatNLO Gotchas

### 5.1 Convention mismatch with LHC-TOPWG

SMEFTatNLO's definition of $c_{tG}$ differs from the LHC-TOPWG convention by
a factor of $g_s$ (the strong coupling). Specifically:

$$c_{tG}^{\text{TOPWG}} = g_s \cdot c_{tG}^{\text{SMEFTatNLO}}$$

If a downstream fitter (SFitter) expects TOPWG conventions, the
extracted contributions must be rescaled:

$$D6tg_{\text{lin}}^{\text{TOPWG}} = \frac{1}{g_s} \cdot D6tg_{\text{lin}}^{\text{SMEFTatNLO}}$$
$$D6tg_{\text{quad}}^{\text{TOPWG}} = \frac{1}{g_s^2} \cdot D6tg_{\text{quad}}^{\text{SMEFTatNLO}}$$

At the $t\bar t$ scale, $g_s \approx 1.22$, so $1/g_s \approx 0.82$ and
$1/g_s^2 \approx 0.67$. **Check the convention of the target fitter before
running any scan**, and bake the correct convention into the output to avoid
post-hoc rescaling confusion.

### 5.2 $\mathcal{O}(C^3)$ truncation residual

The linear + quadratic parameterization has an intrinsic residual from neglected
$\mathcal{O}(C^3)$ and higher terms. For $|c_{tG}| \sim 1$, this residual is
~5–8% in the high-$m_{t\bar t}$ tail bins of $pp \to t\bar t$. It's fine for
fits that pull $|c|$ to small values, but should be documented as a caveat
in any output where large WC values are probed.

### 5.3 Pure four-top operators (code 23)

$c_{tt}^{(1)}$ is a $(\bar t\gamma^\mu t)(\bar t\gamma_\mu t)$ contact
interaction with four top quarks. It has no initial-state legs in a
$pp \to t\bar t$ amplitude, so MadGraph excludes it automatically. It still
gets zeroed defensively because:
- It's cheap
- It catches accidental misuse (e.g., if someone later runs $pp \to t\bar t t\bar t$)
- It keeps the zeroing list complete and consistent
