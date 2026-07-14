# FantasyILP — a fantasy-squad optimizer

## Purpose

Build a fantasy-football squad optimizer: pick the 11 players that maximize projected
points under a budget, a legal formation, and a per-country cap — as an **integer linear
program** — then extend it to captaincy and multi-week transfers.

## Background

- **Method.** This is a 0/1 integer linear program, the knapsack/portfolio problem in
  disguise. `scipy.optimize.milp` solves it with no extra dependency; PuLP and CVXPY
  offer a more readable modeling layer if you want one.
- **Starting point.** The workshop's [`exercises-worldcup/02-planning/`](/exercises-worldcup/02-planning/)
  builds the single-week version with `scipy.optimize.milp` — lift its `squad_ilp.py` as
  a base.
- **Data.** `players.csv` (`player, country, position, price, proj_points`). Fantasy
  prices/projections are proprietary, so the workshop's are **synthetic**; swap in a real
  open projection source if you have one. See
  [`exercises-worldcup/DATA_SOURCE.md`](/exercises-worldcup/DATA_SOURCE.md).

## Problem Statement

Maximize `Σ proj_points·x` over binary player-selection variables `x`, subject to:

- **budget:** `Σ price·x ≤ B`
- **size:** exactly 11 players
- **formation:** 1 GK; 3–5 DEF; 3–5 MID; 1–3 FWD
- **diversity:** at most `N` players per country

Then grow the model: a **captain** (one player's points count double) and **multi-week
transfers** (a limited budget of swaps between game-weeks, carrying squad state forward).

## Suggested Approach

1. **Single-week ILP.** Model each constraint as a linear row; solve with
   `scipy.optimize.milp` (`integrality=1`, `Bounds(0,1)`). **Verify the returned squad**
   against every constraint — an ILP with a wrong row returns a confident illegal answer.
2. **Captain.** Add a second 0/1 variable `cap_p` per player with `cap_p ≤ x_p` (captain
   implies selected) and `Σ cap_p = 1`; add `Σ proj·cap` to the objective.
3. **Multi-week transfers.** Introduce per-week selection variables and transfer
   variables linking consecutive weeks, with a cap on transfers per week (and a penalty
   for exceeding it). This becomes a larger ILP over the planning horizon.
4. **Robustness (stretch).** Treat `proj_points` as uncertain and optimize a
   worst-case or chance-constrained objective.

## Outline of Tasks

1. Build and verify the single-week optimizer; confirm it's infeasibility-aware.
2. Add captaincy; check the captain is always a selected player.
3. Add a two- or three-week transfer model; show the transfer cap binding.
4. Record the formulation decisions in a short `LOGBOOK.md` (objective vs constraint,
   why binary, what happens when infeasible).
5. **Stretch:** compare `scipy.optimize.milp` against a PuLP/CVXPY rewrite for
   readability and speed; add the robust/chance-constrained variant.

## What good looks like

- The objective and every constraint are cleanly separated, and the code **asserts** the
  returned squad is legal (size, budget, formation, country cap).
- The optimizer reports **infeasibility** gracefully (tight budget + low cap) instead of
  crashing.
- Captaincy and transfers are added as *constraints and variables*, not hacks — and each
  is checked.
- A one-line writeup explains the `scipy.optimize.milp` vs PuLP/CVXPY trade-off you chose.

*Have fun — and always verify the constraints on the solution.*
