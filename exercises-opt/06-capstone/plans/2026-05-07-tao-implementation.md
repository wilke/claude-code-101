# Plan — TAO/PETSc backend for the inverse Poisson problem

Created: 2026-05-07
Status: active

## Goal
Replace the `NotImplementedError` stub in `run_petsc()` with a working
implementation using TAO BLMVM for the outer optimization and KSP+PCG for
the inner PDE solves. Match the numpy backend's I/O so `bench.py` can
compare them.

## Context
- numpy backend works end-to-end and passes `--check-grad` at rel error ~3e-10.
- An L-curve sweep on the numpy backend has settled `alpha = 1e-5` for the
  65×65 grid (see MEMORY.md).
- Existing `ReducedObjective.value_and_grad` already computes objective and
  adjoint gradient correctly. We can call into it from TAO if we lift its
  data structures to PETSc Vec/Mat.

## Steps

1. **PETSc Mat for the discrete Laplacian.** Wrap `laplacian_2d(N)` so it
   produces a `PETSc.Mat` (AIJ, sequential is fine for now). Verify the
   matvec matches the scipy version on a random vector to 1e-12.

2. **KSP for forward and adjoint solves.** Construct one `KSP` with PCG +
   ICC preconditioner; reuse for both forward and adjoint (operator is
   symmetric). Set `KSP_TOL=1e-10` to keep solver-induced gradient noise
   below the outer tolerance.

3. **TAO context.** Build a `PETSc.TAO` of type `blmvm`. Register objective
   and gradient via `setObjectiveGradient`. Bounds: `f >= 0` (for nonnegative
   sources) — set lower bound to a Vec of zeros, upper bound to None.

4. **Adapter from numpy to PETSc.** TAO callbacks receive `Vec`. Inside the
   callback, use `getArray()` (not copy) to view it as a numpy array,
   call `ReducedObjective.value_and_grad`, copy the gradient back into
   the PETSc gradient Vec.

5. **Run loop.** Call `tao.solve()`. Capture iteration history via a
   monitor callback. Write `runs/<timestamp>/summary.json` matching the
   numpy backend's schema, plus `runs/<timestamp>/petsc_log.txt` from
   `PETSc.Log.view()`.

6. **Smoke test (code-correctness layer).** Add `tests/test_petsc_smoke.py`
   that runs grid 17 with `alpha = 1e-5` and asserts:
   - the run terminates without exception,
   - `‖∇J‖` at termination < 1e-6,
   - rel L2 error < 0.8 (a loose bound — we just want obvious regressions).

7. **Experimental-regression test (result-quality layer).** Add
   `bench/test_recovery_regression.py` (marked `@pytest.mark.slow`) that
   runs grid 65 with `alpha = 1e-5` and asserts rel L2 error ≤ 0.6.
   Backed by the sweep recorded in MEMORY.md
   (run `2026-05-07T1730/sweep.csv`). If this test ever fails, either
   (a) we degraded the method, or (b) the parameter is no longer
   appropriate — both worth surfacing immediately.

8. **Bench harness update.** Extend `bench.py` (if present) to run both
   backends and produce a side-by-side table of (iters, time, final obj,
   rel L2 error).

## Files to be modified / created
- `poisson_inverse.py` — flesh out `run_petsc()`
- `tests/test_petsc_smoke.py` — new (code-correctness)
- `bench/test_recovery_regression.py` — new (result-quality)
- `bench.py` — new (or extend if it already exists)

## Open questions
- Should we use a DMDA instead of a flat AIJ matrix for the Laplacian?
  DMDA would parallelize for free. Out of scope for this plan; revisit
  in a follow-up.
- Default TAO line search: armijo or more-thuente? Start with TAO's
  default for BLMVM (more-thuente) and revisit if convergence is slow.

## I will not
- Touch the numpy backend or the existing tests.
- Install PETSc system-wide; assume `petsc4py` is already available
  (capstone README documents the install).
- Implement DMDA-based parallel solves — separate plan.
