# Solution — Exercise 01 (CLAUDE.md, predictive modeling)

## What this exercise is doing

Two files ship: `experiment.csv` (the same messy ~400-row lab table from track a0)
and `load.py` (a stub that only reads and prints the shape). The learner asks the
same vague question — *"build a model to predict outcome"* — across three phases:
cold (Phase 1), after `/init` (Phase 2), and with a hand-written `CLAUDE.md`
(Phase 3). That one sentence hides a stack of decisions Claude will otherwise make
silently:

1. **Target & task** — is the target `outcome` (binary classification) or `yield`
   (regression)? "predict outcome" *says* `outcome`, but a model that quietly
   regresses `yield` still "runs".
2. **The leak** — `outcome_label` is `outcome` restated as `success`/`failure`.
   Left in the feature matrix, the model predicts the target from a copy of itself.
3. **Leaky preprocessing** — fitting a scaler/imputer on the full table *before*
   the split lets test-fold information bleed into training; CV looks optimistic.
4. **Evaluation** — one train/test split vs stratified cross-validation; bare
   accuracy vs F1/ROC-AUC on a ~30%-positive target.

A good `CLAUDE.md` turns all four silent guesses into explicit, up-front rules.

## Phase 2 — what `/init` produces here (a little, from `load.py`)

Unlike track a0's 01 (data only), this folder ships `load.py`, so `/init` has code
to read. Expect it to correctly note "loads `experiment.csv` with pandas, prints
shape" — and **nothing** about the target, the forbidden column, or split-before-fit,
because a read-and-print stub encodes none of that. That's the lesson: `/init`
infers from *code*, and the modeling contract simply isn't in the code. It's on you.

## The two traps (what a good run avoids)

| Trap | How it shows up | The blunder it causes |
|------|-----------------|-----------------------|
| Leaky column | `outcome_label` ∈ {success, failure} == `outcome` | ~1.00 accuracy; a model that learned nothing |
| Leaky preprocessing | fit `StandardScaler`/`SimpleImputer`/SMOTE on full data before split | optimistic CV, collapses on held-out test |
| Wrong target | regressing `yield` instead of classifying `outcome` | "works", answers the wrong question |
| Wrong metric | accuracy on a ~30%-positive target | 70% looks fine but is the majority baseline |

Plus the same dirty numerics from a0 (blanks, the `9999` temperature, unit-suffixed
`concentration`) — which is *why* imputing/scaling is needed at all, and therefore
why the fit-after-split rule matters.

## A worked CLAUDE.md (Phase 3)

```markdown
# Project: predict `outcome` from experiment.csv

## Stack
- pandas / numpy / scikit-learn (+ matplotlib for figures, saved to figures/)

## The task
- Target = `outcome`, BINARY CLASSIFICATION. Not `yield`, not regression.
- FORBIDDEN feature: `outcome_label` (it restates `outcome`). Drop it.
- Features: batch, treatment_group (categorical), temperature_C, concentration
  (numeric; clean as in a0).

## No leakage — the hard rule
- Split BEFORE fitting anything. Never fit a scaler/imputer/resampler on full data.
- Every fitted step inside one Pipeline / ColumnTransformer, re-fit per CV fold.

## Reporting
- Stratified CV metrics (accuracy, F1, ROC-AUC) with per-fold spread.
- Imbalanced (~30% positive) — never accuracy alone.
- random_state=0 everywhere accepted.

## Don'ts
- Never use outcome_label. Never fit before splitting. No plt.show().
```

## What Claude should produce after reading it

A good response names the target, drops the leak, and builds a leak-free pipeline
*before* quoting any number:

> Target is `outcome` (binary). I dropped `outcome_label` (it's the target restated,
> so it would leak). Features: `treatment_group`, `batch` (one-hot), `temperature_C`,
> `concentration` (imputed + scaled). All preprocessing sits in a `Pipeline`, so it
> re-fits inside each CV fold — no leakage.
>
> Stratified 5-fold CV (LogisticRegression, `random_state=0`):
> - accuracy 0.78 ± 0.03, F1 0.61 ± 0.05, ROC-AUC 0.83 ± 0.03
>
> Held-out test (20%, stratified): F1 0.60, ROC-AUC 0.82 — consistent with CV, so
> the pipeline isn't leaking. *(Numbers illustrative.)*

Contrast the leak: if `outcome_label` is left in (or one-hot encoded), accuracy jumps
to ~1.00 across every fold — the unmistakable signature of a leaked target.

A minimal leak-free script it might write:

```python
"""train.py — leak-free baseline classifier for `outcome`."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

df = pd.read_csv("experiment.csv").drop_duplicates()
df["treatment_group"] = df["treatment_group"].str.strip().str.lower().replace(
    {"ctrl": "control"})
df["concentration"] = df["concentration"].str.extract(
    r"([-+]?\d*\.?\d+)").astype(float)
df.loc[df["temperature_C"] > 200, "temperature_C"] = np.nan

y = df["outcome"].astype(int)
X = df.drop(columns=["outcome", "outcome_label", "sample_id"])  # drop the leak!

num = ["temperature_C", "concentration"]
cat = ["batch", "treatment_group"]
pre = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                      ("sc", StandardScaler())]), num),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
])
pipe = Pipeline([("pre", pre),
                 ("clf", LogisticRegression(max_iter=1000, random_state=0))])

cv = StratifiedKFold(5, shuffle=True, random_state=0)
scores = cross_validate(pipe, X, y, cv=cv,
                        scoring=["accuracy", "f1", "roc_auc"])
for m in ["accuracy", "f1", "roc_auc"]:
    s = scores[f"test_{m}"]
    print(f"{m:9s} {s.mean():.3f} ± {s.std():.3f}")
```

## Where it usually goes wrong on the first try

- **The leak.** Claude keeps `outcome_label`, one-hot encodes it, reports ~1.00
  accuracy, and calls it a great model. **Add the forbidden-column rule** — and use
  the 1.00 as the teaching moment.
- **Fit before split.** Claude fits `StandardScaler().fit(X)` on the whole frame,
  *then* splits. CV looks a touch optimistic. **Pin the Pipeline / fit-after-split
  rule.**
- **One split, one number.** Claude reports a single 80/20 accuracy with no spread.
  **Require stratified CV with per-fold spread.**
- **Accuracy only.** On a 30%-positive target, ~0.70 accuracy is just "predict the
  majority". **Require F1 / ROC-AUC too.**
- **Wrong target.** Claude regresses `yield`. **Pin target = `outcome`,
  classification.**

The loop is identical to a0: ask → notice a silent guess → put the rule in
`CLAUDE.md` → re-ask. The difference is that here the silent guesses don't just make
an ugly summary — they manufacture a **model that lies**.
