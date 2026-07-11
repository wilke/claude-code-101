# 2026-03-18 — Unit-square Laplace: convergence study and figure conventions

Started from a bare `laplace_square.py` that solved `-Δu = f` on `(0,1)²`
against the manufactured solution `u_exact = sin(πx) sin(πy)` once on
`UnitSquareMesh(8, 8)` and printed essentially nothing useful. Spent the day
turning it into a real convergence harness with figure conventions the rest of
the group can re-use without rederiving them.

- **Convergence sweep.** Mesh sequence is `n ∈ (4, 8, 16, 32, 64)`. Output is a
  table with columns `n`, `dofs`, `L² error`, `L² rate`, `H¹ error`, `H¹ rate`,
  `max(u_h)`. Rates computed as `log2(err_prev / err_curr)` between consecutive
  rows.
- **Both norms, every time.** L² rate alone is the most-overfit number in this
  group's history — everyone remembers L² should be `O(h^(p+1))` and forgets
  H¹ should be `O(h^p)`. Reporting both kills the most common misreading at
  source.
- **`max(u_h)` column.** Cheap sanity check that the solver is doing anything
  at all. For `sin(πx) sin(πy)` it should climb toward 1.0 as the mesh refines.
  Caught a bug on the first run where I had a sign wrong in the forcing — the
  rates looked fine but `max(u_h)` was 0.42 and not moving.

**Decision:** convergence sweep is `n ∈ (4, 8, 16, 32, 64)` with the table
above. Both L² and H¹ rates are always reported. The `max(u_h)` column stays;
it has already earned its line.

**Decision:** element order is now configurable via `--order` (default 1). The
script prompts to confirm the order on first use of a new value and persists
the confirmation in `.element_order_confirmed`. The prompt is annoying once
and free forever after — the reason is a wasted afternoon last month when
someone ran a sweep at P3 thinking it was P1 and reported "anomalously fast
convergence" to the group. Never again.

- **Figures.** All figures go to `figures/` as PDF, 4 inches wide so they drop
  into a two-column layout without rescaling. Convergence plot uses log-log
  axes with `h` on x, axis inverted (finer to the right, matching how the
  table reads top-to-bottom). Dotted reference lines drawn at slope
  `O(h^(p+1))` for L² and `O(h^p)` for H¹.
- The dotted reference lines are the whole point. Without them the plot is
  two curves you can't read; with them, "parallel to the dotted line" means
  "right rate" at a glance, even for an audience that doesn't remember the
  expected exponents.
- **Never `plt.show()`.** Always save. We've had enough headless-cluster runs
  killed by a stray interactive figure that this is now a hard rule.

**Decision:** figure conventions above (PDF, 4 inches, log-log, dotted slope
references, save-don't-show) are the group default. Code is in
`exercises-pde/01-claude-md/laplace_square.py`; new convergence scripts should
copy from there.

**Parameters from a clean P1 run:** L² and H¹ rates both climb toward the
optimal values for P1 across the sweep, and `max(u_h)` climbs toward 1.0 from
below. These are the qualitative landmarks anyone else should reproduce when
they run the harness on a fresh checkout — if a rate column isn't climbing or
`max(u_h)` is stuck below ~0.9 at the coarsest level, something is off
before the sweep is even worth interpreting.

**Open question:** when do we *need* P2 vs P1 for production runs in this
group? Nothing in the current setup answers this. Probably a function of
target accuracy vs cost; would benefit from one careful P1-vs-P2
cost-per-error comparison on the catalog of problems we actually care about.
Not urgent, but it's the next question anyone asks after seeing the
convergence table.
