# 2026-02-10 — Heat testbench: implicit stepping and a baseline preconditioner

Set up the time-stepping testbench the imaging work will build on: the 2D heat
equation u_t = Δu on the unit square, backward-Euler in time, 5-point finite
differences in space. Each step solves (I − dt·L) u^{n+1} = u^n. The step
operator is the one now living in
`exercises-lin_alg/02-planning/heat_operator.py`. The goal this session was just
to get long, many-step runs stable and instrumented before worrying about speed.

- **Time integrator.** Backward Euler, chosen for unconditional stability — we
  want large dt over long horizons with no CFL limit. The central-hot-spot test
  decays monotonically over 200 steps.
- **Per-step solve.** Conjugate gradients (the step matrix I − dt·L is SPD). A
  direct sparse factorization (splu) is fine at N=40, but it won't scale to the
  3D imaging meshes, so the plan is iterative from the start.
- **Baseline preconditioner.** Jacobi (diagonal) — trivial, cheap, a reference
  point. Nothing clever yet.

**Parameters from a clean run:** N=40 (1600 unknowns), dt=0.01, CG tol=1e-8.
With Jacobi, CG takes ~55 iterations per step, essentially flat across the
horizon (the operator doesn't change step to step).

**Decision:** backward Euler + CG is the fixed backbone of the testbench. The
per-step matrix is *constant in time* — the same operator is inverted every
step — which we should be able to exploit.

**Open question:** ~55 CG iterations/step × thousands of steps is the cost wall.
The operator is fixed but the right-hand side (the previous solution) evolves —
is there structure in the *sequence of solutions* we can precondition against?
