"""Inverse Poisson source identification — workshop capstone skeleton.

Solves

    min_f  0.5 || S u(f) - u_obs ||^2 + alpha || f ||^2
    s.t.   u(f) solves   -Delta u = f  on (0,1)^2,
                          u = 0       on the boundary.

The PDE is discretized by the standard 5-point stencil on a uniform grid.
The reduced gradient is computed by the adjoint method: solving the same
discrete operator with the residual as RHS gives the gradient up to a
mass-weighting factor (here `h^2` because the grid is uniform).

Two backends are provided:

* `numpy` — scipy.sparse.linalg.spsolve for the PDE solve, scipy.optimize
  L-BFGS-B for the outer problem. Use this if PETSc is not installed.
* `petsc` — petsc4py + KSP for the PDE, PETSc.TAO for the outer problem.
  Use this on a real workstation with PETSc set up.

The exercise is to turn this skeleton into a complete, well-instrumented
implementation, guided by Claude Code in plan mode. See README.md.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from scipy.sparse import diags, eye, kron
from scipy.sparse.linalg import factorized


# --------------------------------------------------------------------------
# Discretization
# --------------------------------------------------------------------------

def laplacian_2d(N: int):
    """Discrete -Δ with homogeneous Dirichlet BCs on an N×N interior grid.

    Returns a sparse (N^2, N^2) matrix scaled by 1/h^2, h = 1/(N+1).
    """
    h = 1.0 / (N + 1)
    e = np.ones(N)
    T = diags([-e[:-1], 2 * e, -e[:-1]], offsets=[-1, 0, 1])
    I = eye(N)
    A = (kron(I, T) + kron(T, I)) / h**2
    return A.tocsc(), h


def make_truth_and_obs(N: int, n_sensors: int = 30, noise_sigma: float = 1e-2,
                       rng: np.random.Generator | None = None):
    """Return (f_true, S, u_obs) for a synthetic problem."""
    rng = rng or np.random.default_rng(0)
    h = 1.0 / (N + 1)
    xs = np.linspace(h, 1 - h, N)
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    f_true = (np.exp(-((X - 0.3) ** 2 + (Y - 0.3) ** 2) / 0.05) +
              0.5 * np.exp(-((X - 0.7) ** 2 + (Y - 0.7) ** 2) / 0.03))
    f_true = f_true.ravel()

    A, _ = laplacian_2d(N)
    solve = factorized(A)
    u_true = solve(f_true)

    sensor_idx = rng.choice(N * N, size=n_sensors, replace=False)
    S = np.zeros((n_sensors, N * N))
    S[np.arange(n_sensors), sensor_idx] = 1.0

    u_obs = S @ u_true + noise_sigma * rng.standard_normal(n_sensors)
    return f_true, S, u_obs


# --------------------------------------------------------------------------
# Reduced-space objective and adjoint gradient (numpy backend)
# --------------------------------------------------------------------------

class ReducedObjective:
    def __init__(self, N: int, S: np.ndarray, u_obs: np.ndarray, alpha: float):
        self.N = N
        self.A, self.h = laplacian_2d(N)
        self._solve = factorized(self.A)
        self.S = S
        self.u_obs = u_obs
        self.alpha = alpha
        self.history = []

    def value_and_grad(self, f: np.ndarray):
        u = self._solve(f)
        r = self.S @ u - self.u_obs
        J = 0.5 * r @ r + self.alpha * (f @ f)

        # Adjoint: A^T p = S^T r. A is symmetric here.
        p = self._solve(self.S.T @ r)
        grad = p + 2.0 * self.alpha * f
        self.history.append((J, np.linalg.norm(grad)))
        return J, grad


# --------------------------------------------------------------------------
# Drivers
# --------------------------------------------------------------------------

def run_numpy(N: int, alpha: float, tol: float = 1e-8, maxiter: int = 200):
    from scipy.optimize import minimize
    f_true, S, u_obs = make_truth_and_obs(N)
    obj = ReducedObjective(N, S, u_obs, alpha)

    f0 = np.zeros(N * N)
    t0 = time.time()
    res = minimize(obj.value_and_grad, f0, jac=True, method="L-BFGS-B",
                   options={"gtol": tol, "maxiter": maxiter, "ftol": 1e-14})
    elapsed = time.time() - t0

    return {
        "backend": "numpy",
        "N": N,
        "alpha": alpha,
        "iters": res.nit,
        "obj": float(res.fun),
        "grad_norm": float(np.linalg.norm(res.jac)),
        "wall_seconds": elapsed,
        "rel_l2_error": float(np.linalg.norm(res.x - f_true) / np.linalg.norm(f_true)),
    }


def run_petsc(N: int, alpha: float, tol: float = 1e-8, maxiter: int = 200):
    """Stub. Implement with petsc4py + TAO as part of the capstone exercise.

    Suggested approach:
      * Wrap `laplacian_2d(N)` as a PETSc Mat (or build directly with DMDA).
      * Use a KSP + PCG with ILU preconditioner for forward and adjoint solves.
      * Use TAO with type='blmvm', set objective+gradient via `setObjectiveGradient`.
      * Write convergence log to runs/<timestamp>/summary.json.
    """
    raise NotImplementedError(
        "PETSc backend is left as the capstone implementation step. "
        "Use plan mode in Claude Code: see README.md."
    )


def check_grad(N: int = 17, alpha: float = 1e-3, h: float = 1e-6):
    """Finite-difference check of the adjoint gradient — sanity test."""
    f_true, S, u_obs = make_truth_and_obs(N)
    obj = ReducedObjective(N, S, u_obs, alpha)

    rng = np.random.default_rng(42)
    f = rng.standard_normal(N * N)
    d = rng.standard_normal(N * N)

    J0, g = obj.value_and_grad(f)
    Jp, _ = obj.value_and_grad(f + h * d)
    Jm, _ = obj.value_and_grad(f - h * d)

    fd = (Jp - Jm) / (2 * h)
    ad = g @ d
    rel = abs(fd - ad) / max(abs(ad), 1e-16)
    print(f"finite-diff: {fd:.6e}")
    print(f"adjoint:     {ad:.6e}")
    print(f"rel error:   {rel:.3e}")
    return rel


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--backend", choices=["numpy", "petsc"], default="numpy")
    p.add_argument("--grid", type=int, default=33)
    p.add_argument("--alpha", type=float, default=1e-3)
    p.add_argument("--check-grad", action="store_true")
    p.add_argument("--out", type=Path, default=Path("runs"))
    args = p.parse_args()

    if args.check_grad:
        check_grad()
        return

    runner = run_numpy if args.backend == "numpy" else run_petsc
    summary = runner(args.grid, args.alpha)

    args.out.mkdir(exist_ok=True)
    stamp = time.strftime("%Y-%m-%dT%H%M%S")
    run_dir = args.out / stamp
    run_dir.mkdir()
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(f"\nWrote {run_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
