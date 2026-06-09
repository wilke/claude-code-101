---
name: wave-cfl-checker
origin: workshop
description: |
  Verify that a proposed timestep dt satisfies the element-wise CFL
  condition dt < 2/sqrt(lambda_max) for the second-order wave equation
  u_tt = div(c^2 grad u) on a Firedrake mesh, where lambda_max is the
  largest eigenvalue of the generalized eigenproblem K_e v = lambda M_e v
  on each cell (M_e: local consistent mass, K_e: local c^2-weighted
  stiffness). Reports per-element violations with offending cell indices,
  their lambda_max, and the local time-step bound.
---

<!--
The `origin:` field is a small convention worth borrowing from the
`affaan-m/everything-claude-code` skill collection: tag skills you write
yourself versus skills you imported, so future-you knows what's safe to
modify. Use any short tag - `workshop`, `mygroup`, `community`, etc.
-->


# wave-cfl-checker skill

Use this skill when:

- The user proposes a timestep `dt` for an explicit time-stepping scheme on a wave-equation script and wants to know whether it is stable.
- The user asks "what is the largest stable dt for this mesh?" for a problem in the supported form.
- The user wants to localize CFL violations to specific cells - for example to see which region of a heterogeneous mesh or a heterogeneous medium is forcing the tightest time step.

## How to invoke

The helper script needs Firedrake, which the workshop runs inside a Docker container (see `../01-claude-md/INSTALL.md` for the install). The skill therefore wraps the helper in the same `docker run` + bind-mount pattern the rest of the PDE track uses. Run from the exercise directory:

```bash
docker run --rm \
    -v "$PWD":/home/firedrake/work \
    -w /home/firedrake/work \
    firedrakeproject/firedrake:latest \
    python3 .claude/skills/wave-cfl-checker/check_cfl.py \
        --problem problem.py \
        --candidate candidate.json
```

The `--problem` argument should point to a Python file exposing a `get_problem()` function returning `(mesh, V, c2)`:

- `mesh` is a `firedrake.Mesh` of triangular cells.
- `V` is a `firedrake.FunctionSpace`. The helper currently hardcodes the per-element matrices for P2 CG on a triangle; pointing at a different element will need a code update.
- `c2` is a `firedrake.Function` on `("DG", 0)` giving `c^2` per cell.

The `--candidate` argument should point to a JSON file with at least the key `dt` (float).

## Output

A passing run prints a one-line summary plus the global safe-dt bound:

```
PASS: dt = 0.00200, safe = 0.00824 (min over 512 cells)
       limited by cell 384  (lambda_max = 5.89e+04,  dt_e = 8.24e-03)
       layer c^2 = 1.0  min dt_e = 1.65e-02
       layer c^2 = 4.0  min dt_e = 8.24e-03
```

A failing run prints the same summary line plus a sample of violating cells:

```
FAIL: dt = 0.05000, safe = 0.00824 (min over 512 cells)
       347 cells violate the bound; first 5 below
       cell    lambda_max   dt_e         c^2
       0       5.89e+04     8.24e-03     4.0
       1       5.89e+04     8.24e-03     4.0
       2       5.89e+04     8.24e-03     4.0
       ...
       layer c^2 = 1.0  min dt_e = 1.65e-02
       layer c^2 = 4.0  min dt_e = 8.24e-03
```

## Interpreting the output

- **All cells passing** - the proposed `dt` is below `2/sqrt(lambda_max)` on every element, so explicit time stepping is stable everywhere on this mesh.
- **Some cells failing** - time stepping with this `dt` will blow up locally. The failing cells tell you *where* in the mesh the CFL bound is tightest - usually the smallest cells, or the cells with the largest local wave speed.
- **The reported safe dt** is the global maximum stable timestep (= `min_e 2/sqrt(lambda_max(e))`). Use it directly as the upper bound, or multiply by a safety factor in the range 0.5 - 0.9 to give the scheme headroom against unmodelled effects (variable c, source terms, time-quadrature error).
- **Layer summary** - in a heterogeneous-medium problem (different `c^2` values), the per-layer minimum `dt_e` tells you which layer is the binding constraint. In a problem with uniform `c` but a graded mesh, all cells share one `c^2` and the layer summary will report a single row.

## Stretch ideas

- Add a `--safety` argument that prints the recommended `dt = safety * safe`, with a default in `[0.5, 0.9]`.
- Write a `firedrake.Function` on `("DG", 0)` holding `dt_e` per cell and save it to a Paraview file, so the learner can see the CFL bound spatially.
- Compare consistent-mass and mass-lumped variants (add `--mass lumped`); lumping typically increases `lambda_max` and tightens `dt`.
- Generalize the per-cell assembly so the skill works for arbitrary CG degree (currently P2-triangle is hardcoded in the helper).

If you extend the helper, also update the `description` line at the top of this file so future natural-language requests find the extension. Descriptions are how Claude routes prompts to skills - an extension that does not change the description is invisible to skill matching.
