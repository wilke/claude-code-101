# Exercise 3 — Use a skill to verify a KKT point (15 min)

**Goal.** See how a custom skill encapsulates a recurring research task — here, KKT verification.

## What ships

```
03-skills/
├── README.md
├── problem.py           # a small QP whose true KKT point is known
├── solution.json        # candidate (x, y, z) — initially correct
└── skills/
    ├── kkt-checker/             # the main exercise
    │   ├── SKILL.md
    │   └── check_kkt.py
    └── paper-summary/           # bonus: literature-research skill
        ├── SKILL.md
        └── examples/
            └── example-output.md
```

The `paper-summary` skill is used in the literature stretch goal of the capstone 
and in the dedicated literature exercise in `../../LITERATURE.md`.

Before running the exercise, install the skill into `.claude/skills/`:

```bash
mkdir -p .claude
cp -R skills .claude/
# Or, if you prefer to keep one source: ln -s ../skills .claude/skills
```

## The problem

A bound-constrained QP:

$$
\min_{x \in \mathbb{R}^3} \quad \tfrac{1}{2} x^\top Q x + c^\top x
\quad \text{s.t.} \quad A x = b, \quad x \ge 0
$$

Specific data is in `problem.py`. The candidate KKT point in `solution.json` is correct.

## Steps

1. `cd exercises/03-skills && claude`
2. Ask:

   ```
   verify the candidate solution in solution.json against the QP
   defined in problem.py using the kkt-checker skill.
   ```

   Claude should locate the skill (because the description matches the task), run `check_kkt.py`, and report residuals.

3. Open `solution.json` and corrupt one component — for example, change `z[0]` from `0.0` to `0.5`. Save.

4. Ask Claude to re-verify. Confirm the failing residual is reported clearly.

5. Restore the file.

## Stretch

Ask Claude (in plan mode):

```
extend the kkt-checker skill so it also reports the active set
(indices where x_i = 0 and z_i > 0) and warns about strict
complementarity violations.
```

Read the diff carefully before accepting. The `check_kkt.py` script and the SKILL.md should both change.

## Discussion prompts

- What other recurring checks in your work could become skills?
- What's the smallest skill that would still pay for itself?

## Stretch

- Extend the kkt-checker skill to general nonlinear optimization problems.
- What would you need, if only primal variables were given/avaibable?
- Ask claude to generate a plan ... 
