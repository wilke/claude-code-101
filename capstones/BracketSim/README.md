# BracketSim — Monte-Carlo the knockout bracket

## Purpose

Simulate the World Cup knockout bracket thousands of times from a match-probability
model to produce each team's **advance and win probabilities with uncertainty bands** —
turning a single-match predictor into a tournament forecast.

## Background

- **Method.** Monte-Carlo simulation: sample each match outcome from a probability model,
  propagate winners through the bracket, repeat `M` times, and read off the empirical
  frequencies. The uncertainty bands come from the spread across simulations.
- **Inputs.** A per-match win/draw/loss model (from ratings + a goal model) and the
  bracket structure. The workshop's [`exercises-worldcup/03-skills/`](/exercises-worldcup/03-skills/)
  `rating-fit` skill produces the ratings; its stretch points at exactly this
  `simulate-bracket` companion.
- **Data.** `matches.csv` for fitting the model, including the 2026 group + knockout
  results **through the semifinals** (the final is pending — a natural thing to predict).
  See [`exercises-worldcup/DATA_SOURCE.md`](/exercises-worldcup/DATA_SOURCE.md).

## Problem Statement

Given (a) a model that outputs P(team A beats team B) for any pairing at a neutral venue,
and (b) the bracket, estimate for every team its probability of reaching each round and of
winning the tournament — with a Monte-Carlo standard error on each estimate.

Knockout matches can draw, so the model must resolve draws the way the real tournament
does (extra time / penalties → a coin-ish tilt toward the stronger side), and every
knockout match is neutral (no home advantage).

## Suggested Approach

1. **Match model.** Reuse ratings (Elo/Bradley–Terry) + a goal model for P(win) at a
   neutral venue; define a draw-resolution rule for knockouts.
2. **Simulator.** From the last completed round, sample each remaining match, advance the
   winner, and record how far each team got. Vectorize over `M` simulations.
3. **Aggregate.** For each team, report P(reach QF/SF/final/win) as frequencies, with a
   Monte-Carlo standard error (`√(p(1−p)/M)`) or bootstrap band.
4. **Report.** A table sorted by win probability and a bar chart with error bars; sanity
   checks (probabilities per round sum correctly; the field sums to 1 for "wins it").

## Outline of Tasks

1. Wrap the match model behind a clean `p_win(team_a, team_b)` interface.
2. Build the bracket advancer and the `M`-simulation loop; fix the RNG seed for
   reproducibility.
3. Produce advance/win probabilities with uncertainty bands; verify they're consistent.
4. Record the draw-resolution choice and `M` in a short `LOGBOOK.md`.
5. **Stretch:** predict the **pending 2026 final** specifically; show how the forecast
   shifts if you change the ratings' `K` (ties into the logbook's `K` conflict); add
   correlated match outcomes (an upset cascade) instead of independent samples.

## What good looks like

- Win probabilities are **sensible** (favourites lead, minnows are long shots) and the
  field sums to 1.
- Every estimate carries a **Monte-Carlo error band**, and `M` is large enough that the
  bands are tight.
- Knockout matches are neutral and draws are resolved explicitly — no accidental home
  advantage, no matches left tied.
- The simulation is **seeded and reproducible**, and the draw rule is written down.

*Have fun — and remember a single simulation is an anecdote; the distribution is the
result.*
