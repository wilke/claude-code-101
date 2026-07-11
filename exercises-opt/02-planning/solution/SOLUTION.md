# Solution — Cardinality-constrained portfolio with `unopy`

This is the worked solution to Exercise 02. The point of the exercise is the
*plan* (`plan.md`); this file documents the implementation that was built from
that plan, how to run it, and where it deliberately departed from the literal
prompt.

## Files

| File | Role |
|------|------|
| `nlp_seed.py` | Problem data (given): `mu`, `Sigma`, `n=50`, `K=8`. Unmodified. |
| `portfolio_model.py` | The `unopy` formulation: `build_model(Σ, μ, τ, K, x0)` + analytic objective / Jacobian / Lagrangian Hessian, PSD-validating data loader, metric helpers. |
| `solve.py` | `solve_once(...)` (one UNO solve) and `check_derivatives(...)` (finite-difference validation). Runnable standalone. |
| `benchmark.py` | τ-sweep + multistart → two CSVs. |
| `plot_pareto.py` | Reads the summary CSV → `pareto.png`. |

## Environment

`unopy` (UNO 2.7.4) runs in the exercise environment (the `optimization` conda
env from Exercise 01, or your pip venv). Activate it first, then use `python3`:

```bash
conda activate optimization        # or: source .venv/bin/activate
```

## How to run

```bash
# 1. Validate derivatives + one solve (fast sanity check)
python3 solve.py

# 2. Run the Pareto sweep -> bench_runs.csv + bench_summary.csv
python3 benchmark.py                       # full default grid (25 τ, 5 starts)
python3 benchmark.py --tau-grid "0,0.5,5" --n-starts 2   # quick smoke test

# 3. Plot the trade-off -> pareto.png
python3 plot_pareto.py
```

### Run-time parameters (`benchmark.py`)

| Flag | Default | Meaning |
|------|---------|---------|
| `--n-starts` | `5` | random restarts per τ (multistart; see below) |
| `--tau-grid` | *(log grid)* | comma-separated τ list, e.g. `"0,0.5,5"`; omit for the default 25-point grid |
| `--K` | `8` (from `nlp_seed.py`) | cardinality bound |
| `--preset` | `filtersqp` | UNO preset (`filtersqp` / `ipopt` / `filterslp`) |
| `--seed` | `0` | base RNG seed (restarts are reproducible) |
| `--runs-csv` | `bench_runs.csv` | per-`(τ, start)` output |
| `--summary-csv` | `bench_summary.csv` | per-τ output (consumed by the plot) |

`plot_pareto.py` takes `--summary-csv` (default `bench_summary.csv`) and `--out`
(default `pareto.png`).

### What a full default run produces

- `bench_runs.csv` — **149 rows**. The smallest τ has no warm start (5 random
  starts); each of the other 24 τ adds one *continuation* start, so
  `5 + 24×6 = 149`.
- `bench_summary.csv` — **25 rows**, one per τ, holding the best feasible solve
  plus `hit_fraction`.
- `pareto.png` — the efficient frontier (left) and the multistart hit-fraction
  diagnostic (right).

Observed frontier (seed 0): risk `wᵀΣw` rises `0.0064 → 0.112`, the return
objective `−μᵀw` improves `−0.071 → −0.160`, and the number of selected assets
shrinks `8 → 3` as τ grows — a textbook Markowitz bullet.

## How the τ grid was chosen (why the CSV is not equidistant)

τ is the scalarization weight in the objective

$$ f(w) = \underbrace{w^\top\Sigma w}_{\text{risk}} - \tau\,\mu^\top w
       = \text{risk} + \tau\cdot(\underbrace{-\mu^\top w}_{\text{return obj.}}). $$

Sweeping τ from 0 to ∞ traces the whole Pareto front: τ = 0 is pure
**minimum-variance**, τ → ∞ is pure **maximum-return**.

The front is sharply curved — the "knee" of the bullet. Almost all of the
interesting movement happens for small τ, while large τ produces diminishing
change (the return objective flattens out near −0.16). **Equidistant (linear)
τ spacing would oversample the flat high-return tail and undersample the knee.**

So the default grid is **geometric (log) spacing**, defined in
`benchmark.py:default_tau_grid`:

```python
np.concatenate([[0.0], np.logspace(-2, 1.5, 24)])
```

- `np.logspace(-2, 1.5, 24)` = 24 points **equally spaced in log₁₀** from
  $10^{-2}=0.01$ to $10^{1.5}\approx 31.62$. Consecutive values differ by a
  constant *ratio* $10^{3.5/23}\approx 1.42\times$, not a constant difference —
  hence the non-equidistant τ column in the CSV.
- The explicit `0.0` is prepended because log spacing can never reach the exact
  min-variance endpoint (τ = 0). It is the one point not on the geometric ladder.
- The grid is sorted ascending so the **continuation warm-start** (each τ seeded
  from the previous τ's best solution) walks a connected branch of the front.

Pass `--tau-grid` to override with any explicit list.

## How the implementation differs from the original prompt

The prompt was implemented faithfully, with four deliberate, documented choices —
the kind the planning step exists to surface:

1. **Risk metric corrected.** The prompt listed the CSV risk objective as
   `μᵀw`, but its own plot instruction defines risk as `wᵀΣw`. Treated as a
   typo (confirmed with the user): **risk = `wᵀΣw`**, **return = `−μᵀw`**, and
   the raw `μᵀw` is logged too so nothing is lost.

2. **"Optimality gap" reinterpreted.** UNO is a *local* NLP solver and this
   model is **nonconvex** (the complementarity constraint `wᵀ(1−z) ≤ 0` is
   bilinear), so there is no certified global gap. The harness instead records,
   per the user's choice:
   - UNO's native **KKT residuals** (`kkt_stationarity/feasibility/complementarity`);
   - a **multistart gap-to-best** `gap_to_best = (f − f_best)/(|f_best|+ε)`,
     gap to the best objective *found across starts* — not a global certificate;
   - **`hit_fraction`** — the fraction of starts that reach `f_best`, a basin /
     difficulty measure. (It hovers near 0.17, i.e. only ~1 in 6 starts finds
     the best local optimum — concrete evidence of the nonconvexity, and the
     reason multistart is needed rather than a single solve.)

3. **Continuous relaxation of the MINLP.** UNO solves continuous NLPs, so `z` is
   relaxed to `[0,1]` and cardinality is enforced softly via the complementarity
   constraint. Selected assets are read off as `wᵢ > 1e-5`. (`|selected|` can
   slightly differ from K; a stretch goal is to round `z` to the top-K and
   re-solve `w`.)

4. **Two CSVs instead of one.** The prompt said "to a CSV"; the harness writes a
   detailed per-`(τ, start)` `bench_runs.csv` (gap, KKT residuals, timing,
   assets) and a per-τ `bench_summary.csv` (best solve + `hit_fraction`) that
   drives the plot.

Additions beyond the prompt that make the result trustworthy:

- **Analytic derivatives** (gradient, sparse Jacobian, lower-triangle Lagrangian
  Hessian) under UNO's `MULTIPLIER_NEGATIVE` convention.
- **`check_derivatives()`** — a finite-difference check (max error ~1e-8) that
  in particular validates the Hessian sign convention before any sweep is trusted.
- **PSD validation** of `Σ` (symmetrize, assert `min eig > 0`) at load time.
