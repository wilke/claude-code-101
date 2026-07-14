# Exercise 04 — Bootstrap a modeling LOGBOOK.md (10 min)

**Goal.** Turn three dated modeling notes into a structured `LOGBOOK.md`, use it to
decide one next step, and end with a two-minute append. The synthesis is the
pretext; **the file is the artifact** — how the next session inherits the modeling
decisions (and the *leakage dead end*) this one made, instead of re-deriving them or
re-shipping the same lying model.

**Setup.** This is a *writing* exercise — no code runs, no environment needed. The
three notes are already in `notebooks/`. Just `cd exercises-a/04-logbook && claude`.
Keep the `CLAUDE.md` you wrote for Exercises 01–03.

## The project

The three entries in `notebooks/` (`2026-05-11`, `2026-05-12`, `2026-05-13`) all come
from modeling the same `experiment.csv`: choosing a baseline classifier, discovering
**two leaks** (the `outcome_label` column and preprocessing fit before the split),
and hitting the class-imbalance question. Useful individually, unsearchable as a set
— the exercise is to consolidate them into a `LOGBOOK.md` the next session reads on
load.

## Steps

1. `cd exercises-a/04-logbook && claude`
2. Paste verbatim:

   ```
   Read everything under notebooks/ and produce LOGBOOK.md with the sections:
   Decisions, Parameters, Dead Ends, Open Questions. Each entry should cite
   the notebook file it came from.
   ```

3. **Review and trim.** Read it end-to-end and, for each line, ask: *would a
   future-me on a different session actually consult this?* Cut everything that's
   just "what I did that day." What survives are decisions you'd re-derive, parameters
   you'd re-tune, dead ends you might repeat, and still-open questions. The **leakage
   dead end must keep its mechanism** — not "leakage is bad" but "fitting the scaler
   on full data before the split made CV F1 0.72 while test collapsed to 0.55."

4. **Use the new LOGBOOK.md to pick the next step.** Paste:

   ```
   Given LOGBOOK.md, what is the single most important thing to resolve
   before trusting this model's reported metrics? Justify in two sentences.
   ```

   A good answer names the **class-imbalance open question** *or* re-verifying the
   no-leak guarantee (CV/test agreement) — and cites the entry that motivates it. If
   the answer is generic ("collect more data"), push back: "name the entry that
   motivates this."

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
| Did the leakage Dead End keep its **mechanism and numbers**? | "Leakage is bad" stops nobody; "full-data scaler fit → CV 0.72 / test 0.55" does. |
| Did it preserve the imbalance **open question** instead of asserting a fix? | Picking a resampling scheme before knowing the error costs is premature. |
| Did the next-step answer cite a specific entry? | If it doesn't, it could've been written without the file. |

## Discussion prompts

- What goes in `CLAUDE.md` vs `LOGBOOK.md`? "Always split before fit" is true every
  session → `CLAUDE.md`. "The leak-free baseline scored F1 ≈ 0.61 for *this* dataset"
  depends on the data → `LOGBOOK.md`. Pick one entry and argue where it goes.
- The imbalance question is left *open* on purpose. When is recording an unresolved
  question (with the options weighed) more useful than forcing a metric choice you
  can't yet justify?

## Stretch

Split the new `LOGBOOK.md` into
`logbook/{decisions,parameters,dead-ends,open-questions}.md` plus a `logbook/INDEX.md`,
and add a line to your `CLAUDE.md` telling Claude to update the index whenever it
appends. Re-run the end-of-session append and check whether the index updated without
prompting.
