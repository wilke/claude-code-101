# MEMORY — Inverse Poisson capstone

Durable knowledge. Append-only. Reference plan files by filename when a
decision came out of a plan or a plan was abandoned.

## Decisions

- **2026-05-07 — Default backend: `numpy` for iteration, `petsc` for production.**
  numpy backend implements the same `forward(f)`/`adjoint(p)` interface as
  the planned PETSc backend, so the outer optimizer is interchangeable.
  petsc backend implementation tracked in
  `plans/2026-05-07-tao-implementation.md`.

- **2026-05-07 — Outer optimizer: TAO BLMVM (when on PETSc), L-BFGS-B (numpy).**
  CG stalled on the 33×33 grid around `‖∇J‖ ≈ 1e-3`; BLMVM reached `1e-8`
  in the same wall time. L-BFGS-B is the natural numpy counterpart.

- **2026-05-07 — Regularization parameter: `alpha = 1e-5` on grid 65 (was 1e-3).**
  Initial seed of `1e-3` was too aggressive — recovered f had rel L2 error
  ≈ 0.98 on grid 33 (over-regularized; recovered field essentially zero).
  Sweep over {1e-4, 1e-5, 1e-6}: `1e-5` is the L-curve corner for grid 65.
  See sweep results in `runs/2026-05-07T1730/sweep.csv`.

## Parameters

- `alpha = 1e-5` for grid 65 (decision 2026-05-07).
- `alpha = 1e-5` also reasonable on grid 33 (rel L2 error ≈ 0.72; not great
  but the best of the swept range).
- KSP tolerance: `1e-10` (tighter than outer tol so the inner solve doesn't
  inject gradient noise). Pinned in plan step 2.
- Sensor count: 30; noise sigma: 1e-2. Both fixed in `make_truth_and_obs`.

## Dead ends

*(empty for now — append entries here referencing abandoned plan files
when a direction doesn't pan out)*

Template:
```
- **<short title>.**
  See plans/<date>-<slug>.md (abandoned <date>, <one-line reason>).
  Details in <pointer to notebook or run log>.
```

## Open questions

- **DMDA vs. flat AIJ.** Out of scope of the active plan
  (`plans/2026-05-07-tao-implementation.md`); revisit when we want
  parallel scaling. Likely a follow-up plan.
- **Block-preconditioning the KKT matrix vs. reduced-space.** Reduced is
  simpler but each function evaluation costs one full PDE solve. For
  larger grids, all-at-once may be faster.
- **Sensor placement degradation.** How does the recovered `f` degrade as
  sensors are removed? Quick study; not on a plan yet.
