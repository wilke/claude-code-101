# Exercise 01 — Write a CLAUDE.md (10 min)

**Goal.** Experience how a CLAUDE.md changes the assistant's behavior on the *same* prompt, in the FEM setting.

**Setup.** This exercise runs against a containerized Firedrake. If you haven't done the Docker + Firedrake setup yet, follow [`INSTALL.md`](./INSTALL.md) first. The pattern is: `claude` runs on your host (this folder is bind-mounted into the container); `python laplace_square.py` runs inside the container.

## Steps

1. Open this folder in a Claude Code session on your host:

   ```bash
   cd exercises-pde/01-claude-md
   claude
   ```

2. Read `laplace_square.py`. It's a deliberately under-specified Firedrake solve: a single coarse `UnitSquareMesh(8, 8)`, hardcoded P1 elements, one solve, and `print("solve complete")`. There's a manufactured solution `u_exact = sin(πx) sin(πy)` available inside the script (it has `max = 1`), but nothing in `__main__` does anything with it.

3. **First, with no CLAUDE.md.** Ask:

   ```
   add a convergence study for laplace_square.py
   ```

   Watch what Claude produces. It will pick an error norm, a sequence of mesh sizes, a plot style, a file location, and a naming scheme — probably none matching what you'd want.

4. **Now create a CLAUDE.md.** Either:

   - Run `/init` and let Claude generate one, then edit it; or
   - Copy the seed below and edit it.

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
4b. ***When preparing to write Firedrake code, which borrows from python often, it can be helpful to include the following convention in your list above:***

   ```markdown
   - **When writing Firedrake code, always defer to Firedrake/UFL syntax over Python equivalents.**
      Whenever there's a Firedrake/UFL way to express something, use it — even if a Python
      construct would compile. Check the Firedrake/UFL namespace before reaching for any
      Python alternative.
   ```

5. Reset the conversation (`/clear`) and re-ask:

   ```
   add a convergence study for laplace_square.py
   ```

6. Compare. Which conventions did Claude pick up automatically? Which did it miss? Common missed details on the first try:

   - **Dotted reference-slope lines.** A log-log convergence plot is almost unreadable without `O(h^p)` reference lines for the expected slopes. If Claude omitted them, add a rule: *"Convergence plot: include dotted reference lines at the expected slopes — `O(h^(p+1))` for L² and `O(h^p)` for H¹ — anchored at the coarsest data point."*
   - **Element order is hardcoded.** The improved code probably still has `"CG", 1` baked in. Add a rule: *"Element order is configurable via `--order` (default 1); on every `--convergence` run, prompt the user to confirm the order before sweeping, persisting the confirmation in `.element_order_confirmed`."* This is the "tolerance" of the FEM world: a single number with outsized effect on the result, easy to set wrong.

   Add the missing rule to CLAUDE.md and try again. After two iterations the assistant should match your house style.

## Discussion prompts

- This exercise has two safety conventions: *report `max(u_h)`* (so you notice if the solver returned nonsense) and *confirm element order before each convergence run* (so a quiet edit to the polynomial degree doesn't change your reported rates without you knowing). Both protect against the same failure mode — getting a number with the wrong meaning. What's the analog in your own research code?
- Where is the boundary between CLAUDE.md (stable) and MEMORY.md (evolving)? For this exercise, would you put the choice of mesh sweep `(4, 8, 16, 32, 64)` in CLAUDE.md or MEMORY.md, and why?

## Stretch

Ask Claude:

```
suggest three more rules I should add to CLAUDE.md for a research project
on adaptive finite elements with a posteriori error estimators.
```

Read the answer critically — accept maybe two of three. Notice which rules feel like *house style* vs. which feel like *project-specific decisions* — the latter belong in MEMORY.md, not CLAUDE.md.
