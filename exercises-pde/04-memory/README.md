# Exercise 04 — Bootstrap a MEMORY.md from lab notebooks (10 min)

**Goal.** Use Claude to turn three dated lab-notebook entries into a structured `MEMORY.md`, then use that `MEMORY.md` to inform a next-experiment question, and end the session with a two-minute append. The lesson is *MEMORY.md as how the next session inherits what this one learned* — not "build a knowledge base." The synthesis is the pretext; the file is the artifact.

**Setup.** This is a *writing* exercise. No FEM code runs as part of the main workflow. The three notebooks are already written and live in `notebooks/`. **You do not need to start a Firedrake container for this exercise** — just `cd exercises-pde/04-memory && claude` and work from there. If you'd like to verify a claim from one of the notebooks by re-running the actual code (a stretch), follow [`../01-claude-md/INSTALL.md`](../01-claude-md/INSTALL.md) for the Docker setup and `cd` into the relevant prior exercise. **Keep the `CLAUDE.md` you wrote for Exercises 01–03** — Claude reads it every session, and you can extend it here with conventions about *how `MEMORY.md` gets maintained* that you find yourself wanting to repeat.

## The problem

*The project the notebooks come from.* The three entries in `notebooks/` (dated `2026-03-18`, `2026-04-15`, `2026-05-15`) come from a single ongoing project: a small in-house Firedrake testbench for **2D wave propagation in heterogeneous media on geometries with reentrant corners** — the group's longer-term aim is to support imaging-style problems where domains are non-convex and material properties layer. The early entries cover the static-Laplace machinery the group uses to verify any new mesh or element setup before letting it near the time-dependent solver; the May entry documents what happened when those two threads tried to combine.

*The exercise.* Each entry is the kind of thing a researcher writes at the end of a long Firedrake session — what was decided, what parameters were pinned, what was tried and abandoned. They are useful individually but unsearchable as a set. The exercise is to consolidate them into a `MEMORY.md` that the next Claude session can read on load — and to feel how much the resulting file *changes how the next prompt gets answered*.

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

3. **Review and trim.** Read the synthesized `MEMORY.md` end-to-end. For each line, ask: *would a future-me on a different session actually consult this?* Cut everything that is just "and here is what happened that day." What survives should be decisions you would re-derive without this file, parameters you would re-tune without this file, dead ends you might re-attempt without this file, and questions you have not yet answered. Aggressive trimming is the whole point — the resulting file is what your next session reads on load.

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

   The `MEMORY.md` append should name a concrete decision or question, not describe the activity ("we discussed MEMORY.md"). The `STATUS.md` overwrite should be tight enough that the next session can pick up from it without reading anything else first — what's done, what's pending, what to do on the next prompt. If either lands as a recap rather than as actionable text, push back with "write the decision, not the meeting minutes — and make STATUS.md the file the next session reads first."

## Critical-reading checklist

Read both the synthesized `MEMORY.md` and Claude's behavior against this checklist.

| Look for | Why it matters |
|----------|----------------|
| Did the synthesis cite the source notebook for every entry? | A `MEMORY.md` entry whose provenance you cannot recover is an entry you cannot revise when the source notebook is updated. Citations are how the file stays maintainable. Push back: "every entry should name its source notebook by filename." |
| Did Claude actually *trim*, or did the synthesized file come out longer than the three notebooks combined? | Synthesis without trimming is just retyping. The resulting file has to be shorter than the inputs by enough that a future session will actually read it on load. If `MEMORY.md` is dense, future-you will skip it. |
| Did the Dead Ends section preserve the *reason* a path was abandoned, or just the verdict? | "Abandoned graded+wave" stops nobody from retrying it six months later. "Abandoned graded+wave *because the corner-graded cells collapse the CFL bound by three orders of magnitude*" actually prevents the re-attempt. Push back if reasons are missing. |
| Did the next-experiment answer cite a specific MEMORY.md entry, or hand-wave? | The whole point of the file is that it informs subsequent decisions. An answer that doesn't reference it could have been generated without it. Push back: "which entry motivates this?" |
| Did the end-of-session append entry name a concrete decision, or describe the activity? | "We discussed MEMORY.md" decays to nothing in two months. "Decided to skip implicit Newmark-β for now pending preconditioner review" carries forward. Push back on activity-style appends. |
| Did Claude silently smooth over any conflict between two notebooks, or surface it? | If notebook 2 says β=3.0 is the standard and notebook 3 says β=3.0 causes a CFL collapse, that conflict *is* the most important entry in the file — it tells the next session that β=3.0 is context-dependent. A synthesis that hides the conflict has destroyed information. |
| Did the Decisions section lead with the durable rule, or bury it in a narrative? | Future-you scans first lines. If a decision starts "On 2026-04-15 we observed..." instead of "Standard L-shape refinement is β=3.0 radial L∞-grading," the file is harder to scan than the source notebooks were. |

## Discussion prompts

- What goes in `CLAUDE.md` vs `MEMORY.md`? `CLAUDE.md` answers *"how does this project work"*; `MEMORY.md` answers *"what have we learned"*. The test: if a fact would be true in any session of this project regardless of which experiments have been run, it goes in `CLAUDE.md`; if it depends on having run experiments, it goes in `MEMORY.md`. Mis-placing facts is the most common decay path for both files — pick one entry from your synthesized `MEMORY.md` and argue whether it should actually live in `CLAUDE.md` instead.
- How would you index a `MEMORY.md` that grew past 200 lines — when do you split it into a `memory/` directory with topical files, and what does the index look like? The capstone-grade version of this file lives at the project root of this very repo; take a look.

## Stretch (optional, for experienced learners)

Split the new `MEMORY.md` into `memory/decisions.md`, `memory/parameters.md`, `memory/dead-ends.md`, `memory/open-questions.md`, plus a `memory/INDEX.md` that lists each entry with a one-line summary and a link. Then add a line to your project's `CLAUDE.md` instructing Claude to update `memory/INDEX.md` automatically whenever it appends to one of the topical files. Run the end-of-session append again and check whether the index update happened without prompting — the answer tells you whether your `CLAUDE.md` instruction was specific enough, and gives you a small worked example of the `CLAUDE.md`/`MEMORY.md` interaction the discussion prompts above describe.
