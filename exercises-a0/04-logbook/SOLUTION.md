# Solution — Exercise 04 (bootstrap a LOGBOOK.md from cleaning notes)

## What this exercise is doing

Three dated notes describe cleaning one `experiment.csv` — normalizing the
`treatment_group` labels, dealing with the `9999` temperature and the blanks, and
removing duplicate rows. Individually they're a diary; as a set they're unsearchable.
The exercise consolidates them into a `LOGBOOK.md` the next session reads on load. The
test is **editorial**: cite sources, trim hard, keep *why* a dead end died, and leave
the one genuinely-open question open instead of papering over it. The model file below
is *not* shipped — the learner produces it.

## A worked LOGBOOK.md

```markdown
# LOGBOOK — experiment.csv cleaning

## Decisions
- Normalize `treatment_group` with `strip().lower()` then map `ctrl → control`,
  and assert the result is exactly `{control, low, high}` so a new bad label
  fails loudly. [2026-05-04]
- Quarantine impossible temperatures: set `temperature_C > 200 °C` to NaN and
  report the count; never guess a replacement for the 9999. [2026-05-05]
- Keep missing cells as NaN, don't drop rows — the other columns of a row with a
  blank temperature/concentration are still usable. [2026-05-05]
- Drop only full-row duplicates (`drop_duplicates`), not `sample_id` collisions,
  to avoid discarding genuinely different measurements. [2026-05-06]

## Parameters
- Canonical group set `{control, low, high}`; rough counts ≈ 200 / 120 / 80. [2026-05-04]
- Temperature outlier threshold: `> 200 °C → NaN`. [2026-05-05]
- Post-clean row count: 400 (from 403 raw). [2026-05-06]

## Dead Ends
- Alias map `ctrl → high` (a copy-paste slip): inflated the `high` group to ~100
  rows and shrank `control`. Caught by comparing group counts before/after the
  relabel — so always print group counts after a relabel. [2026-05-04]

## Open Questions
- Is 9999 a missing-sentinel or a typo for 99.9? If sentinel, scan all numeric
  columns for other sentinels (−1, 999); if typo, we might recover 99.9. Ask
  whoever exported the data. [2026-05-05]
- Should `sample_id` be enforced unique at export time, so duplicates can't
  recur? Cleaning the same issue every load is a smell. [2026-05-06]
```

A good student version may be shorter — that's fine, shorter-but-faithful beats
longer.

## The `9999` open question is the payload

The single most valuable line in the file is the one that stays *unresolved*: is
`9999` a sentinel for missing, or a fat-fingered `99.9`? The two readings lead to
different cleaning (blank it out vs. recover `99.9`) and different follow-up (scan for
other sentinels vs. not). A consolidation that writes "dropped the 9999 outlier" and
moves on has thrown away the decision the next session actually needs to make.

**Failure mode to catch:** Claude asserts a fix ("replaced 9999 with the column mean")
in Decisions. Push back exactly as the README says — the notes never settled it, so it
belongs in Open Questions, not Decisions.

## What a good consolidation keeps (and cuts)

**Keeps** — the durable, re-consultable facts: the label-normalization decision *with*
the assert-loudly reason; the outlier threshold; the "keep NaN, don't drop rows" rule;
the full-row-only dedup choice *with* its rationale.

**Cuts** — the day-log noise: "then I re-read the CSV", "printed head()", the order I
tried things in. If `LOGBOOK.md` is longer than the three notes, the trimming step
didn't happen.

## The dead end must keep its mechanism

The `2026-05-04` note has a clean dead end: an alias map that mistakenly sent
`ctrl → high`. The consolidation must keep *how it was caught* — "the `high` group
jumped to ~100 rows; group counts before/after the relabel exposed it" — not just
"the alias map was wrong." That mechanism ("always print group counts after a
relabel") is what stops a future session repeating it.

## Step 4 — a good next-step answer

Expected: names the **9999 open question** (sentinel vs typo) and says *why it
matters* — it changes the temperature summary and whether to scan for other sentinels.
The tell of a weak answer is genericness ("clean more", "get more data") untethered to
any entry. Push back: "name the entry that motivates this."

## Step 5 — the ritual

The dated append + `STATUS.md` overwrite is the habit the whole four-file architecture
is built on: `LOGBOOK.md` accretes durable knowledge; `STATUS.md` is overwritten with
just "where we are now" (e.g. "cleaned; 9999 still unresolved"). A good append is 3–5
dated bullets on what changed this session, not a re-summary of the project.

## Discussion: CLAUDE.md vs LOGBOOK.md

The cleanest split: **"strip and lower-case categorical labels"** is true every
session and every dataset → `CLAUDE.md`. **"The 9999 is a bad reading for *this*
table"** depends on the data → `LOGBOOK.md`. The cleaning *rule* is house style; the
cleaning *episode* (with the 9999 question and the group counts) is logbook residue.
