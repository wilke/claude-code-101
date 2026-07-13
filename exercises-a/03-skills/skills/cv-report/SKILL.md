---
name: cv-report
origin: workshop
description: |
  Evaluate a classifier honestly with stratified k-fold cross-validation: per-fold
  and mean±std accuracy, F1, and ROC-AUC, plus a one-line class-balance note so an
  imbalanced target can't hide behind accuracy. Works as a library on your own
  sklearn Pipeline + X, y, or as a CLI on a CSV (it builds a leak-free default
  pipeline). Use it every time you want to report how a model does — instead of a
  single train/test split's lone number.
---

<!--
The `origin:` field tags skills you wrote yourself versus imported ones,
so future-you knows what's safe to modify.
-->


# cv-report skill

Use this skill when:

- You have a classifier (or a full sklearn `Pipeline`) and want **cross-validated
  metrics with spread**, not a single split's number you can't size.
- You want the **class balance surfaced automatically**, so you never quote bare
  accuracy on an imbalanced target and call it a win.
- You want the evaluation to **re-fit preprocessing per fold** — pass a `Pipeline`
  and leakage is structurally impossible.

## How to invoke

As a library, on your own estimator (preferred — you control the pipeline):

```python
from cv_report import cv_report
cv_report(pipe, X, y, n_splits=5)   # pipe is a full sklearn Pipeline
```

As a CLI, on a CSV (it builds a leak-free default pipeline for you):

```bash
python .claude/skills/cv-report/cv_report.py experiment.csv \
    --target outcome --drop outcome_label sample_id
```

`--target` names the label column; `--drop` lists columns to exclude from features
(the leaky `outcome_label` and the `sample_id` are dropped by default);
`--n-splits` sets the number of folds.

Output looks like:

```
class balance: 30.0% positive (120/400) — accuracy alone is misleading
stratified 5-fold CV:
  accuracy  0.780 ± 0.028   [0.750, 0.800, 0.775, 0.812, 0.763]
  f1        0.610 ± 0.049   [...]
  roc_auc   0.831 ± 0.026   [...]
```

## Interpreting the output

- **Read F1 / ROC-AUC before accuracy** when the balance line says the target is
  imbalanced — 78% accuracy on a 30%-positive target is barely above "always predict
  the majority" (70%).
- **The per-fold spread is the point.** A tight `± 0.03` means the estimate is
  stable; a wide `± 0.12` means your single-split number was luck.
- **A suspiciously perfect score (≈ 1.00)** is almost always leakage — a column that
  restates the target (like `outcome_label`) slipped into the features. The CLI
  prints a WARNING if `outcome_label` is present and not dropped.
- **CV that agrees with a held-out test** is your evidence the pipeline is honest;
  CV that beats the test badly is the leakage signature.

## Extending

- Add `--estimator {logreg,rf}` to swap in a `RandomForestClassifier` through the
  same preprocessing, so you compare models on identical folds.
- Add regression support (`--task regression` → R²/MAE with `KFold`) and widen the
  `description:` so a future "cross-validate my regressor" request routes here.
- Emit the metrics table as JSON (`--json`) to feed a model-quality gate in CI.
