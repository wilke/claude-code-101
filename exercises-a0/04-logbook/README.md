# Exercise 04 — Bootstrap a LOGBOOK.md from cleaning notes (10 min)

**Goal.** Turn three dated cleaning notes into a structured `LOGBOOK.md`, use it to
decide one next step, and end with a two-minute append. The synthesis is the
pretext; **the file is the artifact** — how the next session inherits the cleaning
decisions this one made, instead of re-deriving them (or re-making the same
mistake).

**Setup.** This is a *writing* exercise — no code runs, no environment needed. The
three notes are already in `notebooks/`. Just `cd exercises-a0/04-logbook &&
claude`. Keep the `CLAUDE.md` you wrote for Exercises 01–03.

## The project

The three entries in `notebooks/` (`2026-05-04`, `2026-05-05`, `2026-05-06`) all
come from cleaning the same `experiment.csv`: normalizing the `treatment_group`
labels, dealing with the `9999` temperature and the blanks, and removing duplicate
rows. Useful individually, unsearchable as a set — the exercise is to consolidate
them into a `LOGBOOK.md` the next session can read on load.

## Steps

1. `cd exercises-a0/04-logbook && claude`
2. Paste verbatim:

   ```
   Read everything under notebooks/ and produce LOGBOOK.md with the sections:
   Decisions, Parameters, Dead Ends, Open Questions. Each entry should cite
   the notebook file it came from.
   ```

3. **Review and trim.** Read it end-to-end and, for each line, ask: *would a
   future-me on a different session actually consult this?* Cut everything that's
   just "what I did that day." What survives are decisions you'd re-derive,
   parameters you'd re-tune, dead ends you might repeat, and still-open questions.
   Aggressive trimming is the point.

4. **Use the new LOGBOOK.md to pick the next step.** Paste:

   ```
   Given LOGBOOK.md, what is the single most important thing to resolve
   before trusting a summary of this data? Justify in two sentences.
   ```

   A good answer names the **`9999` open question** (sentinel vs typo) — because
   whether it's missing-data or a recoverable `99.9` changes the temperature
   summary and whether we should scan for other sentinels. If the answer is
   generic, push back: "name the entry that motivates this."

5. **End with the two-minute ritual:**

   ```
   Summarize what we did in this session, append it as a dated entry to
   LOGBOOK.md, and overwrite STATUS.md with where we are now.
   ```

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did every entry cite its source notebook? | Provenance you can't recover is an entry you can't revise. |
| Did Claude actually *trim*, or is `LOGBOOK.md` longer than the three notes? | Synthesis without trimming is just retyping. |
| Did Dead Ends keep the *reason*? | "`ctrl → high` was wrong" stops nobody; "…it inflated the high group to ~100 rows, caught by group counts" does. |
| Did it preserve the `9999` **open question** instead of asserting a fix? | The unresolved sentinel-vs-typo call is the most valuable line in the file. |
| Did the next-step answer cite a specific entry? | If it doesn't, it could've been written without the file. |

## Discussion prompts

- What goes in `CLAUDE.md` vs `LOGBOOK.md`? "Strip and lower-case categorical
  labels" is true every session → `CLAUDE.md`. "The `9999` is a bad reading for
  *this* dataset" depends on the data → `LOGBOOK.md`. Pick one entry and argue
  where it goes.
- The `9999` question is left *open* on purpose. When is recording an unresolved
  question more useful than forcing a decision you can't yet justify?

## Stretch

Split the new `LOGBOOK.md` into `logbook/{decisions,parameters,dead-ends,open-questions}.md`
plus a `logbook/INDEX.md`, and add a line to your `CLAUDE.md` telling Claude to
update the index whenever it appends. Re-run the end-of-session append and check
whether the index updated without prompting.
