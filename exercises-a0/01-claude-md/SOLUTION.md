# Solution — Exercise 01 (CLAUDE.md, lab-experiment summary)

## What this exercise is doing

One file ships: `experiment.csv`, ~400 rows of a synthetic lab experiment whose
column meanings and data quality are deliberately undocumented. The learner asks
the same vague question — *"summarize this experiment data"* — across three
phases: cold (Phase 1), after `/init` (Phase 2), and with a hand-written
`CLAUDE.md` (Phase 3). The word "summarize" hides three separate guesses:

1. **Meaning** — what does each column represent, and which is a target vs an id?
2. **Quality** — the data is dirty (inconsistent labels, blanks, a `9999` typo,
   unit-suffixed numbers, duplicate rows); a summary that ignores that is wrong.
3. **Scope** — "summarize" could mean `df.describe()`, or a per-group breakdown,
   or a figure. Without a convention Claude picks one and hides the choice.

A good `CLAUDE.md` turns all three silent guesses into explicit, up-front steps.

## Phase 2 — what `/init` produces here (almost nothing)

This folder ships **only data** — `experiment.csv`, no code — so `/init` has
nothing to read. Expect a thin, generic `CLAUDE.md`: it cannot state what the
columns mean, which are dirty, or what a good summary contains, because none of
that is written anywhere. That is the lesson in its sharpest form: `/init` infers
from *code*, and when the knowledge isn't in the repo, the conventions below are
entirely on you.

## The injected mess (what a good run finds)

| Problem | How it shows up | The blunder it causes |
|---------|-----------------|-----------------------|
| Inconsistent labels | `control`, `Control`, `CTRL`, `" control "` | counts one group as four; per-group means are nonsense |
| Unit-suffixed numbers | `concentration = "1.5 mg/mL"` (string) | column is `object`; can't be averaged without parsing |
| Missing values | blank `temperature_C` and `concentration` cells | silent `NaN`s; mean over a partial column |
| Data-entry outlier | one `temperature_C == 9999` | drags the temperature mean up by orders of magnitude |
| Duplicate rows | a few repeated `sample_id` rows | double-counts samples in any statistic |

## A worked CLAUDE.md (Phase 3)

```markdown
# Project: Lab experiment summary

## Stack
- pandas / numpy (+ matplotlib for figures, saved to figures/, never shown)

## The data (experiment.csv)
- sample_id       row id (NOT unique — duplicate rows exist, drop them)
- batch           B1..B6, the run the sample came from
- treatment_group control / low / high — LABELS ARE INCONSISTENT; normalize
- temperature_C   degrees C; blanks + one bad 9999 entry
- concentration   string with units ("1.5 mg/mL"); parse to float
- yield           numeric result
- outcome         0/1 success flag

## What "summarize" means here
- Report first: row/col count, per-column dtype, per-column missing count,
  duplicate-row count.
- Then per-treatment_group means of yield and temperature_C (after normalizing).
- State every cleaning assumption.

## Don'ts
- Never drop rows silently. Never average unparsed/dirty columns. No plt.show().
```

## What Claude should produce after reading it

A good response **reports and flags before it averages** — it does not jump to
`describe()`:

> `experiment.csv` has 403 rows × 8 columns. Before summarizing I found several
> data-quality issues:
> - `treatment_group` has inconsistent labels — `control`/`Control`/`CTRL`/`" control "`
>   are the same group; normalizing collapses ~6 raw labels to 3 groups.
> - `concentration` is stored as strings with units (`"1.5 mg/mL"`); I parsed the
>   numeric part to a float (5 blanks → `NaN`).
> - `temperature_C` has 6 missing values and one entry of `9999` (a likely typo);
>   I excluded the `9999` from the mean and flagged it rather than guessing 99.9.
> - 3 duplicate rows (repeated `sample_id`) — dropped, leaving 400 unique samples.
>
> After cleaning, per-treatment_group mean yield: control ≈ 50, low ≈ 54, high ≈ 58
> (yield rises with treatment strength). *(Numbers illustrative.)*

A minimal script it might write:

```python
"""summarize.py — clean-then-summarize, reporting every assumption."""
import numpy as np
import pandas as pd

df = pd.read_csv("experiment.csv")
print("shape:", df.shape)
print("dtypes:\n", df.dtypes)
print("missing:\n", df.isna().sum())
print("duplicate rows:", df.duplicated().sum())

# normalize treatment labels
df["treatment_group"] = (
    df["treatment_group"].str.strip().str.lower()
    .replace({"ctrl": "control"})
)
# parse concentration out of "1.5 mg/mL"
df["concentration"] = (
    df["concentration"].str.extract(r"([-+]?\d*\.?\d+)").astype(float)
)
# quarantine the 9999 outlier instead of trusting it
df.loc[df["temperature_C"] > 200, "temperature_C"] = np.nan
df = df.drop_duplicates()

print(df.groupby("treatment_group")[["yield", "temperature_C"]].mean())
```

## Where it usually goes wrong on the first try

- Claude runs `df.describe()` and reports a temperature mean near **60 °C** —
  the `9999` typo silently inflated it. **Add the outlier rule.**
- Claude groups by the raw `treatment_group` and reports **6 groups**. **Require
  label normalization first.**
- Claude reports `concentration` as an `object`/string column and skips it, or
  crashes trying to average it. **Pin the parse-to-float rule.**
- Claude never mentions the duplicate rows, so every count is 3 too high.
  **Require the duplicate-row report.**

The loop is the same every time: ask → notice a silent guess → put the rule in
`CLAUDE.md` → re-ask. After one iteration Claude reports quality issues and states
its cleaning assumptions before averaging anything.
