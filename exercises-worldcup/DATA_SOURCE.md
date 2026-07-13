# Data source & licensing — World Cup track

This track ships two data files. Read this before you trust a number that comes out
of them.

## `matches.csv` — match results

**Schema** (mirrors the well-known open "International football results" dataset):

| column | type | meaning |
|--------|------|---------|
| `date` | `YYYY-MM-DD` | match date |
| `home_team` | str | nominal home side |
| `away_team` | str | nominal away side |
| `home_score` | int | goals, home |
| `away_score` | int | goals, away |
| `tournament` | str | `Friendly`, `FIFA World Cup qualification`, `FIFA World Cup` |
| `neutral` | bool | `True` if played at a neutral venue (no home advantage) |

**Real open sources** this schema is drawn from — match *results are public-domain
facts*:

- openfootball (<https://github.com/openfootball>) — released into the **Public Domain**.
- "International football results from 1872 to present"
  (<https://github.com/martj42/international_results>) — a **CC0** compilation.

**What is actually committed here is a *seeded synthetic snapshot*, not a live pull.**
It is generated deterministically by `tools/make_worldcup_data.py` (seed `2026`) so
that (a) the exercises run **offline** and (b) every attendee gets **byte-identical**
data — a hard requirement the live sources can't guarantee (they change daily). Team
**names are real** (names are facts); the **scores are simulated** from a
strength-based Poisson model, so stronger sides genuinely rank higher and the
rating-fit skill has real signal to recover — but **do not cite these scores as real
results**. The snapshot covers a synthetic 2019–2025 history plus the 2026 World Cup
through the **semifinals**; the final (2026-07-19) is intentionally **pending / absent**,
which is what the bracket-simulation exercises predict.

If you want *real* results instead, run `refresh_data.py` (see below) and record the
new source URL, license, and pull date right here.

## `players.csv` — fantasy prices & projections

**Schema:** `player, country, position (GK/DEF/MID/FWD), price, proj_points`.

Fantasy **prices and projected points are proprietary** (not open), so these columns
are **synthetic**, generated with the same fixed seed and correlated with team
strength + position. **Player names are synthetic too** (`"Brazil FWD1"`) to sidestep
any trademark/likeness question — swap in a real open squad list if you have one; only
the `country`/`position`/`price`/`proj_points` columns matter to the optimizer.

## Snapshot metadata

- **Generator:** `tools/make_worldcup_data.py`, seed `2026`.
- **Snapshot date:** 2026-07-10 (final pending).
- **Provenance of this file's data:** synthetic fallback (source not fetched at build
  time). Update this line if you re-pull real data with `refresh_data.py`.
