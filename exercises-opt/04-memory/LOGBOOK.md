# LOGBOOK — ADMM-Filter project

Distilled from `plans/`. Each entry cites the plan file it came from.

## Decisions

- **ω for the non-smooth `α·TV(y)` term uses a proximal-gradient residual** 
  The projected-gradient `ω_ρ` is undefined on the non-smooth y-block, so the y-gradient 
  is a prox step reusing the existing Chambolle-Pock y-subproblem. (`2026-05-08-filter.md`)
- **`project_box_budget` is a dedicated ~30-line function**, not a call into
  `reciprocal_approx.solve_subproblem` (`2026-05-08-filter.md`)
- **`Filter.add` skips entries with `η == 0`**  (`2026-05-08-filter.md`)
- **Three restoration triggers:** eq.(8) `η ≥ β·U`, eq.(9) `ω ≤ ε ∧ η ≥ β·η_min`,
  and `j+1 == MaxInner` (`2026-05-11-filter.md`, `2026-05-18-filterWalkthrough.md`)
- **Sufficient-decrease failure is logged only — never retried.**
  (`2026-05-11-filter.md`)
- **On MaxRestoration hit: exit with `converged=False`, `reason="restoration_failed"`;
  do not raise.** (`2026-05-11-filter.md`)
- **Plotting gated by a single `plot=True` toggle**, two private helpers
  (`_save_iter_heatmap`, `_save_convergence_plot`); matplotlib imported lazily
  inside the `if plot:` guard; output dir `images/` is hard-coded;
  `plot=True` is the default in `__main__`. (`2026-05-11-filterPlot.md`)
- **CLI via `argparse` with seven flags** (`nelx, nely, volfrac, penal, alpha,
  plot, verbose`) (`2026-05-14-filterInput.md`)
- **Walkthrough notebook is script-generated** (`generate_filter_notebook.py` →
  `filter_walkthrough.ipynb`, 18 cells) (`2026-05-18-filterWalkthrough.md`)
- **`compute_omega` now returns `(float, int)`** exposing its internal CP iteration
  count; `FilterADMM.py` accumulates iteration counts/times. (`2026-06-03-iterCount.md`)
- **Movie option mirrors the plot toggle** (off by default, one `movie` flag /
  `--movie`).  (`2026-06-03-movie.md`)
- **2026-06-24 — Session: bootstrapped project memory & guidance.** Read all
  seven `plans/` files and synthesized this `LOGBOOK.md` (Decisions / Parameters /
  Dead Ends / Open Questions, each entry citing its plan); the user then trimmed
  it. Also created `CLAUDE.md` from a codebase analysis — captures the run-from-
  `src/` rule, the "one module = one `__main__` self-test" testing model, the
  three-layer architecture (solvers → filter primitives → drivers), the
  `a_v=ρ/2, b_v=-ρ·target` subproblem contract shared by both drivers, the
  column-major `ely + elx*nely` indexing, and the `n_iter` off-by-one. (this session)

## Parameters

- **Filter defaults:** `beta=0.99`, `gamma=1e-5`. (`2026-05-08-filter.md`,
  `2026-05-11-filter.md`)
- **`project_box_budget`:** `x_lo=0.0`, `x_hi=1.0`, `lam_tol=1e-12`.
  (`2026-05-08-filter.md`)
- **`compute_omega`:** `tau=1.0`, `cp_tol=1e-8`, `cp_max_iter=2000`.
  (`2026-05-08-filter.md`)
- **`filter_admm_compliance_tv` defaults:** `rho_init=1.0`, `beta=0.99`,
  `gamma=1e-5`, `sigma=1e-5`, `U=10.0`, `max_outer=100`, `max_inner=20`,
  `max_restoration=30`, `eps_opt=1e-3`, `omega_tau=1.0`, `x_lo=1e-4`,
  `max_iter_x=100`, `max_iter_y=2000`. (`2026-05-11-filter.md`)
- **`__main__` self-test overrides:** `max_outer=60`, `eps_opt=1e-2`.
  (`2026-05-14-filterInput.md`)
- **Canonical self-test problem:** `nelx=30, nely=10, penal=3.0, alpha=0.5,
  volfrac=0.4 → budget=120.0`. (`2026-05-11-filter.md`, `2026-05-14-filterInput.md`)
- **CLI defaults:** `nelx=30, nely=10, volfrac=0.4, penal=3.0, alpha=0.5,
  plot=True, verbose=True`. (`2026-05-14-filterInput.md`)
- **Movie:** `fps=2`. (`2026-06-03-movie.md`)
- **Headline results (30×10 default):** FilterADMM converges in **14** after the ω̃₀ correction; 
  (`2026-05-11-filter.md`, `2026-05-18-filterWalkthrough.md`, `2026-06-03-iterCount.md`)

## Dead Ends

- **`U = eta_0 / beta` as the restoration-trigger default** — fails because
  `eta_0 = 0` for the uniform initial design, making `trig_8` fire on every step.
  Replaced with `U = 10.0`. (`2026-05-11-filter.md`)
- **Testing filter acceptance at the top of the inner `j`-loop** — with an empty
  initial filter (`eta_0 = 0` ⇒ no add) the algorithm never makes progress. 
  Moved the test to the bottom of the loop. (`2026-05-11-filter.md`)
- **Reusing `solve_subproblem` for the box+budget projection** — would force a
  degenerate cubic (`c=0`) and an unnecessary `_solve_cubics` Newton loop.
  (`2026-05-08-filter.md`)
- **`flt.entries` / `flt._entries` in the notebook** — private, not part of the
  `Filter` contract; use `__iter__` (`for e, w in flt:` / `list(flt)`).
  (`2026-05-18-filterWalkthrough.md`)
- **`np.arange(1, info["n_iter"]+1)` for plot x-axes in FilterADMM** — off-by-one
  vs the history arrays (the top-of-loop convergence `break` runs before the
  history append), causing `semilogy` length-mismatch crashes. Use
  `len(info["eta_history"])`. Baseline `admm.py` is *not* affected (its appends
  precede the break). (`2026-05-18-filterWalkthrough.md`)

## Open Questions

- **`τ = 1` in `compute_omega`** follows the meeting-notes equation literally, but
  the resulting ω magnitude is problem-scale dependent. If `β, γ` prove hard to
  tune, revisit τ (e.g. `1/ρ` or `1/(ρ + L_F)`). (`2026-05-08-filter.md`)
- **Tuning the filter constants `(β, γ, σ, U)`** beyond the defaults; a 
  parameter-sweep was deferred. (`2026-05-11-filter.md`)
- **`compute_omega` / prox-grad cost** (~6.5 s, 128k CP iters on 30×10) may
  dominate on larger meshes — warrants measurement before optimising.
  (`2026-05-11-filter.md`, `2026-06-03-iterCount.md`)
- **Behaviour at scale** — confirm the filter+restoration logic fixes the
  oscillation on 60×20 and 120×40 meshes (where `admm.py` oscillates more).
  (`2026-05-11-filter.md`)
- **Whether `RASC-MeetingNotes.tex` needs updating** to document the third
  restoration trigger (`j == MaxInner`) added in code. (`2026-05-11-filter.md`)
- **2026-06-24 — Recommended next experiment (not yet run):** run FilterADMM on
  120×40 (README says it *fails*) with `compute_omega` timing/iteration counts
  captured, then sweep `omega_tau` (e.g. `1/ρ`) if it stalls. Tests the central
  "fixes oscillation at scale" claim while exercising the prox-grad-cost and
  `τ=1` open questions at once. (this session)
