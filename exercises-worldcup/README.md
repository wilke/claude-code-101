# Track: World Cup — a sports-analytics on-ramp

A domain-neutral track that exercises the **same muscles as the math tracks** —
constrained optimization, maximum-likelihood fitting, and Monte-Carlo simulation —
on a surface almost anyone can picture: predicting football results and picking a
fantasy squad. If "KKT conditions" and "FEM" made the optimization track bounce off
you, start here. The math is the same; the framing is a World Cup.

One project is carried across all four exercises: a **World Cup outcome-predictor +
fantasy-squad optimizer**. Each exercise builds one honest piece of it and teaches
one Claude Code habit.

## What you'll build (and the muscle each works)

1. [`01-claude-md/`](01-claude-md/) — write the `CLAUDE.md` for the predictor: pin
   the data schema, the rating notation, and a real modeling "don't". *(Conventions.)*
2. [`02-planning/`](02-planning/) — plan and solve the **fantasy-squad ILP** with
   `scipy.optimize.milp`: maximize projected points under a budget, a legal
   formation, and a per-country cap. *(The knapsack/portfolio analogue — same as the
   opt track's planning lesson.)*
3. [`03-skills/`](03-skills/) — package a reusable **`rating-fit`** skill: fit team
   ratings (an Elo pass and/or a Bradley–Terry MLE via `scipy.optimize`). *(MLE /
   eigenvector-style ratings — the lin_alg muscle.)*
4. [`04-logbook/`](04-logbook/) — consolidate three dated notes — **with a built-in
   conflict** about the Elo `K` factor — into a `LOGBOOK.md`. *(Durable memory +
   reconciling contradictory findings.)*

## The data

Two files, described in full in [`DATA_SOURCE.md`](DATA_SOURCE.md) — **read it before
trusting a number**:

- `matches.csv` — `date, home_team, away_team, home_score, away_score, tournament,
  neutral`. A seeded **synthetic** snapshot (real team names, simulated scores) in the
  schema of the well-known open results dataset: a 2019–2025 history plus the 2026
  World Cup through the semifinals; the 2026 final is pending. `refresh_data.py`
  documents how to pull the real CC0/public-domain data if you want it.
- `players.csv` — `player, country, position, price, proj_points`. **Synthetic**
  fantasy prices/projections (real prices are proprietary).

## Setup

conda:

```bash
conda create -n worldcup python=3.11 pandas numpy scipy matplotlib
conda activate worldcup
```

pip + venv:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pandas numpy scipy matplotlib
```

No ILP library is required — `scipy.optimize.milp` covers the squad problem. (PuLP
and CVXPY are more readable alternatives, mentioned where relevant but not needed.)

## How to run each exercise

Open each folder on its own (`cd exercises-worldcup/01-claude-md && claude`) and
follow its `README.md`. A track `SOLUTION.md` (or a `solution/` subdir for
`02-planning`) sits beside each exercise for the instructor — it is deliberately kept
out of the directory where `claude` runs so the model can't read ahead.
