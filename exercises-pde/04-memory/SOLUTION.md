# Solution — Exercise 04 (MEMORY.md, FEM lab notebooks)

## What this exercise is doing

The learner opens `claude` in `exercises-pde/04-memory/`, pastes a one-line synthesis prompt that asks Claude to read everything under `notebooks/` and produce a `MEMORY.md` with four sections — Decisions, Parameters, Dead Ends, Open Questions — citing the source notebook for every entry. They then trim the result, ask Claude for a next experiment that the new `MEMORY.md` would inform, and close with a two-minute end-of-session ritual that appends a dated entry to `MEMORY.md` and overwrites `STATUS.md`.

The pedagogy is **MEMORY.md as the file the next session reads on load**. The synthesis is the pretext; the file is the artifact. Unlike the prior PDE-track exercises, no FEM code runs here — the Claude-as-co-scientist value is editorial (read three loose notebooks, find the durable substance, throw away the rest). The exercise is short on purpose: the workflow is two minutes once you've done it once, and the goal is to make that two-minute habit feel cheap enough to keep.

## The prompts the learner pastes

Synthesis:

```
Read everything under notebooks/ and produce MEMORY.md with the sections:
Decisions, Parameters, Dead Ends, Open Questions. Each entry should cite
the notebook file it came from.
```

Next experiment, after trimming:

```
Given MEMORY.md, what would be the most informative next experiment to
run? Justify in two sentences.
```

End-of-session ritual:

```
Summarize what we did in this session, append as a dated entry to
MEMORY.md, and overwrite STATUS.md with where we are now.
```

## A worked MEMORY.md

The exact wording varies per session and per learner; the *shape* below — four sections, source citations on every entry, dead ends preserving the *why*, total length much smaller than the three source notebooks combined — is what to look for.

```markdown
# MEMORY.md — Firedrake testbench for wave propagation on reentrant-corner geometries

## Decisions

- **Convergence-study harness.** Sweep `n ∈ (4, 8, 16, 32, 64)`, report L²
  and H¹ errors with both rates, and a `max(u_h)` sanity column.
  [src: 2026-03-18-unit-square-convergence.md]
- **Element-order safety.** `--order` flag (default 1) with a one-time
  confirmation persisted in `.element_order_confirmed`. Justified by a past
  P3-mistaken-for-P1 incident.
  [src: 2026-03-18-unit-square-convergence.md]
- **Figure conventions.** PDF, 4 inches wide, log-log axes (`h` on x with
  axis inverted), dotted reference lines at the expected slope per norm,
  never `plt.show()`.
  [src: 2026-03-18-unit-square-convergence.md]
- **Diagnose before refining.** A DG0 per-cell `(u_h - u_exact)²` projection
  with top-10-cell printout is the standard first step on any new
  refinement-strategy discussion.
  [src: 2026-04-15-lshape-graded-refinement.md]
- **L-shape refinement standard.** Radial L∞-grading toward the reentrant
  corner with exponent `β = 3.0`. Implementation: `grade_to_corner(mesh,
  beta)` in `exercises-pde/02-planning/laplace_lshape.py`.
  [src: 2026-04-15-lshape-graded-refinement.md]
- **Per-cell CFL diagnostic exists.** `wave-cfl-checker` skill in our
  toolkit reports per-cell `dt_e` and localizes the limiting cell. Currently
  applied to uniform meshes only (see Dead Ends).
  [src: 2026-05-15-graded-mesh-wave-dead-end.md]

## Parameters

- L-shape grading exponent: `β = 3.0`.
  [src: 2026-04-15-lshape-graded-refinement.md]
- Convergence-sweep mesh sizes: `n ∈ (4, 8, 16, 32, 64)`.
  [src: 2026-03-18-unit-square-convergence.md]
- Quadrature degree for non-polynomial integrands: `dx(degree=4)` on every
  integral; default auto-degree hangs assembly on `r^(2/3)`.
  [src: 2026-04-15-lshape-graded-refinement.md]
- Wave-equation test problem (uniform-mesh use only): `UnitSquareMesh(N)`
  with even `N`, P2 CG, layered medium `c = 1` for `y > 0.5`, `c = 2` for
  `y < 0.5`. Even `N` is required so the interface aligns with a mesh facet.
  [src: 2026-05-15-graded-mesh-wave-dead-end.md]

## Dead Ends

- **Graded L-shape mesh + explicit wave time-stepping.** The radial
  L∞-grading from the April work makes the smallest cells about three orders
  of magnitude smaller than the bulk; combined with `c = 2` in the bottom
  layer, the per-cell explicit-stability bound `dt < 2/sqrt(λ_max(M_e⁻¹K_e))`
  collapses by roughly the same factor relative to a uniform mesh. Softening
  to `β = 2.0` partially recovers `dt` but regresses spatial rates below
  acceptable levels — the two pull in opposite directions and there is no β
  that satisfies both. Mass lumping buys back a small factor in `dt` but the
  lumping dispersion error tracks exactly where the grading is densest, so
  corner accuracy degrades. **Conclusion:** keep two meshes for the same
  geometry (uniform for wave time-stepping, graded for static elliptic),
  pending evaluation of implicit Newmark-β as the alternative single-mesh
  story.
  [src: 2026-05-15-graded-mesh-wave-dead-end.md]

## Open Questions

- Does `β = 3.0` carry to the 3D Fichera-corner analog, or do we need to
  re-derive the grading exponent for the 3D singularity?
  [src: 2026-04-15-lshape-graded-refinement.md]
- When do we *need* P2 vs P1 in production? Would benefit from a deliberate
  P1-vs-P2 cost-per-error comparison on the catalog of problems we care
  about.
  [src: 2026-03-18-unit-square-convergence.md]
- Newmark-β (γ=1/2, β=1/4) on the graded L-shape mesh — could keep the
  single-mesh story without the explicit-step blowup, but the implicit solve
  is non-trivial to set up and the preconditioner choice is open. Skim the
  implicit-wave literature before committing time.
  [src: 2026-05-15-graded-mesh-wave-dead-end.md]
```

Several things to notice:

- Total length is well under the three source notebooks combined.
- Every entry cites a specific filename, not "see notebooks".
- The single Dead Ends entry preserves the *why* (the three sub-failures and the geometry of the trade-off), not just the verdict.
- The Decisions section leads each bullet with the durable rule — "L-shape refinement standard," "diagnose before refining" — not with the date or the narrative.
- Open questions are one per notebook (a reasonable upper bound; trimming further is fine).

## What "next experiment" might look like

A strong response to the next-experiment prompt:

> **Try implicit Newmark-β (γ=1/2, β=1/4) on the corner-graded L-shape mesh from the 2026-04-15 entry.** The 2026-05-15 dead-end ruled out explicit time-stepping on that combination, and the implicit alternative is the most-cited unresolved thread in Open Questions; one afternoon to set up a Newmark-β harness on top of the existing `laplace_lshape.py` mesh code and re-run the layered-medium wave problem would either restore the single-mesh story or pin down the preconditioner-conditioning question, both of which are higher-value than another spatial-rate sweep.

What makes this a strong answer: it cites a specific dated entry (twice), the proposed scope is "one afternoon" rather than "a multi-week project," and it tells you exactly what experimental signal would settle the question.

A weak answer to push back on: "Continue investigating convergence behavior on the L-shape." No citation, no scope, no signal — could have been generated without the file. Push back with "name the entry that motivates this, and pick a scope that fits in one session."

## Where the CLAUDE.md ⇄ MEMORY.md seam sits

`CLAUDE.md` answers *"how does this project work"* — the stack, the file layout, the conventions, the hard rules. `MEMORY.md` answers *"what have we learned"* — the decisions, parameters, dead ends, and open questions discovered through running experiments. The cleanest test is the **time-machine test**: if the fact would be true in any session of this project regardless of which experiments have been run, it belongs in `CLAUDE.md`; if the fact depends on having run experiments, it belongs in `MEMORY.md`.

The `dx(degree=4)` rule in the worked MEMORY.md is a great example of the seam moving over time. It began as a discovery in the April notebook ("first attempt used Firedrake's default and assembly hung"), which made it a Parameters entry. Over a few weeks of repetition it became a permanent rule applied even to fresh problems — the moment it stops being contingent on what we've observed and starts being how we always write integrals, it gets promoted into `CLAUDE.md`. A good end-of-quarter habit is to walk the Parameters and Decisions sections looking for entries ready to graduate.

## The two-minute end-of-session ritual

The highest-leverage habit from the exercise is the closing prompt: summarize the session, append a dated entry to `MEMORY.md`, and overwrite `STATUS.md` with where we are now. It costs two minutes. It pays back in weeks because the next session reads `STATUS.md` before doing anything else, then reads `MEMORY.md` for context, and skips the "what was I working on" reconstruction that otherwise eats the first ten minutes of every resumed session. The append captures durable knowledge; the overwrite captures current state. Both files matter — the append loses value without the state file, and the state file loses value without the long-running decisions index.

## Where it usually goes wrong on the first try

| What Claude often does | What to push back with |
|------------------------|------------------------|
| Synthesizes a file longer than the three source notebooks combined — essentially re-typing rather than consolidating. | "Trim aggressively. Only lines a future session would consult should survive. If `MEMORY.md` is dense, future-me will skip it — half the value of the file is that it stays scan-readable." |
| Drops the *reason* from the dead-end entry ("abandoned graded+wave") and keeps only the verdict. | "Preserve why each path was abandoned, not just what happened. The reason is what stops the next session from re-running the dead end six months from now." |
| Cites notebooks vaguely ("see notebooks") or omits citations entirely. | "Cite the specific filename for every entry. Without provenance, the entries can't be updated when the source notebook is revised." |
| The next-experiment answer paraphrases content from `MEMORY.md` without naming a specific entry. | "Name the entry that motivates this. If you can't, the answer isn't actually using `MEMORY.md`." |
| The end-of-session append describes the activity ("we discussed `MEMORY.md`") instead of naming the decision. | "Write the decision, not the meeting minutes. 'Discussed' decays to nothing in two months; 'decided to X because Y' carries forward." |
| The `STATUS.md` overwrite reads like a session recap — narrative, no actionable next step. | "`STATUS.md` is what the next session reads first. It should say what's done, what's pending, and what to do on the next prompt. Recaps belong in the `MEMORY.md` append; current state belongs in `STATUS.md`." |
| Silently merges two notebook entries that disagree (e.g. β=3.0 as standard in one notebook, β=3.0 as the cause of a CFL collapse in another) into a single smoothed-over statement. | "Surface the conflict; don't smooth it. The fact that β=3.0 is good for static elliptic but breaks explicit wave time-stepping *is* the most important entry in the file." |
| Produces a Decisions section that buries the durable rule behind a narrative ("On 2026-04-15 we observed..."). | "Lead each Decision with the rule itself; the source citation already provides the date and the context." |

## The paper-summary connection (capstone foreshadowing)

The literature side of `MEMORY.md` — citations of papers that motivated a decision or define a method — typically lives in a separate sub-thread that the `paper-summary` skill from Exercise 03 was pre-positioned to feed; the capstone exercises that path explicitly.

## How to use this in the workshop

Hand learners the README and the `notebooks/` folder; let them work through the five steps. This `SOLUTION.md` is a reference for the facilitator, not a script: the `MEMORY.md` a learner produces will not match the worked example above, because the texture of "what to keep" varies with how each learner reads the notebooks. What matters is the *shape* (four sections, citations on every entry, total length much shorter than the source notebooks, dead-end *why* preserved) and the *next-experiment answer* (cites a specific entry, scoped to one session). The pitfalls table is the most useful piece of this document in the debrief — every defect there has shown up at least once when this exercise was piloted, so use it to anchor the conversation rather than the worked `MEMORY.md` itself. The two-minute ritual is the takeaway slide; if learners leave the room willing to spend two minutes at the end of their next real session, the exercise has paid for itself.
