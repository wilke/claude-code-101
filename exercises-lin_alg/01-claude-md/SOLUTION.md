# Solution — Exercise 01 (CLAUDE.md, spectra of matrices)

## What this exercise is doing

Two matrices ship with the exercise: `matrix_A.npy` (a 200×200 dense, **nonsymmetric** real array) and `matrix_B.npz` (a 5000×5000 **sparse, symmetric** matrix in CSR format). Their names and file types are deliberately uninformative about their mathematical structure. The learner asks the same vague question — *"find the spectrum of these matrices"* — across three phases: once cold (Phase 1), once after `/init` (Phase 2), and once with a hand-written CLAUDE.md (Phase 3). The word "spectrum" hides three separate ambiguities:

1. **Type** — symmetric vs nonsymmetric decides `eigvalsh` vs `eigvals` (and whether eigenvalues are real).
2. **Storage** — dense vs sparse decides whether you may form the whole matrix or must use an iterative routine; densifying `matrix_B` is a 5000×5000 = 25M-entry mistake.
3. **Meaning** — eigenvalues vs singular values (they coincide only for symmetric PSD matrices; `matrix_A` is neither) and full spectrum vs dominant-k.

The point is that a good CLAUDE.md converts all three silent guesses into explicit, up-front questions.

## Phase 2 — what `/init` produces here (almost nothing)

This folder ships **only data** — `matrix_A.npy` and `matrix_B.npz`, no source code — so `/init` has nothing to read. Expect a thin, generic CLAUDE.md: it cannot state either matrix's type or storage, cannot resolve eig-vs-svd, and cannot pin the routines, because none of that is written anywhere for it to find. That is the lesson in its sharpest form — `/init` infers from *code*, and when the knowledge isn't in the repo, the conventions below are entirely on you.

## A worked CLAUDE.md (Phase 3)

```markdown
# Project: Spectra of matrices and operators

## Stack
- numpy / scipy (+ matplotlib for figures, saved never shown)

## Conventions
- Before computing anything with a matrix, identify and state its TYPE
  (symmetric? Hermitian? nonsymmetric?) and STORAGE (dense ndarray,
  scipy sparse, matrix-free operator). Report both before proceeding.
- "Spectrum" is ambiguous — do not guess. Ask the user:
  - eigenvalues or singular values?
  - the full spectrum, or only the dominant k (and what k)?
- Match the routine to type + storage, and say why:
  - symmetric/Hermitian dense -> numpy.linalg.eigvalsh
  - nonsymmetric dense        -> numpy.linalg.eigvals
  - singular values (dense)   -> numpy.linalg.svd(..., compute_uv=False)
  - sparse / large            -> scipy.sparse.linalg.eigsh / svds for the
    dominant k; NEVER densify a sparse matrix.

## Don'ts
- Never call .toarray() / .todense() on a sparse matrix to reuse a dense routine.
- No plt.show(); save figures to figures/.
```

## What Claude should produce after reading it

The accept-without-rewriting response comes in two moves. **First**, Claude inspects and reports, then asks — it does *not* compute yet:

> `matrix_A.npy` is a **dense** `ndarray`, shape (200, 200), and is **nonsymmetric** (`A != A.T`), so its eigenvalues are complex and differ from its singular values.
> `matrix_B.npz` is a **sparse** CSR matrix, shape (5000, 5000), `nnz = 49945` (~0.2% dense), and is **symmetric**.
> Before I compute: do you want **eigenvalues or singular values**, and the **full spectrum or the dominant k**? (For `matrix_B`, the full 5000-length spectrum needs a dense eigensolver; the dominant-k is cheap via `eigsh`.)

**Then**, once the user answers (say: "dominant 6 — eigenvalues for the symmetric one, both eig and svd for the nonsymmetric one"), it runs the type/storage-appropriate routines:

```python
"""spectrum.py — report requested spectra, matched to type and storage."""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh

A = np.load("matrix_A.npy")                 # dense, nonsymmetric
B = sp.load_npz("matrix_B.npz")             # sparse, symmetric

# A: nonsymmetric dense -> eigenvalues are complex; also report singular values
eig_A = np.linalg.eigvals(A)
svd_A = np.linalg.svd(A, compute_uv=False)
print("matrix_A (dense, nonsymmetric):")
print("  |lambda| max/min:", abs(eig_A).max(), abs(eig_A).min())
print("  sigma    max/min:", svd_A.max(), svd_A.min())

# B: sparse symmetric -> dominant-k via eigsh, never densified
k = 6
eig_B = eigsh(B, k=k, which="LM", return_eigenvectors=False)
print(f"matrix_B (sparse, symmetric): dominant {k} eigenvalues (|.|):")
print("  ", np.sort(eig_B))
```

## What you'd expect to see

```
matrix_A (dense, nonsymmetric):
  |lambda| max/min: 14.7 ...  0.21 ...
  sigma    max/min: 28.3 ...  0.06 ...
matrix_B (sparse, symmetric): dominant 6 eigenvalues (|.|):
   [-3.29 ... -3.11 ...  3.05 ...  3.14 ...  3.22 ...  3.36 ...]
```

The eigenvalues of `matrix_A` scatter in the complex plane (magnitudes up to ~√n·√n·… — circular-law scale), and its singular values are real and larger than `|λ|`, making the eig-vs-svd distinction concrete. `matrix_B`'s dominant eigenvalues come in both signs (it's indefinite), so `|λ| ≠ λ` — a second place where "eigenvalues or singular values?" actually matters. *(Numbers illustrative; expect the same shape, not these exact values.)*

## Where it usually goes wrong on the first try

- Claude calls `matrix_B.toarray()` (or `np.load` on the `.npz`) and runs a dense eigensolver on 5000×5000. **Add the don't-densify rule.**
- Claude picks eigenvalues (or singular values) without asking, hiding that they differ for the nonsymmetric matrix. **Require the eig-vs-svd question.**
- Claude computes and prints all 5000 eigenvalues of `matrix_B`. **Require the full-vs-dominant-k question.**
- Claude uses `eigvalsh` (symmetric solver) on `matrix_A` and reports real eigenvalues — silently wrong. **Require type identification first.**
- Claude never states type/storage, so you can't tell whether the result means what you think. **Pin "identify and report type + storage before computing."**

The loop is the same every time: ask → notice a silent guess → put the rule in CLAUDE.md → re-ask. After one iteration the assistant reports type/storage and asks its clarifying questions before touching the data.
