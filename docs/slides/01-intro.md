<!--slide n=1 layout=title kicker="Workshop · ~2 hours"-->
# Files, not chats
_Claude Code as a co-scientist — for mathematicians_

A hands-on workshop for researchers in computational mathematics — numerical PDEs, optimization, etc. The four-file architecture (CLAUDE.md, plans/, LOGBOOK.md, STATUS.md), skills, version control, testing, and literature workflows — with runnable exercises.

Contributors: Rebecca Durst · Srini Eswar · Sven Leyffer · Andreas Wilke


<!--slide n=2 layout=content kicker="Audience"-->
# Who this workshop is for
_You don't need any AI experience. You do need the kind of work that benefits from a focused collaborator._

:::columns
### You're in the right room if
- You write or apply numerical solvers.
- You're comfortable with Python and the command line.
- You want less yak-shaving (plot scripts, log parsing, refactors) and more research.

### Out of scope
- Training or fine-tuning models.
- Building chatbots or web apps.
- "Replace your solver with an LLM." We won't.
:::


<!--slide n=3 layout=content kicker="Roadmap"-->
# What you'll leave with
_Central insight: durable AI collaboration is built from files, not from chat history. The whole workshop is a tour of which files to keep and how they fit together._

1. **The four-file architecture** — `CLAUDE.md` (conventions), `plans/` (forward-looking), `LOGBOOK.md` (durable knowledge), `STATUS.md` (current state).
2. **Skills** — packaging recurring domain logic (KKT checks, performance profiles) as reusable artifacts.
3. **Sustainable habits** — version control, recognizing whack-a-mole loops, ending sessions cleanly.
4. **A capstone** — an open-ended project applying everything to your own research, or one of several provided briefs (constrained derivative-free optimization, PDE solver/preconditioner benchmarking, a dependency-free CUTEst in C).


<!--slide n=4 layout=content kicker="Organization"-->
# How the workshop is structured
_Two stages: short guided exercises first, then an open-ended capstone where you put the tools to work on your own research._

:::columns
### Stage 1 · Exercises
- Small, self-contained examples that show how individual Claude features work — CLAUDE.md, plan mode, skills, LOGBOOK.md.
- These are *not* "you must only use it this way" prescriptions. They're starting points.
- During each exercise, keep asking: *how could a tool like this help me in my own research?* The answer looks different for everyone.

### Stage 2 · Capstone
- Open-ended time to try the tools on your own — your code, your problem.
- Push past what you saw in the exercises. The exercises show the shape; the capstone is where you stretch it.
- Goal: actually accomplish a piece of research with Claude as your collaborator, not just rehearse a feature.
:::


<!--slide n=5 layout=content kicker="Organization"-->
# Setting up each exercise
_Every exercise ships a README.md (the instructions) and a SOLUTION.md (the walkthrough). Those are for you — not for Claude._

- Keep `README.md` and `SOLUTION.md` **outside** the directory where you run `claude`. If Claude can see them, it reads ahead and the exercise loses its point.
- As you work through an exercise, **manually copy only the code and data files you need** into your working directory — e.g. `max_conopt.py`, `matrix_A.npy`, `laplace_square.py`.

> Rule of thumb: Claude should see the *problem*, never the *solution*.

:::columns
### Optimization
- [Supplement slides →](slides-supplemental/exercise_slides/slides_supplement_optimization.html)
- [Exercise opt 01 — CLAUDE.md](exercises-opt/01-claude-md/)
- [Exercise opt 02 — planning](exercises-opt/02-planning/)
- [Exercise opt 03 — skills](exercises-opt/03-skills/)
- [Exercise opt 04 — memory](exercises-opt/04-logbook/)

### PDE / FEM
- [Supplement slides →](slides-supplemental/exercise_slides/slides_supplement_pde.html)
- [Exercise pde 01 — CLAUDE.md](exercises-pde/01-claude-md/)
- [Exercise pde 02 — planning](exercises-pde/02-planning/)
- [Exercise pde 03 — skills](exercises-pde/03-skills/)
- [Exercise pde 04 — memory](exercises-pde/04-logbook/)

### Linear algebra
- [Supplement slides →](slides-supplemental/exercise_slides/slides_supplement_lin_alg.html)
- [Exercise lin_alg 01 — CLAUDE.md](exercises-lin_alg/01-claude-md/)
- [Exercise lin_alg 02 — planning](exercises-lin_alg/02-planning/)
- [Exercise lin_alg 03 — skills](exercises-lin_alg/03-skills/)
- [Exercise lin_alg 04 — memory](exercises-lin_alg/04-logbook/)
:::


<!--slide n=6 layout=content kicker="Concept"-->
# What is Claude Code?
An **agentic coding assistant** in your terminal: it reads and writes files, runs commands you approve, and works through multi-step tasks the way you would.

- Not autocomplete — it plans, reads context, edits files, runs tests.
- You stay in control: every edit and command is reviewable.
- Runs locally; nothing leaves your machine without your action.

> Our framing throughout: **Claude Code as a co-scientist** — a collaborator who has read the manual for every library you use but needs you to specify the problem precisely. The four files from the roadmap are how you brief it.


<!--slide n=7 layout=content kicker="Motivation"-->
# Where it actually helps you
:::columns
### Routine work it absorbs
- Plotting helpers (semilog convergence, performance profiles).
- Parsing solver logs into a tidy DataFrame.
- Translating between Pyomo ↔ AMPL ↔ JuMP.
- CUTEst-style test harnesses.
- LaTeX-ing derivations to paper-ready form.

### Research work it accelerates
- "What line-search rule does Wächter–Biegler 2006 use?" — answered from the codebase.
- Rescaling a primal-dual update.
- Large CUTEst sweeps with consistent logging.
- Glue between PETSc, your driver, and your benchmark DB.
:::
