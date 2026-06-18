# 2026-04-29 — Tikhonov regularization on the inverse Poisson is a dead end

Tried adding Tikhonov regularization to the KKT matrix instead of inertia
correction on the inverse Poisson problem. Idea: avoid the indefinite-block
detection and just keep the system positive definite.

- The iterates converge in primal residual.
- The multipliers are noise — not even the right order of magnitude.
- KKT residual on the dual block stays at 1e-2 even with `tol=1e-10`.

Spent two days on this. Concluding it does not work in our setup. The reason:
the dual block is fundamentally indefinite for an inverse problem of this
shape; making it PD by force shifts the saddle point.

**Decision:** abandon Tikhonov-regularized KKT for the inverse Poisson family.
Stay with inertia correction. Document this so I don't repeat it in six months.

**Open question:** does the Vermeersch–Anitescu 2019 saddle-point smoothing
work better here? Skim before committing time.
