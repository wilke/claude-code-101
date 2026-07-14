# Exercise 02 — Plan a data-cleaning pass (15 min)

**Goal.** Use **plan mode** to agree *how* the messy `experiment.csv` will be
cleaned **before** a single cell is changed. The deliverable is the **`plan.md`**;
the lesson is that cleaning is full of silent judgement calls (what to do with a
`9999`, whether `CTRL` and `control` are the same group) and a plan is where you
catch them — while they're still cheap to change.

## Setup

Re-use the environment from Exercise 01 (pandas / numpy / matplotlib), activated
**before you start `claude`**:

```bash
conda activate a0                 # conda
# or:  source .venv/bin/activate  # pip + venv  (Windows: .venv\Scripts\activate)
```

Keep the `CLAUDE.md` you wrote in Exercise 01 — it carries the column dictionary
the plan will lean on.

## The file

`experiment.csv` — the same ~400-row messy table from Exercise 01: inconsistent
`treatment_group` labels, unit-suffixed `concentration` strings, blank cells, one
`9999` temperature, and a few duplicate rows.

## You are the scientist (read before you start)

Cleaning looks mechanical but every step is a decision you own:

- Is `9999` a **sentinel for missing**, or a fat-fingered **99.9**? Drop it, blank
  it, or repair it — and the choice changes your temperature mean.
- Does `" control "` (with spaces) equal `control`? Almost certainly — but
  Claude will silently pick an answer if you don't state one.
- Do you **drop** rows with missing `concentration`, or keep them with `NaN`?

**Claude is a tool; you are the scientist.** Plan mode is where you force these
calls into the open instead of discovering them in a corrupted output later.

## Steps

1. `cd exercises-a0/02-planning && claude`
2. Press `Shift+Tab` twice to enter plan mode.
3. Paste the prompt and submit. Do **not** approve yet:

   ```
   Plan how you would clean experiment.csv into a tidy table and write a
   short summary report. List every cleaning decision as its own step, and
   for anything ambiguous (e.g. the 9999 temperature) present the options
   rather than picking one silently.
   ```

4. **Read the plan critically.** Work through the checklist below; push back on at
   least one silent decision.
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
| Does the plan **enumerate** each cleaning step (labels, units, blanks, outlier, dupes) separately? | A one-line "clean the data" plan hides every real decision. |
| Does it present **options** for the `9999`, not silently drop it? | The choice changes your results; you should make it, not Claude. |
| Does it say how missing values are handled per column? | "Drop rows" vs "keep as NaN" give different summaries. |
| Does it name its **outputs** (`experiment_clean.csv`, a figure, a report)? | A plan with no artifacts can't be checked. |
| Does it plan a **before/after sanity check** (row counts, group counts)? | The cheap way to know the clean didn't lose or invent rows. |

## Discussion prompts

- Which cleaning decisions are *house style* (belong in `CLAUDE.md`, e.g. "always
  strip and lower-case categorical labels") versus *this-dataset* (belong in the
  plan or `LOGBOOK.md`, e.g. "the `9999` is a typo for 99.9")?
- The plan is cheap to edit; a wrong clean re-run on a 10 GB file is not. Where
  else in your own work is a reviewed plan worth more than fast code?

## Optional — implement the plan (if time permits)

Approve the plan and let Claude build `clean.py` and `summary.py`, then re-open
the outputs and check the before/after counts. Watch *how* it executes: does it
follow the plan's steps in order, or quietly merge or skip one (e.g. dropping the
`9999` when the plan said to flag it)? Where Claude rushes is a signal about where
to impose more structure — not a result to accept blindly.

## Stretch

Add a step that writes a tiny `data_dictionary.md` describing each cleaned column
and the decision applied to it — the artifact that turns a one-off clean into
something the next person (or the next session) can trust.
