<!--slide n=23 layout=section kicker="Part 3 · Reusable expertise"-->
# Skills
_A skill is a folder. It contains instructions and helper scripts for one specific kind of task. Claude loads it on demand when the task fits._


<!--slide n=24 layout=content kicker="Skills"-->
# What are skills?
- A **skill** is a folder named after the capability, with a `SKILL.md` at its root — YAML front-matter (`name`, `description`) plus instructions, snippets, references.
- The `description` triggers it: when the task matches, Claude loads the body.
- Lives in `.claude/skills/` (project) or `~/.claude/skills/` (global).

Skills package "the thing my lab always does" — once — and reuse it across projects, students, and papers.


<!--slide n=25 layout=content kicker="Skills"-->
# Anatomy of a skill
```
.claude/skills/kkt-checker/
├── SKILL.md           # front-matter + instructions
├── check_kkt.py       # the actual implementation
└── references/
    └── nocedal-wright-12.4.md
```

```
---
name: kkt-checker
origin: workshop
description: |
  Verify that a candidate primal-dual point (x, y, z) satisfies the KKT
  conditions for an NLP `min f(x) s.t. g(x) = 0, h(x) <= 0`. Use this
  whenever the user reports a "solution" and wants to confirm it is
  actually a KKT point, or wants residuals component-by-component.
---

# KKT checker

Run `python .claude/skills/kkt-checker/check_kkt.py --problem PATH ...`
Returns max residuals for stationarity, feasibility, complementarity.
```

`origin:` tags skills you wrote (`workshop`, `mygroup`) versus imported ones (`community`) — handy when the directory grows and you need to know what's safe to modify.


<!--slide n=26 layout=content kicker="Skills"-->
# Built-in skills you already have
:::columns
### Document-creation built-ins
- **pdf** — extract text and tables from papers; build/fill PDFs.
- **docx** — produce Word reports (referee replies, grant text).
- **pptx** — generate slides from results.
- **xlsx** — turn a benchmark log into a workbook with charts.

### When custom beats built-in
- The same domain check appears across projects.
- The recipe involves exact CLI calls (PETSc, GAMS) you don't want to re-discover.
- You want to encode "house style" — figure dimensions, log binning, etc.
:::


<!--slide n=27 layout=section-->
# Exercise 3
_Please refer to your supplemental slide deck. Open your track's exercise:_

:::columns
### Optimization
- [exercises-opt/03-skills/](exercises-opt/03-skills/)

### PDE / FEM
- [exercises-pde/03-skills/](exercises-pde/03-skills/)

### Linear algebra
- [exercises-lin_alg/03-skills/](exercises-lin_alg/03-skills/)
:::
