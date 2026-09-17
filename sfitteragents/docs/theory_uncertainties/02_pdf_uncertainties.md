# Parton Distribution Function Uncertainties

## 1. Foundations

### 1.1 Factorization Theorem

The predictive power of perturbative QCD at hadron colliders rests on collinear factorization (Collins, Soper, Sterman, Nucl. Phys. B 308 (1989) 833):

$$\sigma(pp \to X) = \sum_{a,b} \int dx_a \, dx_b \; f_a(x_a, \mu_F^2) \; f_b(x_b, \mu_F^2) \; \hat{\sigma}_{ab \to X}(\mu_F^2, \mu_R^2) + \mathcal{O}\!\left(\frac{\Lambda_{\text{QCD}}^2}{Q^2}\right)$$

PDFs $f_a(x, \mu_F^2)$ encode the non-perturbative proton structure. They evolve via DGLAP equations (Altarelli-Parisi, Nucl. Phys. B 126 (1977) 298; Gribov-Lipatov; Dokshitzer) with splitting functions known to NNLO (Moch, Vermaseren, Vogt, Nucl. Phys. B 688 (2004) 101).

### 1.2 PDF Groups and Their Sets

| Group | Release | Method | Reference |
|-------|---------|--------|-----------|
| **NNPDF** | NNPDF4.0 | MC replicas + neural networks | Ball et al., EPJC 82 (2022) 428 |
| **CT** | CT18 | Hessian eigenvectors | Hou et al., Phys. Rev. D 103 (2021) 014013 |
| **MSHT** | MSHT20 | Hessian eigenvectors | Bailey et al., EPJC 81 (2021) 341 |

**LHAPDF naming** (Buckley et al., EPJC 75 (2015) 132):
- `NNPDF40_nnlo_as_0118`: member 0 = mean PDF, members 1-100 = replicas
- `CT18NNLO`: member 0 = best-fit, members 1-58 = eigenvector pairs (at 90% CL)
- `MSHT20nnlo_as118`: member 0 = best-fit, members 1-64 = eigenvector pairs (at 68% CL)

---

## 2. Uncertainty Evaluation Methods

### 2.1 Hessian Method (CT, MSHT)

Eigenvectors of the Hessian matrix $H_{ij} = \partial^2 \chi^2 / \partial a_i \partial a_j$. For each direction $k$, two PDF sets $S_k^+$ and $S_k^-$ displaced by tolerance $T$.

**Symmetric formula** (Pumplin et al., JHEP 07 (2002) 012):

$$\Delta_{\text{PDF}} = \frac{1}{2}\sqrt{\sum_{k=1}^{N_{\text{eig}}} \left[\sigma(S_k^+) - \sigma(S_k^-)\right]^2}$$

**Asymmetric formula:**

$$\Delta^{+} = \sqrt{\sum_k \left[\max(\sigma(S_k^+) - \sigma_0,\; \sigma(S_k^-) - \sigma_0,\; 0)\right]^2}$$

$$\Delta^{-} = \sqrt{\sum_k \left[\min(\sigma(S_k^+) - \sigma_0,\; \sigma(S_k^-) - \sigma_0,\; 0)\right]^2}$$

**CL conversion**: CT18 at 90% CL → divide by 1.645 for 68% CL. MSHT20 already at 68% CL.

### 2.2 Monte Carlo Replica Method (NNPDF)

$N_{\text{rep}}$ replicas of experimental data generated with fluctuations preserving correlations; independent neural network trained on each (Ball et al., Nucl. Phys. B 849 (2011) 296).

**Central value:**

$$\langle \sigma \rangle = \frac{1}{N_{\text{rep}}} \sum_{k=1}^{N_{\text{rep}}} \sigma^{(k)}$$

**Uncertainty (68% CL):**

$$\Delta_{\text{PDF}} = \sqrt{\frac{1}{N_{\text{rep}} - 1} \sum_{k=1}^{N_{\text{rep}}} (\sigma^{(k)} - \langle\sigma\rangle)^2}$$

### 2.3 Conversion Between Methods

`mc2hessian` (Carrazza et al., EPJC 75 (2015) 369) converts MC ensemble to reduced Hessian via PCA. LHAPDF detects `ErrorType` metadata and applies the correct formula automatically.

---

## 3. $\alpha_s$ Uncertainty

**World average**: $\alpha_s(M_Z) = 0.1180 \pm 0.0009$ (PDG 2022).

**Dedicated varied-$\alpha_s$ PDF sets:**
- `NNPDF40_nnlo_as_0117` and `NNPDF40_nnlo_as_0119` ($\pm 0.001$)
- `CT18NNLO_as_0116` through `CT18NNLO_as_0120`

$$\Delta_{\alpha_s} = \frac{\sigma(\alpha_s^{+}) - \sigma(\alpha_s^{-})}{2}$$

Critical: the PDF sets at varied $\alpha_s$ must be **refitted** — cannot simply change $\alpha_s$ in the matrix element while keeping the same PDFs.

**Combined PDF + $\alpha_s$** (PDF4LHC recommendation):

$$\Delta_{\text{PDF}+\alpha_s} = \sqrt{\Delta_{\text{PDF}}^2 + \Delta_{\alpha_s}^2}$$

---

## 4. PDF Uncertainties in SMEFT Fits

### 4.1 As Theory Uncertainties

PDFs enter as a theory systematic on the prediction $\sigma_i^{(p)}(\vec{c})$. The PDF covariance matrix:

**Hessian:**

$$C_{ij}^{\text{PDF}} = \frac{1}{4}\sum_{k=1}^{N_{\text{eig}}} [\sigma_i(S_k^+) - \sigma_i(S_k^-)][\sigma_j(S_k^+) - \sigma_j(S_k^-)]$$

**MC replicas:**

$$C_{ij}^{\text{PDF}} = \frac{1}{N_{\text{rep}}-1}\sum_{k=1}^{N_{\text{rep}}} (\sigma_i^{(k)} - \langle\sigma_i\rangle)(\sigma_j^{(k)} - \langle\sigma_j\rangle)$$

### 4.2 Correlations

- **Across bins**: Highly correlated (same PDFs enter all bins of a distribution)
- **Across processes**: Correlated when processes share initial states (e.g., $t\bar{t}$ and single-top both depend on gluon and $b$-quark PDFs)
- Neglecting correlations **underestimates** PDF impact on SMEFT fits

### 4.3 PDF-EFT Interplay

If BSM effects are present in data used for PDF extraction, "SM" PDFs may absorb new physics. Key work:
- SIMUnet (Carrazza et al., Phys. Rev. D 100 (2019) 074018): simultaneous PDF + WC fits
- Greljo et al., JHEP 07 (2021) 122; Iranipour, Ubiali, JHEP 05 (2022) 032

Most relevant for: four-fermion operators in high-mass Drell-Yan (constrain same large-$x$ quark PDFs), top processes (gluon PDF vs $O_{tG}$).

**Conservative approach**: check whether SMEFT-sensitive data are included in the PDF fit being used.

---

## 5. Practical Implementation

### 5.1 MadGraph Systematics Module

Enable in `run_card.dat`:
```
True = use_syst
```

Stores per-event $x$ values, flavors, and scale choices in LHE file for reweighting.

Reweighting formula for event $e$ with PDF member $k$:

$$w_k = w_0 \times \frac{f_a^{(k)}(x_a, \mu_F) \cdot f_b^{(k)}(x_b, \mu_F)}{f_a^{(0)}(x_a, \mu_F) \cdot f_b^{(0)}(x_b, \mu_F)}$$

### 5.2 Per-Bin Extraction

For each bin $i$ and PDF member $k$:

$$\sigma_i^{(k)} = \sum_{e \in \text{bin}\,i} w_e^{(k)}$$

Then apply the Hessian or MC formula per bin and construct the full covariance matrix.

### 5.3 Practical Notes

- For the Schmal thesis top-sector analysis: NNPDF4.0 NNLO with $\alpha_s = 0.118$ was used, with 100 replica members for PDF uncertainty evaluation
- Earlier NNPDF3.1 showed positivity issues in distribution tails with SMEFT contributions; NNPDF4.0 resolved this

---

## 6. Practical Recipes

### 6.1 LHAPDF Python API

```python
import lhapdf

# Load PDF set (central + all error members)
pdfset = lhapdf.getPDFSet("NNPDF40_nnlo_as_0118")
pdfs = pdfset.mkPDFs()

print(f"Error type: {pdfset.errorType}")        # 'replicas'
print(f"Members: {pdfset.size}")                 # 101
print(f"CL: {pdfset.errorConfLevel}")            # 68

# Evaluate gluon PDF at x=0.01, Q=100 GeV
xfg = pdfs[0].xfxQ(21, 0.01, 100.0)  # member 0 (central)

# Compute uncertainty on an observable using all members
values = [compute_observable(pdf) for pdf in pdfs]
unc = pdfset.uncertainty(values)
# unc.central, unc.errsymm, unc.errplus, unc.errminus
```

The `pdfset.uncertainty()` method auto-detects the error type and applies the correct formula (MC stddev for replicas, Hessian for eigenvectors, with CL rescaling).

### 6.2 MadGraph PDF Reweighting

After generating with `use_syst = True`:

```bash
# Reweight to all members of NNPDF4.0
python <MG5_dir>/bin/systematics <run_dir>/Events/<run_name>/events.lhe.gz \
    --pdf=NNPDF40_nnlo_as_0118 --together=pdf --start_id=2001
```

Events then contain `<rwgt>` blocks with weights for each PDF member. The reweighting formula per event:

$$w_k = w_0 \times \frac{f_a^{(k)}(x_1, \mu_F) \cdot f_b^{(k)}(x_2, \mu_F)}{f_a^{(0)}(x_1, \mu_F) \cdot f_b^{(0)}(x_2, \mu_F)}$$

### 6.3 Per-Bin Covariance Matrix Construction

```python
import numpy as np
import lhapdf

pdfset = lhapdf.getPDFSet("NNPDF40_nnlo_as_0118")

# histograms: shape (n_members, n_bins)
# filled by looping events with each PDF member weight

if pdfset.errorType == "replicas":
    rep = histograms[1:]  # skip member 0
    central = np.mean(rep, axis=0)
    delta = rep - central
    cov_pdf = delta.T @ delta / (len(rep) - 1)

elif pdfset.errorType == "symmhessian":
    central = histograms[0]
    delta = histograms[1:] - central
    cov_pdf = delta.T @ delta
    if pdfset.errorConfLevel != 68:
        cov_pdf /= 1.645**2

elif pdfset.errorType == "hessian":
    central = histograms[0]
    n_eig = (histograms.shape[0] - 1) // 2
    cov_pdf = np.zeros((n_bins, n_bins))
    for i in range(n_eig):
        d = 0.5 * (histograms[2*i+1] - histograms[2*i+2])
        cov_pdf += np.outer(d, d)
    if pdfset.errorConfLevel != 68:
        cov_pdf /= 1.645**2

pdf_unc = np.sqrt(np.diag(cov_pdf))
```

### 6.4 $\alpha_s$ Variation in Practice

```python
# Reweight to alpha_s-varied PDF sets (central member only)
pdf_as_up = lhapdf.mkPDF("NNPDF40_nnlo_as_0119", 0)
pdf_as_dn = lhapdf.mkPDF("NNPDF40_nnlo_as_0117", 0)

# histograms_as_up, histograms_as_dn: shape (n_bins,)
delta_as = 0.5 * (histograms_as_up - histograms_as_dn)

# Combined PDF + alpha_s covariance
cov_as = np.outer(delta_as, delta_as)  # rank-1 (fully correlated)
cov_total = cov_pdf + cov_as
```

### 6.5 PDF4LHC21 Reduced Set

For a simplified single-set prescription (Ball et al., J. Phys. G 49 (2022) 080501):

```python
pdfset = lhapdf.getPDFSet("PDF4LHC21_40")   # 41 members, symmhessian
# Use identically to any symmetric Hessian set
# For PDF+alpha_s: use PDF4LHC21_40_pdfas (members 41,42 = alpha_s varied)
```

Use `PDF4LHC21_40` as the default for most applications. Use the full three-group comparison when PDF uncertainty is a dominant systematic or when probing extreme kinematics.

### 6.6 Cross-Process Covariance

When combining multiple processes in a fit, the same PDF member must be used consistently for both:

```python
def cross_process_cov(hist_A, hist_B, pdfset):
    """hist_A: (n_members, n_bins_A), hist_B: (n_members, n_bins_B)"""
    if pdfset.errorType == "replicas":
        dA = hist_A[1:] - np.mean(hist_A[1:], axis=0)
        dB = hist_B[1:] - np.mean(hist_B[1:], axis=0)
        return dA.T @ dB / (len(dA) - 1)
    elif pdfset.errorType == "symmhessian":
        dA = hist_A[1:] - hist_A[0]
        dB = hist_B[1:] - hist_B[0]
        cov = dA.T @ dB
        if pdfset.errorConfLevel != 68:
            cov /= 1.645**2
        return cov
```

Key correlations: $t\bar{t}$ and $gg \to H$ (both $gg$-initiated, very strong); $t\bar{t}$ and single-top (shared gluon/$b$-quark sensitivity); $W^+$ and $W^-$ (shared $u/d$ PDFs).
