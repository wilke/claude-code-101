"""squad_ilp.py — pick a fantasy World Cup squad with scipy.optimize.milp.

Maximize projected points over an 11-player squad, subject to:
  - budget:    sum(price) <= B
  - size:      exactly 11 players
  - formation: exactly 1 GK; 3-5 DEF; 3-5 MID; 1-3 FWD
  - diversity: at most N players from any one country

This is a 0/1 integer linear program — the knapsack/portfolio analogue of the
optimization track's planning lesson. We model every constraint as a linear system
and hand it to `scipy.optimize.milp`. (PuLP or CVXPY would read more naturally; they
are not required here.)

Run:
    python squad_ilp.py --players players.csv --budget 100 --country-cap 3
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp

POSITIONS = ["GK", "DEF", "MID", "FWD"]
FORMATION = {"GK": (1, 1), "DEF": (3, 5), "MID": (3, 5), "FWD": (1, 3)}
SQUAD_SIZE = 11


def solve_squad(
    players: pd.DataFrame,
    budget: float = 100.0,
    country_cap: int = 3,
) -> pd.DataFrame:
    """Return the chosen 11 players as a DataFrame, or raise if infeasible."""
    n = len(players)
    price = players["price"].to_numpy(dtype=float)
    proj = players["proj_points"].to_numpy(dtype=float)

    # Objective: maximize proj -> minimize -proj.
    c = -proj

    constraints = []

    # Exactly 11 players.
    constraints.append(LinearConstraint(np.ones(n), SQUAD_SIZE, SQUAD_SIZE))

    # Budget: total price <= budget.
    constraints.append(LinearConstraint(price, -np.inf, budget))

    # Formation: per-position lower/upper bounds.
    for pos, (lo, hi) in FORMATION.items():
        indicator = (players["position"].to_numpy() == pos).astype(float)
        constraints.append(LinearConstraint(indicator, lo, hi))

    # Diversity: at most `country_cap` players per country.
    for country, idx in players.groupby("country").groups.items():
        row = np.zeros(n)
        row[[players.index.get_loc(i) for i in idx]] = 1.0
        constraints.append(LinearConstraint(row, 0, country_cap))

    # Binary decision variables.
    integrality = np.ones(n)
    bounds = Bounds(0, 1)

    res = milp(c=c, constraints=constraints, integrality=integrality, bounds=bounds)
    if not res.success:
        raise RuntimeError(f"no feasible squad: {res.message}")

    chosen = np.where(res.x > 0.5)[0]
    return players.iloc[chosen].copy()


def _report(squad: pd.DataFrame, budget: float, country_cap: int) -> None:
    order = {p: i for i, p in enumerate(POSITIONS)}
    squad = squad.sort_values(
        by="position", key=lambda s: s.map(order)
    )
    print(squad[["player", "country", "position", "price", "proj_points"]].to_string(index=False))
    total_price = squad["price"].sum()
    total_proj = squad["proj_points"].sum()
    counts = squad["position"].value_counts().to_dict()
    print("\n--- summary ---")
    print(f"players:       {len(squad)} (need {SQUAD_SIZE})")
    print(f"formation:     " + "  ".join(f"{p}={counts.get(p, 0)}" for p in POSITIONS))
    print(f"spend:         {total_price:.1f} / {budget:.1f}")
    print(f"proj points:   {total_proj:.1f}")
    top_country = squad["country"].value_counts().iloc[0]
    print(f"max per country: {top_country} (cap {country_cap})")

    # Constraint checks — the plan promised these; verify them.
    assert len(squad) == SQUAD_SIZE
    assert total_price <= budget + 1e-6
    for pos, (lo, hi) in FORMATION.items():
        assert lo <= counts.get(pos, 0) <= hi, f"formation broken for {pos}"
    assert top_country <= country_cap
    print("all constraints satisfied.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--players", default="players.csv")
    ap.add_argument("--budget", type=float, default=100.0)
    ap.add_argument("--country-cap", type=int, default=3)
    args = ap.parse_args()

    players = pd.read_csv(args.players).reset_index(drop=True)
    squad = solve_squad(players, budget=args.budget, country_cap=args.country_cap)
    _report(squad, args.budget, args.country_cap)


if __name__ == "__main__":
    main()
