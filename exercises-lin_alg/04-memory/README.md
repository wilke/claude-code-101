# Exercise 04 — Bootstrap a MEMORY.md from lab notebooks (10 min)

**Goal.** Turn three dated lab-notebook entries into a structured `MEMORY.md`, use it to inform a next-experiment question, and end with a two-minute append. The synthesis is the pretext; **the file is the artifact** — how the next session inherits what this one learned.

**Setup.** This is a *writing* exercise — no code runs, no environment needed. The three notebooks are already in `notebooks/`. Just `cd exercises-lin_alg/04-memory && claude`. Keep the `CLAUDE.md` you wrote for Exercises 01–03.

> **Beyond `.md`:** Claude can read almost any file — source code, LaTeX, data — so a whole multi-format project can be distilled into one `MEMORY.md`, not just markdown notebooks. The **optimization track's Exercise 04** does exactly that (from `plans/` + `src/` + `tex/`) — worth a look.

## The project

The three entries in `notebooks/` (`2026-02-10`, `2026-03-05`, `2026-04-02`) come from one project: a testbench that solves the heat equation over many time steps with an **SVD-based (POD) preconditioner re-initialized every 10 steps**. The entries cover the baseline setup (backward Euler + CG), the SVD-preconditioner design, and a dead end chasing a too-aggressive re-init cadence. Useful individually, unsearchable as a set — the exercise is to consolidate them into a `MEMORY.md` the next session can read on load.

## Steps

1. `cd exercises-lin_alg/04-memory && claude`
2. Paste verbatim:

   ```
   Read everything under notebooks/ and produce MEMORY.md with the sections:
   Decisions, Parameters, Dead Ends, Open Questions. Each entry should cite
   the notebook file it came from.
   ```

3. **Review and trim.** Read it end-to-end and, for each line, ask: *would a future-me on a different session actually consult this?* Cut everything that's just "what happened that day." What survives are decisions you'd re-derive, parameters you'd re-tune, dead ends you might re-attempt, and still-open questions. Aggressive trimming is the point — this file is what your next session reads on load.

4. **Use the new MEMORY.md to pick a next experiment.** Paste:

   ```
   Given MEMORY.md, what would be the most informative next experiment to
   run? Justify in two sentences.
   ```

   A good answer cites a *specific* entry (e.g. the adaptive-cadence open question) and proposes something one session could execute. If it's generic, push back: "name the entry that motivates this."

5. **End with the two-minute ritual:**

   ```
   Summarize what we did in this session, append it as a dated entry to
   MEMORY.md, and overwrite STATUS.md with where we are now.
   ```

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did every entry cite its source notebook? | Provenance you can't recover is an entry you can't revise. |
| Did Claude actually *trim*, or is `MEMORY.md` longer than the three notebooks combined? | Synthesis without trimming is just retyping. |
| Did Dead Ends keep the *reason* a path was abandoned? | "Abandoned per-step re-init" stops nobody; "…because the SVD cost dominates the CG savings (2.4× slower)" does. |
| Did the next-experiment answer cite a specific entry? | If it doesn't, it could've been written without the file. |
| Did Claude surface the cadence conflict (10 works / 1 and 40 fail), not smooth it over? | That trade-off is the most valuable thing in the file. |

## Discussion prompts

- What goes in `CLAUDE.md` vs `MEMORY.md`? A fact true in any session regardless of experiments belongs in `CLAUDE.md`; one that depends on experiments (rank 8, cadence 10) belongs in `MEMORY.md`. Pick one entry and argue where it goes.
- How would you index a `MEMORY.md` past 200 lines — when do you split it into a `memory/` directory?

## Stretch

Split the new `MEMORY.md` into `memory/{decisions,parameters,dead-ends,open-questions}.md` plus a `memory/INDEX.md`, and add a line to your `CLAUDE.md` telling Claude to update the index whenever it appends. Re-run the end-of-session append and check whether the index updated without prompting.
