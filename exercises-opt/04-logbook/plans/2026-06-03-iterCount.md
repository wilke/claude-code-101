# Plan: Iteration Counters and CPU Timing for FilterADMM Subproblems

## Context

`FilterADMM.py` runs three types of inner solves per outer iteration — the x-update
(reciprocal approximation), the y-update (Chambolle-Pock), and the proximal-gradient
residual inside `compute_omega` (also Chambolle-Pock). Both subproblem solvers already
return iteration counts in their info dicts, but `FilterADMM.py` discarded them (`_`).
`compute_omega` returned only a float and did not expose the CP iteration count from its
internal prox solve. This plan accumulates iteration counts and CPU times across all solves
and prints them in the end-of-solve summary.

## Files modified

1. `optimality.py` — `compute_omega` returns `(float, int)` instead of `float`
2. `FilterADMM.py` — accumulate counts/times; update call sites; extend `info` dict and print block

---

## Changes made

### `optimality.py`

- Internal CP call: `y_step, _ = chambolle_pock_graph_tv(...)` → `y_step, cp_info = chambolle_pock_graph_tv(...)`
- Return: `return float(r_x @ r_x + r_y @ r_y)` → `return float(...), cp_info["n_iter"]`
- Docstring Returns section updated: added `n_cp_iters : int` line.
- Three call sites in `__main__` self-test updated to unpack the tuple:
  - `omega0 = compute_omega(...)` → `omega0, _ = compute_omega(...)`
  - Two list/append sites use `[0]` indexing: `compute_omega(...)[0]`

### `FilterADMM.py`

- `import time` added at top.
- `_t_algo_start = time.perf_counter()` placed before `n = nelx * nely` (covers FEM setup too).
- Six accumulators initialized after `rho = float(rho_init)`, before the first `compute_omega`
  call (so they are in scope for all four call sites):
  ```python
  total_iter_x, total_iter_y, total_iter_prox = 0, 0, 0
  total_time_x, total_time_y, total_time_prox = 0.0, 0.0, 0.0
  ```
- **x-update call site**: `x_jp1, _ = reciprocal_approximation(...)` → captures `_x_info`;
  accumulates `total_iter_x` and `total_time_x`.
- **y-update call site**: `y_jp1, _ = chambolle_pock_graph_tv(...)` → captures `_y_info`;
  accumulates `total_iter_y` and `total_time_y`.
- **Four `compute_omega` call sites** (initialization, post-inner-step, restoration
  backtracking, post-multiplier-update): each unpacks `(omega_var, _n_cp)` and accumulates
  `total_iter_prox` and `total_time_prox`.
- `_total_time_algo = time.perf_counter() - _t_algo_start` computed before `return`.
- Seven new keys added to `info` dict: `total_iter_x`, `total_iter_y`, `total_iter_prox`,
  `total_time_x`, `total_time_y`, `total_time_prox`, `total_time`.
- Print block added at end of `__main__`:
  ```
  Subproblem statistics:
    x-update  (reciprocal approx) :    1132 iters   18.659 s
    y-update  (Chambolle-Pock)    :   32000 iters   1.559 s
    prox-grad (CP inside omega)   :  128001 iters   6.277 s
    Total algorithm time          :           26.605 s
  ```

---

## Verification result (30×10 default, system python3)

```
Subproblem statistics:
  x-update  (reciprocal approx) :    1132 iters   18.831 s
  y-update  (Chambolle-Pock)    :   32000 iters   1.605 s
  prox-grad (CP inside omega)   :  128001 iters   6.510 s
  Total algorithm time          :           27.056 s
```

Both self-tests pass:
- `python3 optimality.py` — all tests passed; ω drops 2000× over 30 ADMM iterations
- `python3 FilterADMM.py --no-plot --no-verbose-inner` — 14 outer iters, 331.4543 objective,
  3 restorations; byte-identical scientific result

`python3 admm.py` — 30 iters (not converged), objective 334.4672, iter-27→28 oscillation
confirmed; algorithm unchanged.

## Key observations from timing

- **x-update dominates** (~19 s): each reciprocal-approximation outer iteration calls
  `fem(x)` (an FEM solve) and runs Newton on 300 element cubics; on 30×10 this is 1,132
  total iterations spread over ~13 inner ADMM steps.
- **y-update is fast** (~1.6 s for 32,000 CP iters): Chambolle-Pock is cheap per iteration
  (pure vector arithmetic, no FEM).
- **prox-grad (`compute_omega`) is surprisingly expensive** (~6.5 s, 128,001 CP iters):
  called not only once per inner step but also at each restoration backtracking step (m-loop)
  and at initialization + post-multiplier-update. Restoration alone can trigger many calls.
