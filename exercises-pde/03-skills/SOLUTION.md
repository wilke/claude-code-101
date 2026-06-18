# Solution — Exercise 03 (Skills, wave-equation CFL checker)

## What this exercise is doing

The learner copies the shipped `skills/` folder into `.claude/skills/`, launches `claude` in the exercise directory, and pastes a natural-language prompt asking Claude to verify the proposed `dt` in `candidate.json` against the wave problem in `problem.py`. Claude should locate the `wave-cfl-checker` skill (its `description:` is the match), read the `How to invoke` block in `SKILL.md`, issue the docker-wrapped command, and report the result. The learner then bumps `dt` to force a failure, re-runs, restores, and optionally extends the skill (a `--safety` flag is the smallest extension).

The pedagogy is **skills as the package format for the team's recurring checks**. The CFL bound is the worked example: every wave-equation project needs it, the inputs are always `(problem, candidate dt)`, the output is always `pass/fail + per-cell diagnostics`. The skill packages that check exactly once; every project that uses it gets the same answer in the same shape.

## The prompt the learner pastes

```
Verify that the proposed timestep in candidate.json is CFL-safe for the
wave problem defined in problem.py.
```

The prompt deliberately does not name the skill — the test is whether Claude routes the request to `wave-cfl-checker` via description matching alone. If the routing works, the skill mechanism worked end-to-end; if Claude rolls its own check inline, the learner pushes back ("use the `wave-cfl-checker` skill") and you have a teachable moment about how skill descriptions get written.

## What the skill should produce on a passing run

The shipped `candidate.json` has `dt = 0.002`. On `UnitSquareMesh(16, 16)` with P2 CG and layered `c = 1 / 2`, the safe bound is around `8e-3` (set by the bottom, high-`c²` layer). The expected output is shaped like:

```
PASS: dt = 0.00200, safe = 0.00824 (min over 512 cells)
       limited by cell 0  (lambda_max = 5.89e+04,  dt_e = 8.24e-03)
       layer c^2 = 1.0  min dt_e = 1.65e-02
       layer c^2 = 4.0  min dt_e = 8.24e-03
```

(The exact `safe` value and the limiting-cell index depend on Firedrake's cell numbering; the *shape* of the output is what matters — a PASS lead, a `safe` bound near `1e-2`, the limiting cell in the bottom layer, and the per-layer summary showing the bottom layer roughly 2× tighter than the top.)

## What the skill should produce on a failing run

After the learner edits `candidate.json` to `{"dt": 0.05}`:

```
FAIL: dt = 0.05000, safe = 0.00824 (min over 512 cells)
       347 cells violate the bound; first 5 below
       cell    lambda_max   dt_e         c^2
       0       5.89e+04     8.24e-03     4.0
       1       5.89e+04     8.24e-03     4.0
       2       5.89e+04     8.24e-03     4.0
       3       5.89e+04     8.24e-03     4.0
       4       5.89e+04     8.24e-03     4.0
       layer c^2 = 1.0  min dt_e = 1.65e-02
       layer c^2 = 4.0  min dt_e = 8.24e-03
```

What flipped: the lead (`PASS` → `FAIL`) and the violator count. The `safe` bound is unchanged — it is a property of the discretization, not of the proposed `dt`. The per-layer summary localizes the failure to the bottom layer; with `dt = 0.05` between the two per-layer minima, only bottom-layer cells violate. Bump `dt` higher (e.g. `0.05`) and top-layer cells start failing too.

## Why this is a skill — not an MCP and not a CLAUDE.md note

| Container | Right when … | Why not for this check |
|-----------|--------------|------------------------|
| **Skill** | Stateless, deterministic, reusable across projects; everything to run it ships in the repo. | This is exactly the wave-CFL check. |
| **MCP** | The check needs an external system (database, service, license-locked solver, hardware). | The check is local computation. No external surface to wrap. |
| **CLAUDE.md note** | The guidance is a one-shot reminder ("prefer `mumps` for direct solves") or a convention that does not need code. | This check *is* code (eigenvalue solve via SLEPc). A `CLAUDE.md` note describing what to compute does not deduplicate the implementation — every session would re-derive it differently. The whole point of a skill is *the same check every time*. |

## What Claude is supposed to do

1. Match the user's prompt against available `SKILL.md` descriptions. `wave-cfl-checker`'s `description:` names "CFL", "wave equation", "dt", and "lambda_max" — a strong match for the prompt above.
2. Read the matched `SKILL.md`'s `How to invoke` block. The command is docker-wrapped; Claude should copy it verbatim (substituting actual paths if the learner named different files).
3. Run the command via `Bash`. Stream the helper script's stdout back to the learner.
4. Report the verdict. **Do not paraphrase, do not recompute.** A skill is the source of truth for its check; Claude's role is to invoke and report, not to second-guess.

## Where it usually goes wrong on the first try

| What Claude often does | What to push back with |
|-----------------------|------------------------|
| Computes the CFL check inline (writes its own per-cell loop) instead of running the skill. | "Use the `wave-cfl-checker` skill — run its helper, don't reimplement the check." |
| Runs `python3 .claude/skills/wave-cfl-checker/check_cfl.py …` directly on the host. Fails with `ModuleNotFoundError: firedrake`. | "Firedrake is only inside the Docker container. The skill's `SKILL.md` has the docker-wrapped command — use that." |
| Reads `SKILL.md`'s invocation block but drops the bind-mount (`-v "$PWD":…`) or the `-w` flag from the docker command. | "Use the full command from `SKILL.md` verbatim. The bind-mount is what gives the container access to `problem.py` and `candidate.json`." |
| Paraphrases the skill's output ("dt is fine" / "dt is too big") instead of showing the full PASS/FAIL block with the per-layer summary. | "Show the skill's full output, including the limiting cell and the per-layer breakdown. The localization is the diagnostic value." |
| On the stretch step: modifies `check_cfl.py` to add `--safety` but does not update the `description:` field in `SKILL.md`. | "Update the description to mention the new capability. Otherwise the next session asking for 'the recommended safe dt' won't route here." |
| On the stretch step: changes the default output (e.g. always prints the safety-factored `dt`). | "Keep the existing PASS/FAIL output intact when `--safety` is omitted. Extensions should be additive, not breaking." |
| Treats the skill's verdict as advisory ("the skill says FAIL but the dt looks fine"). | "The skill is the source of truth for this check. If you disagree, fix the skill — don't override its verdict in a session." |

## Stretch — extending the skill

The smallest natural extension is a `--safety` flag:

```python
p.add_argument("--safety", type=float, default=None,
               help="If set, also print the recommended dt = safety * safe.")
```

In the PASS branch, after the existing output:

```python
if args.safety is not None:
    print(f"       recommended dt (safety={args.safety}) = {args.safety * safe:.5f}")
```

And — load-bearing — update `SKILL.md`'s `description:` to mention it. For example, append: "With `--safety`, also reports the recommended timestep multiplied by a safety factor in [0.5, 0.9]." Without that line, future Claude sessions asking "what's a safe `dt` with a 90% factor?" won't know this skill answers that question.

## The paper-summary bonus

The same `skills/` folder ships a `paper-summary` skill carried over from the upstream workshop. It is not part of this exercise's main flow; it is pre-positioned for the capstone, which assumes the skill is available. Its `SKILL.md` is a useful contrast — a much richer template (nine output sections, BibTeX, page-numbered pull-quotes, project-fit references) for a much fuzzier task. A learner who finishes early with a PDF on hand can ask Claude to summarize it with `paper-summary` and compare the workflow to `wave-cfl-checker`'s.

## How to use this in the workshop

Hand learners the README and the exercise folder. Let them run the `cp -R skills .claude/` install step themselves — the copy is part of the lesson ("this is where Claude finds skills"). When debriefing, focus on Claude's *behavior* more than the skill's output: did Claude route to the skill at all, did it run the docker-wrapped command, did it show the full output or paraphrase, did it second-guess the verdict? The skill's output values are deterministic (a passing run is always `PASS` with the same `safe`); what varies between learners is how cleanly the skill mechanism worked end-to-end. The pitfalls table is the most useful piece of this document in the room.
