# Exercise 04 — Bootstrap a MEMORY.md from lab notebooks (10 min)

**Goal.** Use Claude to turn three dated lab-notebook entries into a structured `MEMORY.md`, then use that `MEMORY.md` to inform a next-experiment question, and end the session with a two-minute append. The lesson is *MEMORY.md as how the next session inherits what this one learned* — not "build a knowledge base." The synthesis is the pretext; the file is the artifact.

**Setup.** This is a *writing* exercise — no FEM code runs in the main workflow, and **you don't need a Firedrake container**. Just `cd exercises-pde/04-memory && claude`. (To verify a notebook claim by re-running code — a stretch — follow [`../01-claude-md/INSTALL.md`](../01-claude-md/INSTALL.md).) **Keep the `CLAUDE.md` you wrote for Exercises 01–03**; you can extend it with conventions about *how `MEMORY.md` gets maintained*.

> **Beyond `.md`:** Claude can read almost any file — source code, LaTeX, data — so a whole multi-format project can be distilled into one `MEMORY.md`, not just markdown notebooks. The **optimization track's Exercise 04** does exactly that (from `plans/` + `src/` + `tex/`) — worth a look.

## The problem

*The project.* The three entries in `notebooks/` (`2026-03-18`, `2026-04-15`, `2026-05-15`) come from one ongoing project: an in-house Firedrake testbench for **2D wave propagation in heterogeneous media on geometries with reentrant corners**. The early entries cover the static-Laplace machinery used to verify any new mesh or element setup; the May entry documents what happened when those threads were combined.

*The exercise.* Each entry is what a researcher writes at the end of a long session — what was decided, pinned, or abandoned. Useful individually, unsearchable as a set. Consolidate them into a `MEMORY.md` the next session can read on load — and feel how much it *changes how the next prompt gets answered*.

## Steps

1. Open this folder in a Claude Code session on your host:

   ```bash
   cd exercises-pde/04-memory
   claude
   ```

2. **Paste this prompt** verbatim and submit:

   ```
   Read everything under notebooks/ and produce MEMORY.md with the sections:
   Decisions, Parameters, Dead Ends, Open Questions. Each entry should cite
   the notebook file it came from.
   ```

   Watch the result. You should see Claude read each notebook, group entries by section, and cite the source filename next to each one. Length matters — if the synthesized `MEMORY.md` is longer than the source notebooks combined, Claude has copied rather than synthesized.

3. **Review and trim.** Read it end-to-end and, for each line, ask: *would a future-me on a different session actually consult this?* Cut everything that's just "what happened that day." What survives are decisions you'd re-derive, parameters you'd re-tune, dead ends you might re-attempt, and still-open questions. Aggressive trimming is the point — this file is what your next session reads on load.

4. **Use the new MEMORY.md to pick a next experiment.** With the trimmed file in place, paste:

   ```
   Given MEMORY.md, what would be the most informative next experiment to
   run? Justify in two sentences.
   ```

   A good answer references a *specific* MEMORY.md entry by date or topic and proposes something an afternoon could plausibly execute. If the answer is generic ("more research is needed on convergence") or proposes a multi-week project, push back: "name the entry that motivates this, and pick a scope that fits in one session."

5. **End with the two-minute ritual.** Before closing the session, ask:

   ```
   Summarize what we did in this session, append as a dated entry to
   MEMORY.md, and overwrite STATUS.md with where we are now.
   ```

   The append should name a concrete decision or question, not the activity ("we discussed MEMORY.md"). STATUS.md should let the next session pick up without reading anything else first — what's done, what's pending, what to do next. If either reads as a recap, push back: "write the decision, not the meeting minutes."

## Critical-reading checklist

Read both the synthesized `MEMORY.md` and Claude's behavior against this checklist.

| Look for | Why it matters |
|----------|----------------|
| Did the synthesis cite the source notebook for every entry? | Provenance you can't recover is an entry you can't revise. Push back: "name the source notebook for each entry." |
| Did Claude actually *trim*, or is the file longer than the three notebooks combined? | Synthesis without trimming is just retyping — a dense file gets skipped on load. |
| Did Dead Ends keep the *reason* a path was abandoned, not just the verdict? | "Abandoned graded+wave" stops nobody; "...because corner-graded cells collapse the CFL bound by three orders of magnitude" does. |
| Did the next-experiment answer cite a specific entry, or hand-wave? | An answer that doesn't reference the file could've been written without it. Push back: "which entry motivates this?" |
| Did the end-of-session append name a concrete decision, or the activity? | "We discussed MEMORY.md" decays; "skip implicit Newmark-β pending preconditioner review" carries forward. |
| Did Claude surface conflicts between notebooks, or smooth them over? | If one says β=3.0 is standard and another says it causes CFL collapse, that conflict is the most important entry — hiding it destroys information. |
| Did the Decisions section lead with the durable rule, or bury it in narrative? | Future-you scans first lines: "Standard L-shape refinement is β=3.0 radial L∞-grading" beats "On 2026-04-15 we observed...". |

## Discussion prompts

- What goes in `CLAUDE.md` vs `MEMORY.md`? `CLAUDE.md` answers *"how does this project work"*; `MEMORY.md` answers *"what have we learned"*. The test: a fact true in any session regardless of experiments run belongs in `CLAUDE.md`; one that depends on experiments belongs in `MEMORY.md`. Pick one entry from your `MEMORY.md` and argue whether it should actually live in `CLAUDE.md`.
- How would you index a `MEMORY.md` that grew past 200 lines — when do you split it into a `memory/` directory with topical files, and what does the index look like? The capstone-grade version of this file lives at the project root of this very repo; take a look.

## Stretch (optional, for experienced learners)

Split the new `MEMORY.md` into `memory/decisions.md`, `memory/parameters.md`, `memory/dead-ends.md`, `memory/open-questions.md`, plus a `memory/INDEX.md` (one line + link per entry). Then add a line to your `CLAUDE.md` telling Claude to update `memory/INDEX.md` whenever it appends to a topical file. Run the end-of-session append again and check whether the index updated without prompting — that tells you whether your `CLAUDE.md` instruction was specific enough.
