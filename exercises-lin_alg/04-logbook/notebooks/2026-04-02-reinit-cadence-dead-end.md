# 2026-04-02 — DEAD END: re-initializing the SVD preconditioner every step

Wanted to push the SVD preconditioner harder — the intuition was "fresher modes
= better preconditioner = fewer CG iterations," so re-initialize more often. Also
tried shrinking the rank to make the SVD cheap. Neither worked; writing down why
before I forget.

## What broke (1): per-step re-init — the SVD cost eats the CG savings

Set the re-init cadence to 1 (recompute the POD SVD every step). CG iterations
dropped slightly (~12 → ~10), but the svds call now runs every step instead of
every tenth, and that cost dominates: total wall-clock went **up ~2.4×** versus
cadence-10. The preconditioner was marginally better; building it every step
cost far more than the solves it saved.

## What broke (2): rank too low — the preconditioner misses live modes

Dropped k from 8 to 2 to make the SVD cheap. CG iterations ballooned back to
~40/step: rank-2 captures only the two slowest modes, but at dt=0.01 several
mid-frequency modes are still active and undeflated. Cheap SVD, useless
preconditioner. The singular-value decay of the snapshot matrix is *gradual, not
a cliff* — there is no tiny k that captures "the" subspace.

## What broke (3): stale modes — stretching cadence to 40 steps

Opposite experiment: re-init every 40 steps to amortize the SVD further. By
~step 25 past a re-init the deflation subspace no longer matches the solution and
CG creeps from ~12 back toward ~30 iterations. The savings decay between
re-inits; 40 is too long.

## Decision

**Decision:** keep cadence = 10 and rank k = 8. Per-step re-init is abandoned —
the SVD cost is not worth it. The sweet spot re-initializes often enough that the
modes stay fresh (≲ ~15 steps) but rarely enough that the SVD amortizes (≳ ~5
steps); 10 sits in the middle and is what production uses.

## Auxiliary realization (the byproduct)

To compare cadences I needed the singular-value decay of the snapshot matrix —
cheaply, repeatedly, for both the sparse snapshot matrix and the matrix-free step
operator. That is exactly the `lanczos` skill (svds on a sparse matrix or a
matrix-free LinearOperator); it earned its keep here by setting k from where the
singular values flatten out.

---

Two days lost chasing "fresher is better." Do not re-initialize the SVD
preconditioner every step — the SVD cost dominates the CG savings. Cadence 10,
rank 8.
