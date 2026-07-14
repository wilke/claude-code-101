# Solution — Exercise 01 (CLAUDE.md, World Cup predictor)

## What this exercise is doing

Two CSVs ship (`matches.csv`, `players.csv`) with no modeling code. The learner asks
the same vague question — *"predict world cup match outcomes from this data"* — across
three phases: cold (Phase 1), after `/init` (Phase 2), and with a hand-written
`CLAUDE.md` (Phase 3). "Predict outcomes" hides four separate decisions:

1. **Rating method** — win% table, Elo, Bradley–Terry, Poisson goal model?
2. **Home advantage** — is there a term, and is it switched **off** for neutral
   venues? This is the load-bearing trap: World Cup matches are all `neutral == True`,
   so `home_team` is merely "listed first". A cold model that home-boosts them biases
   every tournament prediction.
3. **Goals vs label** — model the score (yields probabilities) or just win/loss?
4. **Evaluation** — hold out later matches, or fit and "predict" the same games?

A good `CLAUDE.md` turns all four silent guesses into explicit rules.

## Phase 2 — what `/init` produces here (little)

Only data ships, so `/init` has no modeling code to read. Expect a thin file that, at
best, lists the columns. It cannot know that `neutral` disables home advantage, which
rating method to use, or that later dates must be held out — none of that is written
anywhere. `/init` infers from code; the modeling contract is on you.

## The neutral-venue trap (what a good run catches)

| Signal | Cold-model blunder | The fix in CLAUDE.md |
|--------|--------------------|----------------------|
| `neutral == True` on all WC matches | gives `home_team` a home-advantage bonus | apply `H` only when `neutral == False` |
| `home_team` is just "first listed" at neutral venues | reads it as a real home side | state that explicitly |
| low-score football (many 0–0, 1–1) | independent Poisson overstates draws | note the Dixon–Coles ρ caveat |
| fitting on all matches | "predicts" games it trained on | hold out later dates |

## A worked CLAUDE.md (Phase 3)

See the seed in the exercise README — the four load-bearing lines are:

- `neutral == True` → **no** home advantage (the trap).
- Each team has a rating `R_i`; home term `H` applied only when not neutral.
- Prefer a **goal model** returning win/draw/loss probabilities.
- **Don't** fit independent Poisson without the Dixon–Coles caveat; **don't** treat
  neutral matches as home wins; **don't** evaluate on trained games.

## What Claude should produce after reading it

A good response names the method and respects the neutral flag *before* quoting a
metric:

> I rated teams with an Elo pass over `matches.csv` (K=32), applying the home term
> `H` only to non-neutral matches — every 2026 World Cup game is neutral, so none got
> a home bonus. For match probabilities I used a Poisson goal model on the rating
> gap, and I flag that independent Poisson slightly overstates 0–0/1–1 (a Dixon–Coles
> ρ would correct it). Evaluated on matches after 2025-06-01 (held out): log-loss
> ≈ 0.61, accuracy ≈ 0.63. Top-rated sides: Brazil, France, Argentina. *(Illustrative.)*

## Where it usually goes wrong on the first try

- **Home-boosts neutral matches.** The single most common miss; every World Cup
  prediction is skewed. **Pin the `neutral` rule.**
- **Grabs win% or a bare Elo** with no probabilities, so nothing can be calibrated or
  scored by log-loss. **Require a goal/probability model.**
- **Fits and scores the same matches**, reporting a rosy accuracy. **Require a
  held-out split by date.**
- **Independent Poisson with no caveat**, overstating draws. **Require the Dixon–Coles
  acknowledgement.**

The loop is the same as every 01: ask → spot a silent guess → write the rule → re-ask.
Here the highest-value rule is the one-liner about `neutral`, because it's invisible
until it has already biased the tournament.
