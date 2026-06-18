"""Toy Laplace solve on the unit square. Used in workshop exercise 01.

This script is deliberately under-specified: no convergence study,
no figures, hardcoded P1 elements. The exercise is to ask Claude Code
to improve it under your CLAUDE.md conventions.
"""
from firedrake import *


def manufactured(mesh):
    """Manufactured solution for -Delta u = f on the unit square.

    u_exact(x, y) = sin(pi x) sin(pi y),  so  f = 2 pi^2 sin(pi x) sin(pi y).
    Vanishes on the boundary, so homogeneous Dirichlet BCs apply.
    """
    x, y = SpatialCoordinate(mesh)
    u_exact = sin(pi * x) * sin(pi * y)
    f = 2 * pi**2 * sin(pi * x) * sin(pi * y)
    return u_exact, f


def solve_square(mesh):
    V = FunctionSpace(mesh, "CG", 1)
    u = TrialFunction(V)
    v = TestFunction(V)

    _, f = manufactured(mesh)

    a = inner(grad(u), grad(v)) * dx
    L = f * v * dx
    bc = DirichletBC(V, 0.0, "on_boundary")

    u_h = Function(V, name="u")
    solve(a == L, u_h, bcs=bc)
    return u_h


if __name__ == "__main__":
    mesh = UnitSquareMesh(8, 8)  # the textbook coarse mesh
    u_h = solve_square(mesh)
    print("solve complete")
