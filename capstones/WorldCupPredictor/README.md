# WorldCupPredictor — a calibrated match-outcome predictor

## Purpose

Build a full World Cup match-outcome predictor: fit team ratings, turn them into
scoreline probabilities with a Poisson/Dixon–Coles goal model, and **evaluate its
calibration and log-loss on held-out matches** — not just its accuracy.

## Background

- **Ratings.** Elo (an online update heuristic) and Bradley–Terry (a maximum-likelihood
  model) are the two standard ways to rate teams from results. The workshop's
  [`exercises-worldcup/`](/exercises-worldcup/) track builds both in a `rating-fit`
  skill you can lift as a starting point.
- **Goal model.** Dixon & Coles (1997), "Modelling Association Football Scores and
  Inefficiencies in the Football Betting Market", *JRSS-C* — the low-score correction
  `ρ` that fixes independent Poisson's overstated 0–0/1–1 rates.
- **Data.** `matches.csv` (`date, home_team, away_team, home_score, away_score,
  tournament, neutral`) — the schema of the open, public-domain "International football
  results" dataset (CC0). See [`exercises-worldcup/DATA_SOURCE.md`](/exercises-worldcup/DATA_SOURCE.md)
  for sourcing and licensing.

## Problem Statement

Given a history of match results, predict the win/draw/loss probabilities (and ideally
the scoreline distribution) of future matches, and quantify **how well-calibrated** those
probabilities are.

Two properties separate a real predictor from a toy:

- It respects the `neutral` flag — home advantage applies **only** to non-neutral
  matches (every World Cup game is neutral).
- It is evaluated on matches it did **not** train on, by **log-loss and calibration**,
  not accuracy alone (accuracy can't tell a confident-and-wrong model from a
  humble-and-right one).

## Suggested Approach

1. **Rate the teams.** Start from Elo and/or Bradley–Terry (reuse the `rating-fit`
   skill). Fit the home-advantage term from the data.
2. **Goal model.** Map the rating gap to expected goals per side; start with independent
   Poisson, then add the **Dixon–Coles `ρ`** correction and confirm the 0–0/1–1 rates
   improve against the observed data.
3. **Probabilities.** Sum the scoreline grid into P(home win) / P(draw) / P(away win).
4. **Evaluate honestly.** Hold out the latest slice of matches by date. Report
   **log-loss** and a **calibration plot** (predicted vs observed win rate in bins);
   compare to a baseline (bookmaker-free: e.g. a bare Elo win probability).

## Outline of Tasks

1. Build the ratings pass; sanity-check that strong sides rank at the top.
2. Add the goal model; show the independent-Poisson vs Dixon–Coles low-score difference.
3. Produce held-out log-loss + a calibration figure.
4. Write a short `LOGBOOK.md` recording the `K`/`ρ` choices and any dead ends (the
   independent-Poisson overstatement is a natural one).
5. **Stretch:** back-test across multiple past tournaments; add a time-decay weight so
   old friendlies count less; try a negative-binomial for high-scoring over-dispersion.

## What good looks like

- Home advantage is **off** for neutral matches, and you can show the effect of getting
  that wrong.
- The calibration plot is close to the diagonal, and log-loss beats the naive baseline.
- The Dixon–Coles correction visibly improves the low-score fit, and you *recorded why*.
- Every reported number is on **held-out** matches, and the split is stated.

*Have fun — and don't trust a predictor you haven't calibrated.*
