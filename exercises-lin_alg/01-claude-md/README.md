# Exercise 01 — Write a CLAUDE.md (15 min)

**Goal.** Experience how a CLAUDE.md changes the assistant's behavior on the *same* vague prompt, in the numerical linear algebra setting — and see exactly where `/init` can help you and where it can't. Without conventions, "find the spectrum" is under-specified in three ways at once — the matrix *type*, how it's *stored*, and what "spectrum" even *means*. `/init` infers such things from your *code*, but this folder ships only data (two matrices, no source), so `/init` has almost nothing to read — which makes the point sharply: these conventions are entirely on you. This exercise walks that boundary in three phases: ask cold, let `/init` try, then add what it couldn't have known.

## Setup

Work in a virtual environment so the exercise's packages stay isolated from your
system Python and don't clash with other projects. Create and activate it
**before you start `claude`** — Claude runs Python itself, so it uses whichever
environment is active. Use conda or pip + venv, whichever you prefer. **On
Windows, conda or the ANL compute nodes are recommended** — native venv
activation differs (`.venv\Scripts\activate`). Feel free to run on your own
machine if that doesn't worry you.

conda:

```bash
conda create -n linalg python=3.11 numpy scipy matplotlib
conda activate linalg
```

pip + venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install numpy scipy matplotlib
```

## The files

Two matrices ship with this exercise. Nothing tells you what they are — that's the point.

- `matrix_A.npy` — load with `numpy.load`.
- `matrix_B.npz` — load with `scipy.sparse.load_npz`.

One is dense, one is sparse; one is symmetric, one is not. Part of the exercise is watching whether Claude *detects* that before it computes anything.

## Phase 1 — Without a CLAUDE.md

1. With no CLAUDE.md in the folder, open a session and ask:

   ```
   find the spectrum of these matrices
   ```

2. Watch what Claude does — this is your baseline. Look for:
   - Does it **identify each matrix's type and storage** before computing, or assume?
   - Does it **densify** `matrix_B.npz` (`.toarray()`) — a 5000×5000 array — instead of using a sparse routine?
   - Does "spectrum" become **eigenvalues** or **singular values**? For the nonsymmetric matrix these differ; does Claude notice, or silently pick one?
   - Does it dump all 5000 values, or ask whether you want the **full spectrum or only the dominant few**?
   - Does it **ask you anything at all**, or just guess?

## Phase 2 — Let `/init` try

The optimization and PDE versions of this exercise lean on `/init` to read the *code* and recover the math living there. This folder is the opposite extreme: it ships only `matrix_A.npy` and `matrix_B.npz` — **no source code at all** — so this phase shows what `/init` can (and can't) do with nothing to read.

3. Reset the conversation and generate a CLAUDE.md from the folder:

   ```
   /clear
   ```

   > **Keep Claude scoped.** This folder sits inside the larger workshop repo, and its
   > `SOLUTION.md`/`README.md` give the answer away. Paste this **before** `/init` so
   > Claude builds the CLAUDE.md from *this folder's* code/data only:
   >
   > ```
   > For this exercise, treat the current folder as the entire project.
   > Build the CLAUDE.md from ONLY the code and data files in this directory.
   > Do NOT read README.md or SOLUTION.md in this folder, and do NOT read any
   > files in parent or sibling directories (the rest of the workshop repo).
   > ```

   ```
   /init
   ```

4. Read what `/init` produced. With no code to scan, expect a thin, generic CLAUDE.md: it has no way to state each matrix's **type** or **storage**, can't resolve the **eigenvalues-vs-singular-values** ambiguity, and can't pin the routines to use — none of that is written anywhere for it to read. That's the lesson in its sharpest form: **`/init` infers from code; when the knowledge isn't in the repo, it's entirely on you.**

## Phase 3 — Add what `/init` couldn't know, then iterate

5. Write the conventions `/init` had no way to infer into `CLAUDE.md` (merge them into whatever `/init` generated). A seed to start from:

   ```markdown
   # Project: Spectra of matrices and operators

   ## Stack
   - numpy / scipy (+ matplotlib for figures, saved never shown)

   ## Conventions
   - Before computing anything with a matrix, identify and state its
     TYPE (symmetric? Hermitian? nonsymmetric?) and STORAGE (dense
     ndarray, scipy sparse, or a matrix-free operator). Report both.
   - "Spectrum" is ambiguous. Do not guess. Ask the user:
     - eigenvalues or singular values?
     - the full spectrum, or only the dominant k (and what k)?
   - Choose the routine to match type + storage, and say why:
     - symmetric/Hermitian dense -> numpy.linalg.eigvalsh
     - nonsymmetric dense        -> numpy.linalg.eigvals
     - singular values (dense)   -> numpy.linalg.svd(..., compute_uv=False)
     - sparse / large            -> scipy.sparse.linalg.eigsh / svds for
       the dominant k; NEVER densify a sparse matrix.

   ## Don'ts
   - Never call .toarray() / .todense() on a sparse matrix to reuse a
     dense routine.
   - No plt.show(); save figures to figures/.
   ```

6. Reset the conversation (`/clear`) and re-ask the exact same prompt:

   ```
   find the spectrum of these matrices
   ```

7. Compare against your Phase 1 baseline. With the CLAUDE.md in place, Claude should first report that `matrix_A.npy` is a dense nonsymmetric array and `matrix_B.npz` is a large sparse symmetric matrix, then *ask* whether you want eigenvalues or singular values and how many — before computing.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did Claude identify each matrix's type and storage first? | The right algorithm depends entirely on this. |
| Did it treat the sparse matrix sparsely (no `.toarray()`)? | Densifying a 5000×5000 sparse matrix is the classic blunder. |
| Did it ask eigenvalues vs singular values? | They differ for the nonsymmetric matrix; guessing hides that. |
| Did it ask full spectrum vs dominant-k? | "All 5000 eigenvalues" is rarely what you wanted. |
| Did it report which routine it used, and why? | Is this the computation you asked for? |

## Discussion prompts

- Which of the three ambiguities (type, storage, eig-vs-svd) is Claude most likely to resolve on its own from the files, and which does it need you to pin?
- Which of these conventions is *house style* (reusable across projects) versus *this-problem* (belongs in a plan or LOGBOOK.md)?

## Stretch

Add a convention that on any sparse spectrum request Claude reports the matrix's `nnz` and density alongside the result, and refuses to densify above a size threshold you set.
