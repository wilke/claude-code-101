# Adaptation notes — Exercise 02-alt (planning)

The three files in this folder (`lshape.msh`, `laplace_lshape.py`, `SOLUTION.md`) were originally drafted as the numerical-PDE alternative to upstream **Exercise 01** (the CLAUDE.md exercise). On review the user judged the FEM material too heavy for an introductory CLAUDE.md exercise — adding a mesh refinement strategy and convergence study to a Firedrake solver is exactly the kind of non-trivial improvement that benefits from being **planned** before being implemented, which is the lesson of upstream **Exercise 02**.

So the material was relocated here. It is **not yet adapted** to fit the planning-exercise structure. This file lists what still needs to change before 02-alt is workshop-ready.

## What upstream Exercise 02 teaches

The upstream `claude-code-101/exercises/02-planning/` exercise hands the learner a starter file (`minlp_seed.py` — a small mean-variance portfolio MINLP) and asks them to enter plan mode in Claude Code and request a **plan** for a non-trivial extension (a Pyomo formulation + relaxation-based heuristic + benchmarking harness). The deliverable is a `plan.md`. The learner reads the plan critically — does it parameterize `tau` and `K`? does it specify how `Sigma` is loaded? — and either approves or revises *before any code is written*.

## Natural adaptation for the FEM material

Map the upstream structure onto the L-shape solver:

- **Starter (already in place):** `laplace_lshape.py` + `lshape.msh`. A working but bare Firedrake solve. No need to change these — they're already the "starter" the planning exercise needs.
- **Extension to plan:** the mesh refinement strategy + convergence study (i.e., the same "improvement" that the original `SOLUTION.md` walked through directly). Plausible learner prompt: *"plan a convergence study for `laplace_lshape.py` using `MeshHierarchy`, plus a CLI for switching polynomial order, plus a log-log error plot saved to `figures/`."*
- **Critical-reading prompts** (analogous to the upstream's "is `tau` parameterized? is the CSV path configurable?"): does the plan specify which error norm? does it parameterize the maximum refinement level? where will the figure be written? does it cap memory at high refinement levels?

## Concrete changes to the moved files

- **`SOLUTION.md`** needs a substantive rewrite. Currently it shows a model good CLAUDE.md and the model improved code (the deliverable for the CLAUDE.md exercise). For the planning exercise the deliverable is a model `plan.md` instead. The "what Claude should produce" section becomes a model plan listing files to be created/modified, assumptions, edge cases, and explicit *out-of-scope* items — mirroring the upstream `02-planning/SOLUTION.md`.
- **`laplace_lshape.py`** likely no changes needed, but verify the docstring still reads correctly in this context (it currently says "deliberately under-specified: no convergence study, the mesh is too coarse" — that framing still works for 02-alt; the lesson is just that the *plan* for the fix comes first now).
- **`lshape.msh`** no changes needed.

## Dependency note

This exercise assumes the learner has already completed Exercise 01-alt's setup — `INSTALL.md` lives in `exercises-pde/01-claude-md/` and is the workshop's Docker + Firedrake bootstrap. By the time the learner reaches 02-planning they should already have a working containerized Firedrake.
