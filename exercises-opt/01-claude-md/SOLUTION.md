# Solution — Exercise 01 (CLAUDE.md via /init, largest small polygon)

## What this exercise is doing

`max_conopt.py` solves a geometric NLP in polar coordinates: `u` is the
radial coordinate and `v` is the angular coordinate of each free vertex.
The documentation in `max_conopt.md` never says this. The exercise asks
Claude to add a polygon solution plot and a convergence plot twice — once
reading only the sparse docs, and once after `/init` has read the source
code and generated a CLAUDE.md.

The point: `/init` reads actual variable names and formulas, not just prose.
Two formulas in the code are sufficient for Claude to deduce the coordinate
system — the polar shoelace area formula and the law-of-cosines distance.

## Where Claude usually goes wrong without /init

**Failure mode 1 — treats u and v as Cartesian coordinates.**
Plots `ax.plot(u, v)` where `v` ranges up to `π ≈ 3.14`. The dead giveaway
is a y-axis that reaches values above 3. The actual polygon vertices all live
in the upper half of the unit disk, so both `x` and `y` should be in `[−1, 1]`.

**Failure mode 2 — wrong fixed last vertex.**
`max_conopt.py` appends `0.0` to `u` and `π` to `v` in several places, but
without `/init` Claude does not know that this corresponds to the Cartesian
origin `(0, 0)`. It may omit the last vertex entirely, or place it at `(0, π)`.

**Failure mode 3 — open polygon.**
Connects vertices `0` through `nv−1` without wrapping back to vertex `0`.
The polygon is visually open on one side.

**Failure mode 4 — full circle as reference.**
Draws a circle of radius 1 as the feasible boundary. The correct reference
is a unit semicircle (`0 ≤ θ ≤ π`) because all vertex angles are in that
range — the polygon always lives in the upper half-plane.

## A worked CLAUDE.md

This is what `/init` should generate after reading `max_conopt.py`.
Every claim here can be traced to a specific line in the source.

```markdown
# Project: Largest Small Polygon (COPS Problem 1)

## Goal
Find the nv-sided polygon of maximum area with diameter <= 1.
Multistart NLP with unopy (filtersqp preset). Problem has many local minima.

## Variables (polar coordinates)
z = [u, v], flat array of length 2*(nv-1):
- u = z[:nv-1]: radial coordinates, bounded in [0, 1]
- v = z[nv-1:]: angular coordinates, bounded in [0, pi]
- Last vertex is fixed: u[nv-1] = 0.0, v[nv-1] = pi (the Cartesian origin)

## Cartesian conversion (required for plotting)
    x = u * np.cos(v)
    y = u * np.sin(v)
Polygon lives in the upper half-disk (y >= 0) because all angles are in [0, pi].

## Commands
- python3 max_conopt.py                          # nv=8, 10 restarts
- python3 max_conopt.py --nv 12 --nstarts 30    # multistart staircase demo
- python3 max_conopt.py --plot                   # solve and write figures/

## Conventions
- Figures saved to figures/ as PDF, 4 inches wide.
- Polygon plot: closed polygon (last vertex back to first), equal aspect ratio,
  unit semicircle reference (r=1, theta in [0, pi]).
- Convergence plot: best area vs restart index, linear y-axis.

## Don'ts
- No plt.show(); always save to figures/.
- Don't pip install new packages without asking.
```

## What Claude should produce after reading the generated CLAUDE.md

A response worth accepting without rewriting will have these properties.

**Correct polygon plot:**

```python
def plot_polygon(u, v, nv, area, out=Path("figures/polygon.pdf")):
    out.parent.mkdir(exist_ok=True)
    x = u * np.cos(v)
    y = u * np.sin(v)
    x_cl = np.append(x, x[0])   # closed
    y_cl = np.append(y, y[0])

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.fill(x, y, alpha=0.15, color="steelblue")
    ax.plot(x_cl, y_cl, "b-o", ms=4)

    theta_ref = np.linspace(0, np.pi, 300)
    ax.plot(np.cos(theta_ref), np.sin(theta_ref), "k--", lw=0.7)
    ax.plot([-1, 1], [0, 0], "k--", lw=0.7)

    ax.set_aspect("equal")
    ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.set_title(f"Optimal {nv}-gon  (area = {area:.4f})")
    fig.tight_layout()
    fig.savefig(out)
    print(f"wrote {out}")
```

Key signals of correctness:
- `x = u * np.cos(v)` — knows the polar-to-Cartesian conversion
- `np.append(x, x[0])` — closes the polygon
- Unit semicircle reference drawn
- `set_aspect("equal")` — geometry is not distorted

**Correct convergence plot:**

```python
def plot_convergence(history, nv, out=Path("figures/convergence.pdf")):
    out.parent.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(4, 2.6))
    ax.plot(np.arange(1, len(history) + 1), history, "b-o", ms=4)
    ax.set_xlabel("restart")
    ax.set_ylabel("best area")
    ax.set_title(f"Multistart convergence  (nv = {nv})")
    fig.tight_layout()
    fig.savefig(out)
    print(f"wrote {out}")
```

Linear y-axis is correct here — best area values are all near 0.727 for nv=8,
so a log scale would compress meaningful variation. The "staircase" shape
(flat segments interrupted by jumps) is visible for nv=12 with 30 restarts.

**argparse addition:**

```python
ap.add_argument("--plot", action="store_true")
```

And in `main()`, after `multistart(...)`:

```python
if args.plot:
    from pathlib import Path
    import matplotlib.pyplot as plt
    plot_polygon(u, v, args.nv, best_area)
    plot_convergence(history, args.nv)
```

## What you'd expect to see

```
$ python3 max_conopt.py --nv 8 --nstarts 10 --seed 0 --plot
restart   1/10: obj=0.726868 (new best)
restart   2/10: obj=0.726868
...
restart  10/10: obj=0.726868

Best area: 0.726868
u: [0.4663 0.8182 1.     1.     0.8774 0.7557 0.4264 0.    ]
v: [0.855  1.3555 1.7852 1.9095 2.4413 2.7306 3.1412 3.1416]
wrote figures/polygon.pdf
wrote figures/convergence.pdf
```

`polygon.pdf` shows an irregular octagon in the upper half-plane, inscribed
in the unit semicircle. `convergence.pdf` is flat for nv=8 (single dominant
basin). Run with `--nv 12 --nstarts 30` to see a clear staircase: restarts
discover area values around 0.750, then 0.755, then 0.761.

## The three formulas /init reads

When `/init` analyzes `max_conopt.py`, it sees:

1. **Area formula** (in `neg_area`):
   `ui1 * ui * np.sin(vi1 - vi)` — this is the polar shoelace formula. A
   product of two radii times the sine of the angle between them is the area
   of a triangle in polar coordinates. Claude deduces: `u` = radii, `v` = angles.

2. **Distance formula** (in `con`):
   `uf[i]**2 + uf[j]**2 - 2*uf[i]*uf[j]*np.cos(vf[j]-vf[i])` — this is
   the law of cosines, giving the squared Euclidean distance between two
   points in polar coordinates. Confirms: `u` = radial, `v` = angular.

3. **Bounds** (in `solve_one`):
   `np.full(n, np.pi)` as the upper bound for `v` — angles are in `[0, π]`,
   placing all vertices in the upper half-plane.

## The loop

The three phases mirror the other tracks: ask cold (Phase 1) → let `/init` read
the code and draft a CLAUDE.md (Phase 2) → add what `/init` couldn't infer, then
iterate (Phase 3). `/init` bootstraps the CLAUDE.md from the code, so the first
attempt is much closer; the remaining manual additions in Phase 3 are typically:

1. Add the `figures/` convention (Claude may save to the working directory).
2. Specify linear y-axis for convergence (Claude may default to log scale).
3. Specify equal aspect ratio for the polygon plot.
