# Solution — Exercise 02 (Planning, L-shape Laplace)

## What this exercise is doing

The learner runs a starter (`laplace_lshape.py`) that solves `-Δu = 0` on an L-shaped domain against the canonical L-shape singular manufactured solution `u(r, φ) = r^(2/3) sin(2φ/3)`, with the trace of `u` imposed on the boundary. Uniform `MeshHierarchy` refinement at P1 produces L² rates around `4/3` and H¹ rates around `2/3` — well below the smooth-problem expectations of `2` and `1`. The rate plateau is a consequence of the geometry: the reentrant corner (at the origin of the `[-1,1] × [-1,1]` minus lower-right-quadrant domain) costs regularity, and uniform refinement does not compensate.

The exercise asks Claude to *plan* the fix in plan mode; the deliverable is the **`plan.md`**. Actually implementing the plan and re-running to verify the rates recover is an **optional step, if time permits**. The canonical a priori fix is graded mesh refinement around the reentrant corner; this SOLUTION gives a facilitator a worked model of both the plan (the deliverable) and the optional implementation, to compare against what learners produce.

## The prompt the learner pastes

```
The convergence in this code is suboptimal. Create a plan to
identify where the error is concentrated, then construct an a
priori mesh refinement strategy in the problem regions.

The polynomial order is fixed at P1; only the mesh is in scope.
```

## A worked model `plan.md`

This is the shape of plan a learner should aim for after one or two rounds of pushback. It is not the *only* correct plan; it is a plan that, after approval, leads to working code in one implementation pass.

```markdown
# Plan — recover P1 rates on the L-shape via a priori graded refinement

## Goal
Modify `laplace_lshape.py` so the convergence study refines the mesh more
densely near the reentrant corner (at the origin) instead of uniformly.
Keep the existing rates harness, the manufactured solution, the boundary
condition, and the P1 element choice unchanged; only change how the
sequence of meshes is generated. Target: L² rate ≥ 1.9 and H¹ rate ≥ 0.95
across the refinement levels.

## Files I will modify
1. `laplace_lshape.py` — add a `graded_meshes(base, levels, beta)` helper
   that returns a sequence of progressively-refined meshes graded toward
   the corner via a radial coordinate transformation. Replace the
   `MeshHierarchy(base, levels)` call in `convergence_study()` with a call
   to the new helper. Before the main loop, add a one-off diagnostic that
   solves on the coarsest mesh, computes the element-wise error
   `|u_h − u_exact|` per cell, and prints which cells carry the largest
   share — confirming the error concentrates at the corner before the
   refinement strategy is applied.

## Step-by-step
1. Inspect `lshape.msh` to confirm the reentrant corner is at the origin
   (the domain is `[-1, 1] × [-1, 1]` minus the lower-right quadrant).
2. Implement the element-wise error diagnostic: build a DG0 function,
   project `|u_h − u_exact|` (or its square) onto it cell-by-cell using
   `assemble(... * v * dx(degree=4))` with `v` a DG0 test function, print
   the top 10 cells by value alongside their centroid coordinates.
3. Implement `graded_meshes(base, levels, beta=3.0)`. Start from a
   `MeshHierarchy(base, levels)` for the uniform topology; on each level,
   apply a radial coordinate transformation centered at the corner that
   maps each interior node toward the origin via
   `(x, y) → (x, y) * (ρ/R)^(β-1)`, where `ρ = max(|x|, |y|)` and `R = 1`.
   The L∞-based scaling preserves the L-shape's axis-aligned boundary
   (nodes on the outer boundary have `ρ = 1` and stay fixed); only
   interior and corner-adjacent nodes move. Choose `β = 3.0` as the
   classical a priori exponent for P1 + `r^(2/3)` singularity.
4. Replace `MeshHierarchy(base, 4)` in `convergence_study()` with
   `graded_meshes(base, 4, beta=3.0)`. Leave the rates loop, the
   assembly, the BCs, the `dx(degree=4)` quadrature settings, and the
   printed table format unchanged.
5. Run; verify the printed rates recover toward 2.0 (L²) and 1.0 (H¹)
   across levels 1–4.

## Open questions for the user
- Grading exponent β. Default proposed: 3.0 (classical for P1 + r^(2/3)).
  Higher β over-grades and can spoil cell shape; lower β under-grades
  and recovers the rate only partially. Confirm 3.0 or override.
- Diagnostic granularity. Default: print top 10 cells by error. If you
  want a saved figure (DG0 field exported for paraview/pyvista), I'll
  add that — but writing figures wasn't in the prompt, so I'm leaving it
  off by default.
- Whether to also report the per-level mesh statistics (minimum cell
  diameter near the corner) alongside the rates table. Helpful for
  understanding what graded refinement is actually doing; happy to add.

## Out of scope
- A posteriori adaptive marking using a residual or error indicator.
- Dörfler-style adaptive loops (mark → refine → re-solve → repeat).
- hp-refinement; alternative element families (DG, mixed).
- Replacing the manufactured solution or changing the boundary trace.
- Modifying or writing any `.msh` or `.geo` file.
- Adding CLI flags.
- Changing the polynomial order from P1.

## I will not
- Write or modify any `.msh` or `.geo` file.
- Pass a `.geo` file to Firedrake's `Mesh()` constructor.
- Change `manufactured()` or the Dirichlet trace.
- Change `"CG", 1` to anything else.
- Add `argparse` or any CLI.
- `pip install` new packages.
```

## Model implementation

If you take the optional implement-the-plan step, a clean implementation looks like this. The diagnostic step and the graded-meshes helper are the only new code; the rates loop is left intact.

```python
"""Laplace solve on an L-shaped domain with corner-graded refinement.

The mesh `lshape.msh` is the square [-1, 1] x [-1, 1] with the lower-right
quadrant [0, 1] x [-1, 0] cut out; the reentrant corner sits at the origin.
The manufactured solution u(r, phi) = r^(2/3) sin(2 phi / 3) is harmonic;
the inhomogeneous Dirichlet trace is imposed on the full boundary.

Under uniform refinement at P1 the L^2 rate plateaus around 4/3 and the
H^1 rate around 2/3. With a priori radial grading toward the corner
(exponent beta = 3), the rates recover toward 2.0 and 1.0.
"""
from math import log2

import numpy as np
from firedrake import *


def manufactured(mesh):
    x, y = SpatialCoordinate(mesh)
    r = sqrt(x ** 2 + y ** 2)
    theta = atan2(y, x)
    phi = conditional(ge(theta, 0), theta, theta + 2 * pi)
    u_exact = r ** (2.0 / 3.0) * sin((2.0 / 3.0) * phi)
    f = Constant(0.0)
    return u_exact, f


def grade_to_corner(mesh, beta=3.0, R=1.0):
    """Apply a radial L-infinity grading transformation centered at the origin.

    Maps each node (x, y) to (x, y) * (rho / R)^(beta - 1), where
    rho = max(|x|, |y|). Boundary nodes (rho = R = 1) stay fixed because
    the scale factor is 1 there; interior nodes are pulled toward the
    corner more strongly the closer they already are to it.
    """
    coords = mesh.coordinates.dat.data
    rho = np.maximum(np.abs(coords[:, 0]), np.abs(coords[:, 1]))
    with np.errstate(invalid="ignore", divide="ignore"):
        scale = np.where(rho > 0, (rho / R) ** (beta - 1.0), 0.0)
    coords[:, 0] = coords[:, 0] * scale
    coords[:, 1] = coords[:, 1] * scale
    return mesh


def graded_meshes(base, levels, beta=3.0):
    """Uniform MeshHierarchy followed by per-level radial grading."""
    hierarchy = MeshHierarchy(base, levels)
    return [grade_to_corner(m, beta=beta) for m in hierarchy]


def diagnose_error_concentration(mesh, top=10):
    """One-off check: print the cells with the largest |u_h - u_exact|.

    Solves on the given mesh once, then projects the squared cell-wise
    error onto DG0 and reports the largest entries alongside cell
    centroids. The expectation is that the largest entries cluster
    near the corner at the origin.
    """
    V = FunctionSpace(mesh, "CG", 1)
    u_exact, f = manufactured(mesh)
    u = TrialFunction(V); v = TestFunction(V)
    bc = DirichletBC(V, u_exact, "on_boundary")
    a = inner(grad(u), grad(v)) * dx(degree=4)
    L = f * v * dx(degree=4)
    u_h = Function(V)
    solve(a == L, u_h, bcs=bc)

    DG0 = FunctionSpace(mesh, "DG", 0)
    w = TestFunction(DG0)
    err_sq = assemble((u_h - u_exact) ** 2 * w * dx(degree=4))
    centroids = assemble(SpatialCoordinate(mesh) * w * dx) / assemble(
        Constant(1.0) * w * dx
    )
    err = np.sqrt(err_sq.dat.data)
    idx = np.argsort(err)[-top:][::-1]
    print(f"Top {top} cells by |u_h - u_exact|:")
    for i in idx:
        cx, cy = centroids.dat.data[i]
        print(f"  centroid=({cx:+.4f}, {cy:+.4f})   err={err[i]:.3e}")


def convergence_study(levels=4, beta=3.0):
    base = Mesh("lshape.msh")
    diagnose_error_concentration(base)
    meshes = graded_meshes(base, levels, beta=beta)

    rows = []
    for level, mesh in enumerate(meshes):
        V = FunctionSpace(mesh, "CG", 1)
        u_exact, f = manufactured(mesh)
        u = TrialFunction(V); v = TestFunction(V)
        a = inner(grad(u), grad(v)) * dx(degree=4)
        L = f * v * dx(degree=4)
        bc = DirichletBC(V, u_exact, "on_boundary")
        u_h = Function(V, name="u")
        solve(a == L, u_h, bcs=bc)

        diff = u_h - u_exact
        l2 = sqrt(assemble(inner(diff, diff) * dx(degree=4)))
        h1 = sqrt(assemble((inner(diff, diff) + inner(grad(diff), grad(diff))) * dx(degree=4)))

        h = 1.0 / 2 ** level
        rows.append((level, h, V.dim(), float(l2), float(h1)))

    header = (f"{'level':>5}  {'h':>10}  {'dofs':>8}  "
              f"{'L2 err':>12}  {'L2 rate':>8}  {'H1 err':>12}  {'H1 rate':>8}")
    print(header); print("-" * len(header))
    for i, (level, h, dofs, l2, h1) in enumerate(rows):
        if i == 0:
            l2_rate, h1_rate = "-", "-"
        else:
            _, _, _, l2_prev, h1_prev = rows[i - 1]
            l2_rate = f"{log2(l2_prev / l2):.3f}"
            h1_rate = f"{log2(h1_prev / h1):.3f}"
        print(f"{level:>5}  {h:>10.4e}  {dofs:>8d}  "
              f"{l2:>12.4e}  {l2_rate:>8}  {h1:>12.4e}  {h1_rate:>8}")
    print()
    print("Expected rates for P1 on a smooth problem: L2 = 2.0, H1 = 1.0.")


if __name__ == "__main__":
    convergence_study()
```

## Sample output (recovered rates)

The exact numbers depend on the base mesh and the grading exponent, but the *shape* of the table should be: the L² rate climbing into the 1.9–2.0 band and the H¹ rate climbing into the 0.95–1.0 band by the last two levels. The diagnostic block before the table should report the largest-error cells clustered near `(±ε, ±ε)` for small `ε`, confirming the error is concentrated at the corner.

```
Top 10 cells by |u_h - u_exact|:
  centroid=(-0.1667, +0.1667)   err=3.4e-02
  centroid=(+0.1667, +0.1667)   err=3.1e-02
  centroid=(-0.1667, -0.1667)   err=2.8e-02
  ... (remaining centroids also near the origin) ...

level           h      dofs        L2 err   L2 rate        H1 err   H1 rate
---------------------------------------------------------------------------
    0  1.0000e+00        21    8.214e-02         -    5.123e-01         -
    1  5.0000e-01        65    2.418e-02     1.764    2.733e-01     0.907
    2  2.5000e-01       225    6.421e-03     1.913    1.401e-01     0.964
    3  1.2500e-01       833    1.640e-03     1.969    7.087e-02     0.984
    4  6.2500e-02      3201    4.131e-04     1.989    3.560e-02     0.994

Expected rates for P1 on a smooth problem: L2 = 2.0, H1 = 1.0.
```

(Illustrative values; expect the same shape, not exactly these numbers.)

**Important caveat for facilitators.** The numbers above are *one* possible outcome of *one* possible implementation. In a workshop run-through the author did not chase the rates all the way into the 1.95–2.0 band because doing so requires tuning the grading exponent, the cell-shape behavior of the chosen primitive, and possibly the number of refinement levels — all of which are FEM craft, not planning craft. **A learner whose run produces L² rates climbing visibly (e.g. from 1.3 → 1.7 → 1.85) but not reaching 2.0 has done the exercise.** The pedagogical point is that the rates moved in the right direction after a planned, scoped change — not that the constants are textbook-perfect. Redirect any learner who starts tuning grading parameters back to the planning lesson; "good enough to see the rate improving" is the success criterion here.

## Where it usually goes wrong on the first try

The L-shape singularity is one of the most-taught problems in finite element analysis, so Claude has strong priors about what a "correct" answer looks like. The defects below are the predictable consequence of Claude pattern-matching on a familiar problem rather than reasoning fresh about the code in front of it. The right-hand column is the line a facilitator can suggest the learner push back with.

| What the first plan often does | What to push back with |
|--------------------------------|------------------------|
| Compresses or omits the error-diagnosis step. ("It's the corner — let's grade.") | "Step 1 of the prompt is *identify where the error is concentrated*. Plan a concrete diagnostic — element-wise `\|u_h − u_exact\|`, a DG0 projection, a printout, or a plot — before you plan the refinement." |
| Substitutes a posteriori adaptive refinement (mark/refine/re-solve loop) for the a priori graded refinement asked for. | "The prompt asks for *a priori graded* refinement. Adaptive loops are out of scope. Use a fixed grading rule chosen up front, not an iterative marker." |
| Proposes a refinement step without naming the Firedrake/UFL mechanism. | "Name the refinement mechanism explicitly — `MeshHierarchy` plus a coordinate transformation, NetgenHierarchy with a marker, PETSc-level cell refinement, etc. If you're unsure which works on a gmsh-imported mesh, list candidates and pick one as the default." |
| Proposes generating a new `.msh` or `.geo` file per refinement level. | "Don't write or modify mesh files. The base `lshape.msh` is the only mesh on disk; refinement happens in memory." |
| Proposes changing the polynomial order to P2 'for better convergence.' | "P1 is fixed by the exercise. Only the mesh is in scope." |
| Doesn't pin grading parameters (radius, exponent, depth) — proposes "refine until the rate recovers." | "Pick concrete defaults for the grading exponent and (if applicable) the marking radius up front. The rates loop runs with fixed parameters so successive runs are comparable." |
| Drops the `dx(degree=4)` quadrature setting on new integrals (the element-wise indicator, the projected DG0 field, etc.). | "Carry forward `dx(degree=4)` on every new integral. The manufactured solution is non-polynomial; without it, the auto-estimator over-estimates and assembly hangs." |
| Drifts straight into implementation without an Open Questions or Out of Scope section. | "Add both sections before stopping. A plan that doesn't bound itself will quietly grow during implementation." |

## How to use this in the workshop

Hand learners the README and let them work through the exercise in their own session. Let them produce their own plan; do not show this SOLUTION until afterwards. When debriefing, compare their plan against the model above — disagreement is fine and often informative. The pitfalls table is the most useful piece of this document during the room: when a learner gets stuck on Claude's plan, you can scan the table for the matching defect and point them at the pushback line. The model implementation is for facilitator reference and parity-checking only; it is not the only correct implementation, and a learner who arrives at a different working approach (e.g. NetgenHierarchy + marker, PETSc DMPlex refinement) has done the exercise correctly.
