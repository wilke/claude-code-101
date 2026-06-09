# Solution — Capstone (Inverse Poisson)

## What this exercise is doing — in plain language

There's a square room. Heat is being generated inside it according to some unknown pattern `f(x, y)`. We can't measure `f` directly, but we have temperature sensors at 30 random points inside the room reading the temperature `u(x, y)`.

Question: can we recover `f` from those 30 noisy temperature readings?

The temperature satisfies a partial differential equation called the *Poisson equation*:

```
−Δu = f       inside the unit square
 u = 0        on the boundary
```

`Δ` here is the *Laplacian* — a measure of how "curved" `u` is at each point. The equation says: where `f` is large (lots of heat being generated), `u` is curved sharply.

Recovery is hard because:

1. We have 30 measurements but the source `f` lives on a grid of (say) 33×33 = 1089 points. The problem is wildly under-determined.
2. The measurements are noisy. Tiny noise in `u` can become huge noise in `f` because the PDE smooths things out (so inverting it amplifies high frequencies).

The standard fix is **Tikhonov regularization** — add a penalty `α‖f‖²` that biases the answer toward a small `f`. Choosing `α` is an art: too large and you bias the answer toward zero; too small and noise dominates.

## What ships

- `poisson_inverse.py` — a complete numpy/scipy implementation of the forward solve, the adjoint gradient, and an L-BFGS-B outer loop. The PETSc/TAO backend is left as a stub for the participant to fill in.
- `CLAUDE.md`, `MEMORY.md` — project conventions and seed memory.

## Verifying the gradient

The first thing to do on any PDE-constrained optimization code is check that the gradient matches finite differences. Otherwise the optimizer minimizes the wrong thing and converges happily to garbage.

```
$ python poisson_inverse.py --check-grad
finite-diff: 3.241525e-02
adjoint:     3.241525e-02
rel error:   2.694e-10
```

A relative error of 2.7e-10 is what you want — within numerical noise of the finite-difference step. If you see anything above 1e-4, something is wrong with the adjoint.

## Running the numpy backend

```
$ python poisson_inverse.py --backend numpy --grid 33 --alpha 1e-3
{
  "backend": "numpy",
  "N": 33,
  "alpha": 0.001,
  "iters": 3,
  "obj": 0.0037973072356263728,
  "grad_norm": 1.5196974711556613e-11,
  "wall_seconds": 0.0018,
  "rel_l2_error": 0.9811
}
```

Look at that `rel_l2_error: 0.98`. The L-BFGS-B optimizer converged in 3 iterations (gradient is essentially zero) but the recovered `f` is **98% off** from the true source. What happened?

`α = 1e-3` is too large for this problem. The regularization term `α‖f‖²` dominated the data fit term, so the optimum is essentially `f ≈ 0`. The optimizer found that quickly and went home.

This is the classic **bias–variance tradeoff** in inverse problems. Let's sweep α:

```
$ for a in 1e-3 1e-5 1e-7 1e-9; do
    python -c "from poisson_inverse import run_numpy
              r = run_numpy(33, $a, tol=1e-10, maxiter=500)
              print(r['alpha'], r['iters'], r['rel_l2_error'])"
  done
1e-03   3  0.981     <- over-regularized (bias)
1e-05   8  0.722     <- best of these
1e-07  50  4.738     <- noise amplification
1e-09  87  8.645     <- catastrophic noise amplification
```

Two-decade window with the best result. On a 65×65 grid we can do better:

```
N=65 alpha=1e-06 iters=10 rel_l2_error=0.587
```

That's a real result — about 60% relative L2 error on a noisy inverse problem with 30 sensors and 4225 unknowns is not bad.

## What this does to MEMORY.md

The MEMORY.md that ships says:

> α = 1e-3 is a reasonable default for the noise level used in the exercise

That's wrong, and discovering it is part of the exercise. The right entry to append after running the sweep:

```markdown
## Decisions

- **2026-05-07 — Default α = 1e-5 on 33² grid, 1e-6 on 65² grid.**
  Earlier seed value of 1e-3 over-regularized — recovered f was nearly
  zero with rel_l2_error ≈ 0.98. Sweep over {1e-3, ..., 1e-9} found a
  sharp valley at 1e-5 (33²) and 1e-6 (65²) with σ_noise = 1e-2 on u_obs.
  Below those values, noise amplification dominates.
```

That's exactly the kind of fact MEMORY.md exists for. CLAUDE.md says *"the default is 1e-3"*; MEMORY.md says *"and here's why we changed it on 2026-05-07."*

## How the gradient is actually computed (brief)

You don't need to follow this to use the code, but for the curious: the objective involves solving a PDE. To compute its gradient with respect to `f`, naively you'd solve the PDE once for each component of `f` — `N²` times. The **adjoint method** computes the same gradient with one extra PDE solve, regardless of how many `f` components there are.

Here, the adjoint PDE looks identical to the forward PDE because the discrete Laplacian is symmetric. The right-hand side is the residual `r = S u − u_obs` mapped back to grid points. That's why the function `value_and_grad` calls `self._solve` twice: once forward (`u = A⁻¹ f`), once adjoint (`p = A⁻¹ Sᵀ r`).

## Filling in the PETSc/TAO backend

Use plan mode. Ask Claude:

```
plan replacing run_petsc with a real implementation: build the
discrete Laplacian as a PETSc Mat (assembled from the 5-point stencil),
use KSP+PCG with ILU for forward and adjoint solves, wrap the reduced
objective for TAO with type='blmvm', set tolerances per CLAUDE.md.
```

The plan should mention:

- DMDA vs. raw Mat construction (DMDA is cleaner for structured grids).
- `KSPSetOptionsPrefix` so forward and adjoint can be tuned independently.
- TAO's `setObjectiveGradient` callback signature (it expects a Vec, not a numpy array — there's a conversion step).
- A monitor that writes per-iteration `‖∇J‖` to `runs/<timestamp>/log.csv`.

After implementation, re-run `--check-grad` against the PETSc backend. The relative error should match the numpy backend's. If it doesn't, the PETSc adjoint is wrong — most often a missing `setTransposed=True` somewhere.

## Putting the whole workshop together

This capstone uses everything from the earlier exercises:

- **CLAUDE.md** — pinned the default tolerance, figure size, file layout.
- **Plan mode** — used before writing the PETSc backend.
- **kkt-checker skill** — use it on the unconstrained problem with `A = 0`-row, `b = []`, just to confirm the gradient is zero at the optimum.
- **MEMORY.md** — recorded the α discovery above, plus any future runs.
- **MCP** — the SQLite-logging MCP from exercise 5 is the natural place to track runs across grid sizes and α values, so you can `SELECT alpha, AVG(rel_l2_error) FROM runs GROUP BY alpha;` later.

That's the workflow. The math is hard; the engineering of the workflow is what makes the math tractable in practice.
