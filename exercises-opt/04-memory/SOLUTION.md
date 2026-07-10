# Solution — Exercise 4 (LOGBOOK.md)

## What this exercise is doing

You have existing plan files in `plans/`. Each one is an actual plan created over the course of this project and captures the kind of thing you'd jot down at the end of a research day: what worked, what didn't, what the next question is. The exercise is to consolidate them into a structured `LOGBOOK.md` that Claude can read on every future session.

## A worked LOGBOOK.md

This is what Claude should produce when you ask it to read `plans/` and synthesize a memory file. Edit it down to the point where every line still earns its place.

```markdown
# MEMORY — ADMM-Filter project

Distilled from `plans/`. Each entry cites the plan file it came from.

## Decisions

- **ω for the non-smooth `α·TV(y)` term uses a proximal-gradient residual, not a
  subgradient.** The literal projected-gradient `ω_ρ` is undefined on the
  non-smooth y-block, so the y-residual is a prox step reusing the existing
  Chambolle-Pock y-subproblem. (`2026-05-08-filter.md`)
- **First pass shipped only the three primitives** (`filter.py`, `projection.py`,
  `optimality.py`), each self-tested in isolation; the outer driver was
  deferred so each piece could be validated alone. (`2026-05-08-filter.md`)
- **`project_box_budget` is a dedicated ~30-line function**, not a call into
  `reciprocal_approx.solve_subproblem` (which would force a degenerate cubic with
  `c=0` and an unnecessary Newton loop). (`2026-05-08-filter.md`)
- **`Filter.add` skips entries with `η == 0`** (per §2.5 footnote "ensures
  η_l > 0"); dominance pruning drops stored `(η_l, ω_l)` with `η_l ≥ η` AND
  `ω_l ≥ ω`. (`2026-05-08-filter.md`)
- **Outer driver lives in a new file `FilterADMM.py`**, sibling of `admm.py`,
  reusing all subproblem solvers with no edits. (`2026-05-11-filter.md`)
- **Three restoration triggers:** eq.(8) `η ≥ β·U`, eq.(9) `ω ≤ ε ∧ η ≥ β·η_min`,
  and `j+1 == MaxInner` (the third is a project-specific addition to the §3.5
  pseudocode). (`2026-05-11-filter.md`, `2026-05-18-filterWalkthrough.md`)
- **Sufficient-decrease failure is logged only — never retried.**
  (`2026-05-11-filter.md`)
- **On MaxRestoration hit: exit with `converged=False`, `reason="restoration_failed"`;
  do not raise.** (`2026-05-11-filter.md`)
- **Three departures from the §3.5 pseudocode (shipped):** (1) `U` default set to
  `10.0` not `eta_0/beta`; (2) inner-loop filter-acceptance test moved from top to
  bottom of the `j`-loop so ≥1 ADMM step always runs; (3) verification criterion
  softened to `reason == "converged"`. (`2026-05-11-filter.md`)
- **Plotting gated by a single `plot=True` toggle**, two private helpers
  (`_save_iter_heatmap`, `_save_convergence_plot`); matplotlib imported lazily
  inside the `if plot:` guard; output dir `images/` is hard-coded;
  `plot=True` is the default in `__main__`. (`2026-05-11-filterPlot.md`)
- **CLI via `argparse` with seven flags** (`nelx, nely, volfrac, penal, alpha,
  plot, verbose`); `budget` is derived (`volfrac×nelx×nely`), never exposed; only
  the `__main__` block was edited, not `filter_admm_compliance_tv`;
  `BooleanOptionalAction` gives `--plot/--no-plot` etc. (`2026-05-14-filterInput.md`)
- **Walkthrough notebook is script-generated** (`generate_filter_notebook.py` →
  `filter_walkthrough.ipynb`, 18 cells); the `.ipynb` is never hand-edited;
  plotting is inlined rather than importing the FilterADMM helpers.
  (`2026-05-18-filterWalkthrough.md`)
- **`compute_omega` now returns `(float, int)`** exposing its internal CP iteration
  count; `FilterADMM.py` accumulates iteration counts and CPU times across all
  solves and prints a subproblem-statistics block. (`2026-06-03-iterCount.md`)
- **Movie option mirrors the plot toggle** (off by default, one `movie` flag /
  `--movie`); uses `FuncAnimation` with a fixed symmetric λ `vmin/vmax` across
  frames; MP4 via `FFMpegWriter`, GIF via `PillowWriter` fallback.
  (`2026-06-03-movie.md`)

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
- **Headline results (30×10 default):** FilterADMM converged in **26** outer
  iters as first shipped, **14** after the ω̃₀ correction; objective ≈ **331.45**,
  `sum(x)=120`, 3 restorations (ρ: 1→2→4→8). Baseline `admm.py`: 30–40 iters,
  **not** converged, objective ≈ **334.47**, with the iter-27→28 oscillation
  (η 0.012→0.85, ω 0.005→0.12). (`2026-05-11-filter.md`,
  `2026-05-18-filterWalkthrough.md`, `2026-06-03-iterCount.md`)
- **Timing breakdown (30×10):** x-update ~19 s / 1,132 iters; y-update ~1.6 s /
  32,000 CP iters; prox-grad inside `compute_omega` ~6.5 s / 128,001 CP iters;
  total ~27 s. (`2026-06-03-iterCount.md`)

## Dead Ends

- **`U = eta_0 / beta` as the restoration-trigger default** — fails because
  `eta_0 = 0` for the uniform initial design, making `trig_8` fire on every step.
  Replaced with `U = 10.0`. (`2026-05-11-filter.md`)
- **Testing filter acceptance at the top of the inner `j`-loop** — with an empty
  initial filter (`eta_0 = 0` ⇒ no add) it short-circuits and the algorithm never
  makes progress. Moved the test to the bottom of the loop.
  (`2026-05-11-filter.md`)
- **"No η-jump of >10× between accepted iterates" verification rule** — too
  strict; the filter legitimately accepts grown-η iterates when the ω-branch
  fires. Demoted to a printed diagnostic. (`2026-05-11-filter.md`)
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
  tune, revisit τ (e.g. `1/ρ` or `1/(ρ + L_F)`). (`2026-05-08-filter.md`,
  `2026-05-11-filter.md`)
- **Tuning the filter constants `(β, γ, σ, U)`** beyond the conservative
  defaults — not yet done; a parameter-sweep notebook section was deferred until
  the constants are validated. (`2026-05-11-filter.md`,
  `2026-05-18-filterWalkthrough.md`)
- **`compute_omega` / prox-grad cost** (~6.5 s, 128k CP iters on 30×10) may
  dominate on larger meshes — warrants measurement before optimising.
  (`2026-05-11-filter.md`, `2026-06-03-iterCount.md`)
- **Behaviour at scale** — confirm the filter+restoration logic fixes the
  oscillation on 60×20 and 120×40 meshes (where `admm.py` oscillates more).
  (`2026-05-11-filter.md`)
- **Whether `RASC-MeetingNotes.tex` needs updating** to document the third
  restoration trigger (`j == MaxInner`) added in code. (`2026-05-11-filter.md`)
```

## What "next experiment" might look like

After this LOGBOOK.md exists and you created CLAUDE.md, ask:

```
given LOGBOOK.md and CLAUDE.md, what's the most informative next experiment to run?
Justify in two sentences.
```

A reasonable answer would be: *Run FilterADMM.py on the 120×40 mesh with compute_omega timing/iteration counts captured, then sweep omega_tau (e.g. 1/ρ) if it stalls.*

That's the kind of answer you can act on in an afternoon. Not because Claude is clever — because LOGBOOK.md gave it the context to be specific.

## Where the seam between CLAUDE.md and LOGBOOK.md sits

These two files are easy to confuse. A working rule:

- **CLAUDE.md** answers *"how does this project work?"* — stack, conventions, commands, do-not-do rules. It changes rarely.
- **LOGBOOK.md** answers *"what have we learned?"* — decisions with dates and reasons, parameter folklore, dead ends. It grows monotonically.

A test: if a fact would be true in any session of this project regardless of what you've discovered, it belongs in CLAUDE.md. If knowing it depends on having run experiments, it belongs in LOGBOOK.md.

## The two-minute end-of-session ritual

The single highest-leverage habit from this exercise is: at the end of every session, ask Claude to summarize what was decided and append it to LOGBOOK.md. Two minutes. Pays back in weeks.

```
summarize what we just did and append a dated entry to LOGBOOK.md under
Decisions or Open Questions, whichever fits.
```
