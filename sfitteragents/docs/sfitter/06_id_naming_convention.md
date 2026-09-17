# SFitter ID Naming Convention

How the `ID` field of an observation/prediction in an SFitter JSON encodes
the measurement metadata. The convention was originally documented by the
SFitter group as the "Top naming convention" (March 2020) and is verified
against real entries in `sfitter/data/Top_Full.json`. This document is the
authoritative reference for the agent system.

---

## 1. Overall Format

```
ocfkkxe[_b]
```

| Position | Length | Symbol | Meaning |
|----------|--------|--------|---------|
| 1 | 1 char | `o` | Perturbative order of the SM prediction |
| 2 | 1 char | `c` | Process channel |
| 3 | 1 char | `f` | Final state / signal region (channel-dependent) |
| 4-5 | 2 chars | `kk` | Kinematic variable / observable (channel-dependent) |
| 6 | 1 char | `x` | Experiment |
| 7 | 1 char | `e` | Collision energy |
| 8+ | optional | `_b` | Bin number, only used for non-distribution measurements (`b=0`) |

The total length is 7 characters for distributions (the bin index is carried
implicitly by the per-bin data array) or 9 characters for single-bin
measurements (`_0` suffix).

**Real examples:**
- `2210913` → `ttbar_CMS_diffxs_13_mtt_lj` (NLO ttbar, l+jets, mtt normalized, CMS, 13 TeV)
- `2210923` → `ttbar_ATLAS_diffxs_13_mtt_lj` (same but ATLAS)
- `2261133` → `ttbar_totalxs_13` (NLO ttbar, total xsec, averaged across experiments, 13 TeV)
- `2130213_0` → `SingleT_tch_tbar_13` (NLO single top, tbar, t-channel, ?, 13 TeV, single bin)
- `2300111_0` → `SingleT_whel_F0_7` (NLO single top, top decay, F0 helicity, ?, 7 TeV)

---

## 2. Position-by-Position Reference

### 2.1 `o` — Perturbative Order

| Code | Meaning |
|------|---------|
| `1` | LO |
| `2` | NLO |
| `3` | Highest available (NNLO at the time of the convention; in practice "NNLO+ via k-factors") |

Use `o=3` when the SM prediction has been corrected to NNLO (e.g., via
HighTea k-factors applied to an NLO MadGraph baseline). Use `o=2` only if the
prediction is genuinely NLO without further corrections.

### 2.2 `c` — Process Channel

| Code | Process |
|------|---------|
| `1` | Single top |
| `2` | $t\bar t$ |
| `3` | Top decay |
| `4` | $t\bar t Z$ |
| `5` | $t\bar t W$ |
| `6` | Flavour observables |
| `9` | Extended/other (used in practice for $t\bar t \gamma$ — not in the original spec) |

The original convention only defines `c=1` through `c=6`. Real datasets
extend this informally (e.g., `c=9` for $t\bar t \gamma$ in `Top_Full.json`).
When generating new IDs, prefer the documented codes; flag any extension as
a deviation from spec.

### 2.3 `f` — Final State / Signal Region

The meaning depends on the channel `c`:

#### `c=2` ($t\bar t$)
| Code | Final state |
|------|-------------|
| `1` | $\ell$ + jets |
| `2` | dilepton |
| `3` | all-jets |
| `4` | high-$p_T$ $\ell$+jets |
| `5` | $W$ helicity |
| `6` | irrelevant (used for total cross-section or total asymmetry) |
| `7` | high-$p_T$ jj |

#### `c=1` (single top)
| Code | Final state |
|------|-------------|
| `0` | top decay |
| `1` | $t$ AND $\bar t$ (combined) |
| `2` | $t$ |
| `3` | $\bar t$ |
| `4` | $tW$ |
| `5` | $tZ$ |

#### `c=4` ($t\bar t Z$), `c=5` ($t\bar t W$)
| Code | Final state |
|------|-------------|
| `6` | irrelevant |

#### `c=6` (flavour)
| Code | Final state |
|------|-------------|
| `1` | combine with `kk` (see flavour `kk` codes below) |

### 2.4 `kk` — Kinematic Variable / Observable

Channel-dependent. Always two characters (zero-padded).

#### `c=2` ($t\bar t$) — kinematic variables
| Code | Observable | Notes |
|------|------------|-------|
| `01` | $p_T^*$ (normalized) | |
| `02` | $p_T$ (normalized) | |
| `03` | $y_t$ (normalized) | |
| `04` | $\Delta\phi(t,\bar t)$ (normalized) | |
| `05` | $p_{T,1}$ (normalized) | |
| `06` | $p_{T,2}$ (normalized) | |
| `07` | $p_T^{t\bar t}$ (normalized) | |
| `08` | $y^{t\bar t}$ (normalized) | |
| `09` | $m_{t\bar t}$ (normalized) | most common differential observable |
| `10` | $m_{t\bar t} \times y_t$ (normalized) | 2D distribution |
| `11` | total cross section | |
| `12` | $p_T(t_h)$ (unnormalized) | hadronically-decaying top |
| `13` | $p_T(t_h)$ (normalized) | |
| `14` | $A_{\rm asym}(m_{t\bar t})$ | charge asymmetry vs $m_{t\bar t}$ |
| `15` | total asymmetry | |
| `16` | $\Delta\|y\|$ (normalized) | |

#### `c=1` (single top) — observational channel
| Code | Channel |
|------|---------|
| `01` | $s$-channel |
| `02` | $t$-channel |
| `03` | $tW$ |
| `04` | $tZ$ |

For $t$-channel distributions specifically:
| Code | Observable |
|------|------------|
| `12` | $p_T$ unnormalized |
| `22` | $\eta$ unnormalized |
| `32` | $p_T$ normalized |
| `42` | $\eta$ normalized |

#### `c=3` (top decay)
| Code | Observable |
|------|------------|
| `01` | $F_O$ |
| `02` | $F_L$ |
| `03` | $F_R$ |
| `04` | $F_1$ |

#### `c=4` ($t\bar t Z$), `c=5` ($t\bar t W$)
| Code | Observable |
|------|------------|
| `01` | total cross section |

#### `c=6` (flavour)
For flavour, use `fkk` together (3 chars):
| Code | Observable |
|------|------------|
| `001` | $B_s \to \mu\mu$ branching ratio |
| `002` | $b \to s\gamma$ branching ratio |

### 2.5 `x` — Experiment

| Code | Experiment |
|------|------------|
| `1` | CMS |
| `2` | ATLAS |
| `3` | "unimportant" — used in practice for averaged/combined results that don't belong to a single experiment, or when experiment-specificity is irrelevant (e.g., total xsec averages) |

### 2.6 `e` — Collision Energy

| Code | Energy |
|------|--------|
| `1` | 7 TeV |
| `2` | 8 TeV |
| `3` | 13 TeV |
| `4` | "low energy" in original spec; used in practice in `Top_Full.json` for **13.6 TeV** (e.g., `2261134` → `ttbar_totalxs_13p6`). Treat with care — verify against the observation name. |

### 2.7 `_b` — Bin Number (suffix)

Optional. When present, format is `_<bin>` appended after the 7-char base.

- For non-distribution measurements (single value, e.g., total cross-section,
  $W$ helicity fraction): `_0`
- For distributions (multiple bins encoded in the `data` array): typically
  **omitted** — bins are tracked by array index, not by separate IDs

In `Top_Full.json`, single-top observations consistently use `_0` suffix
while $t\bar t$ differential distributions like `2210913` use no suffix.
Both styles are valid.

---

## 3. Worked Examples

### 3.1 ID `2210913` → `ttbar_CMS_diffxs_13_mtt_lj`

| Position | Char | Decoded |
|----------|------|---------|
| `o` | `2` | NLO |
| `c` | `2` | $t\bar t$ |
| `f` | `1` | $\ell$+jets |
| `kk` | `09` | $m_{t\bar t}$ (normalized) |
| `x` | `1` | CMS |
| `e` | `3` | 13 TeV |

**Reads as**: NLO $t\bar t$ in the $\ell$+jets channel, normalized $m_{t\bar t}$ differential cross-section measured by CMS at 13 TeV.

### 3.2 ID `2210923` → `ttbar_ATLAS_diffxs_13_mtt_lj`

Same as above but `x=2` → ATLAS instead of CMS.

### 3.3 ID `2261133` → `ttbar_totalxs_13`

| Position | Char | Decoded |
|----------|------|---------|
| `o` | `2` | NLO |
| `c` | `2` | $t\bar t$ |
| `f` | `6` | irrelevant (total xsec) |
| `kk` | `11` | total cross section |
| `x` | `3` | averaged / experiment-irrelevant |
| `e` | `3` | 13 TeV |

**Reads as**: NLO $t\bar t$ total cross-section at 13 TeV, averaged or combined across experiments.

### 3.4 ID `2261134` → `ttbar_totalxs_13p6`

Same as above but `e=4`. The original spec says `e=4` is "low energy", but in
practice this dataset uses it for 13.6 TeV. **Always cross-check against the
observation name when `e=4` appears.**

### 3.5 ID `2130213_0` → `SingleT_tch_tbar_13`

| Position | Char | Decoded |
|----------|------|---------|
| `o` | `2` | NLO |
| `c` | `1` | single top |
| `f` | `3` | $\bar t$ |
| `kk` | `02` | $t$-channel |
| `x` | `1` | CMS |
| `e` | `3` | 13 TeV |
| `_b` | `_0` | single-bin measurement |

**Reads as**: NLO single anti-top $t$-channel cross-section measured by CMS at 13 TeV.

### 3.6 ID `2300111_0` → `SingleT_whel_F0_7`

| Position | Char | Decoded |
|----------|------|---------|
| `o` | `2` | NLO |
| `c` | `3` | top decay |
| `f` | `0` | top decay (single top convention) |
| `kk` | `01` | $F_O$ helicity fraction |
| `x` | `1` | CMS |
| `e` | `1` | 7 TeV |
| `_b` | `_0` | single-bin |

---

## 4. ID Construction Algorithm

To create a new ID for a measurement:

1. **Determine perturbative order** of the SM prediction you have/use:
   - LO MadGraph only → `o=1`
   - NLO MadGraph → `o=2`
   - NLO + applied NNLO k-factor → `o=3`

2. **Identify the process channel**:
   - $t\bar t$? → `c=2`
   - Single top? → `c=1`
   - Top decay observable (helicity)? → `c=3`
   - $t\bar t Z$/$W$? → `c=4`/`5`
   - Flavour? → `c=6`
   - Anything else (e.g., $t\bar t\gamma$) → use the convention extension (`c=9`) and document the deviation

3. **Pick the final-state code** `f` from the table for the chosen channel.
   For total cross-sections of $t\bar t$/$t\bar t V$, use `f=6` (irrelevant).

4. **Pick the kinematic-variable code** `kk` from the table for the chosen
   channel. Always two characters with leading zero. For total xsec, the
   appropriate `kk` is channel-specific (`11` for $t\bar t$, `01` for $t\bar t Z$/$W$).

5. **Pick the experiment** `x`:
   - CMS only → `1`
   - ATLAS only → `2`
   - Combined / averaged / experiment-irrelevant → `3`

6. **Pick the energy** `e`:
   - 7 TeV → `1`
   - 8 TeV → `2`
   - 13 TeV → `3`
   - 13.6 TeV (or low-energy) → `4` (and document which interpretation)

7. **Add bin suffix** `_0` if and only if the measurement is a single value
   (not a distribution). Distributions encode bins via the `data` array index
   and do not need a suffix.

8. **Validate**: round-trip the constructed ID through the decoding tables
   below and confirm the decoded description matches the intended observation
   name.

---

## 5. Validation Rules (for `config-validator`)

When checking an ID, verify:

1. **Length**: 7 characters base, optionally followed by `_<integer>` suffix
2. **All characters digits** (no letters, no leading symbols)
3. **`o` ∈ {1, 2, 3}** — flag any other value as deviation
4. **`c` ∈ {1, 2, 3, 4, 5, 6}** — `c=9` (or other) is allowed but should
   produce a warning that it extends the documented spec
5. **`f` valid for channel `c`** — cross-check against the channel-specific
   table; flag invalid combinations as errors
6. **`kk` valid for channel `c`** — cross-check against the channel-specific
   `kk` table
7. **`x` ∈ {1, 2, 3}**
8. **`e` ∈ {1, 2, 3, 4}** — when `e=4`, cross-reference the observation name
   to determine whether it means "low energy" or "13.6 TeV"
9. **Bin suffix**: if the observation is a distribution (multi-element `data`
   array), the suffix should be absent. If single-bin, suffix `_0` is
   conventional (but absence is also accepted in some datasets).
10. **Name-ID consistency**: decode the ID and check that the decoded
    description is consistent with the `name` field of the observation. If
    the name says "ATLAS" and `x=1` (CMS), flag as a likely error.
11. **Uniqueness within the data card**: no two observations should share
    the same ID. Predictions must have an ID that matches exactly one
    observation.

When the encoding clearly deviates from the spec but the name is unambiguous,
**warn but do not reject** — older datasets contain real deviations and
rejecting them would break compatibility.

---

## 6. Quick Lookup: Reverse Tables

For decoding an unfamiliar ID, use these flattened tables.

### 6.1 First three positions (`ocf`)
```
o = 1     o = 2     o = 3
LO        NLO       NNLO+

c = 1     c = 2     c = 3     c = 4     c = 5     c = 6
single t  ttbar     top decay ttZ       ttW       flavour
```

### 6.2 Common combinations seen in `Top_Full.json`

| ID prefix | Meaning |
|-----------|---------|
| `22` | NLO $t\bar t$ |
| `21` | NLO single top |
| `23` | NLO top decay |
| `24` | NLO $t\bar t Z$ |
| `25` | NLO $t\bar t W$ |
| `14` | LO $t\bar t Z$ |
| `15` | LO $t\bar t W$ |
| `19` | LO $t\bar t \gamma$ (extended `c=9`) |

### 6.3 Common $t\bar t$ kk codes
```
kk = 09 → m_tt normalized       (most common differential)
kk = 11 → total cross section
kk = 13 → pT(t_h) normalized
kk = 14 → A_C(m_tt) charge asymmetry
```

---

## 7. Cross-Reference: Systematic Uncertainty Index

Independent of the ID convention, SFitter assigns numeric indices to
systematic uncertainty sources. The complete list (both Top and Higgs sectors)
is reproduced in [`02_modifier_types.md`](02_modifier_types.md) Section 3. The
relevant top-sector indices are:

| Index | Source |
|-------|--------|
| 20 | Beam |
| 21 | BkgSch |
| 22 | BkgTTBar |
| 23 | BkgTTW |
| 24 | BkgTTZ |
| 25 | BkgTW |
| 26 | BkgTch |
| 27 | BkgWhel |
| 28 | ETmis |
| 29 | Jets |
| 30 | Leptons |
| 31 | LightTagging |
| 32 | Luminosity |
| 33 | Pileup |
| 34 | TriggerEff |
| 35 | Tune |
| 36 | bTagging |
| 37 | dummy |
| 38 | partonShower |
| 39 | tTagging |
| 40 | tauTagging |

These indices are not part of the ID encoding — they apply to the modifier
ordering within the data card. The full uncertainty catalog (including
descriptions and SFitter type codes) is in
[`05_uncertainty_catalog.md`](05_uncertainty_catalog.md).
