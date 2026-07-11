# 2026-03-05 — SVD-based preconditioner from solution snapshots, re-init every 10 steps

Followed up February's open question. The per-step operator is fixed, but the
solution sequence u^0, u^1, … lives near a low-dimensional subspace (heat smooths
everything toward the low modes). Idea: capture that subspace with an SVD of
recent snapshots and use it to accelerate CG.

- **Snapshot POD.** Stack the last m solutions as columns of a snapshot matrix
  S, take its dominant-k left singular vectors (the POD modes), and use them to
  **deflate** CG — project out the well-captured subspace so CG only works on
  the remainder. Computing the dominant SVD of S is exactly the job the
  `lanczos` skill does (svds on S); nothing dense is ever formed.
- **Why re-initialize.** The dominant subspace drifts as the solution evolves —
  early modes are the initial transient, later ones the slow decay. Modes
  computed once at step 0 go stale, so recompute the SVD periodically on the
  most recent snapshots.

**Parameters that worked:** rank k=8 POD modes, snapshot window m=20, and
**re-initialize the SVD every 10 steps**. With deflation, CG drops from ~55 to
~12 iterations/step between re-inits — net wall-clock ~3× faster than Jacobi
over a 500-step run, *including* the periodic SVD cost.

**Decision:** the preconditioner is a rank-8 POD deflation, re-initialized every
10 steps from a 20-snapshot window, with the SVD computed via the `lanczos`
skill. The cadence of 10 is a cost/staleness balance — see the dead-end entry
for why not 1 and not 40.

**Open question:** is a fixed cadence of 10 right, or should re-init fire
*adaptively* when the CG residual stalls (i.e. when the modes have gone stale)?
Fixed-10 is what we run; adaptive is untested.

**Open question:** rank k=8 is hand-tuned. Should the rank come from the
singular-value decay (keep modes above a threshold) rather than being fixed, and
does the right rank depend on dt and the horizon?
