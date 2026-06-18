# Exercise 03 — Verify a CFL condition with a skill (15 min)

**Goal.** Use a pre-built Claude Code *skill* to verify that a proposed timestep satisfies the element-wise CFL bound for a wave-equation problem. You will see Claude route a natural-language request to the right skill, run it, read both a passing and a failing report, and optionally extend the skill. The lesson is *skills as the package format for the team's recurring checks* — not "build a CFL checker." The check is the pretext; the skill is the artifact.

**Setup.** Same Docker + Firedrake bind-mount pattern as the earlier PDE exercises. If you have not done it yet, follow [`../01-claude-md/INSTALL.md`](../01-claude-md/INSTALL.md) — you need Docker installed and the `firedrakeproject/firedrake:latest` image pulled. **You do *not* need to start an interactive container for this exercise.** The skill spins one up per call (`docker run --rm ...`) and the container exits when the script finishes. Just make sure the Docker daemon is running. `claude` runs on your host, in this directory. **Keep the `CLAUDE.md` you wrote for Exercises 01 and 02** — Claude reads it in every session, and you can extend it here with any conventions about *how skills are invoked or extended* that you find yourself wanting to repeat.

**One additional setup step for this exercise.** Skills live in `.claude/skills/` so Claude can find them. The exercise ships them under `skills/`, so before launching Claude install them into the project-local hidden directory:

```bash
mkdir -p .claude
cp -R skills .claude/
# Or, if you prefer to keep one source: ln -s ../skills .claude/skills
```

After this, `.claude/skills/wave-cfl-checker/SKILL.md` and `.claude/skills/paper-summary/SKILL.md` are visible to Claude.

## The problem

The 2D acoustic wave equation `u_tt = ∇·(c²∇u)` on the unit square has a **layered medium**: `c = 1` for `y > 0.5` and `c = 2` for `y < 0.5`. The starter `problem.py` defines this with P2 continuous Lagrange triangles on a `UnitSquareMesh(16, 16)`. The interface aligns with a mesh facet, so every triangle lies entirely in one layer.

An explicit time-stepping scheme on this discretization is stable only when

    dt  <  2 / sqrt( λ_max( M_e⁻¹ K_e ) )      for every cell e,

where `M_e` is the local consistent mass matrix and `K_e` is the local `c²`-weighted stiffness matrix. The bound is tighter in the bottom layer because `c` is larger there, and tighter overall on smaller cells. Checking this bound is exactly the kind of small, deterministic, recurring task that earns its keep as a packaged skill: every wave-equation project needs it, the inputs are always `(problem, candidate dt)`, the output is always `pass/fail + per-cell diagnostics`. The `wave-cfl-checker` skill in this folder is that package.

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

   Notice the prompt does *not* tell Claude which skill to use. That is deliberate — the point of a skill is that Claude finds the right one from your natural-language request by matching the prompt against the `description:` field in each `SKILL.md`. Watch Claude's response: it should locate `wave-cfl-checker`, read its invocation block, run the docker-wrapped command, and report the result. If Claude tries to compute the check inline instead of running the skill, push back with "use the `wave-cfl-checker` skill in `.claude/skills/`" — the failure mode itself is informative (it tells you the description was too weak to route on its own).

   **A couple of things to expect on this first call.** Claude Code's default permission policy treats new shell commands as needing your sign-off — so the first time the skill runs you will likely see Claude print the `docker run …` command it intends to execute and pause for approval. That is normal. Approve it. Claude may also rewrite the path to the helper script before running — substituting `$PWD` for an absolute host path, expanding `.claude/skills/wave-cfl-checker/check_cfl.py` to its full path inside the container, or stitching together a slightly different `-v` mount. Any of these are fine as long as the bind-mount is in place and the command ends with `python3 …/check_cfl.py --problem … --candidate …`. If the rewrite breaks the invocation (typo, wrong mount target, missing `--problem`), point Claude back at the `How to invoke` block in `SKILL.md` and ask it to use that command verbatim.

4. Read the skill's output. With the shipped `dt = 0.002` the report should start with `PASS:` followed by the `safe` bound, the limiting cell, and a per-layer summary. The "limited by" cell sits in the bottom (high-`c²`) layer.

5. **Open `candidate.json` and bump `dt` to a value above the safe bound.** A clear failure: `0.05`. Save the file.

6. Ask Claude to re-verify (you can just say "re-check" or "run it again"). The skill output should now lead with `FAIL:`, name how many cells violate the bound, and show the worst offenders. Confirm the per-layer summary localizes the violation to the bottom layer.

7. Restore `candidate.json` to a passing value (the original `0.002`, or whatever you'd like below `safe`). Re-run once more to confirm the recovery.

8. **Optional — extend the skill.** Pick one of the stretch ideas in `.claude/skills/wave-cfl-checker/SKILL.md` (a `--safety` flag is the smallest one) and ask Claude to add it. Read the diff before accepting; both `check_cfl.py` and the `description:` field in `SKILL.md` should change. An extension that does not update the description is invisible to future natural-language requests.

## Critical-reading checklist

Read Claude's behavior, not just the skill's output, against this checklist.

| Look for | Why it matters |
|----------|----------------|
| Did Claude actually *run* the skill, or did it paraphrase what the skill would do and compute the check inline? | The point of a skill is that Claude defers to it — the helper script is the source of truth. If Claude rolls its own check, the result is no more trustworthy than a Claude one-shot would have been. Push back: "use the wave-cfl-checker skill — run its helper, don't reimplement it." |
| Did Claude use the docker-wrapped invocation from `SKILL.md`, or try `python3 check_cfl.py` directly on the host? | Firedrake is only inside the container. A bare `python3` call will fail with `ModuleNotFoundError: firedrake`. The skill's `How to invoke` block has the right command — Claude should copy it verbatim. |
| On the failing run, did the report localize *which* cells / *which* layer violated the bound? | A check that returns "fail" without saying *where* forces you to re-derive the diagnosis. The output should name the worst cell, its `λ_max` and `dt_e`, and the per-layer minimum. If Claude summarizes "the timestep is too large" without surfacing this detail, ask it to show the full output. |
| If you ran the stretch step, did Claude update the `description:` field in `SKILL.md`? | Descriptions are how skills get found. An extension that changes the helper script but not the description is invisible to future skill-matching — a future Claude session asking for "the recommended safe dt" won't realize this skill can compute it. |
| If you ran the stretch step, did Claude keep the existing output format intact for non-stretch usage? | Extensions should be additive. If `--safety` becomes a required argument or changes the default output, the skill silently broke for everyone else. Push back: "the skill's existing PASS/FAIL output must be unchanged when `--safety` is omitted." |
| Did Claude trust the skill's verdict, or second-guess it? | A skill is the team's agreed-on check. If Claude says "the skill says FAIL, but actually I think the dt is fine," the workflow has broken down. Push back; remind Claude that the skill is the source of truth for this check. |

## Discussion prompts

- The skill packages a check Claude could otherwise compute inline. What does *packaging* buy you that a long `CLAUDE.md` note describing the same check would not? Think about reuse across projects, behavior under unrelated prompts, and what survives a `git clone`.
- What other recurring checks in your own work would earn their keep as skills? Convergence-rate verifiers, mesh-quality reports, residual-history fitters, citation-format validators — pick one you re-derive every project. What would its `description:` line need to say to get matched reliably?

## Stretch (optional, for experienced learners)

If you would like a second skill to try, the same `skills/` folder ships `paper-summary` — a literature-research skill carried over from the upstream workshop. It is *not* part of this exercise's main flow; it is pre-positioned for the capstone, which assumes the skill is available. Read its `SKILL.md` to see a more elaborate skill design (nine-section output template, BibTeX requirements, references to project-level conventions). If you have a PDF handy, ask Claude to summarize it with `paper-summary` and compare the workflow to `wave-cfl-checker`'s.
