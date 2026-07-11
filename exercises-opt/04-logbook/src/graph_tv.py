import numpy as np
from scipy.sparse import csr_matrix


def chambolle_pock_graph_tv(
    n_vertices,
    edges,
    a,
    b,
    budget=None,
    alpha=1.0,
    x_lo=0.0,
    max_iter=2000,
    tol=1e-8,
    callback=None,
    x_init=None,
):
    """
    Solve:
        min_{x in [x_lo,1]^V}  sum_v (a_v * x_v^2 + b_v * x_v)
                              + alpha * sum_{(u,v) in E} |x_u - x_v|
        subject to  sum_v x_v <= budget   (if budget is not None)

    via Chambolle-Pock primal-dual algorithm.

    Parameters
    ----------
    n_vertices : int
    edges      : (|E|, 2) int array of vertex index pairs
    a          : (|V|,) float array, quadratic coefficients (must be > 0)
    b          : (|V|,) float array, linear coefficients
    budget     : float or None; upper bound on sum_v x_v
    alpha      : float; weight on the TV term (dual variable lives in [-alpha, alpha])
    x_lo       : float; lower bound on each x_v
    max_iter   : int
    tol        : float, stopping criterion on max |x^{k+1} - x^k|

    Returns
    -------
    x    : (|V|,) optimal solution
    info : dict with keys 'n_iter' and 'converged'
    """
    edges = np.asarray(edges, dtype=int)
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    assert (a > 0).all(), "quadratic coefficients a must be strictly positive"

    n_edges = len(edges)
    u_idx, v_idx = edges[:, 0], edges[:, 1]

    # Signed incidence matrix D in R^{|E| x |V|}:  D_{e,u}=+1, D_{e,v}=-1
    # We store D^T in R^{|V| x |E|} for fast divergence: div = D^T y1
    rows = np.concatenate([u_idx, v_idx])
    cols = np.tile(np.arange(n_edges), 2)
    vals = np.concatenate([np.ones(n_edges), -np.ones(n_edges)])
    DT = csr_matrix((vals, (rows, cols)), shape=(n_vertices, n_edges))

    # Step sizes: need tau * sigma * ||K||^2 <= 1
    # Without budget: ||K||^2 = lambda_max(L) <= 2 * d_max
    # With budget: K = [D; 1^T], ||K||^2 = lambda_max(L + 11^T) <= 2*d_max + n
    degrees = np.bincount(rows, minlength=n_vertices)
    d_max = max(int(degrees.max()), 1)
    norm_sq = 2.0 * d_max + (n_vertices if budget is not None else 0)
    tau = sigma = 1.0 / np.sqrt(norm_sq)

    # Precompute per-vertex proximal constants (depend on tau)
    denom = 2.0 * tau * a + 1.0

    # Initialise primal (x) and dual variables
    if x_init is not None:
        x = np.clip(np.asarray(x_init, dtype=float), x_lo, 1.0)
    else:
        x = np.full(n_vertices, np.clip(0.5, x_lo, 1.0))
    y1 = np.zeros(n_edges)   # dual for TV term,       lives in [-alpha, alpha]^|E|
    y2 = 0.0                  # dual for sum constraint, lives in [0, inf)
    x_bar = x.copy()

    converged = False
    for k in range(max_iter):
        x_prev = x

        # --- Dual update for TV term ---
        # G(z) = alpha*||z||_1  =>  G*(y1) = indicator{||y1||_inf <= alpha}
        # prox_{sigma G*}(p) = clip(p, -alpha, alpha)
        y1 = np.clip(y1 + sigma * (x_bar[u_idx] - x_bar[v_idx]), -alpha, alpha)

        # --- Dual update for sum constraint (if active) ---
        # G2(t) = indicator{t <= B},  G2*(s) = B*s + indicator{s >= 0}
        # prox_{sigma G2*}(p) = max(0, p - sigma*B)
        if budget is not None:
            y2 = max(0.0, y2 + sigma * (x_bar.sum() - budget))

        # --- Primal update ---
        # w = x - tau * (D^T y1 + 1 * y2)
        # x <- clip( (w - tau*b) / (2*tau*a + 1), x_lo, 1 )
        w = x_prev - tau * (DT @ y1) - tau * y2
        x = np.clip((w - tau * b) / denom, x_lo, 1.0)

        if callback is not None:
            callback(x.copy(), k)

        # --- Extrapolation ---
        x_bar = 2.0 * x - x_prev

        if np.max(np.abs(x - x_prev)) < tol:
            converged = True
            break

    return x, {"n_iter": k + 1, "converged": converged}


def objective(x, edges, a, b):
    """Evaluate the primal objective."""
    local = np.sum(a * x**2 + b * x)
    tv = np.sum(np.abs(x[edges[:, 0]] - x[edges[:, 1]]))
    return local + tv


# ---------------------------------------------------------------------------
# Example: a small path graph
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    rng = np.random.default_rng(0)

    n = 20
    # Path graph: edges 0-1, 1-2, ..., (n-2)-(n-1)
    edges = np.column_stack([np.arange(n - 1), np.arange(1, n)])

    # Random strictly convex quadratics: f_v(x) = a_v*(x - c_v)^2
    # Expanding: a_v*x^2 - 2*a_v*c_v*x + const  =>  b_v = -2*a_v*c_v
    a = rng.uniform(0.5, 2.0, size=n)
    c = rng.uniform(0.0, 1.0, size=n)   # unconstrained minimisers of f_v
    b = -2.0 * a * c

    x_opt, info = chambolle_pock_graph_tv(n, edges, a, b)
    print("-- No budget constraint --")
    print(f"Converged: {info['converged']} in {info['n_iter']} iterations")
    print(f"Objective:  {objective(x_opt, edges, a, b):.6f}")
    print(f"sum(x*) = {x_opt.sum():.3f}")
    print(f"x* = {np.round(x_opt, 3)}")

    budget = 5.0
    x_bud, info_bud = chambolle_pock_graph_tv(n, edges, a, b, budget=budget)
    print(f"\n-- Budget constraint: sum(x) <= {budget} --")
    print(f"Converged: {info_bud['converged']} in {info_bud['n_iter']} iterations")
    print(f"Objective:  {objective(x_bud, edges, a, b):.6f}")
    print(f"sum(x*) = {x_bud.sum():.3f}  (budget = {budget})")
    print(f"x* = {np.round(x_bud, 3)}")
