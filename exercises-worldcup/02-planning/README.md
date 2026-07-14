# Exercise 02 — Plan a fantasy-squad ILP (15 min)

**Goal.** Use **plan mode** to agree the *formulation* of a constrained optimization
problem — pick the fantasy squad that maximizes projected points under a budget, a
legal formation, and a per-country cap — **before** any solver code is written. The
deliverable is the **`plan.md`**; the lesson is that the hard part of an optimization
problem is stating it correctly (what's the objective, what's a constraint, what's a
variable), and a plan is where you get the formulation right while it's still prose.

This is the **knapsack / portfolio analogue** of the optimization track's planning
exercise — the lesson transfers verbatim; only the story changed.

## Setup

Re-use the track environment (pandas / numpy / scipy), activated **before you start
`claude`**:

```bash
conda activate worldcup            # conda
# or:  source .venv/bin/activate   # pip + venv
```

Keep the `CLAUDE.md` from Exercise 01.

## The file

`players.csv` — `player, country, position (GK/DEF/MID/FWD), price, proj_points`.
Synthetic fantasy prices/projections (see [`../DATA_SOURCE.md`](../DATA_SOURCE.md)),
enough players per position and a wide price spread so the constraints actually bind.

## You are the optimizer (read before you start)

An ILP looks like "just maximize points", but every clause is a modeling decision you
own:

- **Objective vs constraint.** Projected points is the *objective*; budget, squad
  size, formation, and country cap are *constraints*. Blur the two and you get a squad
  that's optimal for the wrong problem.
- **Formation is a set of linear bounds.** Exactly 1 GK; 3–5 DEF; 3–5 MID; 1–3 FWD;
  totalling 11. Each is a row in the constraint matrix — miss one and the "optimal"
  squad is illegal.
- **Integrality matters.** You pick a player or you don't (0/1). A continuous relaxation
  ("0.4 of a striker") is not a squad — the variables must be binary.
- **Feasibility isn't guaranteed.** Too tight a budget with too high a country cap can
  make the problem infeasible; a good plan says what happens then.

**Claude is a tool; you are the optimizer.** Plan mode is where you pin the objective,
the decision variables, and every constraint — before a solver silently optimizes the
wrong thing.

## Steps

1. `cd exercises-worldcup/02-planning && claude`
2. Press `Shift+Tab` twice to enter plan mode.
3. Paste the prompt and submit. Do **not** approve yet:

   ```
   Plan an integer linear program that picks a fantasy squad from players.csv
   to maximize total proj_points. State the objective, the decision variables,
   and EVERY constraint separately: budget, exactly 11 players, a legal
   formation (1 GK; 3-5 DEF; 3-5 MID; 1-3 FWD), and at most 3 players per
   country. Say which solver you'll use and what happens if it's infeasible.
   Do not write solver code yet.
   ```

4. **Read the plan critically.** Work through the checklist below; make sure the
   objective and the constraints are cleanly separated and every formation bound is
   listed.
5. **Save it without running the plan.** While still in plan mode:

   ```
   Write the complete plan to plan.md and stop — do not implement it.
   ```

   Then press **`Shift+Tab` to leave plan mode without approving**. That file is the
   deliverable.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Is the **objective** (maximize proj_points) stated separately from the constraints? | Folding a constraint into the objective silently changes the problem. |
| Are the **decision variables binary** (pick/don't-pick), not continuous? | "0.4 of a player" is not a squad; the relaxation is a different problem. |
| Is **every formation bound** listed (GK=1, DEF 3–5, MID 3–5, FWD 1–3, total 11)? | A missing bound yields an illegal squad that still "optimizes". |
| Are budget and per-country cap present as **explicit linear constraints**? | These are what make the problem interesting; without them the answer is trivial. |
| Does the plan name the **solver** (`scipy.optimize.milp`) and the **infeasible** case? | A plan with no solver and no failure path can't be executed safely. |

## Discussion prompts

- Which parts of this belong in `CLAUDE.md` (house style — "use `scipy.optimize.milp`
  for small ILPs", "always verify constraints on the returned solution") versus the
  plan or `LOGBOOK.md` (this week's budget, this squad)?
- `scipy.optimize.milp` wants the problem as matrices; PuLP/CVXPY let you write the
  constraints almost verbatim. When is the more readable modeling layer worth an extra
  dependency, and when is staying within scipy the right call?

## Optional — implement the plan (if time permits)

Approve the plan and let Claude build `squad_ilp.py`, then check the output. Watch
whether it **verifies the constraints on the returned solution** (11 players? under
budget? legal formation? country cap respected?) or just prints whatever the solver
returned. An optimizer you don't check is one bad constraint row away from a confident
wrong answer.

## Stretch

Add a **captain** choice (one player's points count double) and re-plan: does that
change the objective (now `proj + captain_bonus`), the variables (a second 0/1 per
player, with "captain implies selected"), or both? Then extend to **multi-week
transfers** — a budget for swaps between game-weeks — the ILP that turns a one-shot
pick into a season.
