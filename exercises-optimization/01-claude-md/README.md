# Exercise 1 — Write a CLAUDE.md (10 min)

**Goal.** Experience how a CLAUDE.md changes the assistant's behavior on the *same* prompt.

## Steps

1. Open this folder in a Claude Code session:

   ```bash
   cd exercises/01-claude-md
   claude
   ```

2. Read `rosenbrock.py`. It's a deliberately under-specified SciPy solve with no convergence plot, no logging, and a poor starting point.

3. **First, with no CLAUDE.md.** Ask:

   ```
   add a convergence plot for rosenbrock.py
   ```

   Watch what Claude produces. It will pick a plotting library, axis scales, file location, and naming scheme — probably none matching what you'd want.

4. **Now create a CLAUDE.md.** Either:

   - Run `/init` and let Claude generate one, then edit it; or
   - Copy the seed below and edit it.

   ```markdown
   # Project: Rosenbrock playground

   ## Goal
   Toy problem for the workshop. We use it to demonstrate convergence plots
   and our standard logging conventions.

   ## Stack
   - Python 3.11, scipy.optimize for the inner solver
   - matplotlib for figures (semilog by default)

   ## Conventions
   - Optimization variable: `x` (always).
   - Tolerance: 1e-8 unless explicitly noted.
   - Figures saved to `figures/` as PDF, 4 inches wide.
   - Convergence plots: y-axis is `‖∇f‖` on log scale, x-axis iteration count.

   ## Don'ts
   - No GUI plotting (`plt.show()`); always save to `figures/`.
   - Don't pip install new packages without asking.

   ## Testing
   - After any code edit: run `pytest -q` and surface failures in the
     next reply before continuing. Don't claim done until tests pass.
   ```

5. Reset the conversation (`/clear`) and re-ask:

   ```
   add a convergence plot for rosenbrock.py
   ```

6. Compare. Which conventions did Claude pick up automatically? Which did it miss? Add the missing rule to CLAUDE.md and try again.

## Discussion prompts

- What conventions in your own research project would you encode first?
- Where is the boundary between CLAUDE.md (stable) and MEMORY.md (evolving)?

## Stretch

Ask Claude:

```
suggest three more rules I should add to CLAUDE.md for a research project
on inertia-corrected interior-point methods.
```

Read the answer critically — accept maybe two of three.
