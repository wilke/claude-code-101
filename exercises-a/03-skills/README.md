# Exercise 03 — Package cross-validation as a skill (15 min)

**Goal.** See how a **skill** turns a procedure you run on every model — "score this
honestly with stratified cross-validation, not one split" — into a named artifact
Claude invokes for you. The CV report is the pretext; **the skill is the artifact**:
Claude routes a plain-language request ("how good is this model?") to the skill
without you naming it, and the same helper evaluates *any* classifier, not just this
one — while making leakage structurally hard to commit.

## What ships

```
03-skills/
├── README.md
├── SOLUTION.md
├── experiment.csv            # the messy table, target = outcome
└── skills/
    └── cv-report/
        ├── SKILL.md
        └── cv_report.py      # stratified CV: per-fold + mean±std, class balance
```

Install the skill so Claude can find it:

```bash
mkdir -p .claude
cp -R skills .claude/
```

## Setup

Re-use the track A environment (pandas / numpy / scikit-learn), activated **before
you start `claude`**:

```bash
conda activate a                  # conda
# or:  source .venv/bin/activate  # pip + venv
```

## Steps

1. `cd exercises-a/03-skills && claude`
2. Ask — **without naming the skill** (routing is what's being tested):

   ```
   I've got experiment.csv with a binary `outcome` column. How well can a
   model predict it? Give me cross-validated metrics, not a single split.
   ```

   Claude should route this to the **cv-report** skill and run it, then read back the
   per-fold spread and the class-balance note — and, crucially, **drop
   `outcome_label`** (the skill does so by default and warns if it's present). If
   Claude hand-rolls a one-off `cross_val_score` inline instead, push back: "use the
   skill in `.claude/skills/`."

3. Point the skill at a **different classifier or CSV** — pass your own `Pipeline`
   via the library entry point (`from cv_report import cv_report`), or run the CLI on
   another labelled table. The same helper reports *its* folds and *its* balance.
   That reuse is the whole point: a skill is written once and pays off on every model
   you evaluate.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did Claude *run* the skill, or hand-roll `cross_val_score` inline? | The helper is the source of truth; an inline call is a one-shot with no guard rails. |
| Did it **drop `outcome_label`** (or heed the leak WARNING)? | Keeping it yields ~1.00 — a fake win the skill is designed to expose. |
| Did it report **per-fold spread**, not just a mean? | A mean with no spread hides whether the estimate is stable. |
| Did it read the **class-balance line** and not lean on accuracy? | 78% accuracy on a 30%-positive target is near the majority baseline. |
| On an extension, did it update the skill's `description:`? | A capability the description doesn't mention is invisible to routing. |

## Discussion prompts

- The skill takes a full `Pipeline` on purpose. Why is "pass me a Pipeline" a
  better contract than "pass me a fitted model" for an evaluation helper — what does
  it make impossible?
- Which belongs in this shared skill versus a project-specific one: "always report
  ROC-AUC", or "flag if F1 drops below 0.6 for *this* product"?

## Stretch

Add an `--estimator rf` option so the skill can score a `RandomForestClassifier`
through the *same* preprocessing on the *same* folds, and update its `description:`
so a future "compare a random forest to my baseline" request routes here — a
model-comparison you can invoke, not re-code each time.
