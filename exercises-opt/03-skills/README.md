# Exercise 03 — Use a skill to verify a KKT point (15 min)

**Goal.** See how a custom skill encapsulates a recurring research task — here, KKT verification. The check is the pretext; **the skill is the artifact**: a packaged check Claude finds and runs from a plain-language request, without you naming it.

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

1. `cd exercises-opt/03-skills && claude`
2. Ask:

   ```
   verify the candidate solution in solution.json against the QP
   defined in problem.py.
   ```

   Notice the prompt does **not** name the skill — that's deliberate. The point of a skill is that Claude finds the right one by matching your request against the `description:` field in each `SKILL.md`. Claude should locate `kkt-checker`, run `check_kkt.py`, and report residuals. If it computes the check inline instead, push back: "use the kkt-checker skill in `.claude/skills/`" — the failure itself is informative, telling you the description was too weak to route on.

3. Open `solution.json` and corrupt one component — for example, change `z[0]` from `0.0` to `0.5`. Save.

4. Ask Claude to re-verify. Confirm the failing residual is reported clearly.

5. Restore the file.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did Claude *run* `check_kkt.py`, or compute the KKT check inline? | The skill is the source of truth; an inline check is just a one-shot. |
| Did it report residuals per KKT block (stationarity, feasibility, complementarity)? | Is this what you asked the skill for? |
| On the corrupted file, did it localize *which* residual failed? | "It fails" without saying where makes you re-derive it. |
| On the stretch, did it update *both* `check_kkt.py` and the `description:`? | A feature the description doesn't mention is invisible to routing. |
| Did Claude trust the skill's verdict, or second-guess it? | A skill is the agreed-on check; overriding it defeats the point. |

## Discussion prompts

- What other recurring checks in your work could become skills?
- What's the smallest skill that would still pay for itself?

## Stretch

- In plan mode, ask Claude to extend the skill so it also reports the active set (indices where `x_i = 0` and `z_i > 0`) and warns about strict complementarity violations. Read the diff carefully before accepting — both `check_kkt.py` and `SKILL.md` should change.
- Extend the kkt-checker skill to general nonlinear optimization problems.
- What would you need if only the primal variables `x` were available (no multipliers)?
- **The `paper-summary` skill was written by Claude, not by a person.** Try it out on a paper of your choice. Do you like it? How would you change it to your preferences? Everybody reads and summarizes differently.
