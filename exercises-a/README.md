# Track a — predictive modeling, the four files (scikit-learn)

The **second** domain-neutral track. It builds directly on track [`a0`](../exercises-a0/):
same messy `experiment.csv`, same four files — but now the task is **predictive
modeling**, so it adds `scikit-learn`. You'll go clean → **stratified split** →
`Pipeline` → **cross-validated** metrics → figure, and meet the single most common
way a modeling result lies: **data leakage**.

Do track a0 first if you're new to Claude Code. If you already model for a living
and want to see how the four-file architecture keeps a modeling project honest,
start here.

## The task and the trap

Predict the binary `outcome` from the other columns. Two traps are baked in:

- **A leaky column.** `outcome_label` is just `outcome` spelled `success`/`failure`.
  Feed it to a model and you get ~100% accuracy — and a useless model. The
  `CLAUDE.md` you write must forbid it.
- **Leaky preprocessing.** Fit a scaler or imputer (or resample) on the *whole*
  dataset before splitting and your cross-validation scores are optimistic; the
  held-out test collapses. The fix — put every fitted step inside a `Pipeline`,
  after the split — is the spine of the 04 logbook exercise.

## Setup (once)

```bash
# conda
conda create -n a python=3.11 pandas numpy scikit-learn matplotlib
conda activate a

# or pip + venv
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pandas numpy scikit-learn matplotlib
```

## The exercises, in order

1. [`01-claude-md/`](01-claude-md/) — write a `CLAUDE.md` that pins the target, forbids the leaky column, and mandates split-before-fit.
2. [`02-planning/`](02-planning/) — plan the modeling experiment (split → Pipeline → CV → test) before code.
3. [`03-skills/`](03-skills/) — package a reusable `cv-report` skill (stratified CV, per-fold + mean±std, class balance).
4. [`04-logbook/`](04-logbook/) — consolidate modeling notes — including the leakage dead end — into a `LOGBOOK.md`.

Open each folder on its own (`cd exercises-a/01-claude-md && claude`) and follow
its `README.md`.
