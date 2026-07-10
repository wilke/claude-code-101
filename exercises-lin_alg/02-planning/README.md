# Exercise 02 — Plan an SVD of a linear operator (15 min)

**Goal.** Use plan mode to design a singular value decomposition of a linear operator that is **not a matrix** — it is only available as a matrix-free action. The deliverable is the **`plan.md`**; the lesson is that the plan has to confront the matrix-free constraint before a single line is written.

## Setup

Re-use the environment from Exercise 01 (numpy / scipy / matplotlib), activated
**before you start `claude`** so Claude runs Python in it:

```bash
conda activate linalg              # conda
# or:  source .venv/bin/activate   # pip + venv  (Windows: .venv\Scripts\activate)
```

## The operator

`heat_operator.py` is one implicit time step of the 2D heat equation on the unit square, exposed as a matrix-free linear operator: it offers `apply(v)` (its action on a vector) and `shape`, and nothing else — no matrix is ever formed. Run it for 10 time steps to see it drive the physics:

```bash
python3 heat_operator.py --steps 10
```

The peak temperature of a central hot spot decays step by step. `--N` and `--dt` set the grid and time step.

## You are the scientist (read before you start)

The catch: the object *behaves* like a matrix (you can hit any vector with it) but you **cannot index it, transpose it, or form it densely** — each `apply` is a sparse solve. An SVD of a matrix-free operator therefore has to go through a matrix-free algorithm, and the assistant will happily paper over that if you let it: the most common failure is a plan that quietly calls `np.linalg.svd(M)` on a matrix that doesn't exist, or densifies the operator to get one.

**Claude is a tool; you are the scientist.** Your job in plan mode is to force the matrix-free reality (and the choices it implies — how many modes, which algorithm, what parameters) into the plan up front.

## Steps

1. `cd exercises-lin_alg/02-planning && claude`
2. Press `Shift+Tab` twice to enter plan mode.
3. Paste the prompt and submit. Do **not** approve yet:

   ```
   Plan a singular value decomposition of the linear operator in
   heat_operator.py.

   The operator is matrix-free: it exposes only apply(v). Do not form
   or densify the matrix. If a dense representation seems necessary,
   flag it in the plan rather than assuming it.
   ```

4. **Read the plan critically.** Work through the checklist below; push back on at least one gap.
5. **Save it without running the plan.** Approving a plan tells Claude to *implement* it — so don't approve. While still in plan mode, ask:

   ```
   Write the complete plan to plan.md and stop — do not implement it.
   ```

   Claude can create a new file in plan mode, so `plan.md` lands on disk; then press **`Shift+Tab` to leave plan mode without approving**. That file is the deliverable.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Does the plan keep the operator matrix-free (wrap `apply` as `scipy.sparse.linalg.LinearOperator`)? | Densifying a matrix-free operator defeats the whole exercise. |
| Does it say how many singular values (dominant-k), not "all"? | The full SVD of an implicit operator is neither cheap nor what you want. |
| Does it name the algorithm and its cost? | `svds` / randomized SVD each cost one `apply` (a sparse solve) per matvec. |
| Does it pin the operator's parameters (`N`, `dt`)? | The SVD is of *this* discretization; unstated params make results incomparable. |
| Does it plan a correctness check? | A small-`N` dense reference is the cheap way to trust the matrix-free result. |

## Discussion prompts

- The operator is symmetric positive definite, so its singular values equal its eigenvalues. Does the plan exploit that (`eigsh`), or reach for `svds` anyway — and does it say which and why?
- Which parts of this plan are matrix-free *because they have to be*, versus choices you made for convenience?

## Optional — implement the plan (if time permits)

Approve the plan and let Claude build the matrix-free SVD, then sanity-check it against a small-`N` dense reference. Watch *how it executes*: does it follow the plan's steps in order, or combine or skip them (e.g. quietly densifying the operator to move faster)? Pacing is something you can steer — approve edits manually, or pin the constraint in `CLAUDE.md` — so where Claude rushes is a signal about where to impose more structure, not a result to just accept.

## Stretch

Extend the plan to the *k-step* operator `M^k` (k implicit steps as one action) — the object whose dominant singular vectors motivate the SVD-based preconditioner in Exercise 04.
