"""Seed data for the cardinality-constrained portfolio MINLP.

This file is intentionally minimal — the exercise is to *plan* a project
around it before writing the formulation.
"""
import numpy as np

rng = np.random.default_rng(0)

# 50 assets
n = 50

# Expected returns (annualized, decimals)
mu = rng.normal(loc=0.08, scale=0.05, size=n)

# Covariance matrix (synthetic, factor model + idiosyncratic noise)
F = rng.normal(size=(n, 3))
Sigma = F @ F.T + np.diag(rng.uniform(0.02, 0.08, size=n))

# Risk-aversion parameter and cardinality
tau = 0.5
K = 8


if __name__ == "__main__":
    eigs = np.linalg.eigvalsh(Sigma)
    print(f"n = {n}, K = {K}, tau = {tau}")
    print(f"min eig(Sigma) = {eigs.min():.4e}, max = {eigs.max():.4e}")
    print(f"mu range = [{mu.min():.3f}, {mu.max():.3f}]")
