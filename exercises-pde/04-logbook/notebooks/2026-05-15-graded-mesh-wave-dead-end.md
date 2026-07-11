# 2026-05-15 — DEAD END: graded L-shape mesh + explicit wave time-stepping

Had the corner-graded L-shape mesh from the April session (β=3.0 radial
L∞-grading, recovers optimal P1 rates on the singular Laplace) and wanted to
push it harder: use it as the spatial discretization for the 2D acoustic wave
equation `u_tt = ∇·(c²∇u)` with a layered medium (`c = 1` for `y > 0.5`, `c =
2` for `y < 0.5`). The singular geometry felt like the natural test bed for
a Newmark-explicit / leapfrog time-stepping scheme on a non-uniform mesh —
imaging-style problems eventually need exactly this combination. Two days in;
the combination does not work, and I want to write down why before I forget.

## What broke (1): CFL bound collapsed by orders of magnitude

Ran a back-of-envelope CFL estimate on the graded mesh. The explicit stability
bound `dt < 2 / sqrt(λ_max(M_e⁻¹ K_e))` is set per cell and dominated by the
*smallest* cell in the mesh. At β=3.0 the corner-adjacent cells have diameters
pulled down by `ρ²` near the corner — so the smallest cell is roughly three
orders of magnitude finer than the bulk. Combined with `c = 2` in the bottom
layer (the wave speed squared sits in K_e), the explicit bound dropped by
about three orders of magnitude relative to the uniform-mesh case.

A wave simulation that took ~10⁴ time steps on the uniform mesh wanted ~10⁷
on the graded mesh. And those corner-adjacent cells contribute essentially
zero physically interesting information at the time scales we care about for
this problem — wave fronts don't resolve features that small. We were paying
three orders of magnitude in `dt` for resolution we did not want.

## What broke (2): softening β trades spatial accuracy for temporal cost, no win

Tried β=2.0 to soften the grading. The CFL bound recovered partially — back
to maybe 30× the uniform-mesh `dt`, not the 1000× we were paying — but the
spatial rates on the static-Laplace verification regressed below `1.5`,
defeating the original purpose of grading. There is no β that makes both the
spatial rate and the explicit temporal step work; they pull in opposite
directions. Lower β → fewer tiny cells → larger `dt` → worse corner accuracy.
Higher β → more tiny cells → smaller `dt` → better corner accuracy. Pick one.

## What broke (3): mass lumping helps `dt`, hurts corner solution

Tried mass lumping on the graded mesh. A lumped `M_e` shifts the generalized
eigenproblem and loosens the explicit-step constraint — got back roughly a
factor of 5 in `dt`. But the lumping noise interferes with the corner-singular
solution structure; accuracy near the corner degrades visibly (the wavefront
develops a fake artifact that tracks the lumped-mass dispersion error pattern,
worst exactly where the grading is densest). Not a fix.

## Decision

**Decision:** abandon the combined graded-mesh + explicit-wave-time-stepping
approach. Two reasonable directions if we still need wave simulation on the
L-shape: (a) switch to implicit time-stepping — Newmark-β with γ=1/2, β=1/4
is unconditionally stable, no CFL bound — or (b) keep two meshes for the same
geometry, uniform for wave time-stepping and graded for the static elliptic
problems. Default for now: **(b)**, since our static workload dominates and
the two-mesh story is genuinely simple. Implicit Newmark-β stays on the open
list.

## Auxiliary realization (the byproduct)

To even diagnose this dead end I needed a per-cell CFL bound. The global
heuristic `dt < C · h_min / max(c)` told me "small dt" but not *which cell*
was tight or *by how much* — and with the grading making `h_min` collapse,
"small dt" was uninformative. Spent half a day writing a Firedrake-aware
checker that uses the DG-block-diagonal trick to pull out per-cell `(M_e,
K_e)` pairs and SLEPc's generalized Hermitian eigensolver (GHEP) per cell,
reporting `dt_e = 2/sqrt(λ_max)` cell-by-cell with the limiting cell
highlighted.

The diagnostic earned its keep on this dead end immediately — it localized
the violators to a tiny cluster of corner-adjacent cells, which is what
clinched the "the grading itself is the problem" interpretation. It now lives
as the `wave-cfl-checker` skill in our toolkit. Currently in use on uniform
meshes only, consistent with the decision above.

**Open question:** Newmark-β (γ=1/2, β=1/4) on the graded L-shape mesh
might let us keep the single-mesh story without the explicit-step blowup.
Haven't tried — the implicit solve is non-trivial to set up on this mesh, and
the preconditioner choice is open. Skim the implicit-wave literature before
committing time.

**Open question:** how badly does the graded-mesh stiffness matrix condition
the implicit linear solve at each time step? The corner cells will dominate
the spectrum, which is what made the explicit case fail; whether the
condition number translates into a preconditioner headache for the implicit
case is the second-order question we'll need to answer before (a) above is
realistic.

---

Two days lost. Do not retry the explicit + graded combination without first
reading the implicit alternative. If anyone in the group is tempted, point
them at this entry.
