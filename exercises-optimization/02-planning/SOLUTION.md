# Solution — Exercise 2 (Planning)

## What this exercise is doing

The problem is to pick a portfolio of at most 8 stocks (out of 50) that balances expected return against risk. The "at most 8" part is what makes it hard — that's a *combinatorial* constraint, and combined with the nonlinear risk term it's a classic MINLP (mixed-integer nonlinear program).

The exercise isn't about solving it. It's about getting Claude Code to write a *plan* for solving it. The plan tells you what files will exist, what they'll do, what assumptions are being made, and what's still unclear. You read the plan and either accept or revise — before any code is written.

## What a good plan looks like

This is the kind of `plan.md` Claude should produce in plan mode. It is the deliverable; treat it like an outline you'd write before implementing a method yourself.

```markdown
# Plan — sparse portfolio MINLP

## Goal
Solve `min_w w^T Σ w − τ μ^T w  s.t.  1^T w = 1, 0 ≤ w ≤ z, 1^T z ≤ K, z ∈ {0,1}^n`
for n = 50, K = 8, τ = 0.5, with data from minlp_seed.py.

Build (a) a Pyomo model, (b) a relaxation-based heuristic that warm-starts BARON,
and (c) a benchmarking harness that records solve time, optimality gap, and
selected assets to a CSV.

## Files I will create
- `model.py`           — Pyomo formulation (continuous w, binary z, big-M link)
- `relax.py`           — continuous LP/QP relaxation; rounds top-K by w_i
- `bench.py`           — runs both, writes runs/<timestamp>/results.csv
- `tests/test_model.py`— tiny n=10 instance with a known optimum

## Step-by-step
1. Read `minlp_seed.py`. Validate Σ is positive semi-definite.
2. Implement `build_model(mu, Sigma, tau, K)` returning a Pyomo ConcreteModel.
   Use `M = 1.0` for the big-M link `w_i ≤ M z_i` (since 1^T w = 1).
3. Implement `solve_relaxation(model)` that solves the QP with z fixed in [0,1],
   returns w and a heuristic active set (top K by w_i).
4. Implement `solve_minlp(model, warm_start=None)` calling BARON if available,
   else COUENNE; both via Pyomo's solver factory.
5. Bench harness: for each of {relax-only, BARON cold, BARON warm-started},
   record: solver, status, time, objective, gap, selected indices.
6. Write to `runs/<timestamp>/results.csv` per CLAUDE.md conventions.

## Open questions for the user
- Should `tau` and `K` be CLI flags? (Default: yes.)
- BARON not free; do you have a license? If not, fall back to COUENNE.
- Cardinality K = 8 may be infeasible if mu has fewer than 8 non-negative
  entries; should we error or relax?

## Out of scope
- Performance profiles across multiple K values (separate task).
- Robust portfolio variants (uncertainty in mu).

## I will not
- Modify minlp_seed.py.
- Install BARON; assume it's already on PATH or fall back.
```

## What this catches before any code runs

- The big-M is set correctly because 1^T w = 1 makes M = 1 a tight choice. Without the plan, Claude might use M = 10 by default, which numerically loosens the relaxation.
- The license issue is surfaced *before* you discover BARON isn't installed an hour into debugging.
- The "K = 8 vs. mu" edge case is named and decided on, not silently wrong.

## How to run the exercise yourself

```
$ cd exercises/02-planning
$ claude
> # press Shift+Tab twice to enter plan mode
plan> plan a Pyomo formulation for the cardinality-constrained portfolio
       problem in minlp_seed.py, plus a relaxation-based heuristic that
       warm-starts BARON. Include a benchmarking harness that records
       solve time, optimality gap, and selected assets to a CSV.
```

When Claude returns a plan, ask:

```
write the plan to plan.md and stop. Do not implement.
```

Then read the file critically. The "Open questions" section is where 80% of the value lives.

## Stretch — same prompt, with a CLAUDE.md

Add a short CLAUDE.md to `exercises/02-planning/` first:

```markdown
# Project: Sparse-portfolio playground

## Conventions
- All runs write to runs/<ISO timestamp>/results.csv.
- CSV columns, in order: solver, status, time_s, obj, gap_pct, selected.
- All figures saved to figures/ as PDF, 4 inches wide.

## Solvers
- BARON if available (license at $BARON_LICENSE_PATH).
- COUENNE as fallback (free, slower).
- IPOPT for QP relaxations.
```

Re-ask the planning prompt. The new plan will pin down CSV column order and not invent a different one. That's the loop you want.
