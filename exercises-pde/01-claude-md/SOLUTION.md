# Solution — Exercise 01 (CLAUDE.md, FEM Laplace on the unit square)

## What this exercise is doing

We start with a tiny script (`laplace_square.py`) that uses Firedrake to solve `-Δu = f` on the unit square `(0, 1)²` with homogeneous Dirichlet boundary conditions. The right-hand side `f` is chosen so that the exact solution is `u_exact(x, y) = sin(πx) sin(πy)`; this is called a *manufactured solution* and means we always know what the answer should be — including that its maximum value is 1. The script is deliberately bare: a single coarse mesh (`UnitSquareMesh(8, 8)`), one solve, hardcoded P1 elements, and `print("solve complete")`. No convergence study, no plot, no error against `u_exact`, no opinion on what polynomial order to use.

The exercise asks Claude Code the same question (*"add a convergence study"*) twice: once with no instructions, once with a CLAUDE.md. The point is to see how much the briefing matters.

## A worked CLAUDE.md

This is what your CLAUDE.md should look like after editing. Every line earns its place.

```markdown
# Project: Unit-square Laplace playground

## Goal
Toy FEM problem for the workshop. We use it to demonstrate convergence
studies and our standard figure conventions for numerical PDEs.

## Stack
- Firedrake (run inside the firedrakeproject/firedrake container)
- matplotlib for figures (saved, never shown)
- Mesh: built-in UnitSquareMesh; do not load any .msh or .geo file

## Commands
- `python laplace_square.py`                          # one solve, prints "solve complete"
- `python laplace_square.py --convergence`            # writes figures/convergence.pdf
- `python laplace_square.py --convergence --order 2`  # same, but P2 elements

## Conventions
- Element order is configurable via --order (default 1). On every
  --convergence run, prompt the user to confirm the order before
  starting the sweep, unless the same order has already been confirmed.
  Persist the confirmed value in .element_order_confirmed.
- Convergence study: sweep n in (4, 8, 16, 32, 64); print a table with
  columns n, dofs, L2 error, L2 rate, H1 error, H1 rate, max(u_h).
  Compute rates as log2(err_prev / err_curr).
- Sanity check: report max(u_h) at every level. The manufactured
  solution attains max = 1; a value far from this signals trouble.
- Figures go to figures/ as PDF, 4 inches wide.
- Convergence plot: log-log, h on x-axis (inverted so finer is to the
  right), L2 and H1 errors as connected markers, with dotted reference
  lines at the expected slopes (O(h^(p+1)) for L2, O(h^p) for H1).

## Don'ts
- No GUI plotting (no plt.show()); always save to figures/.
- Never pass a .geo file into Firedrake's Mesh() constructor; the unit
  square is built-in and that is the only mesh source for this exercise.
- Don't pip install new packages without asking — the container has
  what's needed.
```

## What Claude should produce after reading it

A reasonable response — the kind you can accept without rewriting — looks like this. The key signals are: it adds an `--order` flag (default 1) and prompts to confirm element order on first use; it computes L² and H¹ errors via `assemble`; it prints a table with both rates and `max(u_h)` per level; it saves the figure as `figures/convergence.pdf` on log-log axes with dotted reference lines for the expected slopes; it leaves the original single-solve path alone behind a `--convergence` CLI arg.

```python
"""laplace_square.py — solve and (optionally) run a convergence study."""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from firedrake import *


def manufactured(mesh):
    x, y = SpatialCoordinate(mesh)
    u_exact = sin(pi * x) * sin(pi * y)
    f = 2 * pi**2 * sin(pi * x) * sin(pi * y)
    return u_exact, f


def solve_square(mesh, degree=1):
    V = FunctionSpace(mesh, "CG", degree)
    u = TrialFunction(V)
    v = TestFunction(V)
    _, f = manufactured(mesh)
    a = inner(grad(u), grad(v)) * dx
    L = f * v * dx
    bc = DirichletBC(V, 0.0, "on_boundary")
    u_h = Function(V, name="u")
    solve(a == L, u_h, bcs=bc)
    return u_h


def errors(u_h):
    u_exact, _ = manufactured(u_h.function_space().mesh())
    e = u_h - u_exact
    l2 = sqrt(assemble(inner(e, e) * dx))
    h1 = sqrt(assemble((inner(e, e) + inner(grad(e), grad(e))) * dx))
    return float(l2), float(h1)


def convergence_study(degree=1, ns=(4, 8, 16, 32, 64)):
    rows = []
    prev_l2 = prev_h1 = None
    for n in ns:
        mesh = UnitSquareMesh(n, n)
        u_h = solve_square(mesh, degree=degree)
        l2, h1 = errors(u_h)
        m = float(u_h.dat.data.max())
        l2r = float(np.log2(prev_l2 / l2)) if prev_l2 else None
        h1r = float(np.log2(prev_h1 / h1)) if prev_h1 else None
        rows.append((n, u_h.function_space().dim(), l2, l2r, h1, h1r, m))
        prev_l2, prev_h1 = l2, h1
    return rows


def print_table(rows):
    print(f"{'n':>4}  {'dofs':>6}  {'L2 err':>10}  {'L2 rate':>8}  "
          f"{'H1 err':>10}  {'H1 rate':>8}  {'max(u_h)':>9}")
    for n, dofs, l2, l2r, h1, h1r, m in rows:
        l2rs = f"{l2r:8.2f}" if l2r is not None else "       —"
        h1rs = f"{h1r:8.2f}" if h1r is not None else "       —"
        print(f"{n:>4}  {dofs:>6}  {l2:>10.3e}  {l2rs}  {h1:>10.3e}  {h1rs}  {m:>9.4f}")


def plot_convergence(rows, degree, out=Path("figures/convergence.pdf")):
    out.parent.mkdir(exist_ok=True)
    hs = np.array([1.0 / n for n, *_ in rows])
    l2s = np.array([r[2] for r in rows])
    h1s = np.array([r[4] for r in rows])
    fig, ax = plt.subplots(figsize=(4, 2.8))
    ax.loglog(hs, l2s, "o-", label="L2 error")
    ax.loglog(hs, h1s, "s-", label="H1 error")
    # dotted reference slopes anchored at the coarsest data point
    p_l2, p_h1 = degree + 1, degree
    ax.loglog(hs, l2s[0] * (hs / hs[0]) ** p_l2, ":", color="C0",
              label=f"O(h^{p_l2})")
    ax.loglog(hs, h1s[0] * (hs / hs[0]) ** p_h1, ":", color="C1",
              label=f"O(h^{p_h1})")
    ax.set_xlabel("h"); ax.set_ylabel("error")
    ax.invert_xaxis(); ax.legend()
    fig.tight_layout()
    fig.savefig(out)


def confirm_element_order(order, marker=Path(".element_order_confirmed")):
    if marker.exists() and marker.read_text().strip() == str(order):
        return
    ans = input(f"Element order set to P{order}. Continue? [y/N] ").strip().lower()
    if ans != "y":
        sys.exit("aborted by user")
    marker.write_text(str(order))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--convergence", action="store_true")
    ap.add_argument("--order", type=int, default=1)
    args = ap.parse_args()

    if args.convergence:
        confirm_element_order(args.order)
        rows = convergence_study(degree=args.order)
        print_table(rows)
        plot_convergence(rows, degree=args.order)
        print("wrote figures/convergence.pdf")
    else:
        mesh = UnitSquareMesh(8, 8)
        u_h = solve_square(mesh)
        print("solve complete")
```

## What you'd expect to see

```
$ python laplace_square.py --convergence
Element order set to P1. Continue? [y/N] y
   n    dofs      L2 err   L2 rate      H1 err   H1 rate   max(u_h)
   4      25   2.310e-02       —      3.821e-01       —      0.8523
   8      81   5.964e-03     1.95     1.946e-01     0.97     0.9301
  16     289   1.508e-03     1.98     9.789e-02     0.99     0.9722
  32    1089   3.785e-04     1.99     4.901e-02     1.00     0.9890
  64    4225   9.471e-05     2.00     2.451e-02     1.00     0.9956
wrote figures/convergence.pdf
```

The table shows the L² rate approaching 2 and the H¹ rate approaching 1 — the textbook `O(h^(p+1))` and `O(h^p)` for P1 elements. `max(u_h)` climbs toward 1 as the mesh resolves the peak of the manufactured solution. The figure is two log-log curves (one per norm) bracketed by dotted reference lines at the expected slopes; if your data line and the reference line are parallel, you have the right rate.

(Numbers above are illustrative; expect the same shape, not exactly these values.)

## Where it usually goes wrong on the first try

- Claude saves the figure to `convergence.png` in the working directory instead of `figures/convergence.pdf`. **Add the rule.**
- Claude uses linear axes for the convergence plot. **Specify "log-log by default".**
- Claude reports only L², skipping H¹. **Pin both norms in the conventions.**
- Claude omits the dotted reference-slope lines. **Specify them — the lines are how you read the plot.**
- Claude leaves the polynomial degree hardcoded as P1. **Require an `--order` parameter and the first-run confirmation.**
- Claude calls `plt.show()`. **Forbid it explicitly.**

The loop is the same every time: try → notice what's wrong → put the fix into CLAUDE.md → try again. After two iterations the assistant matches your house style.
