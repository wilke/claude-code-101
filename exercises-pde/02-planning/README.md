# Exercise 02 — Plan a fix for a broken convergence test (15 min)

**Goal.** Use plan mode to design the fix for a convergence test that visibly fails. The deliverable is the **`plan.md`**; the lesson is plan mode as a *design step you control*, where the value is the questions the act of planning forces you to answer ("which error indicator?", "which refinement mechanism?", "how near the corner, and how much finer?") before you write the wrong implementation.

## Setup

Same containerized Firedrake as Exercise 01 — if you haven't set it up, follow [`../01-claude-md/INSTALL.md`](../01-claude-md/INSTALL.md) first. `claude` runs on your host; `python3 laplace_lshape.py` runs inside the container. **Keep the `CLAUDE.md` from Exercise 01** — you'll extend it here.

## The problem

`laplace_lshape.py` solves `-Δu = f` on an L-shaped domain whose *reentrant corner* destroys the solution's regularity, so uniform mesh refinement gives sub-optimal P1 convergence. Run it and read the table: the L² rate sits near `4/3` (expected `2`) and H¹ near `2/3` (expected `1`). The cure is to refine more densely near the corner, where the regularity is lost — not everywhere.

## You are the scientist (read before you start)

The L-shape corner singularity is one of the most-taught problems in FEM: Claude has seen the canonical answer — graded refinement around the corner — many times. That cuts both ways. It won't flounder, but it drafts from a template rather than reasoning about *your* code, so it may **skip the error-diagnosis step** ("we know it's the corner, just grade the mesh") or **substitute a strategy you didn't ask for** (an a posteriori adaptive loop instead of a priori grading).

**Claude is a tool; you are the scientist.** Your job is to decide how much structure to impose so the plan matches the problem in front of you. The prompt's "only the mesh is in scope" clause is one example — it closes off two common drifts (changing the polynomial order or the manufactured solution).

## Steps

1. `cd exercises-pde/02-planning && claude`, then start the Firedrake container with this folder bind-mounted (see [`../01-claude-md/INSTALL.md`](../01-claude-md/INSTALL.md)).
2. Inside the container, run `python3 laplace_lshape.py` and read the rates — L² near `4/3`, H¹ near `2/3`. This is real, not a bug.
3. Press `Shift+Tab` twice to enter plan mode.
4. Paste the prompt and submit. Do **not** approve yet:

   ```
   The convergence in this code is suboptimal. Create a plan to
   identify where the error is concentrated, then construct an a
   priori mesh refinement strategy in the problem regions.

   The polynomial order is fixed at P1; only the mesh is in scope.
   ```

5. **Read the plan critically; push back on at least one gap.** Work through the checklist below, watching for the two failure modes: diagnosis skipped, or a posteriori substituted for a priori. Promote any pushback you'd repeat every session into your `CLAUDE.md`.
6. **Save it without running the plan.** Approving a plan tells Claude to *implement* it — so don't approve. While still in plan mode, ask:

   ```
   Write the complete plan to plan.md and stop — do not implement it.
   ```

   Claude can create a new file in plan mode, so `plan.md` lands on disk; then press **`Shift+Tab` to leave plan mode without approving**. That file is the deliverable. Discuss with your neighbor: what one assumption would you have made wrong without the plan?

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Is error-diagnosis a distinct step *before* refinement? | The most commonly skipped step — Claude already "knows" it's the corner. It should compute a per-cell error (`u_exact` is in the script) and look at it first. |
| Does it name a Firedrake refinement *mechanism*? | "Refine the mesh" is too vague — it should commit to in-memory graded refinement of the loaded base mesh, not writing a new `.msh`/`.geo`. |
| A priori grading, or an a posteriori loop in disguise? | You asked for a priori grading; a mark→refine→re-solve→repeat loop is different machinery. Accept the swap explicitly or push back. |
| How is "near the corner" defined? | Grading needs concrete parameters — a radius and a depth — not "refine near the corner." |
| Does it keep P1, the harness, and `lshape.msh` untouched? | The prompt fixes P1; the same harness must run before/after; the mesh file stays on disk. |
| Does it carry `dx(degree=4)` into any new assembly? | The manufactured solution is non-polynomial; Firedrake's auto quadrature over-estimates and hangs, so every integral pins `dx(degree=4)`. |

## Discussion prompts

- What did you have to decide that Claude could not — and what did it decide *for you* without asking?
- How would your approach change on a problem Claude has *not* seen (a custom mixed formulation, a non-standard element pair)? Where do you tighten the scaffolding?

## Optional — implement the plan (if time permits)

Approve the plan and let Claude implement it, then re-run `python3 laplace_lshape.py` — the rates should climb *toward* `2.0` / `1.0` (not necessarily reach them; closing the last gap is FEM-tuning craft, out of scope). Watch *how it executes*: does it follow the plan's steps in order, or combine or skip them? Does it pause where you'd want to check in, or race ahead? Pacing is something you can steer — approve edits manually, or add a convention to `CLAUDE.md` — so where Claude rushes is a signal about where to impose more structure, not a result to just accept.

## Stretch (optional)

For a bigger challenge, try the *a posteriori* adaptive version in a fresh session.
