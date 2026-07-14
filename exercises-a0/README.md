# Track a0 — the four files, with plain data (for newcomers)

A gentle, **no-math, no-machine-learning** version of the workshop's four exercises.
Everything runs on one small, messy spreadsheet — `experiment.csv`, a made-up
"generic lab experiment" — using only tools most scientists already touch:
`pandas`, `numpy`, and `matplotlib`.

If you have never used Claude Code before, or you'd bounce off the optimization /
PDE / linear-algebra framing of the other tracks, **start here.** The lesson is
identical to every other track: *durable AI collaboration is built from files, not
chat history.* You'll meet all four files:

| File | What it is | You build it in |
|------|------------|-----------------|
| `CLAUDE.md` | the standing brief Claude reads every session | `01-claude-md/` |
| `plans/` | a forward-looking plan you approve before code runs | `02-planning/` |
| a skill | a reusable procedure you invoke by name | `03-skills/` |
| `LOGBOOK.md` | the durable record the next session inherits | `04-logbook/` |

## The dataset

`experiment.csv` is deliberately **messy** — inconsistent labels, missing cells,
a data-entry typo, numbers stored with unit suffixes, and a few duplicate rows.
That mess is the point: it gives you something real to profile, plan around, and
clean. The same file is used by track **a** (the scikit-learn follow-on), so the
habits you build here carry straight over.

## Setup (once)

Work in an isolated environment, created **before** you start `claude`:

```bash
# conda
conda create -n a0 python=3.11 pandas numpy matplotlib
conda activate a0

# or pip + venv
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pandas numpy matplotlib
```

## The exercises, in order

1. [`01-claude-md/`](01-claude-md/) — write a `CLAUDE.md` and watch it change the answer to the *same* vague prompt.
2. [`02-planning/`](02-planning/) — use plan mode to agree a cleaning plan *before* any edit.
3. [`03-skills/`](03-skills/) — package a reusable `data-profile` skill you can run on any CSV.
4. [`04-logbook/`](04-logbook/) — turn three dated notes into a `LOGBOOK.md` the next session can read.

Open each folder on its own (`cd exercises-a0/01-claude-md && claude`) and follow
its `README.md`.
