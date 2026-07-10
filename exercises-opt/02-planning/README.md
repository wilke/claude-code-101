# Exercise 02 — Plan a small NLP (15 min)

**Goal.** Use plan mode to lay out the structure of a small NLP project before any code is written. The deliverable is the **`plan.md`** itself — the lesson is plan mode as a *design step you control*, where the value is the modeling questions the act of planning forces you to answer before you spend compute.

## The problem

Sparse mean-variance portfolio selection with cardinality constraint,
modeled as complementarity $w^\top (\mathbf{1} - z) \le 0$.

$$
\begin{aligned}
\min_{w, z} \quad & w^\top \Sigma w - \tau \mu^\top w \\
\text{s.t.} \quad & \mathbf{1}^\top w = 1 \\
& \mathbf{1}^\top z \le K \\
& w^\top (\mathbf{1} - z) \le 0 \\
& w \ge 0 \\
& z \in [0, 1]^n
\end{aligned}
$$

with $n = 50$ assets and cardinality $K = 8$. Data is in `nlp_seed.py`.

## You are the scientist (read before you start)

Planning a *new* model from scratch is not the same risk as fixing a known one. There is no
textbook answer for Claude to recite — instead, a greenfield plan hides dozens of small
**modeling decisions**, and Claude will quietly pick a default for each one: how to enforce
the complementarity constraint numerically, which UNO solver to call, how to sweep $\tau$, what
"optimality gap" even means for a nonconvex problem, how the covariance is conditioned. Any of
these defaults can silently turn the problem you posed into a different, easier one.

**Claude is a tool; you are the scientist.** Your job in this exercise is not to read the plan
and accept it. It is to decide *which of those modeling decisions you must own*, and pin them in
the prompt or during plan iteration — so that what lands in `plan.md` is your model, not a
plausible substitute. The scope clause in the prompt below is one example of that structure;
the critical-reading checklist names the rest.

## Setup

Re-use the environment from Exercise 01 (numpy / scipy / matplotlib / unopy), activated
**before you start `claude`** so Claude runs Python in it:

```bash
conda activate optimization        # conda
# or:  source .venv/bin/activate   # pip + venv  (Windows: .venv\Scripts\activate)
```

## Steps

1. `cd exercises-opt/02-planning && claude`
2. Press `Shift+Tab` twice to enter plan mode (look for the `plan mode` indicator at the bottom of the screen).
3. Ask:

   ```
   plan a Python/unopy formulation for the cardinality-constrained portfolio
   problem in nlp_seed.py, plus a strategy for exploring the Pareto
   front with UNO for different \tau. Include a benchmarking harness 
   that records 'tau', the two objectives (risk: 'mu^\top w', and return: 
   '-mu^\top w'), solve time, optimality gap, and selected assets 
   to a CSV. Plot the trade-off between risk ('w^\top \Sigma w') and
   return ('-\mu^\top w') for different values of '\tau'.

   Keep the model exactly as formulated in nlp_seed.py: do not relax,
   smooth, or reformulate the complementarity cardinality constraint, and
   do not switch solver families. If you believe a reformulation is
   necessary, flag it explicitly in the plan rather than adopting it
   silently.
   ```

4. **Read the plan critically. Don't approve it yet.** Work through the critical-reading checklist below.

5. **Save it without running the plan.** Approving a plan tells Claude to *implement* it — so don't approve. While still in plan mode, ask:

   ```
   Write the complete plan to plan.md and stop — do not implement it.
   ```

   Claude can create a new file in plan mode, so `plan.md` lands on disk; then press **`Shift+Tab` to leave plan mode without approving** — the plan is saved and nothing executes. Discuss with your neighbor:
   - What one assumption would you have made wrong without the plan?
   - Does the plan provide a reasonable strategy for the plot?

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Does it specify how `Sigma` is loaded (and validated to be PSD)? | A non-PSD covariance silently changes the problem. |
| Does it parameterize `tau` and `K`, or hardcode them? | Sweeping `tau` is the exercise. |
| Does it allow different parameterizations of `tau`? | The Pareto sweep depends on it. |
| Where will it write the CSV? Is the path configurable? | Output you can't relocate is hard to reuse. |
| Does it describe how to select UNO's solvers? | An unstated solver choice makes runs incomparable. |

## Discussion prompts

- Compare with how you'd write pseudocode before implementing this method.
- What types of mistake does the plan catch *before* compute time is spent?

## Optional — implement the plan (if time permits)

Approve the plan and let Claude build it. Watch *how it executes*: does it follow the plan's steps in order, or combine or skip them? Does it pause where you'd want to check in, or race straight to the CSV and plot? Pacing is something you can steer — approve edits manually, or add a convention to `CLAUDE.md` — so where Claude rushes is a signal about where to impose more structure, not a result to just accept.

## Stretch

Re-ask the same prompt but add: `our benchmarking harness must follow the conventions in CLAUDE.md` 
(write a short CLAUDE.md first specifying figure size, log format, and CSV layout). Compare the two plans.
