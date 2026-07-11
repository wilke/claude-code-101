# Plan: Add plotting option to `FilterADMM.py`

_Executed 2026-05-11. Result: `FilterADMM.py` now accepts `plot=True`, which
writes `images/convergence.pdf` and `images/iter_NNNN.pdf` for each accepted
outer iterate. The `__main__` self-test ships with `plot=True`. See
"Post-implementation notes" at the bottom for the small divergences from this
plan as written._

## Context

`FilterADMM.py` currently produces only console output — a per-iteration trajectory line and a summary block. Diagnosing convergence behaviour, comparing runs, and presenting results to collaborators is much easier with figures than with grep on stdout.

The user wants two kinds of plot, gated by a single boolean toggle:

1. **Convergence history** of `η` and `ω` over outer iterations `k` — single PDF, log-scale y, dual y-axes (left = η, right = ω).
2. **Per-iteration design state** — one PDF per outer iteration, containing 2D heat maps of `x`, `y`, and `λ`.

All output saved under `images/` (which already exists in the project, currently empty).

## File to modify

**`FilterADMM.py`** only. No new files. `requirements.txt` already lists `matplotlib`.

## API addition

One new keyword argument added to `filter_admm_compliance_tv`:

```python
def filter_admm_compliance_tv(
    ...,
    plot=False,          # NEW: when True, save convergence + per-iter heatmap PDFs to images/
    ...,
):
```

`plot=False` is the default so existing behaviour is unchanged. When `plot=True`:

- `import matplotlib.pyplot as plt` and `import matplotlib.colors as mcolors` are deferred to inside the `if plot:` guard at the start of the function (matplotlib stays an optional runtime dependency for users who don't plot).
- `os.makedirs("images", exist_ok=True)` is called once at the start (defensive — `images/` already exists but this protects users who delete it).

## Where the plotting hooks fire

Inside the existing outer loop in `filter_admm_compliance_tv`, the per-iteration heat-map save fires **after** the verbose print and after the existing `outer_callback` invocation, i.e. once `(x, y, lam)` are the finalised accepted iterate for outer index `k` (post-multiplier-update). This matches the indexing used by the existing `eta_history` / `omega_history` arrays.

The convergence plot is saved **after the outer loop ends**, just before building the `info` dict. This means it captures whatever history is available even if the run exits early via `restoration_failed` or `max_outer`.

## Two helper functions (private, in `FilterADMM.py`)

### `_save_iter_heatmap(x, y, lam, k_one_based, nelx, nely, plt, mcolors)`

A 1×3 subplot figure (figsize ≈ `(13, 4)` per the `generate_notebook.py` convention).

- **`x` and `y` panels** — `cmap='gray_r'`, `vmin=0`, `vmax=1`, `origin='lower'`, `axis('off')`. Reshape via `data.reshape(nelx, nely).T` (column-major convention from `CLAUDE.md`).
- **`λ` panel** — diverging colormap `cmap='RdBu_r'` with `norm=mcolors.CenteredNorm()` so zero is white. Same reshape and `origin='lower'`.
- Each panel gets a title (`"x"`, `"y"`, `"λ"` plus `(iter k)`) and a shrunk colorbar (`shrink=0.85`).
- Saved to `images/iter_NNNN.pdf` with 4-digit zero-padding so files sort lexicographically.
- `plt.close(fig)` after each save (avoids memory leak across many iters).

### `_save_convergence_plot(eta_hist, omega_hist, plt)`

A single figure with `twinx`-style dual y-axes:

- x-axis: outer iteration `k = 1..n_iter` (1-based, matches the verbose `FilterADMM N` line).
- Left y-axis: `η = ‖x − y‖²`, log scale, blue colour.
- Right y-axis: `ω̃_ρ`, log scale, red colour.
- Both lines get markers + a combined legend (since twin axes don't auto-merge legends).
- Light grid (`which='both', alpha=0.3`) for log-scale readability.
- Saved to `images/convergence.pdf`. `plt.close(fig)` after.

## Reused conventions (from `generate_notebook.py`)

The existing notebook generator already establishes the project's plotting style:

- `cmap='gray_r'`, `vmin=0`, `vmax=1`, `origin='lower'` for densities.
- `cmap='RdBu_r'` with `mcolors.CenteredNorm()` for signed quantities (sensitivities) — directly reusable for `λ`.
- `axis('off')`, `figsize=(13, 4)`, `colorbar(..., shrink=0.85)`.
- `x.reshape(nelx, nely).T` for the column-major reshape.

The new helpers in `FilterADMM.py` mirror these choices so plots look consistent across the project.

## Verification

1. **Regression**: `python3 FilterADMM.py` (default `plot=False`) — output should be byte-for-byte identical to the current self-test.
2. **End-to-end**: temporarily set `plot=True` in the `__main__` block (or run from a Python REPL) on the 30×10 default. After the run, verify:
   - `images/convergence.pdf` exists, opens, shows two log-scale curves over k=1..26, with the η axis on the left and ω axis on the right.
   - `images/iter_0001.pdf` through `images/iter_0026.pdf` exist (26 files for the 26 outer iterations).
   - Spot-check `images/iter_0001.pdf` — `x` and `y` should be near-uniform grey (close to 0.4 = budget/n); `λ` should be near-zero (small magnitudes, near-white with `RdBu_r` + `CenteredNorm`).
   - Spot-check `images/iter_0026.pdf` — `x` and `y` should look like a settled cantilever density (mostly black=void, with material concentrated near the boundary conditions and load); `λ` should have visible mixed-sign structure.
3. **No matplotlib leak**: after the run, run `lsof | grep matplotlib` (or just trust `plt.close(fig)` after each save).
4. **Reproduction commands**:
   ```bash
   cd /home/leyffer/software/AIML/Claude/ADMM-MIP/admm_sl
   conda activate RASC
   python3 FilterADMM.py                       # default, no plots
   # then edit __main__ to set plot=True (or run from a REPL):
   python3 -c "from FilterADMM import filter_admm_compliance_tv; \
               filter_admm_compliance_tv(30, 10, 3.0, 0.5, 120.0, plot=True)"
   ls images/
   ```

## Out of scope

- **Configurable image directory** — the user's spec says "images/", so it's hard-coded.
- **Animation / GIF** of the iteration sequence — could be added later by stitching the per-iter PDFs but not requested.
- **Plotting `ρ` history or filter contents** — only η and ω are requested for the convergence plot.
- **Multi-page PDF** combining all per-iter snapshots — the user explicitly asked for "single pdf per iteration".
- **Updating documentation** (README, CLAUDE.md, `RASC-MeetingNotes.tex`) — not requested as part of this task; can be added in a follow-up if desired.

---

## Post-implementation notes (added 2026-05-11 after the run)

Two minor divergences from the plan as written above; the file as shipped in
`FilterADMM.py` reflects these.

1. **25 per-iter PDFs, not 26**, on the 30×10 default. Reason: the outer
   loop's convergence test (`if eta_k <= eps_opt and omega_k <= eps_opt:
   break`) sits at the **top** of the `for k in range(max_outer)` body,
   before any work is done. The 26th iteration just verifies convergence and
   exits — no ADMM step, no multiplier update, no plot save. So the 26
   reported by `info['n_iter']` is a "convergence-check ran" count, not a
   "work done" count, and `images/iter_0001.pdf` ... `images/iter_0025.pdf`
   matches the 25 entries in `eta_history`.

2. **`plot=True` is the default in `__main__`** (the verification step above
   suggested temporarily flipping it). The user opted to ship the self-test
   with plots on, so `python3 FilterADMM.py` produces both the trajectory
   print and the PDFs in one shot.

End-to-end verification on the 30×10 default produced one
`images/convergence.pdf` (twin log-axes, η blue / ω red, visible iter-19
spike, both ending at ~10⁻⁴ and ~10⁻³) and 25 `images/iter_NNNN.pdf` files.
Spot-checks: iter 1 shows an aggressive cantilever from the SIMP x-update
with a mostly-uniform y and a full-range (≈±0.7) λ; iter 25 shows nearly
identical x and y (η ≈ 1.6e-4) and a small-magnitude λ concentrated along
the structural members.
