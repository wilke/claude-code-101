"""
Box + budget projection.

Solves
    min_p   (1/2) ||p - s||_2^2
    s.t.    p_v in [x_lo, x_hi],     v = 1..n
            sum_v p_v <= budget.

Per-coordinate the unconstrained problem decouples; the only coupling is
the single budget constraint.  Forming the Lagrangian and eliminating the
box-multipliers gives the closed-form coordinate map

    p_v*(lambda) = clip(s_v - lambda, x_lo, x_hi),     lambda >= 0,

with lambda the multiplier on  sum p_v <= budget.  The aggregate
sum_v p_v*(lambda) is non-increasing in lambda, so:

  - If sum(clip(s, x_lo, x_hi)) <= budget, the budget constraint is inactive
    and the solution is just the elementwise clip with lambda = 0.
  - Otherwise, find lambda* > 0 by bisection (Brent) on the residual
    sum(clip(s - lambda, x_lo, x_hi)) - budget = 0.

The bisection skeleton mirrors reciprocal_approx.solve_subproblem so the two
solvers behave consistently inside the ADMM-Filter machinery.
"""

import numpy as np
from scipy.optimize import brentq


def _aggregate(s, lam, x_lo, x_hi):
    """sum_v clip(s_v - lam, x_lo, x_hi)  - the monotone budget map."""
    return np.clip(s - lam, x_lo, x_hi).sum()


def project_box_budget(s, budget, x_lo=0.0, x_hi=1.0, lam_tol=1e-12):
    """
    Euclidean projection onto { p in [x_lo, x_hi]^n : 1^T p <= budget }.

    Parameters
    ----------
    s        : (n,) array, point to project
    budget   : float, upper bound on sum(p)
    x_lo     : float, per-coordinate lower bound
    x_hi     : float, per-coordinate upper bound
    lam_tol  : float, tolerance for the budget-multiplier bisection

    Returns
    -------
    p   : (n,) projected point
    lam : float, optimal budget multiplier (0 if the constraint is inactive)
    """
    s = np.asarray(s, dtype=float)
    if x_lo > x_hi:
        raise ValueError(f"x_lo ({x_lo}) must be <= x_hi ({x_hi})")
    if budget < x_lo * len(s):
        raise ValueError(
            f"budget ({budget}) is below the minimum feasible "
            f"sum ({x_lo * len(s)}); feasible set is empty."
        )

    # --- Inactive budget case: lambda = 0 already feasible ---
    p0 = np.clip(s, x_lo, x_hi)
    if p0.sum() <= budget:
        return p0, 0.0

    # --- Active budget: find lambda* > 0 such that sum(p*(lambda*)) = budget.
    # Bracket: at lambda=0 the sum exceeds budget; for lambda large enough,
    # all coordinates clip down to x_lo and the sum equals n * x_lo <= budget
    # (guaranteed by the feasibility check above).
    lam_hi = 1.0
    while _aggregate(s, lam_hi, x_lo, x_hi) > budget:
        lam_hi *= 2.0
        if not np.isfinite(lam_hi):
            raise RuntimeError("failed to bracket budget multiplier (lam_hi -> inf)")

    def residual(lam):
        return _aggregate(s, lam, x_lo, x_hi) - budget

    lam_star = brentq(residual, 0.0, lam_hi, xtol=lam_tol)
    p_star = np.clip(s - lam_star, x_lo, x_hi)
    return p_star, lam_star


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    rng = np.random.default_rng(0)

    # ---- Inactive budget: result equals plain clip ----------------------
    s = rng.uniform(0.0, 0.4, size=20)
    p, lam = project_box_budget(s, budget=1e6, x_lo=0.0, x_hi=1.0)
    assert lam == 0.0
    assert np.allclose(p, np.clip(s, 0.0, 1.0))
    print(f"  inactive case: lam=0, p == clip(s)  (sum={p.sum():.3f}, budget=1e6)")

    # ---- Active budget: result sums to budget, KKT sign pattern is right
    n = 30
    s = rng.uniform(-0.3, 1.3, size=n)   # mix of below/in/above box
    budget = 0.4 * n
    p, lam = project_box_budget(s, budget=budget, x_lo=0.0, x_hi=1.0)

    assert abs(p.sum() - budget) < 1e-8, f"sum(p)={p.sum()}  budget={budget}"
    assert lam > 0.0
    assert (p >= 0.0 - 1e-12).all() and (p <= 1.0 + 1e-12).all()

    # KKT residuals: s - p = lam * 1  +  mu_lo - mu_hi   (mu_lo, mu_hi >= 0)
    # On interior coords (0 < p < 1):  s - p == lam.
    # On lower-clipped coords (p == x_lo): s - p <= lam   (since mu_lo >= 0 means s-p = lam - mu_lo)
    # On upper-clipped coords (p == x_hi): s - p >= lam.
    interior = (p > 1e-9) & (p < 1.0 - 1e-9)
    lower_clip = p <= 1e-9
    upper_clip = p >= 1.0 - 1e-9
    assert np.allclose(s[interior] - p[interior], lam, atol=1e-7), \
        "interior KKT failed"
    assert (s[lower_clip] - p[lower_clip] <= lam + 1e-7).all(), \
        "lower-clip KKT failed"
    assert (s[upper_clip] - p[upper_clip] >= lam - 1e-7).all(), \
        "upper-clip KKT failed"
    print(f"  active case:   lam={lam:.4f}, sum(p)={p.sum():.6f} (budget={budget})")
    print(f"                 |interior|={interior.sum()}, |lower|={lower_clip.sum()}, |upper|={upper_clip.sum()}")

    # ---- Cross-check against scipy.optimize.minimize on small n ---------
    try:
        from scipy.optimize import minimize
    except ImportError:
        print("  scipy.optimize.minimize unavailable, skipping cross-check")
    else:
        n_small = 10
        s_small = rng.uniform(-0.5, 1.5, size=n_small)
        B_small = 3.0

        def obj(p):
            return 0.5 * np.sum((p - s_small)**2)
        def obj_grad(p):
            return p - s_small

        cons = [{"type": "ineq", "fun": lambda p: B_small - p.sum()}]
        bounds = [(0.0, 1.0)] * n_small
        x0 = np.full(n_small, B_small / n_small)
        res = minimize(obj, x0, jac=obj_grad, bounds=bounds, constraints=cons,
                       method="SLSQP", options={"ftol": 1e-12})
        p_ref = res.x

        p_ours, _ = project_box_budget(s_small, B_small, x_lo=0.0, x_hi=1.0)
        diff = np.max(np.abs(p_ours - p_ref))
        assert diff < 1e-6, f"differs from SLSQP by {diff}"
        print(f"  scipy SLSQP cross-check: max|p_ours - p_ref| = {diff:.2e}")

    # ---- Edge case: budget = n * x_lo (only feasible point is all-x_lo) -
    n = 5
    s = rng.uniform(0.0, 1.0, size=n)
    p, lam = project_box_budget(s, budget=0.0, x_lo=0.0, x_hi=1.0)
    assert np.allclose(p, 0.0)
    print(f"  degenerate budget=0: p = 0 vector")

    # ---- Infeasible: budget below n * x_lo --------------------------------
    try:
        project_box_budget(np.zeros(5), budget=-1.0, x_lo=0.0, x_hi=1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("infeasible budget should raise ValueError")

    print("projection.py: all self-tests passed")
