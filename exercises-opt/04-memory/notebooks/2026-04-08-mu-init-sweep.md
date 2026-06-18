# 2026-04-08 — mu_init sweep on the cohort

Swept `mu_init` over {1e-6, 1e-4, 1e-2, 1e0} on the seven-problem research
cohort. Report stored in `runs/2026-04-08T0930/summary.csv`.

| mu_init | mean iters | div. count | mean time (s) |
|---------|-----------:|-----------:|--------------:|
| 1e-6    | 89.4       | 0          | 14.2          |
| 1e-4    | 71.2       | 1          | 11.0          |
| 1e-2    | 52.3       | 0          | 7.8           |
| 1e0     | 64.1       | 2          | 9.4           |

The single divergence at 1e-4 was the **catalysis** problem. The two divergences
at 1e0 were **catalysis** and **tube-flow**. In both cases, the first centering
step blows up the iterate because the initial barrier is too weak.

**Decision:** default `mu_init = 1e-2`. Override to `1e-4` only if a problem
shows the catalysis-style instability.

**Aside:** filter parameters were defaults throughout. Should sweep those next.
