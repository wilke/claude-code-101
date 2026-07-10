# Exercise 01 — Write a CLAUDE.md (15 min)

**Goal.** Experience how a CLAUDE.md changes the assistant's behavior on the *same* prompt, in the FEM setting — and see exactly where `/init` can help you and where it can't. `/init` reads your code and infers the *math* that lives there; it cannot infer your *house style* or your *safety conventions*, because those were never in the code. This exercise walks that boundary in three phases: ask cold, let `/init` try, then add what it couldn't have known.

**Setup.** This exercise runs against a containerized Firedrake. If you haven't done the Docker + Firedrake setup yet, follow [`INSTALL.md`](./INSTALL.md) first. The pattern is: `claude` runs on your host (this folder is bind-mounted into the container); `python3 laplace_square.py` runs inside the container.

Open this folder in a Claude Code session on your host:

```bash
cd exercises-pde/01-claude-md
claude
```

Read `laplace_square.py`. It's a deliberately under-specified Firedrake solve: a single coarse `UnitSquareMesh(8, 8)`, hardcoded P1 elements, one solve, and `print("solve complete")`. There's a manufactured solution `u_exact = sin(πx) sin(πy)` available inside the script (it has `max = 1`), but nothing in `__main__` does anything with it.

## Phase 1 — Without a CLAUDE.md

1. With no CLAUDE.md in the folder, ask:

   ```
   add a convergence study for laplace_square.py
   ```

   Watch what Claude produces. It will pick an error norm, a sequence of mesh sizes, a plot style, a file location, and a naming scheme — probably none matching what you'd want. Keep this output in mind; it's your baseline.

## Phase 2 — Let `/init` try

The optimization-track version of this exercise leans on `/init` to *recover hidden meaning* from a cryptic solver. The PDE starter is the opposite — its docstring openly states the manufactured solution, derives `f = 2π² sin(πx) sin(πy)`, and explains the homogeneous Dirichlet BC. So `/init` has real math to capture here, and this phase is about seeing **how much of it `/init` gets right — and what it has no way of knowing.**

2. Reset the conversation and generate a CLAUDE.md from the code:

   ```
   /clear
   ```
   ```
   /init
   ```

3. Read the CLAUDE.md `/init` produced. First, check what it **correctly inferred from the code**:

   - Did it identify the manufactured solution `u_exact = sin(πx) sin(πy)`?
   - Did it capture the relationship `f = 2π²·u_exact`?
   - Did it note that `u_exact` attains `max = 1` (a fact sitting in the docstring)?
   - Did it deduce homogeneous Dirichlet BCs from "vanishes on the boundary"?

   Now check what it **had no way to infer** — none of this is in the source, so `/init` almost certainly missed it:

   - Figure conventions (where figures go, format, width).
   - Plot style (log-log with `h` on an inverted x-axis).
   - `O(h^p)` reference-slope lines on the convergence plot.
   - The `max(u_h)` sanity check at every refinement level.
   - Confirming the element order before a convergence sweep.

   That second list is the lesson: `/init` infers the *math*, but *conventions* and *safety rules* are always on you.

## Phase 3 — Add what `/init` couldn't know, then iterate

4. Merge the conventions below into the CLAUDE.md `/init` generated. Treat this seed as the *answer key* for the second list in Phase 2 — these are exactly the things that were never in the code, so `/init` could not have produced them. Keep whatever `/init` got right about the math; add this on top.

   ```markdown
   # Project: Unit-square Laplace playground

   ## Goal
   Toy FEM problem for the workshop. We use it to demonstrate convergence
   studies and our standard figure conventions for numerical PDEs.

   ## Stack
   - Firedrake (run inside the firedrakeproject/firedrake container)
   - matplotlib for figures (saved, never shown)
   - Mesh: built-in UnitSquareMesh; do not load any .msh or .geo file

   ## Commands
   - `python3 laplace_square.py`               # one solve
   - `python3 laplace_square.py --convergence` # writes figures/convergence.pdf

   ## Conventions
   - Convergence study: sweep n in (4, 8, 16, 32, 64); print a table with
     L2 and H1 errors and rates; report max(u_h) at every level (the
     manufactured solution attains max = 1).
   - Figures go to figures/ as PDF, 4 inches wide. Convergence plots are
     log-log with h on the x-axis (inverted).

   ## Don'ts
   - No GUI plotting (no plt.show()); always save to figures/.
   - Never pass a .geo file into Firedrake's Mesh() constructor.
   - Don't pip install new packages without asking.
   ```

   ***When preparing to write Firedrake code, which borrows from python often, it can be helpful to include the following convention in your list above:***

   ```markdown
   - **When writing Firedrake code, always defer to Firedrake/UFL syntax over Python equivalents.**
      Whenever there's a Firedrake/UFL way to express something, use it — even if a Python
      construct would compile. Check the Firedrake/UFL namespace before reaching for any
      Python alternative.
   ```

5. Reset the conversation (`/clear`) and re-ask the exact same prompt as Phase 1:

   ```
   add a convergence study for laplace_square.py
   ```

6. Compare against your Phase 1 baseline. Which conventions did Claude pick up automatically? Which did it miss? Common missed details on the first try:

   - **Dotted reference-slope lines.** A log-log convergence plot is almost unreadable without `O(h^p)` reference lines for the expected slopes. If Claude omitted them, add a rule: *"Convergence plot: include dotted reference lines at the expected slopes — `O(h^(p+1))` for L² and `O(h^p)` for H¹ — anchored at the coarsest data point."*
   - **Element order is hardcoded.** The improved code probably still has `"CG", 1` baked in. Add a rule: *"Element order is configurable via `--order` (default 1); on every `--convergence` run, prompt the user to confirm the order before sweeping, persisting the confirmation in `.element_order_confirmed`."* This is the "tolerance" of the FEM world: a single number with outsized effect on the result, easy to set wrong.

   Add the missing rule to CLAUDE.md and try again. After two iterations the assistant should match your house style.

## Discussion prompts

- Compare the two halves of your Phase 2 review. `/init` recovered the math because it was written into the code; it missed the conventions and safety rules because they weren't. In your own research code, what's the equivalent split — what would `/init` infer for free, and what would you always have to add by hand?
- This exercise has two safety conventions: *report `max(u_h)`* (so you notice if the solver returned nonsense) and *confirm element order before each convergence run* (so a quiet edit to the polynomial degree doesn't change your reported rates without you knowing). Both protect against the same failure mode — getting a number with the wrong meaning. What's the analog in your own research code?
- Where is the boundary between CLAUDE.md (stable) and MEMORY.md (evolving)? For this exercise, would you put the choice of mesh sweep `(4, 8, 16, 32, 64)` in CLAUDE.md or MEMORY.md, and why?

## Stretch

Ask Claude:

```
suggest three more rules I should add to CLAUDE.md for a research project
on adaptive finite elements with a posteriori error estimators.
```

Read the answer critically — accept maybe two of three. Notice which rules feel like *house style* vs. which feel like *project-specific decisions* — the latter belong in MEMORY.md, not CLAUDE.md.
