# Solution — Exercise 04 (modeling LOGBOOK.md)

## What this exercise is doing

The learner consolidates three dated modeling notes into a `LOGBOOK.md`, then uses it
to choose a next step and closes with a dated append. The synthesis is the pretext;
the artifact is the file — specifically, whether the **leakage dead end** survives
consolidation *with its mechanism intact*, because that is the single most valuable
line in the file. A future session that reads "fitting the scaler on full data before
the split inflated CV to 0.72 while the held-out test collapsed to 0.55" will not
re-ship that model; one that reads "we had a leakage bug" will.

The model file below is *not* shipped — the learner produces it. A good student
version may be shorter.

## A worked LOGBOOK.md

```markdown
# LOGBOOK — predicting `outcome` from experiment.csv

## Decisions
- Target is `outcome`, binary classification; LogisticRegression baseline. Beat
  the simple linear model before reaching for a random forest (RF was ~equal on
  ROC-AUC, so no switch yet). [2026-05-11]
- F1 is the primary metric, accuracy secondary — the target is imbalanced, so
  accuracy flatters a lazy model; also track ROC-AUC. [2026-05-11]
- Evaluate with stratified 5-fold CV + a held-out stratified test; n is small
  (~400), a single split is too noisy to trust. [2026-05-11]
- Every fitted step lives inside one Pipeline: impute/scale/one-hot re-fit per
  fold; only fit-free row-level cleaning runs before the split. [2026-05-12]

## Parameters
- `random_state=0` everywhere; `n_splits=5`; `test_size=0.20`;
  `LogisticRegression(max_iter=1000, C=1.0)`. [2026-05-11]
- Leak-free baseline: CV F1 ≈ 0.61, ROC-AUC ≈ 0.83; held-out test ROC-AUC ≈ 0.82
  (CV/test agreement = the no-leak check). [2026-05-11, 2026-05-12]
- Majority-class ("always failure") accuracy ≈ 70% — the floor to beat. [2026-05-13]

## Dead Ends
- `outcome_label` as a feature → accuracy ≈ 1.00. It restates the target
  (success/failure); one-hot encoding it leaks the answer. Caught by treating a
  perfect score as a leak, not a win; guard with
  `assert "outcome_label" not in X.columns`. [2026-05-12]
- Fitting scaler/imputer (or SMOTE) on the full data before the split. CV F1
  looked great (≈ 0.72) but held-out test F1 collapsed (≈ 0.55) — the fitted
  state had seen the test rows. Fix: move all fitting inside the CV Pipeline;
  honest CV/test both ≈ 0.60. [2026-05-12]

## Open Questions
- How to handle the ~30% positive class? Threshold tuning vs
  `class_weight="balanced"` vs resampling (SMOTE *inside* the Pipeline only). The
  choice depends on the cost of a false negative vs false positive — a question
  for the prediction's user, not the data. Deferred until we know the operating
  point. [2026-05-13]
```

## What a good consolidation keeps (and cuts)

**Keeps** — the durable, re-consultable facts:

- **Decisions** with their *reason*: LogisticRegression baseline (beat the simple
  model first); F1 primary because imbalanced; stratified CV + held-out test because
  n is small; all fitting inside one Pipeline.
- **Parameters** you'd re-tune: `random_state=0`, `n_splits=5`, `test_size=0.20`; the
  leak-free baseline numbers (F1 ≈ 0.61, ROC-AUC ≈ 0.83); the ~70% majority-class
  floor.
- **Dead Ends** with mechanism: both leaks — `outcome_label` → ~1.00, and full-data
  preprocessing fit → CV 0.72 / test 0.55 — plus the fixes.
- **Open Questions** left open: how to handle ~30% positive (threshold vs class
  weights vs in-Pipeline resampling), pending the cost of FN vs FP.

**Cuts** — the day-log noise: "then I re-ran the notebook", "tried RF informally",
timestamps of each experiment. If `LOGBOOK.md` is longer than the three source notes,
the trimming step didn't happen.

## The two leaks are the payload

The whole track exists to teach that a modeling result can look great and still be a
lie. The 05-12 note carries both instances, and the consolidation must preserve the
*distinction*:

- **`outcome_label`** is a *feature-selection* leak — an obvious column that restates
  the target. Signature: ≈1.00 accuracy. Guard: assert it's absent from `X`.
- **Preprocessing-before-split** is a *procedural* leak — subtle, shows up only as a
  CV/test gap. Fix: everything fitted inside the `Pipeline`.

A consolidation that collapses these into one bullet ("avoid leakage") has thrown away
the more valuable of the two lessons.

## Step 4 — a good next-step answer

Expected: names the **imbalance open question** (from `2026-05-13`) or re-verifying
the no-leak CV/test agreement (from `2026-05-12`), and cites the entry. The tell of a
weak answer is genericness — "get more data", "try deep learning" — untethered to any
entry. Push back exactly as the README says: "name the entry that motivates this."

## Step 5 — the ritual

The dated append + `STATUS.md` overwrite is the habit the whole four-file
architecture is built on: the logbook accretes durable knowledge; `STATUS.md` is
overwritten with just "where we are now." A good append is 3–5 bullets, dated, citing
what changed this session — not a re-summary of the whole project.

## Discussion: CLAUDE.md vs LOGBOOK.md

The cleanest split to draw out: **"always split before fit" and "never use
`outcome_label`"** are true every session and every dataset → `CLAUDE.md`. **"The
leak-free baseline is F1 ≈ 0.61" and "the 9999 handling for this table"** are
data-specific findings → `LOGBOOK.md`. The leakage *rule* is house style; the leakage
*episode* (with numbers) is a logbook dead end. Both matter; they live in different
files.
