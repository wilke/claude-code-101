# 2026-03-12 — Solver choice for the catalysis benchmark

Spent the morning comparing IPOPT, SNOPT, and our prototype on the catalysis
problem (n=200, dense Hessian after substitution).

- **IPOPT** — converged in 47 iterations, max KKT residual 3e-9. License is EPL,
  fine for our group's use.
- **SNOPT** — converged in 31 iterations but final multipliers had sign errors
  on 4 of 17 active inequalities. Suspect interface bug; not chasing it now.
  Also: license is per-seat and our shared license is already saturated.
- **Our prototype** — converged in 62 iterations but stalled twice on inertia
  detection. Need to revisit threshold (see open question below).

**Decision:** default to IPOPT for production runs. Use the prototype for
research where we control the inertia logic. Do *not* call SNOPT from this
project — gradient/multiplier sign mismatch is a footgun.

**Open question:** is the inertia threshold problem-dependent? Defaults from
Wächter–Biegler 2006 work on HS071 but not here. Plan a sweep.
