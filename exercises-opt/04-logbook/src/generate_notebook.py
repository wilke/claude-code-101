import json

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
# ADMM for Compliance Minimisation with TV Regularisation

This notebook walks through an ADMM algorithm for

$$\\min_{\\substack{x \\in [\\epsilon,1]^n \\\\ \\mathbf{1}^\\top x \\leq B}}
  F(x) + \\alpha \\cdot \\mathrm{TV}(x)$$

where $F(x)$ is **structural compliance** on a 2-D Q4 FE mesh, \
$\\mathrm{TV}(x) = \\sum_{(u,v)\\in E}|x_u - x_v|$ is **graph total \
variation** over element neighbours, and $\\alpha > 0$ trades off compliance \
against spatial regularity.

**ADMM splitting** — introduce $y = x$ and alternate:

| Step | Update | Solver |
|------|--------|--------|
| **x-update** | $\\min_{x\\in[\\epsilon,1]^n,\\,\\sum x_v\\leq B}\\; F(x)+\\frac{\\rho}{2}\\|x-\\hat y\\|^2$ | Reciprocal approximation |
| **y-update** | $\\min_{y\\in[\\epsilon,1]^n,\\,\\sum y_v\\leq B}\\; \\alpha\\,\\mathrm{TV}(y)+\\frac{\\rho}{2}\\|y-\\hat x\\|^2$ | Chambolle–Pock |
| **dual** | $\\lambda \\leftarrow \\lambda + \\rho(y-x)$ | Closed form |
""")

# ── Imports & parameters ───────────────────────────────────────────────────
code("""\
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from compliance       import ComplianceProblem
from reciprocal_approx import reciprocal_approximation
from graph_tv          import chambolle_pock_graph_tv
from admm              import admm_compliance_tv, build_grid_edges

%matplotlib inline
plt.rcParams.update({"figure.dpi": 110, "font.size": 11})
""")

code("""\
nelx    = 60      # elements in x
nely    = 20      # elements in y
penal   = 3.0     # SIMP penalisation exponent
volfrac = 0.4     # volume fraction
budget  = volfrac * nelx * nely
alpha   = 0.5     # TV weight
rho     = 1.0     # ADMM penalty
x_lo    = 1e-4    # density lower bound
n       = nelx * nely

print(f"Mesh   : {nelx} x {nely} = {n} elements")
print(f"Budget : {budget:.1f}  ({100*volfrac:.0f}% volume fraction)")
""")

# ── Section 1: Compliance ──────────────────────────────────────────────────
md("""\
## 1. Structural Compliance

The compliance objective is $F(x) = \\mathbf{f}^\\top\\mathbf{u}(x)$, \
where $K(x)\\mathbf{u}=\\mathbf{f}$.  Stiffness is assembled using SIMP:

$$E_v(x_v) = E_{\\min} + x_v^p(E_{\\max}-E_{\\min})$$

The sensitivity is

$$\\nabla_v F(x) = -p\\,x_v^{p-1}(E_{\\max}-E_{\\min})\\;\\mathbf{u}_v^\\top K_e\\mathbf{u}_v$$

The domain is a **cantilever**: clamped left edge, unit downward point load \
at the mid-point of the right edge.
""")

code("""\
fem = ComplianceProblem(nelx, nely, penal)

fig, ax = plt.subplots(figsize=(9, 3.5))
ax.set_aspect("equal")
ax.set_facecolor("#f8f8f8")

for elx in range(nelx):
    for ely in range(nely):
        ax.add_patch(plt.Rectangle(
            (elx, ely), 1, 1, linewidth=0.2, edgecolor="#bbb", facecolor="white"))

# Clamped left edge
ax.plot([0, 0], [0, nely], "b-", lw=4)
for ely in range(nely + 1):
    ax.plot([0, -0.5], [ely, ely - 0.5], "b-", lw=1)

# Point load at right mid-edge
mid = nely // 2
ax.annotate("", xy=(nelx, mid),
            xytext=(nelx + 2.5, mid + 1.5),
            arrowprops=dict(arrowstyle="->", color="red", lw=2))
ax.text(nelx + 2.6, mid + 1.8, "f", color="red", fontsize=14, fontweight="bold")

ax.set_xlim(-1.5, nelx + 5)
ax.set_ylim(-1, nely + 1)
ax.set_title(f"Cantilever beam  ({nelx} x {nely} Q4 elements)")
ax.axis("off")
plt.tight_layout()
plt.show()
""")

code("""\
x_uni = np.full(n, volfrac)
C_uni, dC_uni = fem(x_uni)
print(f"Compliance on uniform {volfrac:.0%} design: {C_uni:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 3))

axes[0].imshow(x_uni.reshape(nelx, nely).T, origin="lower",
               cmap="gray_r", vmin=0, vmax=1)
axes[0].set_title("Uniform design")
axes[0].axis("off")

im = axes[1].imshow(dC_uni.reshape(nelx, nely).T, origin="lower",
                    cmap="RdBu_r", norm=mcolors.CenteredNorm())
axes[1].set_title("Compliance sensitivity")
axes[1].axis("off")
fig.colorbar(im, ax=axes[1], shrink=0.85)
plt.tight_layout()
plt.show()
""")

# ── Section 2: ADMM math ──────────────────────────────────────────────────
md("""\
## 2. ADMM Splitting

Introducing $y = x$ and the augmented Lagrangian

$$\\mathcal{L}_\\rho(x,y,\\lambda)
  = F(x) + \\alpha\\,\\mathrm{TV}(y)
  + \\lambda^\\top(y-x) + \\frac{\\rho}{2}\\|y-x\\|^2$$

completing the square separates the two subproblems.  Setting \
$\\hat y = y + \\lambda/\\rho$ and $\\hat x = x - \\lambda/\\rho$:

$$\\text{x-update:}\\quad
  F(x) + \\frac{\\rho}{2}\\|x-\\hat y\\|^2
  = F(x) + \\sum_v\\!\\Bigl(\\underbrace{\\tfrac{\\rho}{2}}_{a_v}x_v^2
    \\underbrace{-\\rho\\hat y_v}_{b_v}x_v\\Bigr)$$

$$\\text{y-update:}\\quad
  \\alpha\\,\\mathrm{TV}(y) + \\frac{\\rho}{2}\\|y-\\hat x\\|^2
  = \\alpha\\,\\mathrm{TV}(y) + \\sum_v\\!\\Bigl(\\tfrac{\\rho}{2}y_v^2
    - \\rho\\hat x_v y_v\\Bigr)$$

Both subproblems use the same $(a_v,b_v)$ parameterisation so they plug \
directly into the existing solvers.
""")

# ── Section 3: x-subproblem ───────────────────────────────────────────────
md("""\
## 3. x-subproblem: Reciprocal Approximation

At current iterate $\\hat x$, $F$ is approximated by

$$F(x) \\approx F(\\hat x)
  + \\sum_v c_v\\!\\left(\\frac{1}{x_v}-\\frac{1}{\\hat x_v}\\right),
  \\qquad c_v = -\\hat x_v^2\\,\\nabla_v F(\\hat x)$$

This matches first derivatives and decouples the subproblem.  The \
per-vertex optimum satisfies the **cubic**

$$2a_v\\,x_v^3 + (b_v+\\lambda)\\,x_v^2 - c_v = 0$$

and the budget multiplier $\\lambda^*$ is found by bisection on \
$\\sum_v x_v^*(\\lambda) = B$.
""")

code("""\
rng = np.random.default_rng(42)

# Fix y and lambda=0 for this demonstration
y_fixed  = np.clip(rng.uniform(0.2, 0.6, n), x_lo, 1.0)
y_fixed *= budget / y_fixed.sum()

a_x = np.full(n, rho / 2.0)
b_x = -rho * y_fixed          # lambda = 0  =>  y_hat = y_fixed

obj_hist = []

def fem_tracked(x):
    F_val, grad = fem(x)
    obj_hist.append(F_val + float(np.dot(a_x, x**2) + np.dot(b_x, x)))
    return F_val, grad

x_sub, info_x = reciprocal_approximation(
    fem_tracked, a_x, b_x, budget,
    x_init=y_fixed.copy(), max_iter=50, tol=1e-6, x_lo=x_lo,
)
print(f"Converged={info_x['converged']}  iters={info_x['n_iter']}  "
      f"sum(x)={x_sub.sum():.3f}")

fig, axes = plt.subplots(1, 3, figsize=(14, 3))

axes[0].imshow(y_fixed.reshape(nelx, nely).T, origin="lower",
               cmap="gray_r", vmin=0, vmax=1)
axes[0].set_title("Input: y_hat")
axes[0].axis("off")

axes[1].imshow(x_sub.reshape(nelx, nely).T, origin="lower",
               cmap="gray_r", vmin=0, vmax=1)
axes[1].set_title("x-subproblem solution")
axes[1].axis("off")

axes[2].plot(obj_hist, "o-", ms=4, color="steelblue")
axes[2].set_xlabel("Reciprocal approximation iteration")
axes[2].set_ylabel("Surrogate objective")
axes[2].set_title("Inner loop convergence")
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
""")

# ── Section 4: y-subproblem ───────────────────────────────────────────────
md("""\
## 4. y-subproblem: Chambolle–Pock

The y-subproblem is graph TV denoising with a quadratic data term:

$$\\min_{y\\in[\\epsilon,1]^n,\\,\\sum y_v\\leq B}
  \\alpha\\,\\mathrm{TV}(y) + \\sum_v\\!\\left(\\tfrac{\\rho}{2}y_v^2
  - \\rho\\hat x_v y_v\\right)$$

Chambolle–Pock solves $\\min_y F(y)+G(Dy)$ where:
- $D$ = signed incidence matrix of the **grid graph** (horizontal + vertical element neighbours),
- $G(z)=\\alpha\\|z\\|_1$ with dual variable $y_1\\in[-\\alpha,\\alpha]^{|E|}$,
- per-vertex prox is a closed-form solve (quadratic + clip to $[\\epsilon,1]$).
""")

code("""\
edges = build_grid_edges(nelx, nely)
print(f"Grid graph: {n} vertices, {len(edges)} edges  "
      f"(horiz={( nelx-1)*nely}, vert={nelx*(nely-1)})")

# Demonstrate: TV-smooth a noisy density field
x_noisy  = np.clip(rng.uniform(0.05, 0.95, n), x_lo, 1.0)
x_noisy *= budget / x_noisy.sum()
x_noisy  = np.clip(x_noisy, x_lo, 1.0)

a_y = np.full(n, rho / 2.0)
b_y = -rho * x_noisy

y_sub, info_y = chambolle_pock_graph_tv(
    n, edges, a_y, b_y,
    budget=budget, alpha=alpha, x_lo=x_lo,
    max_iter=3000, tol=1e-7,
)
print(f"Converged={info_y['converged']}  iters={info_y['n_iter']}  "
      f"sum(y)={y_sub.sum():.3f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 3))
axes[0].imshow(x_noisy.reshape(nelx, nely).T, origin="lower",
               cmap="gray_r", vmin=0, vmax=1)
axes[0].set_title("Input: x_hat (noisy)")
axes[0].axis("off")

axes[1].imshow(y_sub.reshape(nelx, nely).T, origin="lower",
               cmap="gray_r", vmin=0, vmax=1)
axes[1].set_title(f"TV-smoothed output  (alpha={alpha})")
axes[1].axis("off")

plt.suptitle("y-subproblem: TV denoising of a noisy density field", y=1.02)
plt.tight_layout()
plt.show()
""")

# ── Section 5: Full ADMM ──────────────────────────────────────────────────
md("""\
## 5. Full ADMM

Convergence is monitored by two residuals:

$$r^k = \\|x^k - y^k\\|_2 \\quad\\text{(primal: consensus gap)}$$
$$s^k = \\rho\\,\\|y^k - y^{k-1}\\|_2 \\quad\\text{(dual: rate of change of }y\\text{)}$$

Both must fall below their tolerances for the algorithm to terminate.
""")

code("""\
x_opt, info = admm_compliance_tv(
    nelx=nelx, nely=nely,
    penal=penal,
    alpha=alpha,
    budget=budget,
    rho=rho,
    x_lo=x_lo,
    max_iter=40,
    tol_primal=5e-2,
    tol_dual=5e-2,
    max_iter_x=60,
    max_iter_y=2000,
    verbose=True,
)
print(f"\\nConverged : {info['converged']}  in {info['n_iter']} iterations")
print(f"sum(x*)   : {x_opt.sum():.3f}  (budget = {budget:.1f})")
""")

code("""\
iters = np.arange(1, info["n_iter"] + 1)
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].semilogy(iters, info["primal_res"], "b-o", ms=4, label="Primal ||x-y||")
axes[0].semilogy(iters, info["dual_res"],   "r-s", ms=4, label="Dual rho*||dy||")
axes[0].set_xlabel("ADMM iteration")
axes[0].set_ylabel("Residual")
axes[0].set_title("Convergence residuals")
axes[0].legend()
axes[0].grid(True, which="both", alpha=0.3)

axes[1].plot(iters, info["objective"], "g-o", ms=4)
axes[1].set_xlabel("ADMM iteration")
axes[1].set_ylabel("F(x) + alpha * TV(x)")
axes[1].set_title("Primal objective")
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
""")

code("""\
C_final, _ = fem(x_opt)
tv_final   = float(np.sum(np.abs(x_opt[edges[:, 0]] - x_opt[edges[:, 1]])))

fig, axes = plt.subplots(1, 2, figsize=(13, 4))

im0 = axes[0].imshow(x_opt.reshape(nelx, nely).T, origin="lower",
                     cmap="gray_r", vmin=0, vmax=1)
axes[0].set_title(
    f"Optimised density  (alpha={alpha})"
    f"\\nCompliance={C_final:.2f},  TV={tv_final:.2f},  sum={x_opt.sum():.1f}")
axes[0].axis("off")
fig.colorbar(im0, ax=axes[0], shrink=0.85, label="density")

x_bin = (x_opt > 0.5).astype(float)
axes[1].imshow(x_bin.reshape(nelx, nely).T, origin="lower",
               cmap="gray_r", vmin=0, vmax=1)
axes[1].set_title(
    f"Binarised design (threshold 0.5)"
    f"\\nSolid fraction: {x_bin.mean():.2f}")
axes[1].axis("off")

plt.tight_layout()
plt.show()
""")

# ── Section 6: Effect of alpha ────────────────────────────────────────────
md("""\
## 6. Effect of the Regularisation Weight $\\alpha$

Larger $\\alpha$ pushes the design towards piecewise-constant regions with \
sharp interfaces; smaller $\\alpha$ allows grey regions that can reduce \
compliance.
""")

code("""\
alphas  = [0.1, 0.5, 2.0]
results = {}

for a in alphas:
    x_a, info_a = admm_compliance_tv(
        nelx=nelx, nely=nely, penal=penal,
        alpha=a, budget=budget,
        rho=1.0, x_lo=x_lo,
        max_iter=30, tol_primal=0.1, tol_dual=0.1,
        max_iter_x=40, max_iter_y=1000,
        verbose=False,
    )
    C_a  = fem(x_a)[0]
    tv_a = float(np.sum(np.abs(x_a[edges[:, 0]] - x_a[edges[:, 1]])))
    results[a] = (x_a, C_a, tv_a)
    print(f"alpha={a:.1f}:  F={C_a:.2f}  TV={tv_a:.2f}  sum={x_a.sum():.1f}")

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, a in zip(axes, alphas):
    x_a, C_a, tv_a = results[a]
    ax.imshow(x_a.reshape(nelx, nely).T, origin="lower",
              cmap="gray_r", vmin=0, vmax=1)
    ax.set_title(f"alpha={a}\\nF={C_a:.1f},  TV={tv_a:.1f}")
    ax.axis("off")

plt.suptitle("Effect of TV regularisation weight", fontsize=13, y=1.02)
plt.tight_layout()
plt.show()
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
        "language_info": {"name": "python", "version": "3.8.0"},
    },
    "cells": cells,
}

with open("admm_walkthrough.ipynb", "w") as f:
    json.dump(nb, f, indent=1)

print(f"Written {len(cells)} cells to admm_walkthrough.ipynb")
