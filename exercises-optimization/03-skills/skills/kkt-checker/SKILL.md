---
name: kkt-checker
origin: workshop
description: |
  Verify that a candidate primal-dual point (x, y, z) satisfies the KKT
  conditions for a QP or NLP of the form
      min f(x) s.t. A x = b, x >= 0
  Reports max residuals for stationarity, primal feasibility, dual
  feasibility, and complementarity. Use whenever a "candidate solution"
  is reported and you want to confirm it is a KKT point, or to inspect
  per-block residuals.
---

<!--
The `origin:` field is a small convention worth borrowing from the
`affaan-m/everything-claude-code` skill collection: tag skills you write
yourself versus skills you imported, so future-you knows what's safe to
modify. Use any short tag — `workshop`, `mygroup`, `community`, etc.
-->


# KKT checker skill

Use this skill when:

- The user reports a candidate solution `(x, y, z)` from any solver and wants verification.
- The user wants residuals broken down by KKT block (stationarity, feasibility, complementarity).
- The user asks "is this a KKT point?" for a problem of the supported form.

## How to invoke

```bash
python .claude/skills/kkt-checker/check_kkt.py \
    --problem problem.py \
    --solution solution.json \
    --tol 1e-8
```

The `--problem` argument should point to a Python file exposing a `get_qp()` function returning `(Q, c, A, b)`. The `--solution` argument should point to a JSON file with arrays `x`, `y`, `z`.

Output looks like:

```
Stationarity:  max |Qx + c - A^T y - z| = 1.23e-12
Primal feas:   max |A x - b|            = 0.00e+00
               min x_i                   = 1.33e-01
Dual feas:     min z_i                   = 0.00e+00
Complement:    max |x_i * z_i|           = 0.00e+00
==> KKT residual = 1.23e-12  (< tol = 1.00e-08): PASS
```

## Interpreting the output

- **Stationarity** failures usually indicate a wrong gradient or a missing multiplier block.
- **Primal feasibility** failures: the point is not on the feasible set. Check the equality constraint and bounds.
- **Dual feasibility** failures: a multiplier `z_i < 0`. Either the solver returned the wrong sign, or your problem is being interpreted as `x <= 0` instead of `x >= 0`.
- **Complementarity** failures: `x_i > tol` and `z_i > tol` simultaneously. Check whether the active set was identified correctly.

## Extending

To handle inequality constraints `g(x) <= 0`, add `g, jac_g` to the problem interface and a third multiplier block. Keep the four-residual layout — it is the cheapest way to localize what failed.
