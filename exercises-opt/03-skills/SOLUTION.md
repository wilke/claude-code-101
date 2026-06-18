# Solution — Exercise 3 (Skills, KKT checker)

## What this exercise is doing

The problem in `problem.py` is a small *quadratic program* (QP):

```
min  ½ xᵀ Q x + cᵀ x
s.t. A x = b
     x ≥ 0
```

with the data:

```
Q = [[4 1 0],     c = [-1 -1 -1]    A = [1 1 1]    b = [1]
     [1 2 0],
     [0 0 2]]
```

The KKT conditions say four things must hold at any candidate solution:

1. **Stationarity.** `Qx + c − Aᵀ y − z = 0`. The gradient of the objective lines up with the constraint gradients.
2. **Primal feasibility.** `Ax = b` and `x ≥ 0`. The point obeys the rules.
3. **Dual feasibility.** `z ≥ 0`. The bound multipliers have the right sign.
4. **Complementarity.** `xᵢ · zᵢ = 0` for every `i`. Either the bound is active and `zᵢ` can be nonzero, or the bound is inactive and `zᵢ` must be zero.

The skill in `skills/kkt-checker/` runs these four checks and prints residuals.

## The candidate solution

The shipped `solution.json` has the analytical optimum:

```
x = [2/15, 6/15, 7/15] ≈ [0.133, 0.400, 0.467]
y = [-1/15] ≈ [-0.067]
z = [0, 0, 0]
```

You can verify by hand: all components of `x` are strictly positive, so by complementarity all components of `z` must be zero. Then stationarity reduces to `Qx + c = Aᵀ y`, which gives `Qx + c = [-1/15, -1/15, -1/15]`, matching `Aᵀ y` exactly.

## What you'll see — passing run

Install the skill into `.claude/skills/` and run the checker:

```
$ python skills/kkt-checker/check_kkt.py \
    --problem problem.py --solution solution.json --tol 1e-8
Stationarity:  max |Qx + c - A^T y - z| = 1.388e-17
Primal feas:   max |A x - b|            = 0.000e+00
               min x_i                   = 1.333e-01
Dual feas:     min z_i                   = 0.000e+00
Complement:    max |x_i * z_i|           = 0.000e+00
==> KKT residual = 1.388e-17  (< tol = 1.00e-08): PASS
```

The stationarity residual is at machine precision (`1.4e-17`). Nothing else to do.

## What you'll see — failing run

Now corrupt one multiplier — set `z[0] = 0.5`:

```
$ python -c "
import json
d = json.load(open('solution.json'))
d['z'][0] = 0.5
json.dump(d, open('/tmp/bad.json', 'w'))
"
$ python skills/kkt-checker/check_kkt.py \
    --problem problem.py --solution /tmp/bad.json --tol 1e-8
Stationarity:  max |Qx + c - A^T y - z| = 5.000e-01
Primal feas:   max |A x - b|            = 0.000e+00
               min x_i                   = 1.333e-01
Dual feas:     min z_i                   = 0.000e+00
Complement:    max |x_i * z_i|           = 6.667e-02
==> KKT residual = 5.000e-01  (< tol = 1.00e-08): FAIL
```

Two things broke:

- **Stationarity** — adding 0.5 to `z[0]` shifted the gradient balance by 0.5.
- **Complementarity** — `x[0] = 0.133` and `z[0] = 0.5` are now both non-zero, so their product `0.0667 ≠ 0`.

That dual signal is exactly what makes KKT verification useful: when it fails, the *which residual* fails localizes the bug.

## What Claude is supposed to do

In a session with the skill installed, you ask:

```
verify the candidate solution in solution.json against the QP defined
in problem.py using the kkt-checker skill.
```

Claude should:

1. Notice the request matches the skill's `description` (which mentions "verify a candidate primal-dual point").
2. Load the SKILL.md, read the invocation example.
3. Run `python .claude/skills/kkt-checker/check_kkt.py --problem problem.py --solution solution.json --tol 1e-8`.
4. Report the residuals back, in plain English.

The point isn't that Claude couldn't have figured this out from scratch. The point is that the skill captures *your group's* convention for KKT checking: which tolerance, which output format, which residuals reported and in what order. Once captured, every session uses the same convention, including future students.

## Stretch — extending the skill

Asking Claude to add active-set reporting should produce a diff like:

```python
# Add to kkt_residuals():
active = (x < tol).nonzero()[0].tolist()
inactive_with_dual = ((x > tol) & (z > tol)).nonzero()[0].tolist()
return {..., "active_set": active, "strict_complementarity_violations": inactive_with_dual}
```

and a corresponding addition to the printout. The SKILL.md description should be updated to mention the new output, so future tasks that say "show me the active set" trigger it.

## Why this is a skill and not an MCP

KKT checking is **stateless logic that takes a problem and a candidate point and returns residuals**. There's no external system, no database, no long-running service. A skill is the right shape. Reach for an MCP only when you need to talk to something that lives outside Claude Code.
