# Exercise 02 — Plan a modeling experiment (15 min)

**Goal.** Use **plan mode** to agree *how* the `outcome` classifier will be built
**before** a single line of modeling code is written. The deliverable is the
**`plan.md`**; the lesson is that a modeling pipeline is a chain of silent judgement
calls — where does the split go, which columns are features, which metric decides
success — and a plan is where you catch a leak *on paper*, before it inflates a CV
score you'll later have to explain.

## Setup

Re-use the environment from Exercise 01 (pandas / numpy / scikit-learn /
matplotlib), activated **before you start `claude`**:

```bash
conda activate a                  # conda
# or:  source .venv/bin/activate  # pip + venv  (Windows: .venv\Scripts\activate)
```

Keep the `CLAUDE.md` you wrote in Exercise 01 — it carries the target, the
forbidden `outcome_label`, and the split-before-fit rule the plan will lean on.

## The file

`experiment.csv` — the same ~400-row messy table: inconsistent `treatment_group`
labels, unit-suffixed `concentration` strings, blank cells, one `9999` temperature,
a few duplicate rows, a binary `outcome` target, and the leaky `outcome_label`.

## You are the scientist (read before you start)

A modeling pipeline looks mechanical but every stage is a decision you own:

- **Where does the split go?** If any `fit` (scaler, imputer, resampler) touches the
  data *before* the train/test split, the test set has leaked into training — and
  your CV score is a fiction. This is the single most common way a modeling result
  lies.
- **Which columns are features?** `outcome_label` restates `outcome`. Include it and
  you get ~1.00 accuracy and a useless model. The plan must exclude it *explicitly*.
- **Which metric decides?** The target is ~30% positive. Accuracy alone rewards
  predicting "failure" every time. F1 / ROC-AUC or nothing.
- **One split or cross-validation?** A single 80/20 number has no error bar; you
  can't tell signal from split-luck.

**Claude is a tool; you are the scientist.** Plan mode is where you force these
calls into the open — while a leak is a line to move, not a result to retract.

## Steps

1. `cd exercises-a/02-planning && claude`
2. Press `Shift+Tab` twice to enter plan mode.
3. Paste the prompt and submit. Do **not** approve yet:

   ```
   Plan a supervised-learning experiment to predict `outcome` from
   experiment.csv. List every stage as its own step — cleaning, the
   train/test split, preprocessing, the estimator, cross-validation, and
   final evaluation — and for each, say exactly where fitting happens
   relative to the split. Call out any column that must be excluded and why.
   Do not write modeling code yet.
   ```

4. **Read the plan critically.** Work through the checklist below; push back on at
   least one silent decision — especially anything that fits before it splits.
5. **Save it without running the plan.** Approving a plan tells Claude to
   *implement* it — so don't approve. While still in plan mode, ask:

   ```
   Write the complete plan to plan.md and stop — do not implement it.
   ```

   Claude can create a new file in plan mode, so `plan.md` lands on disk; then
   press **`Shift+Tab` to leave plan mode without approving**. That file is the
   deliverable.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Does the plan put the **split before any `fit`**, with preprocessing inside a `Pipeline`? | Fitting on full data leaks the test set; this is the whole lesson. |
| Does it **exclude `outcome_label`** by name, with a reason? | The leaky column is a ~1.00-accuracy trap; excluding it must be deliberate. |
| Does it use **stratified** CV and a **stratified** test split? | A 30%-positive target can lose the minority class in an unlucky split. |
| Does it name metrics **beyond accuracy** (F1, ROC-AUC)? | Accuracy alone is the majority-class baseline here. |
| Does it name its **outputs** (`train.py`, a metrics table, a ROC/confusion figure)? | A plan with no artifacts can't be checked. |

## Discussion prompts

- Which modeling decisions are *house style* (belong in `CLAUDE.md`, e.g. "always
  split before fit", "never use `outcome_label`") versus *this-experiment* (belong
  in the plan or `LOGBOOK.md`, e.g. "chose LogisticRegression baseline, F1 as the
  primary metric this round")?
- The plan is cheap to edit; a leaked pipeline re-run and re-reported to a
  stakeholder is not. Where else in your own work is a reviewed plan worth more than
  fast code?

## Optional — implement the plan (if time permits)

Approve the plan and let Claude build `train.py`, then check the output. Watch *how*
it executes: does every fitted step really live inside the `Pipeline`, or did a
`StandardScaler().fit(X)` sneak in before the split? A quick tell — temporarily add
`outcome_label` back and confirm accuracy jumps to ~1.00, then remove it; if the
leak-free run lands near ~0.8 ROC-AUC, the pipeline is honest.

## Stretch

Add a step that trains a second estimator (`RandomForestClassifier`) through the
*same* `Pipeline` and compares it to the LogisticRegression baseline on the same CV
folds — the artifact that turns "a model" into "a model we chose over an
alternative, on the record."
