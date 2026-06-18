"""2D acoustic wave equation on the unit square with a layered medium.

Used by the wave-cfl-checker skill.

PDE
---
    u_tt = div( c^2 grad u )       on  Omega = (0, 1)^2

Wave speed c is piecewise constant in two horizontal layers:

    c = 1   for y > 0.5            (top half)
    c = 2   for y < 0.5            (bottom half)

The interface y = 0.5 aligns with a mesh facet (N is required even), so
each triangle lies entirely in one layer and a single c^2 value per cell
is exact.

FE discretization
-----------------
P2 continuous Lagrange triangles on a structured UnitSquareMesh(N, N).
get_problem() returns (mesh, V, c2) where c2 is a DG0 Function holding
c^2 per cell.
"""
from firedrake import *


def get_problem(N: int = 16):
    """Build the wave-equation problem the wave-cfl-checker consumes.

    Parameters
    ----------
    N : int
        Number of subdivisions per side. Must be even so the y = 0.5
        interface aligns with a mesh facet.

    Returns
    -------
    mesh : firedrake.Mesh
        UnitSquareMesh(N, N), triangular.
    V : firedrake.FunctionSpace
        P2 continuous Lagrange on the mesh.
    c2 : firedrake.Function
        DG0 (piecewise-constant per cell) c^2 field. Equal to 1.0 on cells
        with centroid above y = 0.5 and 4.0 (= 2^2) on cells below.
    """
    if N % 2 != 0:
        raise ValueError("N must be even so the layer interface aligns with a mesh facet.")
    mesh = UnitSquareMesh(N, N)
    V = FunctionSpace(mesh, "CG", 2)
    DG0 = FunctionSpace(mesh, "DG", 0)
    _, y = SpatialCoordinate(mesh)
    # DG0 nodal point is the cell centroid, so interpolate(conditional(...))
    # gives one c^2 value per cell, exact for cells fully in one layer.
    c2 = Function(DG0).interpolate(conditional(y > 0.5, 1.0, 4.0))
    return mesh, V, c2


if __name__ == "__main__":
    mesh, V, c2 = get_problem()
    n_cells = mesh.num_cells()
    arr = c2.dat.data_ro
    n_top = int((arr == 1.0).sum())
    n_bot = int((arr == 4.0).sum())
    print(f"mesh:   UnitSquareMesh(16, 16),  {n_cells} triangles")
    print(f"V:      P2 CG,  {V.dim()} DOFs")
    print(f"c^2:    top (c=1)    -> {n_top} cells")
    print(f"        bottom (c=2) -> {n_bot} cells")
