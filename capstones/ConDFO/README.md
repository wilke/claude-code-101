# Capstone Project: ConDFO

## Purpose

Build a constrained derivative-free optimization solver

## Background

- **Key Reference:** Larson, menickelly, Wild. "Derivative-free optimization methods". Acta Numerica. 2019;28:287-404. doi:10.1017/S0962492919000060
- **Related Solvers:**
  - libEnsemble `https://libensemble.readthedocs.io/en/main/index.html`
    - Optimization with APOSSM `https://libensemble.readthedocs.io/en/main/tutorials/aposmm_tutorial.html#`
    - Optimization with XOPT `https://libensemble.readthedocs.io/en/main/tutorials/xopt_bayesian_gen.html`
    - git repo `https://github.com/Libensemble` (library to coordinate the concurrent evaluation of dynamic ensembles of calculations)
  - XOPT Flexible Optimizer `https://xopt.xopt.org/`

## Problem Statement

Develop a **constrained** derivative-free optinmization solver for the following problem:
\[
\min_x \; f(x) \quad \text{s.t.} \; l \le c(x) \le u, \; x \in X,
\]
where
- $f(x)$ and $c(x)$ are nonlinear functions that involve a simulation (**derivatives not available**) 
- $l, u$ are bounds (can be infinite)
- $X$ is a *simple* closed and convex set
Plan to allow for more structure such as linear constraints that the solver can exploit.

## Suggested Approach

We will use a model-based approach that solves a *sequence of easier subproblems* where $f(x), c(x)$ are replaced by *model functions* with known approximation properties. 
Letting $m^f(x), m^c(x)$ denote the models constructed at the current iterate $x_k$, the algorithm solves the following subproblem for a possible new iterate, $\hat{x}$:

$$
\min_x \; m^f(x) \quad \text{s.t.} \; l \le m^c(x) \le u, \; x \in X, \; \| x - x_k \| \le \Delta_k
$$

where $\Delta_k>0$ is a trust-region radius.

### Algorithmic Choices 

1. Construction of models, $m^f(x), m^c(x)$. Consider using quadratic models that interpolate/approximate $f(x), c(x)$ at a set of points, $x_{k}, x_{k-1}, \ldots, x_{k-M}$, where $M>1$ is a memory length.
2. Acceptance of steps: Not every new point $\hat{x}$ improves. Evaluate $f(\hat{x}), c(\hat{x})$ and use a penalty finction or filter to measure improvement.
3. Adding new points to the memory.
4. Controlling the trust-region radius $\Delta_k$. E.g. decrease if steps no good, increase if good.

### Efficiency Considerations (stretch)

1. How can you exploit parallel function evaluations?
2. Start-up: Making progress while building an initial memory.
3. Convergence and termination: avoid having to set $\Delta \to 0$.

## Outline of Tasks

1. Literature survey; concentrate on **constrained** problems/solvers.
2. Decide on subproblem solver; consider `unopy`; allow flexible solvers.
3. Create/download some simple test problems; e.g. Hock-Schittkowski set.
4. Create a latex document with the problem statement and approach/algorithm.
5. Plan the solver design; allow for flexible interfacing (plug into xopt/libensemble).
6. Test the solver on some academic and real test problems (ask Jeff, Matt, ...).
7. Finish the paper: Can you write a convergence analysis for the filter method?
8. Submit to SISC and win the SIAM Best Paper Prize :-)

*Good Luck!*

