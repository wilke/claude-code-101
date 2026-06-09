"""Toy Rosenbrock solve. Used in workshop exercise 01.

This script is deliberately under-specified: no logging, no convergence
plot, a poor starting point. The exercise is to ask Claude Code to
improve it under your CLAUDE.md conventions.
"""
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


if __name__ == "__main__":
    x0 = [-1.2, 1.0, -1.2, 1.0, -1.2]  # the textbook bad start
    res = minimize(rosenbrock, x0, jac=rosenbrock_grad, method="BFGS")
    print(res)
