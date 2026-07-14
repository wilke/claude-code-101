# Plan — clean `experiment.csv` and summarize

A model of the `plan.md` a good plan-mode session produces. Note that the
ambiguous decision (the `9999` temperature) is **surfaced as options**, not
silently resolved.

## Goal

Turn the messy `experiment.csv` into a tidy `experiment_clean.csv` and print a
short summary report, keeping a clear before/after audit trail.

## Inputs / outputs

- **Input:** `experiment.csv` (~403 rows, 8 columns; dirty).
- **Outputs:** `experiment_clean.csv`, `figures/yield_by_group.png`, and a printed
  report (shape, dtypes, missingness, per-group means).

## Steps

1. **Load and profile (before).** Read the CSV; record row/column count, per-column
   dtype, per-column missing count, and duplicate-row count. Print this first so
   the "after" is comparable.
2. **Drop duplicate rows.** Full-row duplicates (repeated `sample_id`). Report how
   many were removed.
3. **Normalize `treatment_group`.** `str.strip().str.lower()`, then map `ctrl`
   → `control`. Assert the result is exactly `{control, low, high}`.
4. **Parse `concentration`.** Extract the numeric part of `"1.5 mg/mL"` → float
   (mg/mL). Blank strings become `NaN`.
5. **Handle the `9999` temperature — DECISION REQUIRED.** Options:
   - (a) treat `> 200 °C` as a data-entry error → set to `NaN` (recommended: a
     lab temperature of 9999 °C is impossible; we don't know the true value).
   - (b) assume it's a misplaced decimal for `99.9` → replace with `99.9`.
   - (c) keep it and exclude it only from statistics.
   **Chosen: (a)** — quarantine to `NaN` and report the count. Revisit if the true
   value can be recovered from lab notes.
6. **Report missingness after cleaning** per column (blanks + the quarantined
   outlier now show as `NaN`).
7. **Summarize.** Per-`treatment_group` mean `yield` and mean `temperature_C`
   (NaNs skipped). Save one bar chart of mean `yield` by group to `figures/`.
8. **Sanity check (after).** Assert no duplicate rows remain, group set is the
   three expected values, and `concentration`/`temperature_C` are now floats.

## Non-goals

- No modelling, no imputation beyond the stated rules, no row deletion for
  missing values (kept as `NaN` and reported).
