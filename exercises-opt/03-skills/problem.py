"""Small bound-constrained QP used in the kkt-checker exercise.

Problem:
    min  0.5 x^T Q x + c^T x
    s.t. A x = b
         x >= 0

Returned QP data has a known KKT point stored in solution.json.
"""
import numpy as np


def get_qp():
    Q = np.array([[4.0, 1.0, 0.0],
                  [1.0, 2.0, 0.0],
                  [0.0, 0.0, 2.0]])
    c = np.array([-1.0, -1.0, -1.0])
    A = np.array([[1.0, 1.0, 1.0]])
    b = np.array([1.0])
    return Q, c, A, b


if __name__ == "__main__":
    Q, c, A, b = get_qp()
    eigs = np.linalg.eigvalsh(Q)
    print(f"min eig(Q) = {eigs.min():.4f}  (must be > 0 for strong convexity)")
    print(f"A = {A}, b = {b}")
