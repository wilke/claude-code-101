# Solution — Exercise 02 (fantasy-squad ILP)

## What this exercise is doing

The learner uses **plan mode** to *formulate* an integer linear program before writing
solver code. The artifact is `plan.md`; the point is that the hard part of an
optimization problem is stating it — separating the objective (maximize projected
points) from the constraints (budget, size, formation, country cap), and committing to
binary decision variables. This is deliberately the same lesson as the optimization
track's planning exercise: a knapsack/portfolio problem wearing a football shirt.

## What a good plan looks like

A strong `plan.md` (see `plan.md` here) states four things explicitly:

1. **Binary decision variables** `x_p ∈ {0,1}` — one per player. Not continuous; "0.4
   of a striker" is not a squad.
2. **Objective separate from constraints** — maximize `Σ proj_points·x`, and note that
   `milp` minimizes so you pass `-proj_points`.
3. **Every constraint as a linear row** — size `=11`, budget `≤B`, the four formation
   bounds, the per-country cap. A missing formation bound yields an *illegal* squad
   that still "optimizes".
4. **Solver + failure path** — `scipy.optimize.milp`, and what to do when the problem
   is infeasible.

## Running the reference solution

```bash
python squad_ilp.py --players players.csv --budget 100 --country-cap 3
```

Expected shape of the output (exact players depend on the generated `players.csv`):

```
        player   country position  price  proj_points
   Brazil GK1     Brazil       GK    6.2         41.0
   ...
--- summary ---
players:       11 (need 11)
formation:     GK=1  DEF=4  MID=4  FWD=2
spend:         99.6 / 100.0
proj points:   512.3
max per country: 3 (cap 3)
all constraints satisfied.
```

The `all constraints satisfied.` line comes from the asserts in `_report` — the plan
promised to *verify* the solution, and the code makes good on it.

## Why `scipy.optimize.milp` (and the alternatives)

`milp` wants the problem as matrices: an objective vector `c`, a stack of
`LinearConstraint(A, lb, ub)`, an `integrality` mask, and `Bounds`. That's a little
ceremony, but it's dependency-free (scipy is already in the stack) and exact for a
problem this size. PuLP and CVXPY let you write `prob += lpSum(...)  <= B` almost
verbatim — more readable, at the cost of another dependency. The README's discussion
prompt is exactly this trade-off; either answer is defensible.

## Failure modes to watch for

- **Continuous relaxation.** Forgetting `integrality` returns fractional picks — a
  different (easier, meaningless) problem. Fix: `integrality = np.ones(n)`,
  `Bounds(0, 1)`.
- **Objective sign.** `milp` minimizes; passing `+proj_points` minimizes points. Fix:
  `c = -proj_points`.
- **Missing formation bound.** Drop the GK equality and the "optimal" squad may field
  zero keepers. Fix: all four position rows, plus the size-11 equality.
- **No constraint check.** Printing the solver's output without verifying it hides a
  bad constraint row. Fix: assert size/budget/formation/cap on the returned squad.
- **Infeasible handled as a crash.** A tight budget + low cap can be infeasible; the
  script should say so (`res.success` is False), not throw an opaque error.

## Where it goes next

The stretch — a captain (points-doubling) and multi-week transfers — is where the
formulation grows: the captain adds a second 0/1 variable per player with a "captain
implies selected" coupling constraint, and transfers turn a one-shot pick into a
budgeted sequence. Both are natural next `plan.md` entries, and both are why getting
the *formulation* habit right here pays off.
