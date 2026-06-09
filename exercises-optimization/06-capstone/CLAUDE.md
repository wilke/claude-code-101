# Project: Inverse Poisson capstone

## Goal
Identify `f` in `-Δu = f` on the unit square from noisy interior measurements
of `u`, by solving a reduced-space, Tikhonov-regularized least-squares problem
with TAO.

## Stack
- petsc4py for the PDE and linear algebra (KSP + PCG, ILU preconditioner)
- PETSc.TAO for the outer optimization (BLMVM by default)
- numpy/scipy fallback (`--backend numpy`) when PETSc is not available
- matplotlib for figures

## Commands
- `python poisson_inverse.py --backend petsc --grid 65 --alpha 1e-3`
- `python poisson_inverse.py --backend numpy --grid 33 --alpha 1e-3`
- Verify gradient: `python poisson_inverse.py --check-grad`

## Conventions
- Optimization variable: `f` (the source term, vector of length `Nx * Ny`).
- All tolerances default to 1e-8.
- Figures saved to `figures/` as PDF, 4 inches wide. Convergence plots
  use semilog on the y-axis (`‖∇J‖`) and linear on the x-axis (iteration).
- Run logs go to `runs/<timestamp>/`. Each run writes `summary.json`.

## Don'ts
- Don't pip install new packages without asking.
- Don't replace the adjoint with a finite-difference gradient — we want the
  exact adjoint for verification.

## Testing
- After any code edit: run `pytest -q tests/` and surface failures in the
  next reply before continuing. Don't claim done until tests pass.
- For changes touching solver behavior, also run
  `pytest -q -m slow bench/` and report rel L2 error and iteration count.
- Code-correctness tests live in `tests/`; experimental-regression tests
  live in `bench/` (marked `@pytest.mark.slow`).

## Pointers
- MEMORY.md — durable decisions and parameter choices for this project
- STATUS.md — where the work stands right now (overwritten each session)
- ../03-skills/skills/kkt-checker — verify the optimum

## Session ritual
- Start of session: read STATUS.md to know where to pick up.
- End of session: append a dated entry to MEMORY.md if anything was
  *decided*; overwrite STATUS.md with the current next step.
