---
name: data-profile
origin: workshop
description: |
  Profile a tabular CSV before analysing it: per-column dtype, missingness,
  cardinality, numeric summaries, and top categories — plus automatic FLAGS for
  columns that are constant, mostly-missing, likely an ID, or numbers hidden
  inside unit strings (e.g. "1.5 mg/mL"). Use this as the first step on any new
  or messy dataset, before you clean, plot, or model it.
---

<!--
The `origin:` field tags skills you wrote yourself versus imported ones,
so future-you knows what's safe to modify.
-->


# data-profile skill

Use this skill when:

- You've just been handed a **CSV you don't fully trust** and want a fast, honest
  picture of it before doing anything else.
- You want the **data-quality problems surfaced automatically** — inconsistent
  types, mostly-empty columns, an ID column masquerading as a feature, or numbers
  stored as unit strings — rather than discovering them in a broken plot later.

## How to invoke

```bash
python .claude/skills/data-profile/data_profile.py experiment.csv

# tune the thresholds
python .claude/skills/data-profile/data_profile.py experiment.csv --max-missing 0.3 --top 8
```

`--max-missing` sets the missingness fraction above which a column is flagged;
`--top` sets how many top categories to list for categorical columns.

Output looks like:

```
rows: 403   columns: 8
duplicate rows: 3
--------------------------------------------------------------------
sample_id          int64     missing=   0 ( 0.0%)  unique=400
    min=1000  mean=1200  max=1402
treatment_group    object    missing=   0 ( 0.0%)  unique=6
    top: 'control'×112, 'high'×64, 'Control'×41, 'CTRL'×39, 'low'×61
concentration      object    missing=   0 ( 0.0%)  unique=201
    top: '1.5 mg/mL'×5, '2.1 mg/mL'×4, ...
--------------------------------------------------------------------
FLAGS:
  ! treatment_group: (inconsistent labels visible in the top list)
  ! concentration: numbers stored as unit strings — parse to float
```

## Interpreting the output

- **`unique` ≈ rows** → almost certainly an ID; don't feed it to a model or a mean.
- **A high `missing` %** → decide impute vs drop vs "column is unusable" *before*
  you compute anything over it.
- **`object` dtype on something that should be numeric** → look at `top`; if you
  see unit suffixes (`"1.5 mg/mL"`), it needs parsing.
- The **top-categories list doubles as a label-consistency check**: seeing both
  `control` and `CTRL` in the same list is your cue to normalize.

## Extending

- Add a `--group-cols` option that reports per-group means for chosen numeric
  columns (the summary from Exercise 02, on demand).
- Emit the profile as JSON (`--json`) so it can feed an automated data-quality gate
  in CI.
- Add a check that fuzzy-matches near-duplicate category labels
  (`control`/`Control`/`CTRL`) and suggests a normalization map.
