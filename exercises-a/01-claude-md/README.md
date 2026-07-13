# Exercise 01 — Write a CLAUDE.md for a modeling task (15 min)

**Goal.** Feel how a `CLAUDE.md` changes the assistant's behaviour on a *modeling*
prompt. Ask "build a model to predict outcome" cold and Claude has to guess a pile
of decisions you'd normally make yourself: **which** column is the target,
classification vs regression, whether to split before fitting, which columns are
even allowed as features — and one of those columns is a **trap**. Unlike track a0's
01 (which shipped only a CSV), this folder also ships a tiny `load.py`, so `/init`
has a little code to read. You'll walk the same three phases: ask cold, let `/init`
try, then add what it couldn't have known.

Do track [`a0`](../../exercises-a0/) first if you haven't — the cleaning habits it
builds are assumed here.

## Setup

Work in a virtual environment so the exercise's packages stay isolated. Create and
activate it **before you start `claude`** — Claude runs Python itself, so it uses
whichever environment is active.

conda:

```bash
conda create -n a python=3.11 pandas numpy scikit-learn matplotlib
conda activate a
```

pip + venv:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pandas numpy scikit-learn matplotlib
```

## The files

- `experiment.csv` — the same ~400-row messy lab table from track a0: an id, a
  batch, a treatment group, a temperature, a concentration, a numeric `yield`, a
  binary `outcome`, **and** an `outcome_label`.
- `load.py` — a tiny starter that reads the CSV and prints its shape. It does *not*
  clean, split, or model anything. It exists so `/init` has code to scan (and so you
  can see how thin an inference `/init` still makes from a stub).

Two columns are traps, and neither is labelled as such:

- `outcome_label` is just `outcome` spelled `success`/`failure`. Feed it to a model
  and you predict `outcome` from a copy of itself → ~100% accuracy, zero learning.
- The numeric columns are dirty (blanks, a `9999` temperature, unit-suffixed
  `concentration` strings). Fit a scaler or imputer on the **whole** table before
  splitting and your scores are optimistically biased.

## Phase 1 — Without a CLAUDE.md

1. With no `CLAUDE.md` in the folder, open a session and ask:

   ```
   build a model to predict outcome
   ```

2. Watch what Claude does — this is your baseline. Look for:
   - **Which target** did it model — `outcome` (right) or did it drift to `yield`?
     Did it treat it as **classification** or silently regress?
   - Did it use `outcome_label` as a feature? (If accuracy comes back ~1.00,
     that's the tell — it leaked the answer in.)
   - Did it **split before** fitting any scaler/imputer, or fit on the full data
     first (leakage)?
   - Did it report a **single train/test split** or **cross-validated** metrics
     with spread?
   - Which metric — bare **accuracy** on an imbalanced target, or F1 / ROC-AUC too?
   - Did it **ask you anything**, or guess every one of these at once?

## Phase 2 — Let `/init` try

3. Reset the conversation and generate a `CLAUDE.md` from the folder:

   ```
   /clear
   ```
   ```
   /init
   ```

4. Read what `/init` produced. It can see `load.py`, so expect it to note "loads
   `experiment.csv` with pandas" — but a stub that only reads and prints tells it
   **nothing** about which column is the target, which column is poison, or that
   fitting must happen after the split. That's the lesson: **`/init` infers from
   code; the modeling contract isn't in the code, so it's on you.**

## Phase 3 — Add what `/init` couldn't know, then iterate

5. Write the modeling contract `/init` had no way to infer into `CLAUDE.md` (merge
   it into whatever `/init` generated). A seed to start from:

   ```markdown
   # Project: predict `outcome` from experiment.csv

   ## Stack
   - pandas / numpy / scikit-learn (+ matplotlib for figures, saved to
     figures/, never shown)

   ## The task
   - Target is `outcome` — BINARY CLASSIFICATION (0/1). Not `yield`, not regression.
   - FORBIDDEN feature: `outcome_label`. It is `outcome` restated as
     success/failure — using it leaks the target. Drop it before modeling.
   - Features: batch, treatment_group (categorical), temperature_C, concentration
     (numeric, needs cleaning as in a0).

   ## No leakage — the hard rule
   - ALWAYS split before you fit anything. Never fit a scaler, imputer, or
     resampler on the full dataset.
   - Put every fitted step (impute, scale, one-hot, estimator) inside a single
     sklearn Pipeline / ColumnTransformer, so cross-validation re-fits it per fold.

   ## Reporting
   - Report STRATIFIED cross-validated metrics (accuracy, F1, ROC-AUC) with
     per-fold spread — not a single split's number.
   - The class is imbalanced (~30% positive); never report accuracy alone.
   - random_state=0 everywhere it's accepted, for reproducibility.

   ## Don'ts
   - Never use outcome_label. Never fit before splitting. No plt.show().
   ```

6. Reset the conversation (`/clear`) and re-ask the exact same prompt:

   ```
   build a model to predict outcome
   ```

7. Compare against your Phase 1 baseline. With the `CLAUDE.md` in place, Claude
   should drop `outcome_label`, build a `Pipeline` whose steps fit **after** a
   stratified split, and report cross-validated accuracy/F1/ROC-AUC with spread —
   not a lone accuracy number, and not a suspicious 1.00.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did Claude model `outcome` as **classification**, not drift to `yield`/regression? | Wrong target = wrong project, silently. |
| Did it **exclude `outcome_label`**? | Including it leaks the answer; ~1.00 accuracy is a fake win. |
| Did every fitted step live **inside a Pipeline, after the split**? | Fitting on full data leaks test information into training. |
| Did it report **cross-validated** metrics with spread, not one split? | A single split's number is noise you can't size. |
| Did it go beyond bare **accuracy** (F1 / ROC-AUC) on an imbalanced target? | 70% accuracy is the majority-class baseline here. |

## Discussion prompts

- Which of these belong in `CLAUDE.md` (true every session — "never use
  `outcome_label`", "always split before fit") versus a plan or `LOGBOOK.md`
  (today's choice of estimator, this run's CV scores)?
- `/init` saw `load.py` and still couldn't infer the target or the leak. What
  *would* a richer starter (say, a `train.py` with a labelled `TARGET =` constant)
  have let it infer — and what would still be on you?

## Stretch

Add a convention that every modeling run must save a ROC curve (or confusion
matrix) to `figures/`, and re-ask — does Claude produce the figure unprompted,
purely from the `CLAUDE.md` rule? Then deliberately *leave `outcome_label` in* once
and watch the accuracy jump to ~1.00 — the cheapest possible demo of why the
forbidden-column rule earns its place in `CLAUDE.md`.
