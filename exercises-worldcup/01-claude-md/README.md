# Exercise 01 — Write a CLAUDE.md for the predictor (15 min)

**Goal.** Feel how a `CLAUDE.md` changes the assistant's behaviour on a vague
sports-modeling prompt. Ask "predict world cup match outcomes from this data" cold and
Claude has to guess a stack of modeling choices at once: which **rating method**,
whether there's a **home-advantage** term, how to treat **neutral-venue** matches, and
whether to model **goals** (Poisson) or just win/loss. This folder ships two CSVs; the
conventions that make a *defensible* predictor are on you.

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

## The files

- `matches.csv` — `date, home_team, away_team, home_score, away_score, tournament,
  neutral`. A seeded synthetic snapshot in the real open-dataset schema (see
  [`../DATA_SOURCE.md`](../DATA_SOURCE.md)): a 2019–2025 history plus the 2026 World
  Cup through the semifinals, the 2026 final pending.
- `players.csv` — synthetic fantasy prices/projections (not used until Exercise 02).

One column is a quiet trap: **`neutral`**. World Cup matches are played at neutral
venues, so `home_team` is just "the team listed first" — giving it a home-advantage
bonus would bias every tournament prediction. A cold model usually misses this.

## Phase 1 — Without a CLAUDE.md

1. With no `CLAUDE.md` in the folder, open a session and ask:

   ```
   predict world cup match outcomes from this data
   ```

2. Watch what Claude does — this is your baseline. Look for:
   - **Which rating method?** Win-percentage table, Elo, Poisson goal model,
     logistic regression on rating diffs — did it pick one and justify it, or grab
     the first that came to mind?
   - **Home advantage:** did it add a home term — and did it **switch it off when
     `neutral == True`**, or silently treat every `home_team` as having home
     advantage (wrong for a World Cup)?
   - **Goals vs win/loss:** does it model the score (Poisson) or just the outcome?
   - **Train/test discipline:** does it evaluate on held-out later matches, or fit
     and "predict" the same games?
   - Did it **ask you anything**, or guess all of it?

## Phase 2 — Let `/init` try

3. Reset the conversation and generate a `CLAUDE.md` from the folder:

   ```
   /clear
   ```
   ```
   /init
   ```

4. Read what `/init` produced. With only CSVs and no modeling code to scan, expect a
   thin, generic file — it can describe the columns at best, and knows nothing about
   ratings, home advantage, or the neutral-venue trap. That's the lesson: **`/init`
   infers from code; the modeling contract isn't in the repo, so it's on you.**

## Phase 3 — Add what `/init` couldn't know, then iterate

5. Write the modeling contract into `CLAUDE.md`. A seed to start from:

   ```markdown
   # Project: World Cup match-outcome predictor

   ## Stack
   - pandas + numpy; scipy.stats / scipy.optimize for the models
   - matplotlib for figures, saved to figures/, never plt.show()

   ## Data (matches.csv)
   - date, home_team, away_team, home_score, away_score, tournament, neutral
   - `neutral == True` means NO home advantage — home_team is just listed first.
     World Cup matches are neutral. NEVER give a neutral home_team a home bonus.

   ## Notation & model
   - Each team i has a rating R_i. Home advantage is a single term H, applied
     ONLY when neutral == False.
   - Prefer a goal model: expected goals depend on R_home - R_away (+ H if not
     neutral). Report a win/draw/loss probability, not just a point pick.

   ## Don'ts (real modeling traps)
   - Don't fit an INDEPENDENT-Poisson goal model without acknowledging the
     low-score correlation (Dixon-Coles rho correction) — it overstates 0-0/1-1.
   - Don't treat `neutral == True` matches as home wins for the listed team.
   - Don't evaluate on matches you trained on — hold out later dates.

   ## Reporting
   - Always state the rating method, whether H was applied, and the held-out
     metric (log-loss or accuracy) used.
   ```

6. Reset (`/clear`) and re-ask the exact same prompt:

   ```
   predict world cup match outcomes from this data
   ```

7. Compare against Phase 1. With the `CLAUDE.md` in place, Claude should name a
   rating method, apply home advantage **only** to non-neutral matches, model goals
   (and note the Dixon–Coles caveat), and report a held-out metric — instead of
   silently home-boosting neutral World Cup games.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did Claude switch **off** home advantage when `neutral == True`? | Every World Cup match is neutral; a home bonus biases the whole tournament. |
| Did it pick and **justify** a rating method, not just grab one? | "I used Elo because…" is auditable; a silent choice isn't. |
| Did it model **goals / probabilities**, not just a win/loss label? | A predictor with no probability can't be scored by log-loss or calibrated. |
| Did it **hold out** later matches to evaluate? | Fitting and scoring the same games is the sports-analytics version of leakage. |
| Did it note the independent-Poisson (Dixon–Coles) caveat? | Independent Poisson overstates 0–0/1–1; naming it is the mark of a real model. |

## Discussion prompts

- Which facts belong in `CLAUDE.md` (true every session — "neutral means no home
  advantage", "hold out later dates") versus a plan or `LOGBOOK.md` (today's choice
  of Elo vs Bradley–Terry, this run's `K`)?
- `/init` gave you almost nothing from two CSVs. What *would* it infer if this folder
  also shipped a `rate.py` with a labelled rating function — and what's still on you?

## Stretch

Add a convention that any prediction must save a calibration plot (predicted vs
observed win rate) to `figures/`, and re-ask — does Claude produce it unprompted from
the `CLAUDE.md` rule? A predictor you can't check for calibration is one you can't
trust on the final.
