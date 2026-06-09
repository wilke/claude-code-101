"""KKT residual checker for a QP/NLP of the form

    min  f(x) = 0.5 x^T Q x + c^T x
    s.t. A x = b
         x >= 0

The problem module must expose `get_qp()` returning (Q, c, A, b) as numpy
arrays. The solution JSON must contain arrays "x", "y", "z".
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np


def load_problem(path: Path):
    spec = importlib.util.spec_from_file_location("problem_mod", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["problem_mod"] = mod
    spec.loader.exec_module(mod)
    return mod.get_qp()


def kkt_residuals(Q, c, A, b, x, y, z):
    grad_L = Q @ x + c - A.T @ y - z
    eq_res = A @ x - b
    return {
        "stationarity": float(np.max(np.abs(grad_L))),
        "eq_feas": float(np.max(np.abs(eq_res))),
        "primal_lb": float(np.min(x)),
        "dual_lb": float(np.min(z)),
        "complementarity": float(np.max(np.abs(x * z))),
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--problem", required=True, help="Path to a .py exposing get_qp()")
    p.add_argument("--solution", required=True, help="Path to a JSON with x, y, z arrays")
    p.add_argument("--tol", type=float, default=1e-8)
    args = p.parse_args(argv)

    Q, c, A, b = load_problem(Path(args.problem))
    Q = np.asarray(Q, dtype=float)
    c = np.asarray(c, dtype=float)
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)

    sol = json.loads(Path(args.solution).read_text())
    x = np.asarray(sol["x"], dtype=float)
    y = np.asarray(sol["y"], dtype=float)
    z = np.asarray(sol["z"], dtype=float)

    r = kkt_residuals(Q, c, A, b, x, y, z)

    print(f"Stationarity:  max |Qx + c - A^T y - z| = {r['stationarity']:.3e}")
    print(f"Primal feas:   max |A x - b|            = {r['eq_feas']:.3e}")
    print(f"               min x_i                   = {r['primal_lb']:.3e}")
    print(f"Dual feas:     min z_i                   = {r['dual_lb']:.3e}")
    print(f"Complement:    max |x_i * z_i|           = {r['complementarity']:.3e}")

    bound_violation = max(0.0, -r["primal_lb"], -r["dual_lb"])
    overall = max(r["stationarity"], r["eq_feas"], r["complementarity"], bound_violation)
    verdict = "PASS" if overall < args.tol else "FAIL"
    print(f"==> KKT residual = {overall:.3e}  (< tol = {args.tol:.2e}): {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
