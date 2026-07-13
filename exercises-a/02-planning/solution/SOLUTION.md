# Solution — Exercise 02 (plan a modeling experiment)

## What this exercise is doing

The learner uses **plan mode** to lay out a supervised-learning experiment for
`outcome` *before* writing modeling code. The artifact is `plan.md`; the point is
that a pipeline is a chain of decisions where one wrong ordering — a `fit` before the
split — silently inflates every number downstream. Catching that on paper costs a
line move; catching it after you've reported a CV score costs a retraction.

## What a good plan looks like

A strong `plan.md` (see `plan.md` in this folder) does four things a weak one skips:

1. **Puts the split before any `fit`.** Row-level, fit-free cleaning (dedupe,
   label-normalize, parse concentration, quarantine the `9999`) may run first —
   those learn no parameters. But imputation and scaling *fit state*, so they belong
   **inside a `Pipeline`**, after the split, re-fit per fold. A good plan states this
   distinction explicitly.
2. **Excludes `outcome_label` by name, with a reason.** Not "use the relevant
   columns" — the plan must call the leak out and drop it.
3. **Stratifies** both the CV and the hold-out test, because the target is ~30%
   positive.
4. **Names outputs and metrics** — a per-fold + mean±std table of accuracy/F1/ROC-AUC,
   a held-out test check, and a ROC figure — so the plan is checkable.

## Running the reference solution

```bash
python train.py --in experiment.csv --figdir figures
```

Expected shape of the output (numbers illustrative — exact values depend on the
generated CSV):

```
rows=400  positive rate=0.30  (class balance)

Stratified 5-fold CV (LogisticRegression):
  accuracy  0.78 ± 0.03   [0.75, 0.80, 0.77, 0.81, 0.78]
  f1        0.61 ± 0.05   [...]
  roc_auc   0.83 ± 0.03   [...]

Held-out test (never seen during CV):
  F1      0.60
  ROC-AUC 0.82

wrote figures/roc_curve.png
```

The CV and held-out test numbers agreeing (both ROC-AUC ≈ 0.82) is the signal that
the pipeline **isn't leaking**. That agreement is the payoff of doing the split
right — and it's exactly what collapses in Exercise 04's leakage dead end.

## The leak demo (worth showing the room)

Temporarily add `outcome_label` to the feature matrix — e.g. remove it from
`LEAKY_COLS` — and re-run. Accuracy and ROC-AUC jump to ~1.00 across every fold.
That single number is the cheapest possible illustration of target leakage: the
model "predicts" `outcome` from a renamed copy of `outcome`. Then restore the
exclusion. The `assert "outcome_label" not in X.columns` in `split_xy` is the guard
that makes this mistake loud instead of silent.

## Failure modes to watch for

- **Fit before split.** The plan (or the code) does `StandardScaler().fit(X)` on the
  whole frame, then splits. CV looks a little too good. Fix: every fitted step inside
  the `Pipeline`.
- **Leaky column kept.** `outcome_label` survives into `X`; accuracy ~1.00 is read as
  success instead of alarm.
- **One split, one number.** A lone 80/20 accuracy with no spread — you can't tell a
  real gain from split-luck. Fix: stratified k-fold with per-fold values.
- **Accuracy only.** On a 30%-positive target, ~0.70 accuracy is just the majority
  baseline. Fix: report F1 / ROC-AUC.
- **`plt.show()` / no `Agg` backend.** Blocks in a headless run. Fix: `matplotlib.use("Agg")`
  and save to `figures/`.

## Why plan mode, not just code

The clean/split/fit ordering is invisible in a finished script unless you read it
carefully — but it is the entire difference between an honest model and a lying one.
Forcing it into a reviewed plan is how you catch it while it's still a sentence, not
a result you've already shown someone.
