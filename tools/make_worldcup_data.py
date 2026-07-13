"""Generate the World Cup track's data files, deterministically.

Produces two CSVs used across exercises-worldcup/:

- matches.csv  — schema mirrors the well-known open "International football
  results" dataset: date, home_team, away_team, home_score, away_score,
  tournament, neutral. A seeded synthetic history (2019-2026) plus the 2026
  World Cup through the semifinals (the final, 2026-07-19, is pending).
- players.csv  — synthetic fantasy prices/projections: player, country,
  position (GK/DEF/MID/FWD), price, proj_points.

Why synthetic: match *results* are public-domain facts, but this environment
builds offline and must be byte-identical for every attendee, so the committed
snapshot is generated from a fixed seed (see DATA_SOURCE.md). `refresh_data.py`
documents how to pull the real open snapshot instead. Team names are real
(names are facts); fantasy prices are invented (real prices are proprietary).

Run:
    python tools/make_worldcup_data.py --outdir exercises-worldcup/01-claude-md
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 2026

# 48 teams (2026 expanded format) with a latent "true strength" on an Elo-ish
# scale. These drive the synthetic score model so stronger sides rank higher —
# which is what the rating-fit skill must recover.
TEAM_STRENGTH: dict[str, int] = {
    "Brazil": 2080, "France": 2070, "Argentina": 2065, "England": 2040,
    "Spain": 2035, "Portugal": 2025, "Netherlands": 2015, "Germany": 2010,
    "Belgium": 1995, "Italy": 1985, "Croatia": 1970, "Uruguay": 1960,
    "Colombia": 1945, "Morocco": 1940, "Mexico": 1915, "USA": 1905,
    "Switzerland": 1900, "Denmark": 1895, "Japan": 1890, "Senegal": 1880,
    "Serbia": 1870, "Ecuador": 1860, "South Korea": 1855, "Poland": 1850,
    "Australia": 1835, "Canada": 1830, "Ukraine": 1825, "Austria": 1820,
    "Nigeria": 1815, "Peru": 1800, "Sweden": 1795, "Wales": 1790,
    "Tunisia": 1775, "Iran": 1770, "Ghana": 1760, "Egypt": 1755,
    "Cameroon": 1745, "Ivory Coast": 1740, "Qatar": 1720, "Saudi Arabia": 1715,
    "Costa Rica": 1705, "Paraguay": 1700, "Algeria": 1695, "Chile": 1690,
    "Panama": 1660, "Jamaica": 1650, "New Zealand": 1600, "Honduras": 1590,
}
HOSTS = {"USA", "Canada", "Mexico"}
HOME_ADV = 65.0  # Elo points of home advantage (ignored when neutral=True)
BASE_GOALS = 1.35  # baseline expected goals per side


def _lambda(att: float, deff: float) -> float:
    """Expected goals for an attacker vs defender strength gap."""
    return float(np.clip(BASE_GOALS * 10 ** ((att - deff) / 400.0), 0.15, 6.0))


def _play(rng, home, away, neutral, strength):
    ha = 0.0 if neutral else HOME_ADV
    lam_h = _lambda(strength[home] + ha, strength[away])
    lam_a = _lambda(strength[away], strength[home] + ha)
    return int(rng.poisson(lam_h)), int(rng.poisson(lam_a))


def _historical(rng, teams, strength) -> list[dict]:
    """Friendlies + qualifiers, 2019-2025, home/away (not neutral)."""
    rows = []
    dates = pd.date_range("2019-01-01", "2025-12-01", freq="MS")
    for d in dates:
        # ~10 matches a month among random pairings
        for _ in range(10):
            h, a = rng.choice(teams, size=2, replace=False)
            neutral = bool(rng.random() < 0.15)
            hs, as_ = _play(rng, h, a, neutral, strength)
            tourn = "FIFA World Cup qualification" if rng.random() < 0.4 else "Friendly"
            rows.append(dict(date=d.strftime("%Y-%m-%d"), home_team=h, away_team=a,
                             home_score=hs, away_score=as_, tournament=tourn,
                             neutral=neutral))
    return rows


def _standings(results: dict, group) -> list[str]:
    pts = {t: 0 for t in group}
    gd = {t: 0 for t in group}
    for (h, a), (hs, as_) in results.items():
        gd[h] += hs - as_
        gd[a] += as_ - hs
        if hs > as_:
            pts[h] += 3
        elif hs < as_:
            pts[a] += 3
        else:
            pts[h] += 1
            pts[a] += 1
    return sorted(group, key=lambda t: (pts[t], gd[t]), reverse=True)


def _world_cup(rng, teams, strength) -> list[dict]:
    """2026 World Cup: 12 groups of 4 -> knockouts, through the semifinals."""
    rows = []
    order = sorted(teams, key=lambda t: -strength[t])
    groups = [order[i::12] for i in range(12)]  # snake-ish spread of strength
    date = pd.Timestamp("2026-06-11")

    advancers = []
    thirds = []
    for gi, group in enumerate(groups):
        res = {}
        for h, a in itertools.combinations(group, 2):
            hs, as_ = _play(rng, h, a, True, strength)  # WC matches neutral
            res[(h, a)] = (hs, as_)
            rows.append(dict(date=date.strftime("%Y-%m-%d"), home_team=h,
                             away_team=a, home_score=hs, away_score=as_,
                             tournament="FIFA World Cup", neutral=True))
            date += pd.Timedelta(days=1)
        ranked = _standings(res, group)
        advancers += ranked[:2]
        thirds.append((ranked[2], gi))

    # 8 best third-placed teams by strength (proxy for points, kept simple)
    thirds.sort(key=lambda x: -strength[x[0]])
    advancers += [t for t, _ in thirds[:8]]  # 32 total

    def knockout(qualified, start_date, label):
        rng.shuffle(qualified)
        winners, d = [], start_date
        for i in range(0, len(qualified), 2):
            h, a = qualified[i], qualified[i + 1]
            hs, as_ = _play(rng, h, a, True, strength)
            if hs == as_:  # decide draws so a winner advances
                hs, as_ = (hs + 1, as_) if strength[h] >= strength[a] else (hs, as_ + 1)
            rows.append(dict(date=d.strftime("%Y-%m-%d"), home_team=h, away_team=a,
                             home_score=hs, away_score=as_,
                             tournament="FIFA World Cup", neutral=True))
            winners.append(h if hs > as_ else a)
            d += pd.Timedelta(days=1)
        return winners, d

    r32, date = knockout(advancers, pd.Timestamp("2026-06-28"), "R32")
    r16, date = knockout(r32, pd.Timestamp("2026-07-04"), "R16")
    qf, date = knockout(r16, pd.Timestamp("2026-07-09"), "QF")
    sf, date = knockout(qf, pd.Timestamp("2026-07-14"), "SF")
    # Final (2026-07-19) is pending as of the snapshot date — intentionally omitted.
    return rows


POSITIONS = ["GK", "DEF", "MID", "FWD"]
POS_COUNT = {"GK": 3, "DEF": 6, "MID": 6, "FWD": 4}  # per country -> 19 players


def _players(rng, strength) -> list[dict]:
    rows = []
    for country, s in strength.items():
        base = (s - 1550) / 100.0  # country quality, ~0.4..5.3
        for pos in POSITIONS:
            for n in range(1, POS_COUNT[pos] + 1):
                skill = base + rng.normal(0, 0.8)
                # price 4.0-13.0m, correlated with skill + position premium
                pos_prem = {"GK": -0.5, "DEF": -0.2, "MID": 0.3, "FWD": 0.6}[pos]
                price = float(np.clip(6.0 + 0.9 * (skill + pos_prem) + rng.normal(0, 0.5),
                                      4.0, 13.0))
                proj = float(np.clip(2.5 * (skill + pos_prem) + 30 + rng.normal(0, 4),
                                     8.0, 75.0))
                rows.append(dict(player=f"{country} {pos}{n}", country=country,
                                 position=pos, price=round(price, 1),
                                 proj_points=round(proj, 1)))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=".", help="directory to write the CSVs into")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    teams = list(TEAM_STRENGTH)

    matches = _historical(rng, teams, TEAM_STRENGTH) + _world_cup(rng, teams, TEAM_STRENGTH)
    matches_df = pd.DataFrame(matches).sort_values("date").reset_index(drop=True)

    players_df = pd.DataFrame(_players(rng, TEAM_STRENGTH))

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    matches_df.to_csv(outdir / "matches.csv", index=False)
    players_df.to_csv(outdir / "players.csv", index=False)
    print(f"wrote {len(matches_df)} matches -> {outdir/'matches.csv'}")
    print(f"wrote {len(players_df)} players -> {outdir/'players.csv'}")


if __name__ == "__main__":
    main()
