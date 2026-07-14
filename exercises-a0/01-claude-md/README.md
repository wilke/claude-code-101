# Exercise 01 — Write a CLAUDE.md (15 min)

**Goal.** Feel how a `CLAUDE.md` changes the assistant's behaviour on the *same*
vague prompt — here in a plain data-wrangling setting, no math required. Ask
"summarize this experiment data" cold and Claude has to guess three things at
once: what the columns *mean*, how dirty the data *is*, and what "summarize" even
*asks for*. This folder ships only a CSV (no code), so `/init` has almost nothing
to read — which makes the point sharply: **these conventions are on you.** You'll
walk that boundary in three phases: ask cold, let `/init` try, then add what it
couldn't have known.

## Setup

Work in a virtual environment so the exercise's packages stay isolated. Create and
activate it **before you start `claude`** — Claude runs Python itself, so it uses
whichever environment is active.

conda:

```bash
conda create -n a0 python=3.11 pandas numpy matplotlib
conda activate a0
```

pip + venv:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pandas numpy matplotlib
```

## The file

One spreadsheet ships with this exercise. Nothing tells you what the columns mean
or how clean they are — that's the point.

- `experiment.csv` — load with `pandas.read_csv`. About 400 rows of a made-up lab
  experiment, with columns `sample_id`, `batch`, `treatment_group`,
  `temperature_C`, `concentration`, a numeric `yield`, and an `outcome`.

The file is **messy on purpose**. Part of the exercise is watching whether Claude
*notices* the mess before it summarizes anything.

## Phase 1 — Without a CLAUDE.md

1. With no `CLAUDE.md` in the folder, open a session and ask:

   ```
   summarize this experiment data
   ```

2. Watch what Claude does — this is your baseline. Look for:
   - Does it **report shape, column dtypes, and missingness**, or jump to averages?
   - Does it notice `treatment_group` is **inconsistently labelled**
     (`control`, `Control`, `CTRL`, `" control "`) and count them as *different* groups?
   - Does it spot that `concentration` is stored as a **string with units**
     (`"1.5 mg/mL"`), so it can't be averaged as-is?
   - Does it catch the **`9999` temperature** (a data-entry typo) dragging the mean up?
   - Does it flag the **duplicate rows** (a repeated `sample_id`)?
   - Does it **ask you anything at all**, or just guess what "summarize" means?

## Phase 2 — Let `/init` try

3. Reset the conversation and generate a `CLAUDE.md` from the folder:

   ```
   /clear
   ```
   ```
   /init
   ```

4. Read what `/init` produced. With **no code to scan** — only a CSV — expect a
   thin, generic file: it has no way to state what each column *means*, which are
   dirty, or what a good summary should contain, because none of that is written
   anywhere for it to read. That's the lesson in its sharpest form: **`/init`
   infers from code; when the knowledge isn't in the repo, it's on you.**

## Phase 3 — Add what `/init` couldn't know, then iterate

5. Write the conventions `/init` had no way to infer into `CLAUDE.md` (merge them
   into whatever `/init` generated). A seed to start from:

   ```markdown
   # Project: Lab experiment summary

   ## Stack
   - pandas / numpy (+ matplotlib for figures, saved to figures/, never shown)

   ## The data (experiment.csv)
   - sample_id       row id (NOT unique — there are duplicate rows to drop)
   - batch           B1..B6, the run the sample came from
   - treatment_group control / low / high — but LABELS ARE INCONSISTENT
                     ("control", "Control", "CTRL", " control "); normalize first
   - temperature_C   degrees C; contains blanks and one bad 9999 entry
   - concentration   stored as a string with units ("1.5 mg/mL"); parse to float
   - yield           numeric result
   - outcome         0/1 success flag

   ## What "summarize" means here
   - Always report, in this order: row/column count, per-column dtype,
     per-column missing-value count, and duplicate-row count.
   - Only THEN report per-treatment_group means of yield and temperature_C —
     after normalizing the group labels.
   - State every cleaning assumption you made (how blanks/outliers were handled).

   ## Don'ts
   - Never drop rows silently — report how many and why.
   - Never average concentration or temperature before parsing/cleaning them.
   - No plt.show(); save figures to figures/.
   ```

6. Reset the conversation (`/clear`) and re-ask the exact same prompt:

   ```
   summarize this experiment data
   ```

7. Compare against your Phase 1 baseline. With the `CLAUDE.md` in place, Claude
   should first report shape / dtypes / missingness / duplicates and **flag** the
   inconsistent labels, the unit-suffixed `concentration`, and the `9999`
   outlier — stating how it handled each — before it reports a single average.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did Claude report shape, dtypes, and missingness before averaging? | Averages of dirty columns are worse than no averages. |
| Did it normalize the `treatment_group` labels first? | Otherwise "control" and "CTRL" are counted as two groups. |
| Did it parse `concentration` out of `"1.5 mg/mL"`? | A units-string column can't be summarized numerically as-is. |
| Did it catch the `9999` temperature and the duplicate rows? | Both silently corrupt any summary statistic. |
| Did it state its cleaning assumptions? | A summary you can't audit is a summary you can't trust. |

## Discussion prompts

- Which of these facts belongs in `CLAUDE.md` (house style, true every session)
  versus a plan or `LOGBOOK.md` (specific to today's cleaning decisions)?
- `/init` gave you almost nothing here. In a *real* project of yours with actual
  source files, what would `/init` be able to infer — and what would still be on you?

## Stretch

Add a convention that any summary must save a one-figure overview to `figures/`
(e.g. a bar chart of per-group mean `yield`), and re-ask — does Claude produce the
figure without being told to, purely from the `CLAUDE.md` rule?
