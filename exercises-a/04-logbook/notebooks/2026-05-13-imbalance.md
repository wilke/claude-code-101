# 2026-05-13 — Class imbalance: what to do about ~30% positive

The leak-free baseline is honest but unspectacular (F1 ≈ 0.60). Before tuning
anything, the real open question is how to handle the class imbalance — the positive
`outcome` is only ~30% of rows, so the default 0.5 threshold and plain accuracy both
flatter a lazy model.

- **Observation.** A trivial "always predict failure" classifier scores ~70%
  accuracy here. That's the number any real model has to beat, and it's why accuracy
  was demoted to a secondary metric on 05-11.
- **Three options on the table (none chosen yet):**
  1. **Threshold tuning** — keep the model, move the decision threshold off 0.5 to
     trade precision for recall based on what the downstream use actually costs.
  2. **Class weights** — `class_weight="balanced"` on the estimator, re-weighting the
     minority class during fit. Cheap, stays inside the Pipeline, no new data.
  3. **Resampling** — SMOTE / random over- or under-sampling. NB: must happen
     **inside** the CV Pipeline (via `imblearn`), never on the full data — that was
     exactly Leak 2 on 05-12.
- **Why it's deferred.** The right choice depends on the **cost of a false negative
  vs a false positive**, which is a question for whoever uses the prediction, not one
  the data answers. Picking a resampling scheme now would be optimizing a metric we
  haven't agreed is the right metric.

**Open question:** what is the operating point? Once we know the relative cost of the
two error types, threshold tuning vs class weights vs resampling becomes a decision
we can actually justify — and we can compare them on the *same* CV folds. Until then,
report F1 + ROC-AUC and leave the threshold at 0.5.
