import numpy as np
from scipy.optimize import brentq


# ---------------------------------------------------------------------------
# Per-vertex cubic solve
# ---------------------------------------------------------------------------

def _solve_cubics(a, beta, c, n_iter=50):
    """
    Vectorized Newton solve for the cubic h(t) = 2*a*t^3 + beta*t^2 - c = 0.

    For a > 0 and c > 0 there is exactly one positive real root.

    Starting point: to the right of the local minimum t* = max(-beta/(3a), 0),
    guaranteeing Newton converges monotonically to the positive root.
    """
    # Local minimum of h on (0, inf) is at t* = -beta/(3a) when beta < 0
    t_star = np.maximum(-beta / (3.0 * a), 0.0)

    # Cubic-term guess: h(t) ~= 2*a*t^3 => t0 = (c/(2a))^(1/3)
    t0_cubic = (c / (2.0 * a)) ** (1.0 / 3.0)

    # Start strictly to the right of t* so Newton converges to the positive root
    t = np.maximum(t0_cubic, 2.0 * t_star + 1e-10)

    for _ in range(n_iter):
        h  =  2.0 * a * t**3 + beta * t**2 - c
        dh =  6.0 * a * t**2 + 2.0 * beta * t
        dt = np.where(np.abs(dh) > 1e-300, -h / dh, 0.0)
        t  = np.maximum(t + dt, 1e-14)   # safeguard positivity

    return t


# ---------------------------------------------------------------------------
# Per-vertex optimal x for a given dual variable lambda
# ---------------------------------------------------------------------------

def _x_star(a, b, c, lam, x_lo=1e-8):
    """
    For each vertex v compute x_v*(lambda), the minimiser of

        g_v(x) + lambda * x,   g_v(x) = c_v/x + a_v*x^2 + b_v*x

    clipped to [x_lo, 1].

    c_v > 0: solve the cubic 2*a_v*t^3 + (b_v+lambda)*t^2 - c_v = 0.
    c_v <= 0: reciprocal term is concave; fall back to quadratic minimiser.
    """
    beta = b + lam
    mask = c > 0

    t = np.empty(len(a))

    if mask.any():
        t[mask] = _solve_cubics(a[mask], beta[mask], c[mask])

    if (~mask).any():
        # Quadratic minimiser: -(b+lam)/(2a), clipped to [x_lo, 1]
        t[~mask] = -beta[~mask] / (2.0 * a[~mask])

    return np.clip(t, x_lo, 1.0)


# ---------------------------------------------------------------------------
# Subproblem solver
# ---------------------------------------------------------------------------

def solve_subproblem(a, b, c, budget, lam_tol=1e-12, x_lo=1e-8):
    """
    Solve the approximating subproblem:

        min_{x in [x_lo, 1]^n, 1^T x <= budget}
            sum_v ( c_v/x_v + a_v*x_v^2 + b_v*x_v )

    via bisection on the budget Lagrange multiplier lambda >= 0.

    The aggregate sum(x*(lambda)) is decreasing in lambda, so the optimal
    lambda* is the unique root of sum(x*(lambda)) = budget (when the
    constraint is active), found by Brent's method.

    Parameters
    ----------
    a      : (n,) array, quadratic coefficients, > 0
    b      : (n,) array, linear coefficients
    c      : (n,) array, reciprocal coefficients; c_v > 0 gives a convex g_v
    budget : float
    lam_tol: float, tolerance for the lambda bisection
    x_lo   : float, lower bound on each x_v (keeps 1/x_v finite)

    Returns
    -------
    x      : (n,) optimal solution
    lam    : float, optimal dual variable
    """
    # Check whether the budget constraint is non-binding at lambda = 0
    x0 = _x_star(a, b, c, 0.0, x_lo)
    if x0.sum() <= budget:
        return x0, 0.0

    # Exponential search for an upper bracket on lambda
    lam_hi = 1.0
    while _x_star(a, b, c, lam_hi, x_lo).sum() > budget:
        lam_hi *= 2.0

    # Brent's method: find lambda* such that sum(x*(lambda*)) = budget
    def residual(lam):
        return _x_star(a, b, c, lam, x_lo).sum() - budget

    lam_star = brentq(residual, 0.0, lam_hi, xtol=lam_tol)
    return _x_star(a, b, c, lam_star, x_lo), lam_star


# ---------------------------------------------------------------------------
# Outer successive approximation loop
# ---------------------------------------------------------------------------

def reciprocal_approximation(F_and_grad, a, b, budget,
                              x_init=None, max_iter=200, tol=1e-7,
                              x_lo=1e-8, callback=None):
    """
    Solve:

        min_{x in [x_lo,1]^n, 1^T x <= budget}  F(x) + sum_v f_v(x_v)

    where f_v(x_v) = a_v*x_v^2 + b_v*x_v, via successive reciprocal
    approximation.  At each iteration, F is replaced by

        F(x_hat) + sum_v c_v * (1/x_v - 1/x_hat_v),

    with c_v = -x_hat_v^2 * (dF/dx_v)|_{x_hat} chosen to match first
    derivatives.  The resulting separable subproblem is solved exactly via
    bisection on the budget dual variable.

    Parameters
    ----------
    F_and_grad : callable(x) -> (float, (n,) array)
                 Returns (F(x), gradient of F at x).
    a          : (n,) array, quadratic coefficients, must be > 0.
    b          : (n,) array, linear coefficients.
    budget     : float, upper bound on sum(x).
    x_init     : (n,) initial point in (x_lo, 1]^n with sum <= budget, or None.
    max_iter   : int
    tol        : float, convergence tolerance on max|x^{k+1} - x^k|.
    x_lo       : float, lower bound on each x_v.

    Returns
    -------
    x    : (n,) solution
    info : dict with 'n_iter', 'converged', 'objective_history'
    """
    n = len(a)
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    assert (a > 0).all(), "quadratic coefficients a must be strictly positive"

    if x_init is None:
        x = np.full(n, np.clip(budget / n, x_lo, 1.0 - 1e-8))
    else:
        x = np.clip(np.asarray(x_init, dtype=float), x_lo, 1.0)

    obj_history = []
    converged = False

    for k in range(max_iter):
        F_val, grad_F = F_and_grad(x)
        quadratic_val = np.sum(a * x**2 + b * x)
        obj_history.append(F_val + quadratic_val)

        # Reciprocal coefficients: match dF/dx_v = -c_v / x_hat_v^2
        c = -x**2 * grad_F

        x_new, lam = solve_subproblem(a, b, c, budget, x_lo=x_lo)

        if np.max(np.abs(x_new - x)) < tol:
            converged = True
            x = x_new
            if callback is not None:
                callback(x.copy(), k)
            break

        x = x_new
        if callback is not None:
            callback(x.copy(), k)

    return x, {
        'n_iter': k + 1,
        'converged': converged,
        'objective_history': np.array(obj_history),
        'lam': lam,
    }


# ---------------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    rng = np.random.default_rng(1)
    n = 30
    budget = 10.0

    # Quadratic local terms: f_v(x) = a_v*(x - centre_v)^2
    a = rng.uniform(0.5, 2.0, n)
    centre = rng.uniform(0.1, 0.9, n)
    b = -2.0 * a * centre

    # Nonlinear F: sum of log-barrier terms (gradient always negative => c_v > 0)
    weights = rng.uniform(0.5, 2.0, n)

    def F_and_grad(x):
        F = -np.sum(weights * np.log(x))
        g = -weights / x
        return F, g

    x_opt, info = reciprocal_approximation(F_and_grad, a, b, budget)

    print(f"Converged : {info['converged']} in {info['n_iter']} iterations")
    print(f"sum(x*)   : {x_opt.sum():.6f}  (budget = {budget})")
    print(f"min / max : {x_opt.min():.4f} / {x_opt.max():.4f}")
    print(f"Objective : {info['objective_history'][-1]:.6f}")
