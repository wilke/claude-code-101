<!--slide n=16 layout=section kicker="Part 2 · Think first"-->
# Planning
_Multi-step algorithmic work goes badly without a plan. Plan mode forces Claude to lay out every step before touching a file._


<!--slide n=17 layout=content kicker="Planning"-->
# Why plan first?
Research code has tightly coupled steps — formulation, discretization, scheme, parameters, verification. Without a plan, the assistant fixes one and breaks another.

- A written specification before any code — the plan is itself a deliverable.
- You catch wrong assumptions on a screen, not in a debugger three hours later.

> Same discipline as writing pseudocode before implementing a new method — same payoff.


<!--slide n=18 layout=content kicker="Planning"-->
# Plan mode in Claude Code
- Press Shift+Tab twice — the footer turns into *plan mode*.
- State the task; Claude reads context, asks clarifying questions, proposes a plan.
- Approve to execute, or revise.

Or start directly by typing `plan: <task>` at the prompt.

```
plan: implement a filter line search for our IPM driver,
       then add a CUTEst-style test for problem HS071 with
       tolerances matching logbook/decisions.md.
```


<!--slide n=19 layout=content kicker="Planning"-->
# What a good plan looks like
```
Plan: filter line search for IPM
1. Read driver.py and identify the current Armijo step.
2. Add `filter.py` with the (theta, phi) pair and a switching condition.
3. Modify driver to call filter.accept(...) instead of armijo.accept(...).
4. Update tests/test_linesearch.py: add filter-acceptance tests on
   (i) a synthetic 2D problem, (ii) HS071 from CUTEst.
5. Run pytest -q tests/test_linesearch.py and report.
Files to be modified: driver.py, filter.py (new), tests/test_linesearch.py
Open questions:
  - Filter envelope parameters: use Wächter–Biegler defaults?
  - Should we record filter contents in LOGBOOK.md after each run?
```

Read the open questions before approving — that's where most surprises live.


<!--slide n=20 layout=content kicker="Planning"-->
# Plans as artifacts: the four-file architecture
A plan is the fourth kind of file in the project — alongside CLAUDE.md, LOGBOOK.md, STATUS.md. Each has its own lifecycle.

| File | Says | Lifecycle |
|---|---|---|
| CLAUDE.md | How the project works | Stable; rarely edited |
| plans/<date>-<slug>.md | What's going to happen next | Created → active → executed/abandoned/revised |
| LOGBOOK.md | What's been learned | Append-only; references plans by filename |
| STATUS.md | Where I am right now | Overwritten each session; points at the active plan |

```
project/
├── CLAUDE.md
├── LOGBOOK.md          # references plan outcomes
├── STATUS.md          # points at the active plan
└── plans/
    ├── 2026-04-08-filter-linesearch.md   executed
    ├── 2026-04-22-tikhonov.md            abandoned
    └── 2026-05-07-tao-implementation.md  active
```

> Rule: **plan files are evidence; LOGBOOK.md is the index.** The reasoning lives in the plan, the fact lives in LOGBOOK.md, the file pointer ties them together.


<!--slide n=21 layout=content kicker="Planning"-->
# Prompts that set up and maintain the architecture
Copy these into your sessions — they're the operational moves that keep the four-file structure honest.

```
# Set up the structure in a fresh project
> create CLAUDE.md, LOGBOOK.md, STATUS.md, and a plans/ directory
  in this project, using the workshop conventions. Leave each file
  as a clearly-marked template I'll fill in.

# At the end of a planning session
> save the plan to plans/$(date +%Y-%m-%d)-tao-implementation.md
  and update STATUS.md to point to it as the active plan. Don't
  implement yet.

# At the end of an execution session
> append a dated decision to LOGBOOK.md citing
  plans/2026-05-07-tao-implementation.md, then overwrite STATUS.md
  with the next concrete step inside that plan.

# When revising a plan mid-flight
> save the revised plan as plans/2026-05-07-tao-implementation-v2.md
  and update STATUS.md. Leave v1 in place as history.

# When abandoning a plan
> add an "Abandoned: 2026-05-09, reason: ..." header to
  plans/2026-04-22-tikhonov.md, and append a Dead Ends entry in
  LOGBOOK.md that references it.
```


<!--slide n=22 layout=section-->
# Exercise 2
_Please refer to your supplemental slide deck. Open your track's exercise:_

:::columns
### Optimization
- [exercises-opt/02-planning/](exercises-opt/02-planning/)

### PDE / FEM
- [exercises-pde/02-planning/](exercises-pde/02-planning/)

### Linear algebra
- [exercises-lin_alg/02-planning/](exercises-lin_alg/02-planning/)
:::
