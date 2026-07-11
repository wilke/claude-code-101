# 2026-04-15 — L-shape singular Laplace: graded refinement recovers P1 rates

Copied the convergence harness from the unit-square work and pointed it at the
L-shape (`[-1,1]² \ [0,1]×[-1,0]`, reentrant corner at the origin) with the
canonical singular manufactured solution `u(r, φ) = r^(2/3) sin(2φ/3)`. Out of
the box with uniform `MeshHierarchy` refinement the L² rates plateaued around
`4/3` and H¹ rates around `2/3` — well below the 2 and 1 we'd hope for. The
expected outcome: the corner singularity costs regularity and uniform
refinement just can't recover it. Spent the day on the fix.

- **Step zero: figure out where the error lives.** Before redesigning the
  mesh, I wrote a one-off DG0 diagnostic that projects `(u_h - u_exact)²`
  cell-by-cell and prints the top-10 cells by error magnitude alongside their
  centroids. All ten sat within a few elements of the origin — confirms the
  corner-localization story before committing to a refinement strategy.
- The general rule from this: do not redesign the mesh until the error
  diagnosis says where the error actually lives. We've twice now caught
  ourselves about to over-refine globally for a problem that was really about
  a single corner.

**Decision:** the DG0 cell-error diagnostic is a permanent first step before
any refinement-strategy discussion on a new problem. Cheap, ~20 lines of
Firedrake, no excuse not to run it.

- **Refinement strategy: a priori radial L∞-grading toward the corner.** Use
  `MeshHierarchy(base, levels)` for the topology, then per level apply
  `(x, y) → (x, y) · (ρ/R)^(β-1)` where `ρ = max(|x|, |y|)` and `R = 1`.
  L∞-norm rather than Euclidean because it leaves boundary nodes fixed (the
  L-shape's outer boundary lies on `ρ = 1`); only interior and corner-adjacent
  nodes get pulled in.
- **Grading exponent `β = 3.0`.** Classical Babuška a priori choice for P1 on
  `r^(2/3)` corner singularities. We could derive a different exponent for
  higher-order elements but P1 is what production runs use, so β=3.0 is what
  we standardize on.

**Decision:** radial L∞-grading with β=3.0 is the standard fix for L-shape
problems in this group. The implementation lives in
`exercises-pde/02-planning/laplace_lshape.py` as `grade_to_corner(mesh, beta)`.

- **Quadrature degree is not optional.** First attempt used Firedrake's
  default `dx` (auto-degree). Assembly hung — the auto-estimator over-counts
  the polynomial degree of `r^(2/3)` (it isn't polynomial at all) and picks a
  quadrature rule that's effectively unbounded near the corner. Forced
  `dx(degree=4)` on every integral involving `u_exact`. Assembly finished in
  about a second.

**Decision:** every integral involving a non-polynomial manufactured solution
(or any non-polynomial coefficient) carries `dx(degree=4)` explicitly. This is
a permanent rule — non-negotiable, even for unrelated problems. The reason is
above; the alternative is silent assembly hangs that look like Firedrake
broke.

**Parameters from the fix:** with β=3.0 graded refinement over 4 levels of
`MeshHierarchy`, both L² and H¹ rates climb toward the optimal values for P1
across the sweep — the plateau is gone. DG0 diagnostic confirms the top-error
cells after grading still cluster near the corner (`|x|, |y| ≲ 0.17`) but the
magnitudes are now small enough that the global rate is dominated by the bulk
of the domain rather than by a handful of cells.

**Open question:** does β=3.0 carry to the 3D Fichera-corner analog
(`[-1,1]³` minus one octant), or do we need to re-derive the grading exponent
for the 3D singularity exponent? Untested. The current consensus is "probably
needs re-derivation" but we haven't put a number on it.

**Open question:** for L-shapes with mixed boundary conditions (Dirichlet on
some edges, Neumann on others), does the singularity exponent change enough
to need a different β? The pure Dirichlet case is what's covered by the
classical analysis; we'll hit mixed BC the moment we move past test problems.
