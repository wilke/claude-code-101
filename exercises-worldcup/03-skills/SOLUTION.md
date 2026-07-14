# Solution — Exercise 03 (rating-fit skill)

## What this exercise is doing

The learner installs a **`rating-fit`** skill and asks a plain-language ratings question
*without naming it*. Two things are under test: **routing** (does Claude reach for the
skill instead of hand-rolling a win-percentage table?) and **reuse** (does the same
helper answer a second question — Elo vs MLE, a recent-form slice — unchanged?). The
skill also carries the neutral-venue discipline from Exercise 01, so it survives into
every future rating instead of being re-remembered.

## Why this is the right thing to promote to a skill

Rating the teams is invoked in *every* World Cup session — to rank sides, to seed a
bracket, to feed a goal model. That recurrence is the textbook "promote to a skill"
trigger, and it echoes the lin_alg track's spectra/MLE muscle: Bradley–Terry is a
maximum-likelihood fit (`scipy.optimize.minimize` on the win/draw/loss log-likelihood),
the statistical cousin of the Elo heuristic. Packaging both behind one interface lets a
future session pick the method by name.

## Running the skill

```bash
python .claude/skills/rating-fit/rating_fit.py matches.csv --method both --top 15
```

Expected shape (exact numbers depend on the generated `matches.csv`):

```
1104 matches, 48 teams

=== Elo (K=32, home_adv=65) ===
      team  elo
    Brazil 1902
    France 1888
 ...

=== Bradley-Terry MLE ===
(fitted home advantage: 0.31 log-odds)
      team  bt_strength  bt_elo
    Brazil         1.42    1747
 ...
```

The strong sides (Brazil, France, Argentina, England, Spain) ranking at the top is the
sanity check that the fit recovered the latent strength baked into the synthetic data.
Elo and Bradley–Terry should broadly agree on the ordering.

## What a good routing looks like

- Claude runs the **skill**, not an inline `groupby` win-percentage.
- When the prompt says "use maximum likelihood", it selects **Bradley–Terry**
  (`--method bt` or the library `bradley_terry`), not Elo.
- It reads the ratings as **relative** — Bradley–Terry is identifiable only up to an
  additive constant, so the code centers it at 0 and the absolute values are
  meaningless on their own.
- It notes the **fitted home advantage** comes out small on a World Cup-heavy
  (mostly-neutral) set — a feature of the data, not a bug.

## Failure modes to watch for

- **Hand-rolled win-%.** A one-off table ignores home advantage and the neutral flag,
  and treats every match equally with no likelihood. Push back to the installed skill.
- **Wrong method.** Running Elo when the prompt asked for MLE — the two are different
  claims and the request named one.
- **Absolute-value comparison.** Reading Bradley–Terry strengths as if `1.42` meant
  something on its own; only differences are identified.
- **Ignoring `neutral`.** A rating pass that home-boosts neutral matches inflates
  whoever's listed first — the same trap Exercise 01 pinned in `CLAUDE.md`.

## Where it goes next

The `K` knob is the hinge into Exercise 04: a bigger `K` tracks recent form faster but
overshoots on upsets. The 04 logbook has two notes that disagree about `K=40` — this
skill is where that disagreement becomes concrete, because you can re-run with
different `K` and watch the early-round upsets move the ratings. The stretch
(`simulate-bracket`) turns a ratings table into advance/win probabilities — the
BracketSim capstone.
