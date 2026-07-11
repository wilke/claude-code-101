import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve


def _element_stiffness():
    """Return the 8x8 element stiffness matrix for a unit square Q4 element."""
    E, nu = 1.0, 0.3
    k = np.array([
        1/2 - nu/6,   1/8 + nu/8, -1/4 - nu/12, -1/8 + 3*nu/8,
       -1/4 + nu/12, -1/8 - nu/8,        nu/6,   1/8 - 3*nu/8,
    ])
    KE = E / (1 - nu**2) * np.array([
        [k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7]],
        [k[1], k[0], k[7], k[6], k[5], k[4], k[3], k[2]],
        [k[2], k[7], k[0], k[5], k[6], k[3], k[4], k[1]],
        [k[3], k[6], k[5], k[0], k[7], k[2], k[1], k[4]],
        [k[4], k[5], k[6], k[7], k[0], k[1], k[2], k[3]],
        [k[5], k[4], k[3], k[2], k[1], k[0], k[7], k[6]],
        [k[6], k[3], k[4], k[1], k[2], k[7], k[0], k[5]],
        [k[7], k[2], k[1], k[4], k[3], k[6], k[5], k[0]],
    ])
    return KE


class ComplianceProblem:
    """
    Finite-element compliance evaluator for a 2-D cantilever beam.

    The domain is nelx-by-nely Q4 elements, clamped on the left edge,
    with a unit downward point load at the mid-point of the right edge.

    Parameters
    ----------
    nelx, nely : int
        Number of elements in x and y directions.
    penal : float
        SIMP penalization exponent.
    Emin, Emax : float
        Minimum and maximum Young's modulus.
    """

    def __init__(self, nelx, nely, penal, Emin=1e-9, Emax=1.0):
        self.nelx  = nelx
        self.nely  = nely
        self.penal = penal
        self.Emin  = Emin
        self.Emax  = Emax

        ndof = 2 * (nelx + 1) * (nely + 1)
        self.ndof = ndof

        # --- Element stiffness matrix ---
        self.KE = _element_stiffness()

        # --- Element DOF map (nelx*nely x 8) ---
        edofMat = np.zeros((nelx * nely, 8), dtype=int)
        for elx in range(nelx):
            for ely in range(nely):
                el = ely + elx * nely
                n1 = (nely + 1) * elx + ely
                n2 = (nely + 1) * (elx + 1) + ely
                edofMat[el, :] = [
                    2*n1+2, 2*n1+3, 2*n2+2, 2*n2+3,
                    2*n2,   2*n2+1, 2*n1,   2*n1+1,
                ]
        self.edofMat = edofMat

        # --- Sparse stiffness matrix index vectors ---
        self.iK = np.kron(edofMat, np.ones((8, 1), dtype=int)).flatten()
        self.jK = np.kron(edofMat, np.ones((1, 8), dtype=int)).flatten()

        # --- Boundary conditions: clamp left edge, free everything else ---
        dofs  = np.arange(ndof)
        fixed = np.union1d(
            dofs[0 : 2*(nely+1) : 2],          # left edge, x-dofs
            np.array([2*(nelx+1)*(nely+1) - 1]) # bottom-right corner, y-dof
        )
        self.free = np.setdiff1d(dofs, fixed)

        # --- Load: unit downward force at mid-point of right edge ---
        self.f = np.zeros((ndof, 1))
        self.f[1, 0] = -1.0

        # --- Displacement vector (reused across calls) ---
        self.u = np.zeros((ndof, 1))

        # --- Timing accumulators (updated on each __call__) ---
        self.total_time_pde     = 0.0   # K assembly + spsolve
        self.total_time_adjoint = 0.0   # strain energies + sensitivity
        self.n_pde_calls        = 0     # total number of __call__ invocations

    def __call__(self, xPhys):
        """
        Evaluate compliance and its sensitivity for a given design.

        Parameters
        ----------
        xPhys : (nelx*nely,) array
            Physical element densities in [0, 1].

        Returns
        -------
        compliance : float
            Structural compliance (scalar objective to minimise).
        sensitivity : (nelx*nely,) array
            Gradient of compliance with respect to xPhys (unfiltered).
        """
        nelx, nely   = self.nelx, self.nely
        penal        = self.penal
        Emin, Emax   = self.Emin, self.Emax
        KE           = self.KE
        edofMat      = self.edofMat
        iK, jK       = self.iK, self.jK
        free         = self.free

        # --- PDE solve: assemble K and solve Ku = f ---
        _t0 = time.perf_counter()
        E_elem = Emin + xPhys**penal * (Emax - Emin)   # SIMP interpolation
        sK = (KE.flatten()[np.newaxis].T * E_elem).flatten(order='F')
        K  = coo_matrix((sK, (iK, jK)), shape=(self.ndof, self.ndof)).tocsc()
        K  = K[free, :][:, free]
        self.u[free, 0] = spsolve(K, self.f[free, 0])
        self.total_time_pde += time.perf_counter() - _t0
        self.n_pde_calls    += 1

        # --- Adjoint: element strain energies and sensitivity ---
        _t0 = time.perf_counter()
        ue  = self.u[edofMat].reshape(nelx * nely, 8)   # element displacements
        ce  = (ue @ KE * ue).sum(axis=1)                # u_e^T K_e u_e
        compliance  = (E_elem * ce).sum()
        sensitivity = (-penal * xPhys**(penal - 1) * (Emax - Emin)) * ce
        self.total_time_adjoint += time.perf_counter() - _t0

        return compliance, sensitivity


# ---------------------------------------------------------------------------
# Quick smoke test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    prob = ComplianceProblem(nelx=60, nely=20, penal=3.0)

    # Uniform design at 40 % density
    x = np.full(60 * 20, 0.4)
    c, dc = prob(x)
    print(f"Compliance : {c:.6f}")
    print(f"Sensitivity: min={dc.min():.4f}, max={dc.max():.4f}")
