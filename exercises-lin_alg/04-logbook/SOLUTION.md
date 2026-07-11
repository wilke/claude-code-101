# Solution — Exercise 04 (bootstrap a LOGBOOK.md)

## What this exercise is doing

Three dated notebook entries describe one project — a heat-equation testbench with an SVD/POD preconditioner re-initialized every 10 steps. Individually they're a diary; as a set they're unsearchable. The exercise consolidates them into a `LOGBOOK.md` the next session reads on load. The test is **editorial**: cite sources, trim hard, preserve *why* dead ends died, and surface the trade-off rather than smoothing it over. The model file below is *not* shipped — the learner produces it.

## A worked LOGBOOK.md

```markdown
# LOGBOOK — heat-equation SVD-preconditioner testbench

## Decisions
- Backward Euler + CG is the fixed backbone; the per-step matrix (I - dt L)
  is constant in time, so the operator is inverted every step. [2026-02-10]
- Preconditioner: rank-8 POD deflation, re-initialized every 10 steps from a
  20-snapshot window; dominant SVD computed with the `lanczos` skill (svds,
  never densified). [2026-03-05]
- Cadence 10 / rank 8 is the sweet spot; per-step re-init abandoned. [2026-04-02]

## Parameters
- N=40 (1600 unknowns), dt=0.01, CG tol=1e-8. [2026-02-10]
- POD rank k=8, snapshot window m=20, re-init cadence=10 steps. [2026-03-05]
- Jacobi baseline: ~55 CG iters/step. With deflation: ~12/step, ~3x faster
  over 500 steps. [2026-02-10, 2026-03-05]

## Dead Ends
- Per-step re-init (cadence 1): CG only ~12->10 but total wall-clock ~2.4x
  WORSE — the svds cost dominates the CG savings. [2026-04-02]
- Rank k=2: CG balloons to ~40/step; the snapshot singular values decay
  gradually, so no tiny k captures the active subspace. [2026-04-02]
- Cadence 40: modes go stale, CG creeps ~12 -> ~30 by ~25 steps past a
  re-init. [2026-04-02]

## Open Questions
- Adaptive re-init (fire when the CG residual stalls) vs fixed cadence 10 —
  untested. [2026-03-05]
- Set rank from the singular-value decay (threshold) rather than fixing k=8;
  does the right rank depend on dt and horizon? [2026-03-05]
```

## Where the CLAUDE.md ⇄ LOGBOOK.md seam sits

"Backward Euler + CG is the backbone" is arguably stable enough to be a `CLAUDE.md` convention; "rank 8, cadence 10" is pure experimental residue and belongs in `LOGBOOK.md`. The rule: if a fact is true in any session regardless of experiments run, it's `CLAUDE.md`; if it depends on having run experiments, it's `LOGBOOK.md`.

## The two-minute end-of-session ritual

`append a dated entry to LOGBOOK.md, then overwrite STATUS.md with where we are now`. The append names a concrete decision or question (not "we discussed LOGBOOK.md"); STATUS.md is tight enough that the next session picks up from it without reading anything else first.

## Where it usually goes wrong on the first try

- The synthesized file is longer than the three notebooks combined — that's copying, not synthesis. **Trim until a future session would actually read it.**
- Dead Ends record the verdict but not the reason ("abandoned per-step re-init") — useless six months later. **Keep the 2.4×-slower reason.**
- Claude smooths the cadence results into "re-init periodically," hiding that 1 and 40 both fail and only ~10 works. **That trade-off is the point; surface it.**
- Entries drop their source dates, so you can't trace a claim back to revise it. **Cite the notebook on every entry.**
- The next-experiment answer is generic ("study convergence more") instead of naming the adaptive-cadence or rank-from-decay open question. **Push back: which entry motivates this?**
