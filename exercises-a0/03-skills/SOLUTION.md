# Solution — Exercise 03 (a data-profile skill)

## What this exercise is doing

A **skill** packages the "profile any CSV" procedure so Claude runs it on request
without you re-explaining it each session. The lesson is *routing + reuse*: a
plain-language ask ("what's in this file?") should trigger the skill, and the same
helper should work on any table — not just `experiment.csv`.

The `skills/data-profile/` folder ships:

- `SKILL.md` — the frontmatter (`name`, `origin: workshop`, `description:`) that
  makes the skill discoverable, plus how-to-invoke and interpretation notes.
- `data_profile.py` — the implementation: per-column dtype, missingness,
  cardinality, numeric summaries, top categories, and automatic FLAGS.

## What a good run produces

Claude runs the skill (not an inline `df.info()`) and reads the flags back:

```
$ python .claude/skills/data-profile/data_profile.py experiment.csv
rows: 403   columns: 8
duplicate rows: 3
...
FLAGS:
  ! concentration: numbers stored as unit strings — parse to float
  ! sample_id: near-unique — likely an ID, not a feature
```

Then it interprets them for you: the `treatment_group` top-categories list shows
both `control` and `CTRL` (normalize needed); `concentration` needs parsing;
`sample_id` is an identifier, not a feature; and there are 3 duplicate rows to
drop. That is exactly the pre-flight you want before Exercise 02's clean.

## Why the FLAGS are the value

`df.info()` and `df.describe()` tell you *what is*; they don't tell you *what's
wrong*. The skill encodes judgement — "near-unique means ID", "unit strings need
parsing", "constant columns are dead weight" — so that judgement is applied
consistently on every dataset, by anyone, without remembering to look. That's the
difference between a one-off command and a reusable artifact.

## Where it usually goes wrong on the first try

- Claude answers with an inline `df.describe()` and never runs the skill. **Push
  back:** "use the skill in `.claude/skills/`." Routing is the thing being taught.
- The skill runs but Claude doesn't *read the flags back* — it just pastes output.
  A good run turns the flags into next actions ("so first parse `concentration`…").
- On the second CSV, someone edits `data_profile.py` to hard-code column names.
  The whole point is that it's dataset-agnostic — keep it general.
- An extension adds a capability but not a line to `description:`. If the
  description doesn't mention it, routing can't find it.

## Discussion

Splitting "profile" from "clean" mirrors the four-file philosophy: profiling is a
stable, reusable capability (a skill); the specific cleaning decisions for *this*
file are project state (a plan / `LOGBOOK.md`). Keeping them apart is what lets the
profile pay off on the next dataset instead of being rewritten each time.
