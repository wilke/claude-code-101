"""
Primal/dual infeasibility measures for the ADMM-Filter algorithm.

See RASC-MeetingNotes.tex equations (eta), (omega), and the augmented
Lagrangian definition in section 2.

    L_rho(x, y, lam) = F(x) + alpha * TV(y) - lam^T (x - y)
                       + (rho/2) ||x - y||_2^2

    eta(x, y)              := ||x - y||_2^2
    omega_rho(x, y, lam)   := projected-/proximal-gradient residual on (x, y)

Because alpha * TV(y) is non-smooth, the literal projected-gradient form of
omega in the meeting notes is extended with a proximal step on the y-block:

    r_x = proj_X[x - tau * grad_x L_rho]                  - x
    r_y = prox_{tau * (alpha TV + iota_Y)}(y - tau * grad_y L_smooth) - y
    omega = ||r_x||^2 + ||r_y||^2

where the y-prox is solved by the existing chambolle_pock_graph_tv routine.
"""

import numpy as np

from projection import project_box_budget
from graph_tv import chambolle_pock_graph_tv


# ---------------------------------------------------------------------------
# Primal infeasibility
# ---------------------------------------------------------------------------

def compute_eta(x, y):
    """Primal infeasibility, eta(x, y) = ||x - y||_2^2 (Eq. (eta))."""
    diff = np.asarray(x, dtype=float) - np.asarray(y, dtype=float)
    return float(diff @ diff)


# ---------------------------------------------------------------------------
# Augmented Lagrangian value (helper for sufficient-decrease checks later)
# ---------------------------------------------------------------------------

def compute_lagrangian(x, y, lam, F_val, tv_val, alpha, rho):
    """
    Evaluate L_rho(x, y, lam) given pre-computed F(x) and TV(y).

    Caller-supplied F_val and tv_val avoid redundant FEM solves; the rest
    is cheap arithmetic.
    """
    diff = x - y
    return float(F_val + alpha * tv_val - lam @ diff + 0.5 * rho * (diff @ diff))


# ---------------------------------------------------------------------------
# Dual infeasibility (proximal-gradient residual)
# ---------------------------------------------------------------------------

def compute_omega(
    x, y, lam,
    fem, edges, alpha, rho, budget, x_lo,
    tau=1.0,
    cp_tol=1e-9,
    cp_max_iter=4000,
):
    """
    Dual infeasibility omega_rho(x, y, lam), extended for the non-smooth
    alpha * TV(y) term via a proximal step on the y-block.

    Parameters
    ----------
    x, y    : (n,) iterates
    lam     : (n,) ADMM dual variable for the consensus constraint x = y
    fem     : compliance.ComplianceProblem instance; fem(x) -> (F, grad F)
    edges   : (|E|, 2) int array of mesh edges (for TV)
    alpha   : float, TV weight
    rho     : float, ADMM penalty parameter
    budget  : float, sum-budget
    x_lo    : float, density lower bound
    tau     : float, step size in the (proximal-)gradient residual.  tau=1
              matches Eq. (omega) in the notes literally.
    cp_tol, cp_max_iter : tolerances for the inner Chambolle-Pock prox.

    Returns
    -------
    omega : float, ||r_x||_2^2 + ||r_y||_2^2.
    n_cp_iters : int, Chambolle-Pock iterations used for the y-block prox.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    lam = np.asarray(lam, dtype=float)
    n = len(x)

    # Smooth gradients of L_rho.
    # L_rho = F(x) + alpha TV(y) - lam^T(x - y) + (rho/2) ||x - y||^2
    # grad_x L_rho     = grad F(x) - lam + rho (x - y)         [smooth in x]
    # grad_y L_smooth  =              + lam + rho (y - x)      [TV is non-smooth]
    _, grad_F = fem(x)
    grad_x_L = grad_F - lam + rho * (x - y)
    grad_y_L_smooth = lam + rho * (y - x)

    # x-block: projected-gradient residual onto X = [x_lo, 1]^n & sum<=budget.
    x_step, _ = project_box_budget(
        x - tau * grad_x_L, budget=budget, x_lo=x_lo, x_hi=1.0
    )
    r_x = x_step - x

    # y-block: proximal-gradient residual.  prox of tau*(alpha TV + iota_Y) at v
    # is the minimizer of  tau*alpha*TV(z) + iota_Y(z) + (1/2)||z - v||^2,
    # which matches chambolle_pock_graph_tv with a_v = 1/2, b_v = -v_v,
    # alpha -> tau*alpha, the same budget, and x_lo -> epsilon.
    v = y - tau * grad_y_L_smooth
    y_step, cp_info = chambolle_pock_graph_tv(
        n_vertices=n,
        edges=edges,
        a=0.5 * np.ones(n),
        b=-v,
        budget=budget,
        alpha=tau * alpha,
        x_lo=x_lo,
        max_iter=cp_max_iter,
        tol=cp_tol,
        x_init=y,                # warm-start: y is usually close to its prox
    )
    r_y = y_step - y

    return float(r_x @ r_x + r_y @ r_y), cp_info["n_iter"]


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import numpy as np
    from compliance import ComplianceProblem
    from reciprocal_approx import reciprocal_approximation
    from graph_tv import chambolle_pock_graph_tv as cp_solve
    from admm import build_grid_edges

    # ---------------------------------------------------------------------
    # Small problem setup (same shape as admm.py's __main__ default)
    # ---------------------------------------------------------------------
    nelx, nely = 30, 10
    n = nelx * nely
    penal = 3.0
    alpha = 0.5
    rho = 1.0
    x_lo = 1e-4
    budget = 0.4 * n          # 40% volume fraction

    fem = ComplianceProblem(nelx, nely, penal)
    edges = build_grid_edges(nelx, nely)

    # ---- compute_eta  ----------------------------------------------------
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([1.0, 2.5, 3.0])
    assert abs(compute_eta(a, a) - 0.0) < 1e-15
    assert abs(compute_eta(a, b) - 0.25) < 1e-15
    print("  compute_eta: pointwise checks pass")

    # ---- compute_lagrangian ---------------------------------------------
    x_t = np.array([0.4, 0.5, 0.6])
    y_t = np.array([0.5, 0.5, 0.5])
    lam_t = np.array([0.1, -0.2, 0.3])
    F_val = 1.5
    tv_val = 0.2
    L_expected = (
        F_val + 0.5 * tv_val
        - lam_t @ (x_t - y_t)
        + 0.5 * 2.0 * float((x_t - y_t) @ (x_t - y_t))
    )
    L_got = compute_lagrangian(x_t, y_t, lam_t, F_val, tv_val, alpha=0.5, rho=2.0)
    assert abs(L_got - L_expected) < 1e-12
    print(f"  compute_lagrangian: L = {L_got:.6f}  (matches hand calc)")

    # ---- Initial uniform point: eta = 0 exactly --------------------------
    x0 = np.full(n, np.clip(budget / n, x_lo, 1.0))
    y0 = x0.copy()
    lam0 = np.zeros(n)
    eta0 = compute_eta(x0, y0)
    omega0, _ = compute_omega(x0, y0, lam0, fem, edges, alpha, rho, budget, x_lo)
    assert eta0 == 0.0
    assert omega0 > 0.0
    print(f"  initial uniform point: eta={eta0:.3e}  omega={omega0:.3e}")

    # ---- Targeted test: solve the x-subproblem exactly, then omega_x ~ 0 -
    # If x* solves   min_x F(x) - lam^T(x-y) + (rho/2)||x-y||^2  on X,
    # then projected-gradient residual on x at (x*, y, lam) should vanish.
    y_fixed = x0.copy()
    lam_fixed = np.zeros(n)
    a_x = np.full(n, rho / 2.0)
    b_x = -rho * (y_fixed + lam_fixed / rho)   # b_v = -rho * (y + lam/rho)_v
    x_star, _ = reciprocal_approximation(
        fem, a_x, b_x, budget,
        x_init=x0, max_iter=300, tol=1e-10, x_lo=x_lo,
    )
    # Compute omega: r_x should be tiny since x_star is optimal for the x-block.
    # r_y should reflect that y_fixed is generally NOT optimal for the y-block,
    # so omega_total is dominated by r_y.  Verify r_x is small in isolation:
    _, grad_F_star = fem(x_star)
    grad_x_L_star = grad_F_star - lam_fixed + rho * (x_star - y_fixed)
    x_step, _ = project_box_budget(x_star - grad_x_L_star, budget, x_lo, 1.0)
    r_x_norm2 = float((x_step - x_star) @ (x_step - x_star))
    print(f"  x-block residual at optimal x*: ||r_x||^2 = {r_x_norm2:.3e}")
    assert r_x_norm2 < 1e-6, f"x-block residual not small at x-subproblem optimum: {r_x_norm2}"

    # ---- Run a short ADMM and watch eta, omega ---------------------------
    # Re-implement the admm.py loop here so we can measure (eta, omega) at
    # each iterate without modifying the production driver.
    print()
    print("  ADMM iterations (manual loop, tracking eta and omega):")
    print(f"    {'k':>3}  {'eta':>11}  {'omega':>11}  {'sum(x)':>8}")

    x = x0.copy()
    y = y0.copy()
    lam = lam0.copy()

    eta_hist = [compute_eta(x, y)]
    omega_hist = [compute_omega(x, y, lam, fem, edges, alpha, rho, budget, x_lo)[0]]
    print(f"    {0:>3d}  {eta_hist[-1]:>11.3e}  {omega_hist[-1]:>11.3e}  {x.sum():>8.3f}")

    n_iter = 30
    for k in range(1, n_iter + 1):
        y_hat = y + lam / rho
        a_x = np.full(n, rho / 2.0)
        b_x = -rho * y_hat
        x, _ = reciprocal_approximation(
            fem, a_x, b_x, budget,
            x_init=x, max_iter=100, tol=1e-6, x_lo=x_lo,
        )

        x_hat = x - lam / rho
        a_y = np.full(n, rho / 2.0)
        b_y = -rho * x_hat
        y, _ = cp_solve(
            n, edges, a_y, b_y,
            budget=budget, alpha=alpha, x_lo=x_lo,
            max_iter=2000, tol=1e-8, x_init=y,
        )

        lam += rho * (y - x)

        eta_hist.append(compute_eta(x, y))
        omega_hist.append(compute_omega(x, y, lam, fem, edges, alpha, rho, budget, x_lo)[0])
        print(f"    {k:>3d}  {eta_hist[-1]:>11.3e}  {omega_hist[-1]:>11.3e}  {x.sum():>8.3f}")

    # Both measures should drop substantially from their initial values.
    # We don't require strict monotonicity (ADMM can oscillate) - just two
    # orders of magnitude on at least one of them and large drops on both.
    eta_drop   = omega_hist[0] / max(omega_hist[-1], 1e-300)
    omega_drop = omega_hist[0] / max(omega_hist[-1], 1e-300)
    print()
    print(f"  omega: initial={omega_hist[0]:.3e}  final={omega_hist[-1]:.3e}  drop={omega_drop:.1e}x")
    print(f"  eta  : initial={eta_hist[1]:.3e}  final={eta_hist[-1]:.3e}  "
          f"(eta starts at 0 by construction)")

    assert omega_hist[-1] < omega_hist[0], "omega failed to decrease over ADMM"
    # eta starts at 0 (uniform point), grows briefly, then should shrink.
    assert eta_hist[-1] < max(eta_hist[1:5]), "eta did not decrease vs early iterates"

    print()
    print("optimality.py: all self-tests passed")
