# Files, not chats

**Claude Code as a co-scientist — a workshop for mathematicians.**

A hands-on workshop for researchers in nonlinear, discrete, and PDE-constrained optimization. The central insight: durable AI collaboration is built from files, not chat history. The workshop is a tour of which files to keep and how they fit together.

Open `slides.html` in any modern browser.

- ← / → / Space — navigate
- type a number, then Enter — jump to slide
- `t` — toggle auto-advance (5-second timer)
- the nav bar at the bottom right has the same controls as buttons

The exercises live in `exercises-opt/`, `exercises-pde/`, and `exercises-lin_alg/` (one per track) and are referenced from the slides.

## How long does this take?

The full deck is **52 slides** with ~85 minutes of exercises (15+15+15+10+30). Three honest pacings:

| Format | Total time | What you do |
|---|---|---|
| **Talk only** (~75 min) | ~75 min | All 52 slides; exercises assigned as homework. |
| **2-hour workshop** (~2 h) | ~110 min | Slides + exercises 1–4; capstone as homework. |
| **Half-day workshop** (recommended) (~3 h) | ~150 min | Everything in-room, including the capstone. |

If you have only 90 minutes and want it hands-on, run exercises 1 and 3 only (CLAUDE.md and the kkt-checker skill). Everything else takes one paragraph to motivate and stays as a take-home.

## Quick setup

```bash
# Node 18+ required
npm install -g @anthropic-ai/claude-code

# Authenticate (opens a browser)
claude

# Minimum Python deps for exercises 1–4
python -m pip install --user numpy scipy matplotlib pytest

# Capstones have their own setup paths — see capstones/README.md and each project's README
```

## Layout

```
.
├── slides.html               # the workshop deck (52 slides)
├── slides-supplemental/      # intro deck + per-track supplement decks (opt / pde / lin_alg)
├── README.md                 # this file
├── SOLUTIONS.md              # walkthrough index for all tracks
├── exercises-opt/            # optimization track (SciPy / Uno / CVXPY, KKT, portfolio NLP)
│   └── 01-claude-md/  02-planning/  03-skills/  04-logbook/
├── exercises-pde/            # PDE/FEM track (Firedrake in Docker; Laplace, wave, CFL)
│   └── 01-claude-md/  02-planning/  03-skills/  04-logbook/
├── exercises-lin_alg/        # numerical linear algebra track (numpy/scipy; spectra, SVD)
│   └── 01-claude-md/  02-planning/  03-skills/  04-logbook/
└── capstones/                # open-ended project briefs (README index + one dir per project)
```

Each track follows the same numbered progression (`01-claude-md` … `04-logbook`); the open-ended capstone projects live in the shared top-level `capstones/` directory.

## How to use the exercises

Each exercise folder is meant to be opened on its own. From the workshop root:

```bash
cd exercises-opt/01-claude-md   # or exercises-pde/… , exercises-lin_alg/…
claude
```

Inside Claude Code, follow the steps in that exercise's `README.md`.

> **Keep Claude scoped when running `/init`.** Each exercise folder lives inside this
> larger workshop repo and ships a `SOLUTION.md`/`README.md` that give the answer away, so
> before you run `/init` in the `01-claude-md` step, paste this so Claude builds the
> CLAUDE.md from *that folder's* code/data only (each `01-claude-md/README.md` repeats it
> inline):
>
> ```
> For this exercise, treat the current folder as the entire project.
> Build the CLAUDE.md from ONLY the code and data files in this directory.
> Do NOT read README.md or SOLUTION.md in this folder, and do NOT read any
> files in parent or sibling directories (the rest of the workshop repo).
> ```

## Speaker notes

- **Pacing.** Pick the table row above that fits your slot. The deck is dense and growing; you'll need to pick what to cut, not what to add. See "What to cut for a shorter slot" below.
- **Section dividers** (Parts 1 through 7) introduce each section; use them to take questions.
- **Stretch goals** appear in callout boxes labeled "Stretch" — skip them under time pressure.
- **Power features (Part 6)** is short and reference-y — checkpoints, subagents, hooks, headless mode. If you're tight on time, summarize verbally.

### What to cut for a shorter slot

- **Below 90 min:** Drop Part 6 (Power features) and Part 7 (Working sustainably) entirely; turn them into reading. Keep CLAUDE.md, planning, skills, LOGBOOK.md, MCP, capstone-as-demo.
- **Below 60 min:** Drop the literature/RAG slides (Part 4 tail), Power features (Part 6), and Working sustainably (Part 7). Run only one exercise (Exercise 1 — CLAUDE.md). Treat the rest as a guided tour.

### What never to cut

- Slide 3 (Roadmap with the central insight).
- Slide 4 (Concept — introduces the co-scientist framing).
- The Plans-as-artifacts slide and prompt cookbook in Part 2.
- The STATUS.md handoff slides in Part 4.
- The verification/tests slide in Part 7.

## Audience

Mathematicians working on:

- Efficient and reliable methods for large-scale nonlinear optimization
- Applications of nonlinear and discrete optimization
- MINLP, optimization with PDE constraints, optimization with complementarity constraints

No AI background is assumed. Comfort with Python and the command line is.
