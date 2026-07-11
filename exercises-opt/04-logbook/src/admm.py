import numpy as np

from compliance import ComplianceProblem
from reciprocal_approx import reciprocal_approximation
from graph_tv import chambolle_pock_graph_tv


# ---------------------------------------------------------------------------
# Grid graph
# ---------------------------------------------------------------------------

def build_grid_edges(nelx, nely):
    """
    Edge list for the rectangular grid graph on nelx x nely elements.

    Element (elx, ely) has index  ely + elx*nely  (same convention as
    topopt.py).  Edges connect horizontally and vertically adjacent elements.
    """
    rows, cols = [], []

    # Horizontal edges: (elx, ely) -- (elx+1, ely)
    for elx in range(nelx - 1):
        for ely in range(nely):
            rows.append(ely + elx * nely)
            cols.append(ely + (elx + 1) * nely)

    # Vertical edges: (elx, ely) -- (elx, ely+1)
    for elx in range(nelx):
        for ely in range(nely - 1):
            rows.append(ely + elx * nely)
            cols.append((ely + 1) + elx * nely)

    return np.column_stack([rows, cols])


# ---------------------------------------------------------------------------
# ADMM
# ---------------------------------------------------------------------------

def admm_compliance_tv(
    nelx,
    nely,
    penal,
    alpha,
    budget,
    rho=1.0,
    x_lo=1e-4,
    max_iter=100,
    tol_primal=1e-3,
    tol_dual=1e-3,
    max_iter_x=100,
    max_iter_y=2000,
    verbose=True,
    outer_callback=None,
    x_inner_callback=None,
    y_inner_callback=None,
):
    """
    Minimise  F(x) + alpha * TV(x)
    subject to  sum_v x_v <= budget,   x in [x_lo, 1]^n

    where F is structural compliance on a nelx x nely Q4 mesh and TV is
    graph total variation over element neighbours.

    ADMM splitting:  introduce y = x, then alternate

      x-update:  min_x  F(x) + (rho/2) ||x - (y + lam/rho)||^2
                 s.t.   sum(x) <= budget,  x in [x_lo, 1]
                 --> solved by successive reciprocal approximation

      y-update:  min_y  alpha*TV(y) + (rho/2) ||y - (x - lam/rho)||^2
                 s.t.   sum(y) <= budget,  y in [x_lo, 1]
                 --> solved by Chambolle-Pock

      dual:      lam <- lam + rho * (y - x)

    Both quadratic proximal terms are written as  a_v*z_v^2 + b_v*z_v  with
      a_v = rho/2,   b_v = -rho * target_v
    so they plug directly into the existing subproblem solvers.

    Parameters
    ----------
    nelx, nely  : int, mesh dimensions (number of elements)
    penal       : float, SIMP penalisation exponent
    alpha       : float, TV regularisation weight
    budget      : float, upper bound on sum of element densities
    rho         : float, ADMM penalty parameter
    x_lo        : float, lower bound on element densities (keeps 1/x finite)
    max_iter    : int, maximum ADMM iterations
    tol_primal  : float, convergence tolerance on ||x - y||_2
    tol_dual    : float, convergence tolerance on rho*||y^k - y^{k-1}||_2
    max_iter_x  : int, inner iterations for reciprocal approximation
    max_iter_y  : int, inner iterations for Chambolle-Pock
    verbose     : bool

    Returns
    -------
    x    : (n,) design at convergence
    info : dict with keys 'y', 'lam', 'n_iter', 'converged',
                         'primal_res', 'dual_res', 'objective'
    """
    n     = nelx * nely
    edges = build_grid_edges(nelx, nely)
    fem   = ComplianceProblem(nelx, nely, penal)

    # Initialise: uniform design satisfying the budget
    x   = np.full(n, np.clip(budget / n, x_lo, 1.0))
    y   = x.copy()
    lam = np.zeros(n)

    primal_res_hist = []
    dual_res_hist   = []
    obj_hist        = []
    converged       = False

    for k in range(max_iter):
        y_prev = y.copy()

        # -------------------------------------------------------------------
        # x-update
        # min_x  F(x) + (rho/2)||x - y_hat||^2   s.t. sum(x)<=B, x in [x_lo,1]
        # where  y_hat = y + lam/rho
        #
        # Quadratic proximal term: (rho/2)x^2 - rho*y_hat*x  (per vertex)
        #   => a_v = rho/2,  b_v = -rho * y_hat_v
        # -------------------------------------------------------------------
        y_hat = y + lam / rho
        a_x   = np.full(n, rho / 2.0)
        b_x   = -rho * y_hat

        x, _ = reciprocal_approximation(
            fem, a_x, b_x, budget,
            x_init=x, max_iter=max_iter_x, tol=1e-6, x_lo=x_lo,
            callback=x_inner_callback,
        )

        # -------------------------------------------------------------------
        # y-update
        # min_y  alpha*TV(y) + (rho/2)||y - x_hat||^2   s.t. sum(y)<=B, y in [x_lo,1]
        # where  x_hat = x - lam/rho
        #
        # Quadratic data term: (rho/2)y^2 - rho*x_hat*y  (per vertex)
        #   => a_v = rho/2,  b_v = -rho * x_hat_v
        # TV weight alpha is passed directly to Chambolle-Pock.
        # -------------------------------------------------------------------
        x_hat = x - lam / rho
        a_y   = np.full(n, rho / 2.0)
        b_y   = -rho * x_hat

        y, _ = chambolle_pock_graph_tv(
            n, edges, a_y, b_y,
            budget=budget,
            alpha=alpha,
            x_lo=x_lo,
            max_iter=max_iter_y,
            tol=1e-8,
            callback=y_inner_callback,
            x_init=y,
        )

        # -------------------------------------------------------------------
        # Dual update
        # -------------------------------------------------------------------
        lam += rho * (y - x)

        # -------------------------------------------------------------------
        # Residuals and logging
        # -------------------------------------------------------------------
        primal_res = float(np.linalg.norm(x - y))
        dual_res   = float(np.linalg.norm(rho * (y - y_prev)))

        F_val, _ = fem(x)
        tv_val   = float(np.sum(np.abs(x[edges[:, 0]] - x[edges[:, 1]])))
        obj      = F_val + alpha * tv_val

        primal_res_hist.append(primal_res)
        dual_res_hist.append(dual_res)
        obj_hist.append(obj)

        if verbose:
            print(
                f"ADMM {k+1:3d} | obj={obj:.4f}  F={F_val:.4f}  TV={tv_val:.4f}"
                f" | primal={primal_res:.2e}  dual={dual_res:.2e}"
                f" | sum(x)={x.sum():.3f}"
            )

        if outer_callback is not None:
            outer_callback(x.copy(), y.copy(), k)

        if primal_res < tol_primal and dual_res < tol_dual:
            converged = True
            break

    return x, {
        "y":          y,
        "lam":        lam,
        "n_iter":     k + 1,
        "converged":  converged,
        "primal_res": np.array(primal_res_hist),
        "dual_res":   np.array(dual_res_hist),
        "objective":  np.array(obj_hist),
    }


# ---------------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    x_opt, info = admm_compliance_tv(
        nelx=30, nely=10,
        penal=3.0,
        alpha=0.5,
        budget=0.4 * 30 * 10,   # 40 % volume fraction
        rho=1.0,
        x_lo=1e-4,
        max_iter=30,
        tol_primal=1e-2,
        tol_dual=1e-2,
    )

    print(f"\nConverged : {info['converged']} in {info['n_iter']} iterations")
    print(f"sum(x*)   : {x_opt.sum():.3f}  (budget = {0.4*30*10:.1f})")
    print(f"Objective : {info['objective'][-1]:.4f}")
