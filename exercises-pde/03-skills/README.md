# Exercise 03 — Verify a CFL condition with a skill (15 min)

**Goal.** Use a pre-built Claude Code *skill* to verify that a proposed timestep satisfies the element-wise CFL bound for a wave-equation problem. You will see Claude route a natural-language request to the right skill, run it, read both a passing and a failing report, and optionally extend the skill. The lesson is *skills as the package format for the team's recurring checks* — not "build a CFL checker." The check is the pretext; the skill is the artifact.

**Setup.** Same Docker + Firedrake bind-mount pattern as the earlier PDE exercises. If you have not done it yet, follow [`../01-claude-md/INSTALL.md`](../01-claude-md/INSTALL.md) — you need Docker installed and the `firedrakeproject/firedrake:latest` image pulled. **You do *not* need to start an interactive container for this exercise:** the skill spins one up per call (`docker run --rm ...`) and it exits when the script finishes. Just keep the Docker daemon running; `claude` runs on your host, in this directory. **Keep the `CLAUDE.md` you wrote for Exercises 01 and 02** — Claude reads it every session, and you can extend it with conventions about *how skills are invoked or extended*.

**One additional setup step for this exercise.** Skills live in `.claude/skills/` so Claude can find them. The exercise ships them under `skills/`, so before launching Claude install them into the project-local hidden directory:

```bash
mkdir -p .claude
cp -R skills .claude/
# Or, if you prefer to keep one source: ln -s ../skills .claude/skills
```

After this, `.claude/skills/wave-cfl-checker/SKILL.md` and `.claude/skills/paper-summary/SKILL.md` are visible to Claude.

## What ships

```
03-skills/
├── README.md
├── SOLUTION.md
├── problem.py                 # layered-medium wave problem (P2 on UnitSquareMesh)
├── candidate.json             # proposed dt (0.002 — you'll edit it to make it fail)
└── skills/
    ├── wave-cfl-checker/      # element-wise CFL bound check (docker-wrapped Firedrake)
    │   ├── SKILL.md
    │   └── check_cfl.py
    └── paper-summary/         # a second skill, for routing contrast
        ├── SKILL.md
        └── examples/example-output.md
```

## The problem

The 2D acoustic wave equation `u_tt = ∇·(c²∇u)` on the unit square has a **layered medium**: `c = 1` for `y > 0.5` and `c = 2` for `y < 0.5`. The starter `problem.py` defines this with P2 continuous Lagrange triangles on a `UnitSquareMesh(16, 16)`. The interface aligns with a mesh facet, so every triangle lies entirely in one layer.

An explicit time-stepping scheme on this discretization is stable only when

    dt  <  2 / sqrt( λ_max( M_e⁻¹ K_e ) )      for every cell e,

where `M_e` is the local consistent mass matrix and `K_e` is the local `c²`-weighted stiffness matrix. The bound is tighter in the bottom layer (larger `c`) and tighter on smaller cells. Checking it is exactly the kind of small, deterministic, recurring task that earns its keep as a skill: the inputs are always `(problem, candidate dt)`, the output always `pass/fail + per-cell diagnostics`. The `wave-cfl-checker` skill is that package.

`candidate.json` proposes `dt = 0.002`, which should pass; you will edit it during the exercise to make it fail.

## Steps

1. Open this folder in a Claude Code session on your host:

   ```bash
   cd exercises-pde/03-skills
   claude
   ```

   No interactive container needed — the skill takes care of `docker run` itself when it runs the helper.

2. Make sure the skill-install step above has been run — `.claude/skills/wave-cfl-checker/SKILL.md` should exist.

3. **Paste this prompt** and submit:

   ```
   Verify that the proposed timestep in candidate.json is CFL-safe for the
   wave problem defined in problem.py.
   ```

   Notice the prompt does *not* name the skill — that's deliberate. Claude should find it by matching your request against the `description:` field in each `SKILL.md`, then run the docker-wrapped command and report the result. If it computes the check inline instead, push back: "use the `wave-cfl-checker` skill in `.claude/skills/`" — the failure itself is informative, telling you the description was too weak to route on.

   **Expect two things on this first call.** (1) Claude Code's default permission policy treats new shell commands as needing sign-off, so the first `docker run …` will pause for your approval — that's normal. (2) Claude may rewrite the helper path or `-v` mount (an absolute host path, `$PWD`, a full in-container path). Any rewrite is fine as long as the bind-mount holds and the command ends with `python3 …/check_cfl.py --problem … --candidate …`. If the rewrite breaks it, point Claude back at the `How to invoke` block in `SKILL.md` and ask for that command verbatim.

4. Read the skill's output. With the shipped `dt = 0.002` the report should start with `PASS:` followed by the `safe` bound, the limiting cell, and a per-layer summary. The "limited by" cell sits in the bottom (high-`c²`) layer.

5. **Open `candidate.json` and bump `dt` to a value above the safe bound.** A clear failure: `0.05`. Save the file.

6. Ask Claude to re-verify (you can just say "re-check" or "run it again"). The skill output should now lead with `FAIL:`, name how many cells violate the bound, and show the worst offenders. Confirm the per-layer summary localizes the violation to the bottom layer.

7. Restore `candidate.json` to a passing value (the original `0.002`, or whatever you'd like below `safe`). Re-run once more to confirm the recovery.

8. **Optional — extend the skill.** Pick one of the stretch ideas in `.claude/skills/wave-cfl-checker/SKILL.md` (a `--safety` flag is the smallest one) and ask Claude to add it. Read the diff before accepting; both `check_cfl.py` and the `description:` field in `SKILL.md` should change. An extension that does not update the description is invisible to future natural-language requests.

## Critical-reading checklist

Read Claude's behavior, not just the skill's output, against this checklist.

| Look for | Why it matters |
|----------|----------------|
| Did Claude actually *run* the skill, or compute the check inline? | The helper script is the source of truth. If Claude rolls its own check, the result is no more trustworthy than a one-shot. Push back: "run the wave-cfl-checker helper, don't reimplement it." |
| Did Claude use the docker-wrapped invocation, or try `python3 check_cfl.py` on the host? | Firedrake is only inside the container; a bare `python3` fails with `ModuleNotFoundError: firedrake`. The `How to invoke` block has the right command — Claude should copy it verbatim. |
| On the failing run, did the report localize *which* cells / *which* layer violated the bound? | A "fail" without *where* forces you to re-derive the diagnosis. The output should name the worst cell, its `λ_max` and `dt_e`, and the per-layer minimum. If Claude just says "the timestep is too large," ask for the full output. |
| On the stretch, did Claude update the `description:` field in `SKILL.md`? | Descriptions are how skills get found. An extension that changes the helper but not the `description:` is invisible to future skill-matching. |
| On the stretch, did Claude keep the existing output format intact? | Extensions should be additive. If `--safety` becomes required or changes the default output, the skill silently broke for everyone else. Push back: "existing PASS/FAIL output must be unchanged when `--safety` is omitted." |
| Did Claude trust the skill's verdict, or second-guess it? | A skill is the team's agreed-on check. If Claude says "the skill says FAIL, but I think the dt is fine," the workflow has broken down — remind it the skill is the source of truth. |

## Discussion prompts

- The skill packages a check Claude could otherwise compute inline. What does *packaging* buy you that a long `CLAUDE.md` note describing the same check would not? Think about reuse across projects, behavior under unrelated prompts, and what survives a `git clone`.
- What other recurring checks in your own work would earn their keep as skills? Convergence-rate verifiers, mesh-quality reports, residual-history fitters, citation-format validators — pick one you re-derive every project. What would its `description:` line need to say to get matched reliably?

## Stretch (optional, for experienced learners)

If you would like a second skill to try, the same `skills/` folder ships `paper-summary` — a literature-research skill carried over from the upstream workshop. It is *not* part of this exercise's main flow; it is pre-positioned for the capstone, which assumes the skill is available. Read its `SKILL.md` to see a more elaborate skill design (nine-section output template, BibTeX requirements, references to project-level conventions). If you have a PDF handy, ask Claude to summarize it with `paper-summary` and compare the workflow to `wave-cfl-checker`'s.
