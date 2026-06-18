"""Toy Rosenbrock solve. Used in workshop exercise 01."""
import numpy as np
from scipy.optimize import minimize


def rosenbrock(x):
    return sum(100.0 * (x[i + 1] - x[i] ** 2) ** 2 + (1.0 - x[i]) ** 2
               for i in range(len(x) - 1))


def rosenbrock_grad(x):
    n = len(x)
    g = [0.0] * n
    for i in range(n - 1):
        g[i] += -400.0 * x[i] * (x[i + 1] - x[i] ** 2) - 2.0 * (1.0 - x[i])
        g[i + 1] += 200.0 * (x[i + 1] - x[i] ** 2)
    return g


def solve(x0):
    history = []  # list of ||grad f|| per iteration

    def cb(xk):
        f = rosenbrock(xk)
        gn = float(np.linalg.norm(rosenbrock_grad(xk)))
        history.append(gn)
        print(f"iter {len(history):3d}  f={f:.6e}  ||grad f||={gn:.3e}")

    res = minimize(rosenbrock, x0, jac=rosenbrock_grad, method="BFGS",
                   callback=cb)
    return res, history


if __name__ == "__main__":
    x0 = [-1.2, 1.0, -1.2, 1.0, -1.2]  # the textbook bad start
    res, _ = solve(x0)
    print(res)
