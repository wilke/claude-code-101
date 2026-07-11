# Exercise 01 — Write a CLAUDE.md (15 min)

**Goal.** Experience how a CLAUDE.md changes the assistant's behavior on the *same* prompt, in the optimization setting — and see exactly where `/init` can help you and where it can't. `/init` reads your code and infers the *math* that lives there (here, the polar-coordinate geometry hidden in `max_conopt.py`); it cannot infer your *plotting conventions* or *house style*, because those were never in the code. This exercise walks that boundary in three phases: ask cold, let `/init` try, then add what it couldn't have known.

## The problem

`max_conopt.py` solves a mysterious constrained optimization problem.
It uses `unopy` (Uno NLP solver) and a multistart strategy to escape
local minima.

The script has no plot. The documentation in `max_conopt.md` describes the
interface but deliberately omits the geometric meaning of the variables.

## Setup (needs Python with numpy, scipy, matplotlib, and unopy)

Work in a virtual environment so the exercise's packages stay isolated from your
system Python and don't clash with other projects. Create and activate it
**before you start `claude`** — Claude runs Python itself, so it uses whichever
environment is active. Use conda or pip + venv, whichever you prefer. **On
Windows, conda or the ANL compute nodes are recommended** — native venv
activation differs (`.venv\Scripts\activate`). Feel free to run on your own
machine if that doesn't worry you.

conda:

```bash
cd exercises-opt/01-claude-md
conda create -n optimization python=3.11 numpy scipy matplotlib
conda activate optimization
pip install unopy
```

pip + venv:

```bash
cd exercises-opt/01-claude-md
python3 -m venv .venv
source .venv/bin/activate
pip install numpy scipy matplotlib unopy
```

Verify the solver works:

```bash
python3 max_conopt.py --nv 8 --nstarts 10
# should print: Best objf: 0.726868
```

For a run that shows the multistart staircase:

```bash
python3 max_conopt.py --nv 12 --nstarts 30
# should show 2-3 improvements before settling at Best objf ~0.761
```

## Phase 1 — Without a CLAUDE.md

1. Open this folder in a Claude Code session:

   ```bash
   claude
   ```

2. Read `max_conopt.md`. This is Claude's only project context.

3. Ask:

   ```
   add a conopt solution plot and a convergence plot to max_conopt.py
   ```

4. Study what Claude produces — this is your baseline. Look for:
   - Does it use `u` and `v` directly as x/y coordinates?
   - Does the y-axis of the conopt plot reach values near π (~3.14)?
   - Is the conopt closed (last vertex connected back to first)?
   - Does it know what the fixed last vertex represents geometrically?

## Phase 2 — Let `/init` try

Unlike the linear-algebra version (data only), `max_conopt.py` has real math written into it — the area objective and the diameter constraint encode a polar-coordinate interpretation of the variables. So `/init` has something to capture here, and this phase is about **how much of it `/init` gets right — and what it has no way of knowing.**

5. Reset the conversation and generate a CLAUDE.md from the code:

   ```
   /clear
   ```
   ```
   /init
   ```

6. Read the CLAUDE.md `/init` produced. First, check what it **correctly inferred from the code**:

   - Did it identify that the variables are **polar coordinates**, with the conversion formula from `max_conopt.py`?
   - Did it capture the geometry — maximizing area under a diameter constraint?
   - Did it recognize the problem (COPS 3.0)? You can check against the problem set: <https://www.mcs.anl.gov/~more/cops/cops3.pdf>

   Now check what it **had no way to infer** — none of this is in the source, so `/init` almost certainly missed it:

   - The solution polygon should be drawn **closed** (last vertex connected back to the first); the fixed final vertex is the reference point.
   - Figure conventions (save to `figures/`, format and width, no `plt.show()`).
   - The convergence plot as the **multistart staircase** (best objective so far vs. start index).

   That second list is the lesson: `/init` infers the *math*, but *plotting conventions* and *house style* are always on you.

## Phase 3 — Add what `/init` couldn't know, then iterate

7. Merge the conventions below into the CLAUDE.md `/init` generated — the *answer key* for that second list. Keep whatever `/init` got right about the math; add this on top.

   ```markdown
   # Project: Maximum-area polygon ("conopt", COPS 3.0)

   ## Goal
   Multistart NLP (unopy / Uno) that maximizes a polygon's area under a
   diameter constraint. Used here to demonstrate solution + convergence plots.

   ## Stack
   - unopy (Uno NLP solver) + numpy; matplotlib for figures (saved, never shown)

   ## Conventions
   - The variables are polar coordinates, not raw x/y: convert them to the
     plane with the formula in max_conopt.py before plotting.
   - Solution plot: draw the polygon CLOSED (last vertex back to the first);
     the fixed final vertex is the reference point.
   - Convergence plot: the multistart staircase — best objective so far vs.
     start index — not per-iteration solver output.
   - Figures go to figures/ as PDF; also print the best objective found.

   ## Don'ts
   - No plt.show(); always save figures to figures/.
   - Don't pip install new packages without asking.
   ```

8. Reset the conversation (`/clear`) and re-ask the exact same prompt as Phase 1:

   ```
   add a conopt solution plot and a convergence plot to max_conopt.py
   ```

9. Compare against your Phase 1 baseline. Which conventions did Claude pick up automatically? Add any it missed to CLAUDE.md and try again — after an iteration or two it should match your house style.

## Discussion prompts

- Which formula in `max_conopt.py` let `/init` deduce the coordinate
  system? (Hint: look at what the area objective and the diameter
  constraint have in common.)
- What would you need to add manually to the generated CLAUDE.md that
  `/init` is unlikely to infer on its own?
- What variable names in your own research code would confuse Claude
  without `/init`?
- Can you get intermediate output from unopy, and choose a different
  solver?

## Stretch

Run `python3 max_conopt.py --nv 12 --nstarts 30 --plot` after adding the
`--plot` flag. The convergence plot should show a clear staircase where
multistart finds successively better local optima.

Ask claude to update/rename 'max_conopt.py` and add better documentation.

Ask Claude to suggest two more rules to add to the generated CLAUDE.md.
Accept one, discard one, and explain why.
