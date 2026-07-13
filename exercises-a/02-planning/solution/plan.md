# Plan — predict `outcome` from `experiment.csv`

A model of the `plan.md` a good plan-mode session produces. The load-bearing detail
is **where fitting happens relative to the split**: every fitted step lives inside a
`Pipeline`, so cross-validation re-fits it per fold and nothing leaks.

## Goal

Build and honestly evaluate a binary classifier for `outcome`, producing
cross-validated metrics with spread, a held-out test check, and one evaluation
figure — with a clear audit trail that no test information leaked into training.

## Inputs / outputs

- **Input:** `experiment.csv` (~403 rows, 9 columns; dirty; ~30% positive `outcome`).
- **Outputs:** `train.py`, a printed metrics table (per-fold + mean±std accuracy /
  F1 / ROC-AUC), a held-out test score, and `figures/roc_curve.png`.

## Feature / target contract

- **Target:** `outcome` (binary, 0/1). Classification — *not* `yield`, *not*
  regression.
- **EXCLUDED — `outcome_label`.** It is `outcome` restated as `success`/`failure`;
  including it leaks the target (→ ~1.00 accuracy). Drop it before `X` is built.
- **EXCLUDED — `sample_id`.** A row id, not a feature.
- **Features:** `treatment_group`, `batch` (categorical → one-hot); `temperature_C`,
  `concentration` (numeric → impute + scale, cleaned as in a0).

## Steps

1. **Clean (row-level, safe before split).** Drop full-row duplicates; normalize
   `treatment_group` (`strip().lower()`, `ctrl→control`); parse `concentration` out
   of `"1.5 mg/mL"` → float; quarantine `temperature_C > 200 → NaN`. These are
   deterministic per-row transforms with no fitted state, so they may run before the
   split. **Imputation and scaling do NOT belong here** — they fit parameters.
2. **Build `X`, `y`.** `y = outcome`; `X = df.drop(columns=[outcome, outcome_label,
   sample_id])`. Assert `outcome_label` is absent from `X`.
3. **Stratified train/test split.** 80/20, `stratify=y`, `random_state=0`, so the
   ~30% positive rate is preserved in both halves.
4. **Preprocessing inside a `ColumnTransformer` / `Pipeline`.** Numerics:
   `SimpleImputer(median)` → `StandardScaler`. Categoricals:
   `OneHotEncoder(handle_unknown="ignore")`. The transformer is a Pipeline *step*, so
   it is fit on training folds only — never on the full data.
5. **Estimator.** `LogisticRegression(max_iter=1000, random_state=0)` baseline as the
   final Pipeline step. (Optional: a `RandomForestClassifier` through the same
   Pipeline for comparison — see stretch.)
6. **Stratified k-fold CV.** `StratifiedKFold(n_splits=5, shuffle=True,
   random_state=0)`; `cross_validate` scoring `accuracy`, `f1`, `roc_auc`. Report
   per-fold values and mean±std — the whole Pipeline re-fits each fold.
7. **Fit on the full training set, evaluate once on the held-out test.** Compare test
   metrics to CV; a large gap is the leakage alarm.
8. **Figure.** ROC curve (or confusion matrix) on the held-out test → `figures/`.

## Sanity checks

- Assert `outcome_label` not in `X.columns` (the leak guard).
- Confirm no `.fit(` touches data outside the Pipeline / before the split.
- Sanity demo: adding `outcome_label` back should spike accuracy to ~1.00 — proof
  the exclusion matters.

## Non-goals

- No hyperparameter search this round (fixed `random_state=0`, default `C`).
- No resampling/SMOTE (class imbalance is deferred to the logbook's open question).
