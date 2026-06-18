"""Laplace solve on an L-shaped domain with a corner-singular manufactured solution.

This script runs a convergence study under uniform mesh refinement and prints
L^2 and H^1 error rates against the exact solution. The mesh `lshape.msh` is
the square [-1, 1] x [-1, 1] with the lower-right quadrant [0, 1] x [-1, 0]
cut out; the reentrant corner sits at the origin. The manufactured solution
is the canonical L-shape singular function

    u(r, phi) = r^(2/3) sin(2 phi / 3)

in polar coordinates centered at the origin, with phi measured counterclockwise
from the +x wedge edge (the segment y = 0, x > 0). The function is harmonic,
so f = 0; the inhomogeneous Dirichlet condition is the trace of u on the full
boundary.

Under uniform mesh refinement at P1 the L^2 rate plateaus around 4/3 and the
H^1 rate around 2/3, well below the smooth-domain expectations of 2 and 1.
Restoring the optimal rates requires refining the mesh more densely near the
reentrant corner. This file is deliberately left in the uniform-refinement
state so that running it surfaces the problem.
"""
from math import log2

from firedrake import *


def manufactured(mesh):
    """L-shape singular manufactured solution u(r, phi) = r^(2/3) sin(2 phi / 3).

    Polar coordinates centered at the reentrant corner (the origin); phi
    measured counterclockwise from the +x wedge edge (the segment y = 0,
    x > 0). Harmonic, so f = 0. The Dirichlet trace vanishes on the two
    wedge edges; on the rest of the L-shape boundary the trace is non-zero
    and is imposed as a non-homogeneous BC.

    The L-shape interior wraps from the +x wedge edge counterclockwise
    through +y, -x, around to the -y wedge edge, spanning 3 pi / 2 of angle
    around the corner. `atan2` returns values in (-pi, pi], so to make phi
    increase continuously across the interior the negative angles are
    shifted up by 2 pi.
    """
    x, y = SpatialCoordinate(mesh)
    r = sqrt(x ** 2 + y ** 2)
    theta = atan2(y, x)  # range (-pi, pi]
    phi = conditional(ge(theta, 0), theta, theta + 2 * pi)
    u_exact = r ** (2.0 / 3.0) * sin((2.0 / 3.0) * phi)
    f = Constant(0.0)
    return u_exact, f


def convergence_study(levels=4):
    """Uniform-refinement convergence study at P1.

    Loads lshape.msh as the base mesh, builds MeshHierarchy(base, levels) for
    a total of levels + 1 meshes, solves -Delta u = 0 with the singular trace
    as Dirichlet data at each level, and prints L^2 and H^1 errors plus
    consecutive rates. Polynomial order is hardcoded at P1; the only available
    lever for changing solution accuracy is the mesh.
    """
    base = Mesh("lshape.msh")
    hierarchy = MeshHierarchy(base, levels)

    rows = []
    for level, mesh in enumerate(hierarchy):
        V = FunctionSpace(mesh, "CG", 1)
        u_exact, f = manufactured(mesh)

        u = TrialFunction(V)
        v = TestFunction(V)
        a = inner(grad(u), grad(v)) * dx(degree=4)
        L = f * v * dx(degree=4)
        bc = DirichletBC(V, u_exact, "on_boundary")

        u_h = Function(V, name="u")
        solve(a == L, u_h, bcs=bc)

        diff = u_h - u_exact
        l2 = sqrt(assemble(inner(diff, diff) * dx(degree=4)))
        h1 = sqrt(assemble((inner(diff, diff) + inner(grad(diff), grad(diff))) * dx(degree=4)))

        # MeshHierarchy halves the representative cell size at each level.
        h = 1.0 / 2 ** level
        rows.append((level, h, V.dim(), float(l2), float(h1)))

    header = (
        f"{'level':>5}  {'h':>10}  {'dofs':>8}  "
        f"{'L2 err':>12}  {'L2 rate':>8}  {'H1 err':>12}  {'H1 rate':>8}"
    )
    print(header)
    print("-" * len(header))
    for i, (level, h, dofs, l2, h1) in enumerate(rows):
        if i == 0:
            l2_rate = "-"
            h1_rate = "-"
        else:
            _, _, _, l2_prev, h1_prev = rows[i - 1]
            l2_rate = f"{log2(l2_prev / l2):.3f}"
            h1_rate = f"{log2(h1_prev / h1):.3f}"
        print(
            f"{level:>5}  {h:>10.4e}  {dofs:>8d}  "
            f"{l2:>12.4e}  {l2_rate:>8}  {h1:>12.4e}  {h1_rate:>8}"
        )
    print()
    print("Expected rates for P1 on a smooth problem: L2 = 2.0, H1 = 1.0.")


if __name__ == "__main__":
    convergence_study()
