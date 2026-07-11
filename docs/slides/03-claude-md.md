<!--slide n=11 layout=section kicker="Part 1 · The brief"-->
# CLAUDE.md
_A markdown file at the root of your project. Claude Code reads it at the start of every session. Treat it as the briefing document for a new collaborator._


<!--slide n=12 layout=content kicker="CLAUDE.md"-->
# CLAUDE.md, in practice
Two details make it more than a static readme:

- Keep a personal one at `~/.claude/CLAUDE.md` for cross-project preferences.
- It can reference other files: `see memory/solvers.md for our notation`.

> Mental model: the README that's specifically for the AI — it sits beside your README, doesn't replace it.


<!--slide n=13 layout=content kicker="CLAUDE.md"-->
# Why mathematicians need one
Without one, every session starts from zero. With one, Claude knows your conventions before it writes a line — notation, tooling, tolerances, tests, and hard "don'ts":

- **Notation.** `x` primal, `λ` equality mult., `μ` inequality mult.
- **Tooling & tolerances.** Pyomo / IPOPT / BARON / petsc4py; tolerances default to 1e-8.
- **Don'ts.** "No `scipy.optimize.minimize` for constrained problems — it ignores active sets near the boundary in our setup."

Each exercise supplement opens with the domain-specific version of this list.


<!--slide n=14 layout=content kicker="CLAUDE.md"-->
# Anatomy of a good CLAUDE.md
```
# Project: Inertia-Corrected Interior-Point Method

## Goal
Develop a primal-dual IPM with inertia correction for nonconvex NLPs.

## Stack
- Python 3.11, Pyomo for modeling, casadi for AD where Pyomo is awkward
- petsc4py for sparse linear algebra; mumps via PETSc as the default solver
- pytest for tests; matplotlib for figures (semilog by default)

## Commands
- `pytest -q tests/`
- `python bench/run.py --suite cutest_small`
- `python paper/figures/perf_profile.py`

## Conventions
- Variables: x (primal), y (eq mult), z (ineq mult). Use these names.
- Tolerances default to 1e-8.
- Never call scipy.optimize for constrained problems (see logbook/decisions.md).

## Pointers
- logbook/decisions.md — solver and parameter choices
- logbook/dead-ends.md — things we tried and why they failed
- docs/derivations.tex — the math in publishable form
```


<!--slide n=15 layout=section-->
# Exercise 1
_Please refer to your supplemental slide deck. Open your track's exercise:_

:::columns
### Optimization
- [Supplement slides →](slides-supplemental/exercise_slides/slides_supplement_optimization.html)
- [exercises-opt/01-claude-md/](exercises-opt/01-claude-md/)

### PDE / FEM
- [Supplement slides →](slides-supplemental/exercise_slides/slides_supplement_pde.html)
- [exercises-pde/01-claude-md/](exercises-pde/01-claude-md/)

### Linear algebra
- [Supplement slides →](slides-supplemental/exercise_slides/slides_supplement_lin_alg.html)
- [exercises-lin_alg/01-claude-md/](exercises-lin_alg/01-claude-md/)
:::
