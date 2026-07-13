"""rating_fit — fit national-team ratings from a match table.

Two methods, one interface:

- `elo_ratings(matches, k, home_adv)` — an online Elo update pass in date order.
- `bradley_terry(matches, home_adv, ridge)` — a Bradley-Terry maximum-likelihood
  fit via `scipy.optimize.minimize`, the statistical cousin of the Elo heuristic.

Both respect the `neutral` column: home advantage is applied only when
`neutral == False` (World Cup matches are neutral, so they get no home bonus).

Library:
    from rating_fit import elo_ratings, bradley_terry
    elo = elo_ratings(df); bt = bradley_terry(df)

CLI:
    python rating_fit.py matches.csv --method both --top 15
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit  # logistic sigmoid


def _to_bool(s: pd.Series) -> pd.Series:
    """Coerce a neutral-flag column to real bools.

    Guards the footgun where a CSV round-trip leaves `neutral` as the *strings*
    "True"/"False": a bare `.astype(bool)` would map "False" -> True and hand
    every match a home advantage. Handles bool, 0/1, and common string spellings.
    """
    if s.dtype == bool:
        return s
    if pd.api.types.is_numeric_dtype(s):
        return s.astype(bool)
    return s.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "t"})


def _prep(matches: pd.DataFrame) -> pd.DataFrame:
    df = matches.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["neutral"] = _to_bool(df["neutral"])
    return df.sort_values("date").reset_index(drop=True)


def elo_ratings(
    matches: pd.DataFrame,
    k: float = 32.0,
    home_adv: float = 65.0,
    base: float = 1500.0,
) -> pd.DataFrame:
    """Online Elo pass. Returns a ratings table sorted strongest-first."""
    df = _prep(matches)
    teams = pd.unique(pd.concat([df["home_team"], df["away_team"]]))
    R = {t: base for t in teams}

    for row in df.itertuples(index=False):
        ha = 0.0 if row.neutral else home_adv
        exp_home = 1.0 / (1.0 + 10 ** ((R[row.away_team] - R[row.home_team] - ha) / 400.0))
        if row.home_score > row.away_score:
            s_home = 1.0
        elif row.home_score < row.away_score:
            s_home = 0.0
        else:
            s_home = 0.5
        delta = k * (s_home - exp_home)
        R[row.home_team] += delta
        R[row.away_team] -= delta

    out = pd.DataFrame({"team": list(R), "elo": list(R.values())})
    return out.sort_values("elo", ascending=False).reset_index(drop=True)


def bradley_terry(
    matches: pd.DataFrame,
    home_adv_init: float = 0.3,
    ridge: float = 1e-3,
) -> pd.DataFrame:
    """Bradley-Terry MLE. Fits team strengths + a home term by maximizing the
    win/draw/loss likelihood. Returns ratings centered at 0, plus an Elo-scaled
    column for readability. Draws contribute half a win to each side.
    """
    df = _prep(matches)
    teams = sorted(pd.unique(pd.concat([df["home_team"], df["away_team"]])))
    idx = {t: i for i, t in enumerate(teams)}
    n = len(teams)

    h = df["home_team"].map(idx).to_numpy()
    a = df["away_team"].map(idx).to_numpy()
    not_neutral = (~df["neutral"].to_numpy()).astype(float)
    hs = df["home_score"].to_numpy()
    as_ = df["away_score"].to_numpy()
    # outcome weight for "home win": 1 win, 0 loss, 0.5 draw
    y = np.where(hs > as_, 1.0, np.where(hs < as_, 0.0, 0.5))

    def neg_log_lik(params: np.ndarray) -> float:
        theta = params[:n]
        home = params[n]
        diff = theta[h] - theta[a] + home * not_neutral
        p = np.clip(expit(diff), 1e-12, 1 - 1e-12)
        ll = y * np.log(p) + (1 - y) * np.log(1 - p)
        return -ll.sum() + ridge * np.sum(theta ** 2)

    x0 = np.concatenate([np.zeros(n), [home_adv_init]])
    res = minimize(neg_log_lik, x0, method="L-BFGS-B")
    theta = res.x[:n] - res.x[:n].mean()  # identifiable up to a constant -> center
    home = res.x[n]

    out = pd.DataFrame(
        {
            "team": teams,
            "bt_strength": theta,
            "bt_elo": 1500 + theta * 400 / np.log(10),  # Elo-like readable scale
        }
    )
    out.attrs["home_advantage"] = float(home)
    return out.sort_values("bt_strength", ascending=False).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Fit team ratings from a match table.")
    ap.add_argument("matches", help="path to matches.csv")
    ap.add_argument("--method", choices=["elo", "bt", "both"], default="both")
    ap.add_argument("--k", type=float, default=32.0, help="Elo K factor")
    ap.add_argument("--home-adv", type=float, default=65.0, help="Elo home advantage")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()

    df = pd.read_csv(args.matches)
    print(f"{len(df)} matches, {pd.unique(pd.concat([df.home_team, df.away_team])).size} teams\n")

    if args.method in ("elo", "both"):
        elo = elo_ratings(df, k=args.k, home_adv=args.home_adv)
        print(f"=== Elo (K={args.k}, home_adv={args.home_adv}) ===")
        print(elo.head(args.top).to_string(index=False, float_format=lambda v: f"{v:.0f}"))
        print()

    if args.method in ("bt", "both"):
        bt = bradley_terry(df)
        print("=== Bradley-Terry MLE ===")
        print(f"(fitted home advantage: {bt.attrs['home_advantage']:.3f} log-odds)")
        print(
            bt.head(args.top).to_string(
                index=False, float_format=lambda v: f"{v:.2f}"
            )
        )


if __name__ == "__main__":
    main()
