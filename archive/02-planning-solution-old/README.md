# Exercise 2 — Plan a small MINLP (15 min)

***THIS NEEDS TO BE CHANGED! I THINK THERE NEEDS TO BE A PROCESS OF CHECKING/WALKING THROUGH THE PLAN***

**Goal.** Use plan mode to lay out the structure of a small MINLP project before any code is written.

## The problem

Sparse mean-variance portfolio selection with cardinality constraint:

$$
\begin{aligned}
\min_{w, z} \quad & w^\top \Sigma w - \tau \mu^\top w \\
\text{s.t.} \quad & \mathbf{1}^\top w = 1 \\
& 0 \le w \le z \\
& \mathbf{1}^\top z \le K \\
& z \in \{0, 1\}^n
\end{aligned}
$$

with $n = 50$ assets and cardinality $K = 8$. Data is in `minlp_seed.py`.

## Steps

1. `cd exercises/02-planning && claude`
2. Press `Shift+Tab` twice to enter plan mode (look for the `plan mode` indicator at the bottom of the screen).
3. Ask:

   ```
   plan a Pyomo formulation for the cardinality-constrained portfolio
   problem in minlp_seed.py, plus a relaxation-based heuristic that
   warm-starts BARON. Include a benchmarking harness that records
   solve time, optimality gap, and selected assets to a CSV.
   ```

4. Read the plan critically. Don't approve it yet. Look for:

   - Does it specify how `Sigma` is loaded (and validated PSD)?
   - Does it parameterize `tau` and `K`, or hardcode them?
   - Where will it write the CSV? Is the path configurable?
   - Does it describe the warm-start mechanism, or just say "warm-start"?

5. Save the plan: ask Claude to write it to `plan.md`. Discuss with your neighbor: what one assumption would you have made wrong without the plan?

## Discussion prompts

- Compare with how you'd write pseudocode before implementing this method.
- What types of mistake does the plan catch *before* compute time is spent?

## Stretch

Re-ask the same prompt but add: `our benchmarking harness must follow the conventions in CLAUDE.md` (write a short CLAUDE.md first specifying figure size, log format, and CSV layout). Compare the two plans.
