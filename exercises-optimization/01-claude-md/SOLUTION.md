# Solution — Exercise 1 (CLAUDE.md)

## What this exercise is doing

We start with a tiny script (`rosenbrock.py`) that minimizes a function called the Rosenbrock function — a classic test problem for optimization algorithms shaped like a curved valley. The script is deliberately bare: no plot, no log, a poor starting point.

The exercise asks Claude Code the same question (*"add a convergence plot"*) twice: once with no instructions, once with a CLAUDE.md. The point is to see how much the briefing matters.

## A worked CLAUDE.md

This is what your CLAUDE.md should look like after editing. Every line earns its place.

```markdown
# Project: Rosenbrock playground

## Goal
Toy problem for the workshop. We use it to demonstrate convergence plots
and our standard logging conventions.

## Stack
- Python 3.11, scipy.optimize for the inner solver
- matplotlib for figures (semilog by default)

## Commands
- `python rosenbrock.py`               # solve and print the result
- `python rosenbrock.py --plot`        # write figures/convergence.pdf

## Conventions
- Optimization variable is `x`. Always.
- Tolerance defaults to 1e-8.
- Figures go to `figures/` as PDF, 4 inches wide.
- Convergence plots: y-axis is `‖∇f‖` on log scale, x-axis iteration count.

## Don'ts
- No GUI plotting (no `plt.show()`); always save to `figures/`.
- Don't pip install new packages without asking.
```

## What Claude should produce after reading it

A reasonable response — the kind you can accept without rewriting — looks like this. The key signals are: it saves to `figures/` (not the working directory), it uses semilog axes, it captures the gradient norm at each iteration via a callback, and it doesn't import anything new.

```python
"""rosenbrock.py — solve and (optionally) plot convergence."""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize


def rosenbrock(x):
    return float(np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1.0 - x[:-1]) ** 2))


def rosenbrock_grad(x):
    g = np.zeros_like(x)
    g[:-1] += -400.0 * x[:-1] * (x[1:] - x[:-1] ** 2) - 2.0 * (1.0 - x[:-1])
    g[1:]  +=  200.0 * (x[1:] - x[:-1] ** 2)
    return g


def solve_with_history(x0, tol=1e-8):
    history = []  # gradient norms per iteration

    def cb(xk):
        history.append(float(np.linalg.norm(rosenbrock_grad(xk))))

    res = minimize(rosenbrock, x0, jac=rosenbrock_grad, method="BFGS",
                   tol=tol, callback=cb)
    return res, np.array(history)


def plot_convergence(history, out=Path("figures/convergence.pdf")):
    out.parent.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(4, 2.6))
    ax.semilogy(np.arange(1, len(history) + 1), history)
    ax.set_xlabel("iteration")
    ax.set_ylabel(r"$\|\nabla f\|$")
    fig.tight_layout()
    fig.savefig(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plot", action="store_true")
    args = ap.parse_args()

    x0 = np.array([-1.2, 1.0, -1.2, 1.0, -1.2])
    res, hist = solve_with_history(x0)
    print(res)
    if args.plot:
        plot_convergence(hist)
        print("wrote figures/convergence.pdf")
```

## What you'd expect to see

```
$ python rosenbrock.py --plot
   ...
   message: Optimization terminated successfully.
   ...
wrote figures/convergence.pdf
```

The figure is a downward-sloping line on a log scale — `‖∇f‖` shrinks from order 1 to about 1e-8 over a few dozen iterations. That shape is what convergence looks like for a well-behaved nonlinear solver.

## Where it usually goes wrong on the first try

- Claude saves the figure to `convergence.png` in the working directory instead of `figures/convergence.pdf`. **Add the rule.**
- Claude uses linear axes. **Specify "semilog by default".**
- Claude calls `plt.show()`. **Forbid it explicitly.**

The loop is the same every time: try → notice what's wrong → put the fix into CLAUDE.md → try again. After two iterations the assistant matches your house style.
