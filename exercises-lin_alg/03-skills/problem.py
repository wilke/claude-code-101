"""The three objects from exercises 01-02, exposed for the singular-value skills:

    get_dense()    -> the dense matrix                   (matrix_A.npy)
    get_sparse()   -> the sparse matrix                  (matrix_B.npz)
    get_operator() -> the matrix-free heat-step operator (heat_operator.py)

All three files are expected in this exercise directory — copy matrix_A.npy,
matrix_B.npz, and heat_operator.py here alongside problem.py. Paths are resolved
relative to this file, so it works from any cwd.
"""
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp

HERE = Path(__file__).resolve().parent


def get_dense():
    return np.load(HERE / "matrix_A.npy")


def get_sparse():
    return sp.load_npz(HERE / "matrix_B.npz")


def get_operator():
    sys.path.insert(0, str(HERE))
    from heat_operator import HeatStepOperator
    return HeatStepOperator(N=40, dt=0.01)


if __name__ == "__main__":
    A = get_dense()
    B = get_sparse()
    M = get_operator()
    print(f"dense   : {A.shape} {A.dtype}")
    print(f"sparse  : {B.shape} {type(B).__name__}, nnz {B.nnz}")
    print(f"operator: {M.shape} matrix-free (apply only)")
