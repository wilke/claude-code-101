"""
Generator for `filter_walkthrough.ipynb`.

Sibling to `generate_notebook.py` (which generates `admm_walkthrough.ipynb`
covering the baseline fixed-rho ADMM driver).  This script generates a parallel
notebook for `FilterADMM.py` -- the double-loop ADMM-Filter with adaptive rho,
defined in `RASC-MeetingNotes.tex` Sec. 4.

Re-run after edits:

    python3 generate_filter_notebook.py

The .ipynb is the output of `json.dump(...)` below -- do NOT edit it by hand.
"""

import json

# Cell-id counter and accumulator -- same pattern as generate_notebook.py.
_cid = [0]
cells = []


def _id():
    _cid[0] += 1
    return f"cell{_cid[0]:03d}"


def md(src):
    cells.append({"cell_type": "markdown", "id": _id(), "metadata": {}, "source": src})


def code(src):
    cells.append({"cell_type": "code", "id": _id(), "metadata": {},
                  "source": src, "outputs": [], "execution_count": None})


# ── Title ──────────────────────────────────────────────────────────────────
md("""\
# ADMM-Filter for Compliance Minimisation with TV Regularisation

This notebook walks through the **ADMM-Filter** algorithm (`FilterADMM.py`)
for the same compliance + graph-TV problem covered by `admm_walkthrough.ipynb`:

$$\\min_{\\substack{x \\in [\\epsilon,1]^n \\\\ \\mathbf{1}^\\top x \\leq B}}
  F(x) + \\alpha \\cdot \\mathrm{TV}(x)$$

The baseline fixed-$\\rho$ ADMM driver (`admm.py`) **oscillates** near
convergence on the 30x10 default problem and fails to reach the standard
tolerance in 30 iterations. ADMM-Filter fixes this by:

1. Tracking an **augmented-Lagrangian filter** of past $(\\eta, \\omega)$
   pairs and rejecting new iterates that are dominated by them.
2. Triggering a **restoration phase** when the new iterate is unacceptable,
   which backtracks $y$ toward $x$ and doubles $\\rho$.

The result on the 30x10 default: convergence in ~14 outer iterations, with
$\\rho$ stepping $1 \\to 2 \\to 4 \\to 8$.

> **See also.** `admm_walkthrough.ipynb` covers the x- and y-subproblem
> solvers (reciprocal approximation, Chambolle--Pock) in detail.  This
> notebook treats them as black boxes and focuses on the filter, the
> optimality measures, and the restoration phase that wraps them.

**Algorithm reference.** `RASC-MeetingNotes.tex` Sec. 3 (meeting algorithm),
Sec. 4 (as-implemented Algorithm 2 with the four documented departures and
the $\\widetilde{\\omega}_0$ correction).
""")


# ── Imports ────────────────────────────────────────────────────────────────
code("""\
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from compliance       import ComplianceProblem
from admm             import admm_compliance_tv, build_grid_edges
from FilterADMM       import filter_admm_compliance_tv
from filter           import Filter
from optimality       import compute_eta, compute_omega

%matplotlib inline
plt.rcParams.update({"figure.dpi": 110, "font.size": 11})
""")


# ── Parameters ─────────────────────────────────────────────────────────────
code("""\
# Problem: 30x10 cantilever at 40% volume.  Smaller than the 60x20 used in
# admm_walkthrough.ipynb so that both drivers run in ~10 seconds and so this
# matches the canonical 30x10 oscillation example documented in LOGBOOK.md.
nelx     = 30
nely     = 10
penal    = 3.0
volfrac  = 0.4
budget   = volfrac * nelx * nely     # 120.0
alpha    = 0.5
rho_init = 1.0
eps_opt  = 1e-2                       # both drivers terminate at this level
x_lo     = 1e-4
n        = nelx * nely
edges    = build_grid_edges(nelx, nely)
fem      = ComplianceProblem(nelx, nely, penal)

print(f"Mesh    : {nelx} x {nely} = {n} elements")
print(f"Budget  : {budget:.1f}  ({100*volfrac:.0f}% volume fraction)")
print(f"eps_opt : {eps_opt:.0e}")
""")


# ── Section 1: Motivation ──────────────────────────────────────────────────
md("""\
## 1. Motivation: why a filter?

The baseline ADMM driver alternates the x-update, y-update, and dual update
with a **fixed** penalty parameter $\\rho$.  Near convergence this can
oscillate without recovering: on the 30x10 default the primal residual
jumps roughly $10\\times$ between outer iterations 27 and 28, and the
algorithm does not return to tolerance within 30 iterations.

Below we run the baseline at $\\rho = 1$ for 40 outer iterations so this
oscillation is visible.  The resulting trajectory is stored in
`info_admm` and reused in Sec. 3 (where we compute the *real* optimality
measures $\\eta$ and $\\widetilde{\\omega}_\\rho$ along it) and in Sec. 6
(side-by-side comparison with ADMM-Filter).
""")

code("""\
# Capture per-iteration (x, y) snapshots via outer_callback (admm.py only
# stores the final iterate).  We need them in Sec. 3 to compute eta and
# omega along the whole baseline trajectory; reused in Sec. 4 as well.
admm_xy_traj = []
def _store_xy(x, y, k):
    admm_xy_traj.append((x.copy(), y.copy()))

x_opt_admm, info_admm = admm_compliance_tv(
    nelx=nelx, nely=nely, penal=penal,
    alpha=alpha, budget=budget,
    rho=rho_init, x_lo=x_lo,
    max_iter=40,             # > 27 so the oscillation is visible
    tol_primal=eps_opt, tol_dual=eps_opt,
    max_iter_x=60, max_iter_y=2000,
    verbose=False,
    outer_callback=_store_xy,
)
print(f"Baseline ADMM: converged={info_admm['converged']}, n_iter={info_admm['n_iter']}")
print(f"  Final primal residual: {info_admm['primal_res'][-1]:.3e}")
print(f"  Final dual residual  : {info_admm['dual_res'][-1]:.3e}")
print(f"  Final objective      : {info_admm['objective'][-1]:.4f}")

# Plot the primal/dual residuals on log-y so the iter-27 jump is obvious.
iters = np.arange(1, info_admm["n_iter"] + 1)
fig, ax = plt.subplots(figsize=(9, 4))
ax.semilogy(iters, info_admm["primal_res"], "b-o", ms=4, label=r"primal $\\|x-y\\|$")
ax.semilogy(iters, info_admm["dual_res"],   "r-s", ms=4, label=r"dual $\\rho\\|\\Delta y\\|$")
ax.axvline(27, color="gray", linestyle="--", alpha=0.6)
ax.text(27.3, ax.get_ylim()[1] * 0.5, "iter 27\\noscillation onset",
        color="gray", fontsize=9)
ax.axhline(eps_opt, color="green", linestyle=":", alpha=0.6, label=f"tolerance = {eps_opt:g}")
ax.set_xlabel("ADMM iteration")
ax.set_ylabel("Residual")
ax.set_title("Baseline ADMM (fixed rho=1) on 30x10 -- does NOT converge")
ax.legend(loc="lower left")
ax.grid(True, which="both", alpha=0.3)
plt.tight_layout()
plt.show()
""")


# ── Section 2: Filter ──────────────────────────────────────────────────────
md("""\
## 2. The augmented-Lagrangian filter

The filter $\\mathcal{F}$ stores past *non-dominated* pairs
$(\\eta^{(l)}, \\omega^{(l)})$ where $\\eta = \\|x-y\\|_2^2$ measures primal
infeasibility and $\\omega$ measures dual infeasibility (defined in Sec. 3).
A new candidate $(\\eta, \\omega)$ is **acceptable** iff for every entry $l$,

$$\\eta \\leq \\beta\\,\\eta^{(l)} \\quad \\text{or} \\quad
  \\omega \\leq \\omega^{(l)} - \\gamma\\,\\eta,
  \\qquad 0 < \\beta, \\gamma < 1.$$

That is, the candidate must beat each existing entry on **at least one**
axis (either reduce primal infeasibility geometrically, or improve dual
infeasibility by more than $\\gamma\\,\\eta$).  Dominance pruning then
removes any old entry beaten on both axes by the new one.

`RASC-MeetingNotes.tex` Sec. 3.1 has the formal definition.  The implementation
is the `Filter` class in `filter.py`.
""")

code("""\
# Demo: create a filter with 3 contrived entries and visualise the
# acceptance region in (eta, omega) space.
beta_demo  = 0.99
gamma_demo = 1e-2     # exaggerated from the FilterADMM default 1e-5 to make the
                       # slanted "omega-branch" lines clearly visible in the plot
flt_demo = Filter(beta=beta_demo, gamma=gamma_demo)

# Three contrived entries.
demo_entries = [(2.0, 1.0), (0.5, 3.0), (0.05, 5.0)]
for e, w in demo_entries:
    flt_demo.add(e, w)
print(f"Filter has {len(flt_demo)} entries after dominance pruning: ", end="")
print(list(flt_demo))

# Six test candidates -- a mix of accept/reject.
candidates = [
    (0.01, 0.2), (1.0, 0.3),    # should accept
    (3.0, 2.0), (1.5, 6.0),     # should reject
    (0.3, 1.5), (0.04, 4.0),    # mixed
]

# Plot the acceptance region.  For each filter entry l, a candidate (eta, omega)
# is REJECTED by l iff eta > beta*eta_l AND omega > omega_l - gamma*eta.  The
# total reject region is the UNION over l.
fig, ax = plt.subplots(figsize=(7, 5))
eta_grid   = np.linspace(0.001, 4.0, 400)
omega_grid = np.linspace(0.0, 7.0, 400)
EE, WW = np.meshgrid(eta_grid, omega_grid)
rejected = np.zeros_like(EE, dtype=bool)
for e_l, w_l in flt_demo:
    rejected |= (EE > beta_demo * e_l) & (WW > w_l - gamma_demo * EE)
ax.contourf(EE, WW, rejected.astype(float),
            levels=[0.5, 1.5], colors=["#dddddd"], alpha=0.7)

# Filter entries (black dots).
for e, w in flt_demo:
    ax.plot(e, w, "ko", ms=10)
    ax.annotate(f"({e}, {w})", (e, w), textcoords="offset points",
                xytext=(8, 6), fontsize=9)

# Candidates -- green check for acceptable, red x for rejected.
print()
for e, w in candidates:
    ok = flt_demo.is_acceptable(e, w)
    color, marker, label = ("green", "P", "accept") if ok else ("red", "X", "reject")
    ax.plot(e, w, marker=marker, color=color, ms=12, mec="black", mew=0.5)
    print(f"  ({e:.2f}, {w:.2f}) -> {label}")

ax.set_xlabel(r"$\\eta = \\|x-y\\|^2$")
ax.set_ylabel(r"$\\omega$  (dual infeasibility)")
ax.set_title("Filter acceptance region (grey = rejected;"
             f" beta={beta_demo}, gamma={gamma_demo})")
ax.set_xlim(0, 4.0)
ax.set_ylim(0, 7.0)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
""")


# ── Section 3: Optimality measures ─────────────────────────────────────────
md("""\
## 3. Optimality measures $\\eta$ and $\\widetilde{\\omega}_\\rho$

The filter and the convergence test both compare against two quantities:

$$\\eta(x, y) := \\|x - y\\|_2^2 \\qquad\\text{(primal infeasibility)}$$

For dual infeasibility, the literal projected-gradient form is undefined
because $\\alpha\\,\\mathrm{TV}(y)$ is non-smooth.  We use the
**proximal-gradient extension** with step size $\\tau$:

$$\\widetilde{\\omega}_\\rho(x,y,\\lambda)
    := \\bigl\\|r_x\\bigr\\|_2^2 + \\bigl\\|r_y\\bigr\\|_2^2$$

where $r_x$ is a projected-gradient residual on the smooth $x$-block and
$r_y$ uses the Chambolle--Pock prox on the $\\alpha\\,\\mathrm{TV} + \\iota_{\\mathcal{Y}}$
y-block.  See `RASC-MeetingNotes.tex` Sec. 3.1 (eq. omega-prox).

> **Identity (Sec. 3.3 of the notes).** After the multiplier update
> $\\lambda^{k+1} = \\lambda^k - \\rho(x^{k+1} - y^{k+1})$,
> $\\;\\widetilde{\\omega}_\\rho(x^{k+1}, y^{k+1}, \\lambda^k)
>  = \\widetilde{\\omega}_0(x^{k+1}, y^{k+1}, \\lambda^{k+1})$.
> The convergence test uses the latter (FilterADMM passes `rho=0` to
> `compute_omega` post-multiplier-update -- the $\\widetilde{\\omega}_0$
> correction documented in Sec. 4.5 of the notes).

Below we compute $\\eta$ and $\\widetilde{\\omega}_\\rho$ along the baseline
trajectory captured in Sec. 1.  The dual residual $\\rho\\|\\Delta y\\|$ that
the baseline uses as a stopping criterion fluctuates wildly near iter 27,
but $\\eta$ and $\\widetilde{\\omega}_\\rho$ show the same instability and
do not approach zero -- the algorithm has not actually converged.
""")

code("""\
# Reconstruct lambda along the baseline trajectory by replaying admm.py's
# update rule  lam <- lam + rho*(y - x)  with the (x, y) pairs captured in
# Sec. 1.  admm.py starts from lam_0 = 0 (see admm.py initialisation).
admm_lam_traj = []
lam_replay    = np.zeros(n)
for x_k, y_k in admm_xy_traj:
    admm_lam_traj.append(lam_replay.copy())   # lam BEFORE the k-th update
    lam_replay = lam_replay + rho_init * (y_k - x_k)

# Now compute eta and omega along the trajectory.
eta_traj   = np.array([compute_eta(x_k, y_k)
                       for (x_k, y_k) in admm_xy_traj])
omega_traj = np.array([compute_omega(x_k, y_k, lam_k,
                                     fem, edges, alpha, rho_init,
                                     budget, x_lo, tau=1.0)
                       for (x_k, y_k), lam_k in zip(admm_xy_traj, admm_lam_traj)])

iters = np.arange(1, len(eta_traj) + 1)
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.semilogy(iters, info_admm["primal_res"], "b-o", ms=3, alpha=0.5,
            label=r"primal $\\|x-y\\|$ (admm.py stop criterion)")
ax.semilogy(iters, info_admm["dual_res"],   "r-s", ms=3, alpha=0.5,
            label=r"dual $\\rho\\|\\Delta y\\|$ (admm.py stop criterion)")
ax.semilogy(iters, eta_traj,   "C0-D", ms=5,
            label=r"$\\eta = \\|x-y\\|^2$ (filter measure)")
ax.semilogy(iters, omega_traj, "C3-v", ms=5,
            label=r"$\\widetilde{\\omega}_\\rho$ (filter measure)")
ax.axvline(27, color="gray", linestyle="--", alpha=0.5)
ax.axhline(eps_opt, color="green", linestyle=":", alpha=0.6,
           label=f"tolerance = {eps_opt:g}")
ax.set_xlabel("ADMM iteration")
ax.set_ylabel("Residual / infeasibility")
ax.set_title(r"Baseline ADMM: $\\eta$ and $\\widetilde{\\omega}_\\rho$ along the trajectory")
ax.legend(loc="lower left", fontsize=9)
ax.grid(True, which="both", alpha=0.3)
plt.tight_layout()
plt.show()
""")


# ── Section 4: Restoration phase ───────────────────────────────────────────
md("""\
## 4. The restoration phase

When the new inner iterate $(x^{(j+1)}, y^{(j+1)})$ fails the filter
acceptance test, ADMM-Filter enters a **restoration phase**.  Three triggers
fire it (`RASC-MeetingNotes.tex` Sec. 3.1 and Sec. 4.1):

1. $\\eta^{(j+1)} \\geq \\beta \\cdot U$ -- primal infeasibility above the
   restoration upper bound $U$ (default $U = 10$).
2. $\\omega^{(j+1)} \\leq \\varepsilon \\;\\wedge\\; \\eta^{(j+1)} \\geq \\beta \\cdot \\eta_{\\min}$
   -- dual converged but primal stale.
3. $j + 1 = M_{\\max}$ -- inner-iteration cap exhausted (added by the
   implementation; see Sec. 4.1 of the notes).

The restoration **backtracks** the auxiliary variable toward consensus:

$$\\hat y_m := x^{(j+1)} + 2^{-m}\\bigl(y^{(j+1)} - x^{(j+1)}\\bigr), \\quad m = 1, 2, 3, \\dots$$

which drives $\\eta(x^{(j+1)}, \\hat y_m) = 4^{-m} \\cdot \\eta(x^{(j+1)}, y^{(j+1)})$
geometrically toward zero.  The first $\\hat y_m$ that is filter-acceptable
is taken, and $\\rho$ is doubled so subsequent inner ADMM steps push the
two blocks back together more aggressively.

`FilterADMM.py` adds four documented departures (Sec. 4.1--4.4) plus one
correction (Sec. 4.5, $\\widetilde{\\omega}_0$ at the convergence test).
Algorithm 2 in Sec. 4.6 of the notes is the formal as-implemented statement.

The demo below takes the (x, y) at the baseline's oscillation iterate 28
(where $\\eta \\approx 0.85$ is the biggest in the run) and shows how the
backtracking shrinks $\\eta$.
""")

code("""\
# Take the pair (x, y) at iter 28 of the baseline -- right at the post-iter-27
# oscillation peak -- and show that backtracking pulls eta geometrically to 0.
k_bad = 27   # 0-indexed -> "iter 28" in the 1-indexed plot
x_bad, y_bad = admm_xy_traj[k_bad]
eta_bad = compute_eta(x_bad, y_bad)
print(f"Pre-backtrack iter {k_bad + 1}: eta = {eta_bad:.4f}")

# Backtracking sequence.
m_values  = np.arange(0, 7)
eta_seq   = []
omega_seq = []
lam_k     = admm_lam_traj[k_bad]
for m in m_values:
    y_hat = x_bad + (0.5 ** m) * (y_bad - x_bad)   # m=0 -> original y_bad
    eta_seq.append(compute_eta(x_bad, y_hat))
    omega_seq.append(compute_omega(x_bad, y_hat, lam_k,
                                   fem, edges, alpha, rho_init,
                                   budget, x_lo, tau=1.0))
eta_seq   = np.array(eta_seq)
omega_seq = np.array(omega_seq)

# Predict eta = 4**(-m) * eta_bad for comparison.
eta_pred = eta_bad * (4.0 ** -m_values)

# Demo filter (using the Sec. 2 entries -- realistic-shape acceptance region).
flt_show = Filter(beta=0.99, gamma=1e-5)
for e, w in demo_entries:
    flt_show.add(e, w)
accepts = [flt_show.is_acceptable(e, w) for e, w in zip(eta_seq, omega_seq)]
m_star = next((m for m, ok in zip(m_values, accepts) if ok), None)
print(f"\\nBacktracking sequence (rho={rho_init}):")
print(f"{'m':>3} | {'eta':>10} | {'eta predicted':>14} | {'omega':>10} | filter?")
print("-" * 60)
for m, e, ep, w, ok in zip(m_values, eta_seq, eta_pred, omega_seq, accepts):
    tag = "accept" if ok else "reject"
    print(f"{m:>3} | {e:>10.4e} | {ep:>14.4e} | {w:>10.4e} | {tag}")
if m_star is not None:
    print(f"\\nFirst acceptable m: {m_star}")

# Plot eta vs m on log-y.
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.semilogy(m_values, eta_seq, "bo-", ms=8, label=r"$\\eta(x, \\hat y_m)$ (actual)")
ax.semilogy(m_values, eta_pred, "k--", alpha=0.5,
            label=r"$4^{-m} \\cdot \\eta_0$ (predicted)")
if m_star is not None:
    ax.axvline(m_star, color="green", linestyle=":", alpha=0.5)
    ax.text(m_star + 0.1, ax.get_ylim()[0] * 5, f"first filter-acceptable m = {m_star}",
            color="green", fontsize=10)
ax.set_xlabel("backtracking step $m$")
ax.set_ylabel(r"$\\eta(x, \\hat y_m)$")
ax.set_title(r"Restoration backtracking on iter 28: $\\hat y_m = x + 2^{-m}(y - x)$")
ax.legend(loc="upper right")
ax.grid(True, which="both", alpha=0.3)
plt.tight_layout()
plt.show()
""")


# ── Section 5: Full FilterADMM ─────────────────────────────────────────────
md("""\
## 5. Full ADMM-Filter

Putting the pieces together: the outer loop maintains $(x^{(k)}, y^{(k)},
\\lambda^{(k)})$ and the filter $\\mathcal{F}_k$; the inner loop runs
ADMM steps until the new iterate is filter-acceptable or a restoration
trigger fires.  On every restoration $\\rho$ doubles.  Convergence is
$\\eta \\leq \\varepsilon_{\\mathrm{opt}}$ and $\\widetilde{\\omega}_0 \\leq
\\varepsilon_{\\mathrm{opt}}$.

The full pseudocode is Algorithm 2 in `RASC-MeetingNotes.tex` Sec. 4.6.

**Four departures** from the meeting algorithm (Sec. 4.1--4.4):

1. **Third restoration trigger** added: $j+1 = M_{\\max}$.
2. **Inner-loop acceptance test moved to the bottom** of the $j$-loop --
   the top-test would short-circuit on an empty filter, which is the
   algorithm's state at outer iter 0 since uniform init gives $\\eta_0 = 0$
   and `Filter.add` rejects $\\eta \\leq 0$.
3. **Restoration backtracking accepts the first filter-acceptable $m$**
   (matches the pseudocode literally; for an empty filter this is $m=1$).
4. **$U = 10$ default** instead of $\\eta_0 / \\beta$, which is degenerate
   when $\\eta_0 = 0$.

**Plus one correction** (Sec. 4.5, $\\widetilde{\\omega}_0$): the
post-multiplier-update dual residual at Algorithm 2 line 26 is evaluated
with $\\rho = 0$ (passes `rho=0.0` to `compute_omega`), matching the
$\\varepsilon$-optimality condition.  This fix nearly halved the iteration
count on the 30x10 default (26 -> 14).

The run below uses default filter constants ($\\beta = 0.99$, $\\gamma = 10^{-5}$,
$\\sigma = 10^{-5}$, $U = 10$) and the same problem/$\\varepsilon$ as the
baseline above.
""")

code("""\
# Run FilterADMM.  Disable the tabular log + plotting since we render
# everything inline in the next cells.
x_opt, info = filter_admm_compliance_tv(
    nelx=nelx, nely=nely, penal=penal,
    alpha=alpha, budget=budget,
    rho_init=rho_init,
    eps_opt=eps_opt,
    max_outer=60,
    x_lo=x_lo,
    verbose=False,
    verbose_inner=False,
    plot=False,
    plot_inner=False,
)
print("ADMM-Filter results:")
print(f"  Converged          : {info['converged']}  ({info['reason']})")
print(f"  Outer iterations   : {info['n_iter']}")
print(f"  Total restorations : {info['restoration_count']}")
print(f"  Final rho          : {info['rho']:.3e}")
print(f"  Final |F|          : {len(info['filter_entries'])}")
print(f"  Final eta          : {info['eta_history'][-1]:.3e}")
print(f"  Final omega        : {info['omega_history'][-1]:.3e}")
print(f"  Final objective    : {info['objective'][-1]:.4f}")
print(f"  sum(x*)            : {x_opt.sum():.3f}  (budget = {budget:.1f})")
""")

code("""\
# Plot the convergence trajectory: eta, omega, rho across outer iters.
eta_hist   = info["eta_history"]
omega_hist = info["omega_history"]
rho_hist   = info["rho_history"]
iters      = np.arange(1, len(eta_hist) + 1)

fig, axes = plt.subplots(1, 3, figsize=(15, 3.8))

axes[0].semilogy(iters, eta_hist, "b-o", ms=5)
axes[0].axhline(eps_opt, color="green", linestyle=":", alpha=0.7,
                label=f"eps_opt = {eps_opt:g}")
axes[0].set_xlabel("outer iteration $k$")
axes[0].set_ylabel(r"$\\eta = \\|x-y\\|^2$")
axes[0].set_title("Primal infeasibility")
axes[0].legend()
axes[0].grid(True, which="both", alpha=0.3)

axes[1].semilogy(iters, omega_hist, "r-s", ms=5)
axes[1].axhline(eps_opt, color="green", linestyle=":", alpha=0.7,
                label=f"eps_opt = {eps_opt:g}")
axes[1].set_xlabel("outer iteration $k$")
axes[1].set_ylabel(r"$\\widetilde{\\omega}_0$")
axes[1].set_title("Dual infeasibility (post-multiplier-update, rho=0)")
axes[1].legend()
axes[1].grid(True, which="both", alpha=0.3)

# rho is piecewise constant -- step plot makes the doublings clear.
axes[2].step(iters, rho_hist, where="post", color="purple", lw=2)
# Mark each restoration with an R.
for k in range(1, len(rho_hist)):
    if rho_hist[k] != rho_hist[k - 1]:
        axes[2].plot(iters[k], rho_hist[k], "kx", ms=10)
        axes[2].text(iters[k] + 0.3, rho_hist[k], "R",
                     fontsize=11, fontweight="bold", color="black")
axes[2].set_xlabel("outer iteration $k$")
axes[2].set_ylabel(r"$\\rho$")
axes[2].set_title(f"Penalty (3 restorations: 1 to 2 to 4 to 8)")
axes[2].set_yscale("log", base=2)
axes[2].grid(True, which="both", alpha=0.3)

plt.tight_layout()
plt.show()
""")

code("""\
# Final design: 1x3 heatmap of (x, y, lambda) matching FilterADMM's
# per-iteration PDF output (images/iter_NNNN.pdf).
y_final   = info["y"]
lam_final = info["lam"]

fig, axes = plt.subplots(1, 3, figsize=(13, 4))

# x and y: gray_r, fixed [0, 1] range.
for ax, data, title in zip(axes[:2], (x_opt, y_final), ("x", "y")):
    im = ax.imshow(
        data.reshape(nelx, nely).T,
        cmap="gray_r", vmin=0.0, vmax=1.0, origin="lower",
    )
    ax.set_title(f"{title}  (final, iter {info['n_iter']})")
    ax.axis("off")
    fig.colorbar(im, ax=ax, shrink=0.85)

# lambda: diverging, centered on zero.
ax = axes[2]
im = ax.imshow(
    lam_final.reshape(nelx, nely).T,
    cmap="RdBu_r", norm=mcolors.CenteredNorm(), origin="lower",
)
ax.set_title(f"lambda  (final)")
ax.axis("off")
fig.colorbar(im, ax=ax, shrink=0.85)

plt.suptitle(
    f"ADMM-Filter final iterate: F = {info['objective'][-1]:.2f}, "
    f"sum(x) = {x_opt.sum():.1f}",
    y=1.02,
)
plt.tight_layout()
plt.show()

print(f"\\nFilter entries at exit ({len(info['filter_entries'])}):")
for i, (e, w) in enumerate(info["filter_entries"]):
    print(f"  [{i}]  eta = {e:.3e}   omega = {w:.3e}")
""")


# ── Section 6: Comparison ──────────────────────────────────────────────────
md("""\
## 6. Comparison with the baseline

Same problem, same $\\varepsilon_{\\mathrm{opt}}$, both drivers.  The
baseline (Sec. 1) runs to its `max_iter=40` cap without reaching tolerance;
ADMM-Filter (Sec. 5) converges in ~14 outer iterations.  We reuse the
already-computed trajectories from Sec. 1 and Sec. 5 -- no re-runs needed.

Below: residual trajectories side by side, then final designs.
""")

code("""\
fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))

# Top-left: baseline primal/dual residuals.
iters_admm = np.arange(1, info_admm["n_iter"] + 1)
ax = axes[0, 0]
ax.semilogy(iters_admm, info_admm["primal_res"], "b-o", ms=4, label="primal")
ax.semilogy(iters_admm, info_admm["dual_res"],   "r-s", ms=4, label="dual")
ax.axhline(eps_opt, color="green", linestyle=":", alpha=0.6,
           label=f"eps_opt = {eps_opt:g}")
ax.set_xlabel("ADMM iteration")
ax.set_ylabel("Residual")
ax.set_title(f"Baseline ADMM (fixed rho)\\n"
             f"n_iter = {info_admm['n_iter']}, "
             f"converged = {info_admm['converged']}")
ax.legend()
ax.grid(True, which="both", alpha=0.3)

# Top-right: FilterADMM (eta, omega).  History length is n_iter - 1 because
# the final outer iter is just the convergence check at the top of the loop.
iters_filter = np.arange(1, len(info["eta_history"]) + 1)
ax = axes[0, 1]
ax.semilogy(iters_filter, info["eta_history"],   "C0-D", ms=4,
            label=r"$\\eta$ (primal)")
ax.semilogy(iters_filter, info["omega_history"], "C3-v", ms=4,
            label=r"$\\widetilde{\\omega}_0$ (dual)")
ax.axhline(eps_opt, color="green", linestyle=":", alpha=0.6,
           label=f"eps_opt = {eps_opt:g}")
ax.set_xlabel("outer iteration $k$")
ax.set_ylabel("Infeasibility")
ax.set_title(f"ADMM-Filter (adaptive rho)\\n"
             f"n_iter = {info['n_iter']}, "
             f"converged = {info['converged']}")
ax.legend()
ax.grid(True, which="both", alpha=0.3)

# Bottom-left: baseline final design.
F_admm = fem(x_opt_admm)[0]
ax = axes[1, 0]
ax.imshow(x_opt_admm.reshape(nelx, nely).T, origin="lower",
          cmap="gray_r", vmin=0, vmax=1)
ax.set_title(f"Baseline final design\\n"
             f"F = {F_admm:.2f}, sum(x) = {x_opt_admm.sum():.1f}")
ax.axis("off")

# Bottom-right: FilterADMM final design.
F_filter = fem(x_opt)[0]
ax = axes[1, 1]
ax.imshow(x_opt.reshape(nelx, nely).T, origin="lower",
          cmap="gray_r", vmin=0, vmax=1)
ax.set_title(f"ADMM-Filter final design\\n"
             f"F = {F_filter:.2f}, sum(x) = {x_opt.sum():.1f}")
ax.axis("off")

plt.suptitle("Baseline ADMM vs ADMM-Filter on 30x10 (40% volume)", fontsize=13)
plt.tight_layout()
plt.show()
""")

code("""\
# Summary table.
F_admm    = fem(x_opt_admm)[0]
tv_admm   = float(np.sum(np.abs(x_opt_admm[edges[:, 0]] - x_opt_admm[edges[:, 1]])))
obj_admm  = F_admm + alpha * tv_admm

F_filter   = fem(x_opt)[0]
tv_filter  = float(np.sum(np.abs(x_opt[edges[:, 0]] - x_opt[edges[:, 1]])))
obj_filter = F_filter + alpha * tv_filter

rows = [
    ("Converged?",                f"{info_admm['converged']}",          f"{info['converged']}"),
    ("Reason",                    "(stopping criterion)",                f"{info['reason']}"),
    ("Outer iterations",          f"{info_admm['n_iter']}",              f"{info['n_iter']}"),
    ("Final primal / eta",        f"{info_admm['primal_res'][-1]:.3e}", f"{info['eta_history'][-1]:.3e}"),
    ("Final dual / omega",        f"{info_admm['dual_res'][-1]:.3e}",   f"{info['omega_history'][-1]:.3e}"),
    ("Final F(x)",                f"{F_admm:.4f}",                       f"{F_filter:.4f}"),
    ("Final TV(x)",               f"{tv_admm:.4f}",                      f"{tv_filter:.4f}"),
    ("Final F + alpha*TV",        f"{obj_admm:.4f}",                     f"{obj_filter:.4f}"),
    ("sum(x*)",                   f"{x_opt_admm.sum():.3f}",             f"{x_opt.sum():.3f}"),
    ("Final rho",                 f"{rho_init:.3e} (fixed)",             f"{info['rho']:.3e}"),
    ("Restorations",              "n/a",                                  f"{info['restoration_count']}"),
]

print(f"{'Metric':<25} | {'Baseline (admm.py)':<22} | {'ADMM-Filter':<22}")
print("-" * 75)
for label, a, b in rows:
    print(f"{label:<25} | {a:<22} | {b:<22}")
""")


# ── Write notebook ─────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.11"},
    },
    "cells": cells,
}

with open("filter_walkthrough.ipynb", "w") as f:
    json.dump(nb, f, indent=1)

print(f"Written {len(cells)} cells to filter_walkthrough.ipynb")
