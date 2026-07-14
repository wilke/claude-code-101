---
name: rating-fit
origin: workshop
description: |
  Fit national-team strength ratings from a match-results table, two ways: an online
  Elo update pass, and a Bradley-Terry maximum-likelihood fit (via scipy.optimize)
  that also estimates a home-advantage term. Both respect a `neutral` column so
  neutral-venue matches get no home bonus. Use it whenever you need a ratings table
  to rank teams or to feed a match-outcome or bracket model.
---

<!--
The `origin:` field tags skills you wrote yourself versus imported ones,
so future-you knows what's safe to modify.
-->


# rating-fit skill

Use this skill when:

- You have a table of match results and want a **ratings table** — to rank teams, or
  as the input to a Poisson goal model or a bracket simulation.
- You want to compare a **heuristic (Elo)** against a **principled MLE
  (Bradley–Terry)** on the same data, and see the fitted **home advantage** fall out
  of the likelihood.
- You keep re-deriving "rate the teams" every session — the exact signal to promote it
  to a skill.

## How to invoke

Library form:

```python
from rating_fit import elo_ratings, bradley_terry
elo = elo_ratings(df, k=32, home_adv=65)   # online Elo pass
bt = bradley_terry(df)                       # MLE + fitted home term
```

CLI form:

```bash
python .claude/skills/rating-fit/rating_fit.py matches.csv --method both --top 15
```

`--method {elo,bt,both}` picks the estimator; `--k` and `--home-adv` tune the Elo pass;
`--top` sets how many teams to print.

Output looks like:

```
1104 matches, 48 teams

=== Elo (K=32, home_adv=65) ===
      team  elo
    Brazil 1902
    France 1888
 Argentina 1875
 ...

=== Bradley-Terry MLE ===
(fitted home advantage: 0.31 log-odds)
      team  bt_strength  bt_elo
    Brazil         1.42    1747
    France         1.36    1736
 ...
```

## Interpreting the output

- **Ratings are relative.** Elo is anchored at 1500; Bradley–Terry strengths are
  centered at 0 (identifiable only up to a constant), with `bt_elo` rescaled to an
  Elo-like range for readability. Compare *differences*, not absolute values.
- **The two methods should broadly agree** on the ordering. Where they diverge, Elo is
  recency-weighted (later matches move ratings more), while the MLE weights all matches
  equally — a real modeling choice, not a bug.
- **The fitted home advantage** (Bradley–Terry) is estimated from the data; if it comes
  out near zero, your match set is mostly neutral (as a World Cup-heavy set would be).
- **`K` is a knob, not a truth.** A larger `K` tracks recent form faster but overshoots
  on upsets — which is exactly the conflict the 04 logbook exercise asks you to
  reconcile.

## Extending

- Add a `simulate-bracket` companion skill: Monte-Carlo the knockout tree from these
  ratings to get each team's advance/win probabilities (the BracketSim capstone).
- Add a Poisson/Dixon–Coles goal model on top of the ratings, returning per-match
  scorelines instead of just win probabilities.
- Add a `--since DATE` filter and a time-decay weight so old friendlies count less, and
  widen the `description:` so "rate teams using only recent form" routes here.
