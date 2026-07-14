# Solution — Exercise 03 (cv-report skill)

## What this exercise is doing

The learner installs a **`cv-report`** skill and asks a plain-language evaluation
question *without naming it*. Two things are under test: **routing** (does Claude
reach for the skill instead of hand-rolling `cross_val_score`?) and **reuse** (does
the same helper evaluate a second classifier/CSV unchanged?). The skill also bakes in
two habits from Exercises 01–02 — drop the leaky column, read the class balance —
so they survive into every future evaluation instead of being re-remembered.

## Why this is the right thing to promote to a skill

Cross-validating a classifier is the textbook "promote to a skill" trigger: it's a
procedure you run on *every* model, its correct form is easy to get subtly wrong
(single split, accuracy-only, fit-before-fold), and the fix is worth encoding once.
The skill makes the honest version the path of least resistance:

- It takes a **full `Pipeline`**, so preprocessing re-fits per fold — leakage is
  structurally hard to commit through this entry point.
- It **drops `outcome_label` by default** and **warns** if it's present — the leak
  guard travels with the tool.
- It **prints the class balance** and says "accuracy alone is misleading" when the
  target is imbalanced, so nobody quotes bare accuracy by accident.

## Running the skill

Library form (preferred — you pass the pipeline):

```python
from cv_report import cv_report
cv_report(pipe, X, y, n_splits=5)
```

CLI form (builds a leak-free default pipeline):

```bash
python .claude/skills/cv-report/cv_report.py experiment.csv \
    --target outcome --drop outcome_label sample_id
```

Expected output (numbers illustrative):

```
class balance: 30.0% positive (120/400) — accuracy alone is misleading
stratified 5-fold CV:
  accuracy  0.780 ± 0.028   [0.750, 0.800, 0.775, 0.812, 0.763]
  f1        0.610 ± 0.049   [...]
  roc_auc   0.831 ± 0.026   [...]
```

## The leak the skill catches for you

Run it *without* dropping the leaky column and the guard fires:

```bash
python .claude/skills/cv-report/cv_report.py experiment.csv --target outcome --drop sample_id
# WARNING: 'outcome_label' is present and NOT dropped — this leaks the target!
# ... accuracy 1.000 ± 0.000 ...
```

That WARNING plus the ~1.00 line is exactly the failure Exercise 04's logbook records
as a dead end. Having it emitted by the tool, every run, is the point of a skill.

## Failure modes to watch for

- **Claude hand-rolls `cross_val_score`** inline and reports a bare accuracy. Push
  back to the installed skill — the inline version has none of the guard rails.
- **`outcome_label` left in.** Read as a great model instead of the leak alarm the
  WARNING flags.
- **Mean without spread.** The per-fold list is what tells you the estimate is
  stable; a lone mean hides that.
- **Extension without a `description:` update.** If someone adds regression support
  but doesn't widen the frontmatter, "cross-validate my regressor" won't route here —
  the capability is invisible.

## Where it goes next

The stretch (`--estimator rf` on the same folds) turns the skill from "score one
model" into "compare models fairly" — same preprocessing, same splits, one number
each. That's the on-ramp to the model-selection decisions the 04 logbook records.
