# Plan — fantasy-squad ILP

A model of the `plan.md` a good plan-mode session produces. The point is a clean
separation of **objective**, **decision variables**, and each **constraint** — stated
as prose you can check before any solver runs.

## Goal

Pick the 11-player fantasy squad from `players.csv` that maximizes total projected
points, subject to a budget, a legal formation, and a per-country cap. Produce a
solver script and a printed squad with a constraint check.

## Inputs / outputs

- **Input:** `players.csv` (`player, country, position, price, proj_points`).
- **Outputs:** `squad_ilp.py`, and a printed squad + summary (spend, formation counts,
  max-per-country) with an assertion that every constraint holds.

## Formulation

**Decision variables.** For each player `p`, a binary `x_p ∈ {0, 1}` — 1 if selected.
Binary, not continuous: you can't field 0.4 of a striker.

**Objective.** Maximize `Σ_p proj_points_p · x_p`. `scipy.optimize.milp` minimizes, so
pass `c = -proj_points`.

**Constraints (each a linear row):**

1. **Squad size:** `Σ_p x_p = 11` (equality).
2. **Budget:** `Σ_p price_p · x_p ≤ B` (default `B = 100`).
3. **Formation** (indicator sums over each position):
   - GK: `Σ x_p = 1`
   - DEF: `3 ≤ Σ x_p ≤ 5`
   - MID: `3 ≤ Σ x_p ≤ 5`
   - FWD: `1 ≤ Σ x_p ≤ 3`
   (These force the outfield ten into a legal shape; they sum to 11 with the GK.)
4. **Diversity:** for every country `c`, `Σ_{p in c} x_p ≤ 3`.

**Solver.** `scipy.optimize.milp` with `integrality = 1` for all variables and
`Bounds(0, 1)`. (PuLP/CVXPY would express the constraints more readably; not required.)

## Steps

1. Load `players.csv`; extract `price`, `proj_points`, and position/country indicator
   groups.
2. Build the objective vector `c = -proj_points`.
3. Assemble the constraints above as `LinearConstraint` rows.
4. Solve with `milp`; if `res.success` is False, **report infeasibility** (e.g. budget
   too low for the country cap) rather than crashing.
5. Read the selected players (`x_p > 0.5`), print the squad sorted by position, and
   print spend / formation counts / max-per-country.

## Sanity checks (the plan promises these)

- Exactly 11 players selected.
- Total spend ≤ budget.
- Each position within its formation bounds.
- No country over the cap.
Assert each on the returned solution — an ILP that returns an illegal squad means a
missing or wrong constraint row, and the assert is how you catch it.

## Non-goals (this round)

- No captain (points-doubling) and no multi-week transfers — see the stretch.
- No re-projection of points; `proj_points` is taken as given.
