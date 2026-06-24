# Exercise 1 — Let /init write CLAUDE.md (10 min)

**Goal.** Experience how `/init` reads your source code and generates a
CLAUDE.md that knows your variable names and conventions — without you
having to write it by hand.

## The problem

`max_conopt.py` solves a mysterious constrained optimization problem.
It uses `unopy` (Uno NLP solver) and a multistart strategy to escape
local minima.

The script has no plot. The documentation in `max_conopt.md` describes the
interface but deliberately omits the geometric meaning of the variables.

## Setup

```bash
cd exercises/01-claude-md
conda create -n optimization python=3.11 numpy scipy matplotlib
conda activate optimization
pip install unopy
```

Verify the solver works:

```bash
python max_conopt.py --nv 8 --nstarts 10
# should print: Best objf: 0.726868
```

For a run that shows the multistart staircase:

```bash
python max_conopt.py --nv 12 --nstarts 30
# should show 2-3 improvements before settling at Best objf ~0.761
```

## Phase 1 — Without /init

1. Open this folder in a Claude Code session:

   ```bash
   claude
   ```

2. Read `max_conopt.md`. This is Claude's only project context.

3. Ask:

   ```
   add a conopt solution plot and a convergence plot to max_conopt.py
   ```

4. Study what Claude produces. Look for:
   - Does it use `u` and `v` directly as x/y coordinates?
   - Does the y-axis of the conopt plot reach values near π (~3.14)?
   - Is the conopt closed (last vertex connected back to first)?
   - Does it know what the fixed last vertex represents geometrically?

## Phase 2 — With /init

5. Download the problem descriptions of COPS 3.0, e.g. from `bash` shell:

   ```bash
   xdg-open https://www.mcs.anl.gov/~more/cops/cops3.pdf
   ```

6. Back in `claude`, clear the conversation:

   ```
   /clear
   ```

7. Run:

   ```
   /init
   ```

   Read the CLAUDE.md that Claude generates. Does it mention polar
   coordinates? Does it include the conversion formula? Did it find
   the problem?

8. Re-ask the same prompt:

   ```
   add a conopt solution plot and a convergence plot to max_conopt.py
   ```

9. Compare Phase 1 and Phase 2. Which output is closer to correct?

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

Run `python max_conopt.py --nv 12 --nstarts 30 --plot` after adding the
`--plot` flag. The convergence plot should show a clear staircase where
multistart finds successively better local optima.

Ask claude to update/rename 'max_conopt.py` and add better documentation.

Ask Claude to suggest two more rules to add to the generated CLAUDE.md.
Accept one, discard one, and explain why.
