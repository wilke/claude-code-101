# Solution — Exercise 02 (planning a data clean)

## What this exercise is doing

The learner uses plan mode to force the *decisions* inside a data clean into the
open before any code runs. `experiment.csv` has five distinct problems (duplicate
rows, inconsistent labels, unit-suffixed `concentration`, blanks, a `9999`
outlier), and each is a judgement call. The deliverable is `plan.md` — a plan that
**enumerates** the steps and **surfaces the ambiguous one as options** instead of
silently resolving it.

The `solution/` here is the *reference answer*, kept out of the run directory so
Claude can't read ahead. It contains:

- `plan.md` — the model plan (note step 5 presents three options for the `9999`).
- `clean.py` — implements the plan; prints a before/after audit; writes
  `experiment_clean.csv`.
- `summary.py` — saves one bar chart of mean `yield` per group to `figures/`.

## What a good plan looks like

A strong `plan.md`:

- lists each cleaning step separately (labels, units, blanks, outlier, dupes),
- names its outputs (`experiment_clean.csv`, a figure, a printed report),
- treats the `9999` temperature as a **decision**, not a foregone conclusion —
  drop / repair-to-99.9 / keep-and-exclude — and records which was chosen and why,
- plans a before/after check (row counts, group counts) so you can prove the clean
  didn't lose or invent rows.

## Running the reference solution

From a directory containing `experiment.csv`:

```bash
python clean.py        # -> experiment_clean.csv  (prints before/after)
python summary.py      # -> figures/yield_by_group.png
```

`clean.py` prints something like:

```
== before ==
shape: (403, 8)
duplicate rows: 3
...
dropped 3 duplicate rows
treatment groups after normalize: ['control', 'high', 'low']
quarantined 1 temperature outlier(s) (> 200.0 C) -> NaN
== after ==
shape: (400, 8)
per-treatment_group means:
          yield  temperature_C
control   ~50        ~37
low       ~54        ~37
high      ~58        ~37
```

Yield rises with treatment strength (control < low < high) — the signal the clean
is meant to expose. *(Exact numbers depend on the committed CSV; expect the same
shape.)*

## Where it usually goes wrong on the first try

- The plan says "clean the data and summarize" in one bullet — **push back** and
  make it enumerate the five problems.
- The plan silently drops the `9999` row. **Require it to present the options** so
  *you* choose; a dropped row you didn't authorize is a decision made for you.
- The plan normalizes labels *after* grouping, so the report still shows six
  groups. Order matters: normalize, then summarize.
- Implementation deletes rows with missing `concentration`. The plan said keep as
  `NaN` and report — silent row deletion is the classic clean-up bug.

## Discussion

The value here is not the cleaned file — it's that the *decisions* were reviewable
while still cheap. "Strip and lower-case categorical labels" is house style
(`CLAUDE.md`); "the `9999` is a bad reading, quarantine it" is a dataset fact
(`LOGBOOK.md`). Sorting decisions into the right file is the skill the whole
workshop is teaching.
