# Exercise 4 — Bootstrap MEMORY.md from notebook entries (10 min)

**Goal.** Use Claude Code to turn loose lab notebook entries into a structured `MEMORY.md`.

## What ships

```
04-memory/
├── README.md
└── notebooks/
    ├── 2026-03-12-solver-choice.md
    ├── 2026-04-08-mu-init-sweep.md
    └── 2026-04-29-tikhonov-deadend.md
```

These are stand-ins for the kind of dated notes you'd write yourself during a research project on inertia-corrected interior-point methods.

## Steps

1. `cd exercises/04-memory && claude`
2. Ask:

   ```
   read everything under notebooks/ and produce MEMORY.md with the
   sections: Decisions, Parameters, Dead Ends, Open Questions.
   Each entry should cite the notebook file it came from.
   ```

3. Review the result. It will be too long. Edit ruthlessly.

4. Now, with the new MEMORY.md in place, ask:

   ```
   given MEMORY.md, what would be the most informative next experiment
   to run? Justify in two sentences.
   ```

   The answer should reference at least one specific entry.

5. End the session by asking:

   ```
   summarize what we did in this session and append it to MEMORY.md
   under Decisions or Open Questions, whichever fits.
   ```

## Discussion prompts

- What goes in CLAUDE.md vs MEMORY.md? (Hint: stable conventions vs evolving facts.)
- How would you index a MEMORY.md that grows past 200 lines?

## Stretch

Split MEMORY.md into a directory: `memory/decisions.md`, `memory/parameters.md`, `memory/dead-ends.md`, plus a `memory/INDEX.md`. Ask Claude to maintain the index automatically when it appends new entries.
