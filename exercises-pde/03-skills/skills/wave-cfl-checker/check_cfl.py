"""wave-cfl-checker - verify the element-wise CFL condition.

For each cell of a Firedrake mesh, computes the largest eigenvalue of
the generalized eigenproblem K_e v = lambda M_e v with SLEPc, where M_e
is the local consistent mass matrix and K_e is the local c^2-weighted
stiffness matrix for the wave equation u_tt = div(c^2 grad u). Then
checks whether the proposed timestep dt is below 2/sqrt(lambda_max) on
every element and reports any violators.

Implementation note
-------------------
Per-cell M_e and K_e are obtained by assembling the bilinear forms on
a discontinuous Galerkin space at the same polynomial degree as V. DG
basis functions on different cells do not overlap, so the global mass
and stiffness matrices are block-diagonal and each block is exactly
the per-cell M_e or K_e of the continuous problem - the same local
matrix values that govern the CG-discretized CFL bound.

Run via the wave-cfl-checker skill (see SKILL.md for the docker-wrapped
invocation).
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from firedrake import *
from petsc4py import PETSc
from slepc4py import SLEPc


def load_problem(path):
    """Import the user's problem module and call its get_problem()."""
    spec = importlib.util.spec_from_file_location("problem_mod", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["problem_mod"] = mod
    spec.loader.exec_module(mod)
    return mod.get_problem()


def _to_petsc_dense(arr):
    """Wrap a square numpy array as a serial PETSc dense matrix."""
    n = arr.shape[0]
    A = PETSc.Mat().createDense((n, n), comm=PETSc.COMM_SELF)
    A.setUp()
    idx = np.arange(n, dtype=PETSc.IntType)
    A.setValues(idx, idx, arr)
    A.assemble()
    return A


def largest_generalized_eigenvalue(K_block, M_block):
    """Largest lambda of K_e v = lambda M_e v via SLEPc EPS (GHEP, LARGEST)."""
    K_pet = _to_petsc_dense(K_block)
    M_pet = _to_petsc_dense(M_block)

    eps = SLEPc.EPS().create(comm=PETSc.COMM_SELF)
    eps.setOperators(K_pet, M_pet)
    eps.setProblemType(SLEPc.EPS.ProblemType.GHEP)
    eps.setWhichEigenpairs(SLEPc.EPS.Which.LARGEST_MAGNITUDE)
    eps.setDimensions(nev=1)
    eps.solve()

    if eps.getConverged() < 1:
        raise RuntimeError("SLEPc converged 0 eigenpairs on a local element")
    return eps.getEigenvalue(0).real


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--problem", required=True,
                   help="Path to a .py exposing get_problem() -> (mesh, V, c2)")
    p.add_argument("--candidate", required=True,
                   help="Path to a JSON file with key 'dt'")
    args = p.parse_args(argv)

    mesh, V, c2 = load_problem(Path(args.problem))
    dt = float(json.loads(Path(args.candidate).read_text())["dt"])

    # Assemble M and (c^2-weighted) K on a DG space at V's degree, so
    # each diagonal block of the global matrix is one cell's local matrix.
    degree = V.ufl_element().degree()
    W = FunctionSpace(mesh, "DG", degree)
    u = TrialFunction(W)
    w = TestFunction(W)
    M_global = assemble(u * w * dx)
    K_global = assemble(c2 * inner(grad(u), grad(w)) * dx)
    M_pet = M_global.M.handle
    K_pet = K_global.M.handle

    cell_to_dof = W.cell_node_map().values_with_halo
    c2_per_cell = c2.dat.data_ro
    num_cells = mesh.num_cells()

    lambdas = np.zeros(num_cells)
    for c in range(num_cells):
        dofs = np.asarray(cell_to_dof[c], dtype=PETSc.IntType)
        M_block = np.array(M_pet.getValues(dofs, dofs))
        K_block = np.array(K_pet.getValues(dofs, dofs))
        lambdas[c] = largest_generalized_eigenvalue(K_block, M_block)

    dt_e = 2.0 / np.sqrt(lambdas)
    safe = float(dt_e.min())
    worst = int(dt_e.argmin())
    violators = np.where(dt >= dt_e)[0]

    layers = sorted(set(float(val) for val in c2_per_cell))
    layer_summary = [(c2v, float(dt_e[c2_per_cell == c2v].min())) for c2v in layers]

    if len(violators) == 0:
        print(f"PASS: dt = {dt:.5f}, safe = {safe:.5f} (min over {num_cells} cells)")
        print(f"       limited by cell {worst}  "
              f"(lambda_max = {lambdas[worst]:.2e},  dt_e = {dt_e[worst]:.2e})")
        for c2v, mindt in layer_summary:
            print(f"       layer c^2 = {c2v:>3.1f}  min dt_e = {mindt:.2e}")
        return 0
    else:
        print(f"FAIL: dt = {dt:.5f}, safe = {safe:.5f} (min over {num_cells} cells)")
        print(f"       {len(violators)} cells violate the bound; first 5 below")
        print(f"       cell    lambda_max   dt_e         c^2")
        for vi in violators[:5]:
            print(f"       {int(vi):6d}  {lambdas[vi]:.2e}     "
                  f"{dt_e[vi]:.2e}     {float(c2_per_cell[vi]):>3.1f}")
        for c2v, mindt in layer_summary:
            print(f"       layer c^2 = {c2v:>3.1f}  min dt_e = {mindt:.2e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
