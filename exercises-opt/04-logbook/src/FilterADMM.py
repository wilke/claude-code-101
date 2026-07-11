"""
Double-loop ADMM-Filter driver for compliance + graph-TV topology optimisation.

Implements the algorithm of section 3.5 of RASC-MeetingNotes.tex:

    min  F(x) + alpha * TV(x)   s.t.   sum(x) <= B,   x in [eps, 1]^n

Outer loop iterates on (x, y, lam) and the penalty rho.  Inner loop runs ADMM
steps on the augmented Lagrangian until the new iterate is acceptable to a
non-dominated filter of (eta, omega) pairs.  Restoration backtracks
y_hat = x + 2^{-m}(y - x) and doubles rho when the iterate is too far from
feasible (eta too large), stalled (omega small but eta still large), or has
exhausted the inner-iteration budget.

Reuses the existing primitives:
    - admm.build_grid_edges
    - compliance.ComplianceProblem
    - reciprocal_approx.reciprocal_approximation       (x-update)
    - graph_tv.chambolle_pock_graph_tv                 (y-update)
    - filter.Filter                                    (acceptance + dominance)
    - optimality.compute_eta / compute_lagrangian / compute_omega
"""

import argparse
import os
import time
import numpy as np

from compliance import ComplianceProblem
from reciprocal_approx import reciprocal_approximation
from graph_tv import chambolle_pock_graph_tv
from admm import build_grid_edges
from filter import Filter
from optimality import compute_eta, compute_lagrangian, compute_omega


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tv_value(z, edges):
    """Graph TV at z: sum_{(u,v)} |z_u - z_v|."""
    return float(np.sum(np.abs(z[edges[:, 0]] - z[edges[:, 1]])))


def _save_iter_heatmap(x, y, lam, k_one_based, nelx, nely, image_dir,
                       plt, mcolors, j_one_based=None):
    """
    Save a 1x3 heat-map figure of (x, y, lambda) to:
      <image_dir>/iter_NNNN.pdf            if j_one_based is None  (outer iter)
      <image_dir>/iter_NNNN_jJJ.pdf        otherwise                (inner iter)

    Title strings include "iter K" or "iter K.J" accordingly so the inner
    plot is visually distinguishable from the outer one.

    x and y are densities in [x_lo, 1] (sequential gray colormap, vmin=0/vmax=1).
    lambda is signed (diverging RdBu_r with CenteredNorm so zero is white).
    Reshape uses the column-major convention from CLAUDE.md: data.reshape(nelx, nely).T.
    """
    # Compose the iteration tag and filename based on whether this is an
    # outer-only call (j_one_based is None, original behaviour) or an
    # inner-iteration call (suffix j_one_based onto both).
    if j_one_based is None:
        tag = f"iter {k_one_based}"
        fname = f"iter_{k_one_based:04d}.pdf"
    else:
        tag = f"iter {k_one_based}.{j_one_based}"
        fname = f"iter_{k_one_based:04d}_j{j_one_based:02d}.pdf"

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    # x and y: sequential gray, fixed [0, 1] range
    for ax, data, title in zip(axes[:2], (x, y), ("x", "y")):
        im = ax.imshow(
            data.reshape(nelx, nely).T,
            cmap="gray_r", vmin=0.0, vmax=1.0, origin="lower",
        )
        ax.set_title(f"{title}  ({tag})")
        ax.axis("off")
        fig.colorbar(im, ax=ax, shrink=0.85)

    # lambda: diverging, centered on zero
    ax = axes[2]
    im = ax.imshow(
        lam.reshape(nelx, nely).T,
        cmap="RdBu_r", norm=mcolors.CenteredNorm(), origin="lower",
    )
    ax.set_title(f"λ  ({tag})")  # λ = greek lambda
    ax.axis("off")
    fig.colorbar(im, ax=ax, shrink=0.85)

    fig.tight_layout()
    fig.savefig(os.path.join(image_dir, fname))
    plt.close(fig)


# Column widths shared between the table header and every data row.  Defined
# once so the dashes under the header and the values printed below always have
# matching widths.  `L` is the augmented Lagrangian (can be negative and
# typically of the same magnitude as `obj`, hence width 11 to match).
_LOG_FMT = (
    "{io:<6} {it:>6} {obj:>11} {F:>10} {TV:>10} {L:>11}"
    " {eta:>8} {omega:>8} {rho:>8} {nf:>4} {R:>2}"
)


def _print_log_header():
    """Print the two-line tabular log header (column titles, then dashes)."""
    print(_LOG_FMT.format(
        io="In/Out", it="iter",
        obj="obj", F="F", TV="TV", L="L",
        eta="eta", omega="omega", rho="rho",
        nf="|F|", R="R",
    ))
    print(_LOG_FMT.format(
        io="-" * 6, it="-" * 6,
        obj="-" * 11, F="-" * 10, TV="-" * 10, L="-" * 11,
        eta="-" * 8, omega="-" * 8, rho="-" * 8,
        nf="-" * 4, R="-" * 2,
    ))


def _save_convergence_plot(eta_hist, omega_hist, rho_hist, rho_init, image_dir, plt):
    """
    Save a single-figure convergence plot vs outer iteration k (1-based).
    Left axis (log scale): eta (blue circles) and omega_0 (red squares) share
    the same axis so their magnitudes are directly comparable.
    Right axis (linear scale): rho as a piecewise-constant step curve (green
    dashed) starting at k=0 with rho_init, with yticks at the unique rho
    values actually visited (including the initial value).
    """
    iters = np.arange(1, len(eta_hist) + 1)

    # Prepend k=0 with rho_init so the step curve shows the initial penalty.
    # eta and omega are NOT extended — they have no value at k=0.
    rho_iters = np.concatenate([[0], iters])
    rho_vals  = [rho_init] + list(rho_hist)

    fig, ax_left = plt.subplots(figsize=(8, 5))
    ax_right = ax_left.twinx()

    eta_color   = "tab:blue"
    omega_color = "tab:red"
    rho_color   = "tab:green"

    ln_eta = ax_left.semilogy(
        iters, eta_hist,
        color=eta_color, marker="o", markersize=4, linewidth=1.2,
        label=r"$\eta = \|x - y\|^2$ (primal)",
    )
    ln_omega = ax_left.semilogy(
        iters, omega_hist,
        color=omega_color, marker="s", markersize=4, linewidth=1.2,
        label=r"$\widetilde{\omega}_0$ (dual)",
    )

    ln_rho = ax_right.step(
        rho_iters, rho_vals, where="post",
        color=rho_color, linewidth=1.5, linestyle="--",
        label=r"$\rho$",
    )

    ax_left.set_xlabel("outer iteration $k$")
    ax_left.set_ylabel("primal / dual infeasibility")
    ax_right.set_ylabel(r"$\rho$", color=rho_color)
    ax_right.tick_params(axis="y", labelcolor=rho_color)

    unique_rho = sorted(set(rho_vals))
    ax_right.set_yticks(unique_rho)
    ax_right.set_ylim(0, max(unique_rho) * 1.3)

    # Combined legend across both axes
    lines = ln_eta + ln_omega + ln_rho
    ax_left.legend(lines, [ln.get_label() for ln in lines], loc="upper right")

    ax_left.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(image_dir, "convergence.pdf"))
    plt.close(fig)


def _save_movie(frames, nelx, nely, image_dir, plt, mcolors, fps=2):
    """
    Animate outer-iteration frames and save to images/movie.mp4 (MP4 via
    FFMpegWriter) or images/movie.gif (GIF via PillowWriter as fallback).

    Each frame is a tuple (x, y, lam, k_one_based) captured after the outer
    multiplier update.  The 1x3 layout matches _save_iter_heatmap for visual
    consistency.  The lambda colormap uses a fixed symmetric range derived from
    all frames so it is stable across the animation (unlike the per-frame
    CenteredNorm used in the static PDFs).

    Returns the path of the saved file, or None on failure.
    """
    import matplotlib.animation as animation

    def _reshape(data):
        return data.reshape(nelx, nely).T

    # Fixed symmetric lambda range across all frames keeps the colormap stable.
    lam_abs_max = max(float(np.abs(lam).max()) for _, _, lam, _ in frames) or 1.0

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    ax_x, ax_y, ax_lam = axes

    x0, y0, lam0, k0 = frames[0]
    im_x = ax_x.imshow(_reshape(x0), cmap="gray_r", vmin=0.0, vmax=1.0,
                        origin="lower", aspect="auto")
    im_y = ax_y.imshow(_reshape(y0), cmap="gray_r", vmin=0.0, vmax=1.0,
                        origin="lower", aspect="auto")
    im_lam = ax_lam.imshow(_reshape(lam0), cmap="RdBu_r",
                            vmin=-lam_abs_max, vmax=lam_abs_max,
                            origin="lower", aspect="auto")

    for ax, ttl in zip(axes, ["x (density)", "y (copy)", "λ (multiplier)"]):
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(ttl, fontsize=10)

    suptitle = fig.suptitle(f"iter {k0:04d}", fontsize=12)
    fig.tight_layout()

    def update(i):
        x, y, lam, k = frames[i]
        im_x.set_data(_reshape(x))
        im_y.set_data(_reshape(y))
        im_lam.set_data(_reshape(lam))
        suptitle.set_text(f"iter {k:04d}")
        return [im_x, im_y, im_lam, suptitle]

    ani = animation.FuncAnimation(fig, update, frames=len(frames),
                                  blit=False, interval=int(1000 / fps))

    mp4_path = os.path.join(image_dir, "movie.mp4")
    gif_path = os.path.join(image_dir, "movie.gif")
    saved_path = None
    try:
        ani.save(mp4_path, writer=animation.FFMpegWriter(fps=fps))
        saved_path = mp4_path
        print(f"  [movie] saved {mp4_path}")
    except Exception:
        try:
            ani.save(gif_path, writer=animation.PillowWriter(fps=fps))
            saved_path = gif_path
            print(f"  [movie] saved {gif_path}  (GIF fallback; ffmpeg unavailable)")
        except Exception as exc:
            print(f"  [movie] WARNING: could not save movie: {exc}")

    plt.close(fig)
    return saved_path


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

def filter_admm_compliance_tv(
    nelx,
    nely,
    penal,
    alpha,
    budget,
    # filter / restoration parameters ----------------------------------------
    rho_init=1.0,
    beta=0.99,
    gamma=1e-5,
    sigma=1e-5,
    U=10.0,
    max_outer=100,
    max_inner=20,
    max_restoration=30,
    eps_opt=1e-3,
    omega_tau=1.0,
    # subproblem solver knobs ------------------------------------------------
    x_lo=1e-4,
    max_iter_x=100,
    max_iter_y=2000,
    tol_x=1e-6,
    tol_y=1e-8,
    # diagnostics ------------------------------------------------------------
    verbose=True,           # outer-iteration log rows
    verbose_inner=True,     # inner-iteration log rows (one per ADMM step)
    plot=False,             # per-outer-iteration heat-map PDFs (iter_NNNN.pdf)
    plot_inner=False,       # per-inner-iteration heat-map PDFs (iter_NNNN_jJJ.pdf)
    movie=False,            # assemble outer iterates into images/movie.mp4 (or .gif)
    outer_callback=None,
    x_inner_callback=None,
    y_inner_callback=None,
):
    """
    Solve  min F(x) + alpha*TV(x)  s.t. sum(x) <= budget, x in [x_lo, 1]^n
    with the double-loop ADMM-Filter algorithm.

    Parameters
    ----------
    nelx, nely : int
        Mesh dimensions (number of finite elements).
    penal : float
        SIMP penalisation exponent.
    alpha : float
        TV regularisation weight.
    budget : float
        Upper bound on sum(x) (volume budget).
    rho_init : float
        Initial ADMM penalty parameter rho_0.
    beta, gamma : float in (0, 1)
        Filter acceptance constants (eq. (filter)).
    sigma : float
        Sufficient-decrease constant for L_rho (eq. (suffRed)).  Failures are
        logged but do NOT trigger a retry; the inner-iteration cap acts as the
        recovery mechanism (per the agreed design).
    U : float
        Restoration trigger threshold for primal infeasibility:
        restore when  eta >= beta * U  (eq. (8)).
    max_outer : int
        Maximum number of outer (k-loop) iterations.
    max_inner : int
        Maximum inner (j-loop) iterations per outer iteration.  Reaching this
        cap is treated as a third restoration trigger.
    max_restoration : int
        Maximum backtracking steps in the restoration m-loop.  On overflow the
        driver returns with converged=False and reason='restoration_failed'.
    eps_opt : float
        Optimality tolerance: terminate when both eta and omega <= eps_opt.
    omega_tau : float
        Step size used inside compute_omega's proximal-gradient residual.
        Default 1.0 matches eq. (omega) literally.
    x_lo : float
        Lower bound on each x_v (keeps 1/x_v finite in the reciprocal solver).
    max_iter_x, max_iter_y : int
        Inner solver iteration caps for the x- and y-updates.
    tol_x, tol_y : float
        Inner solver tolerances.
    verbose : bool
        Print one tabular log row per outer iteration if True.  A header is
        printed once at the start whenever either verbose or verbose_inner is
        True.
    verbose_inner : bool
        Print one tabular log row per inner (j-loop) ADMM step if True.
        Independent of `verbose`.  Default True; pass False for outer-only
        logging.
    plot : bool
        If True, save plots to ``images/`` (created if missing): one
        ``convergence.pdf`` (eta and omega vs outer iteration on log-scale
        twin y-axes) and one ``iter_NNNN.pdf`` per outer iteration containing
        2D heat maps of the accepted (x, y, lambda).  matplotlib is imported
        lazily so it remains optional when both plot and plot_inner are False.
    plot_inner : bool
        If True, additionally save one ``iter_NNNN_jJJ.pdf`` per inner ADMM
        step (same 1x3 layout, plotting the per-step candidate (x, y, lambda)).
        Default False -- on a typical run this can produce hundreds of files.
    outer_callback(x, y, k) : callable or None
        Called once per outer iteration with the accepted (x, y) and index k.
    x_inner_callback, y_inner_callback : callables or None
        Forwarded to the x- and y-subproblem solvers.

    Returns
    -------
    x : (n,) array
        Accepted design at termination.
    info : dict
        Diagnostic record, with keys:
            'y'                    final auxiliary variable
            'lam'                  final ADMM dual variable
            'rho'                  final penalty parameter
            'n_iter'               number of outer iterations performed
            'converged'            True iff (eta, omega) <= eps_opt at exit
            'reason'               one of 'converged', 'max_outer',
                                   'restoration_failed'
            'objective'            ndarray, F(x) + alpha*TV(x) per outer iter
            'eta_history'          ndarray, accepted eta per outer iter
            'omega_history'        ndarray, accepted omega per outer iter
            'rho_history'          ndarray, rho per outer iter
            'filter_size_history'  ndarray, |F_k| per outer iter
            'inner_iter_history'   ndarray, # inner steps per outer iter
            'restoration_count'    total restoration phases triggered
            'suff_dec_failures'    total sufficient-decrease violations
            'filter_entries'       list of (eta, omega) at exit
    """
    _t_algo_start = time.perf_counter()

    n = nelx * nely
    edges = build_grid_edges(nelx, nely)
    fem = ComplianceProblem(nelx, nely, penal)
    flt = Filter(beta=beta, gamma=gamma)

    # Lazy plotting setup: matplotlib is only imported (and images/ ensured)
    # when the user explicitly opts in, so it stays an optional dependency.
    # Either plot=True (per-outer-iteration PDFs) or plot_inner=True (per-inner
    # PDFs) triggers the import.
    plt = mcolors = None
    image_dir = "images"
    if plot or plot_inner or movie:
        import matplotlib.pyplot as plt          # noqa: E402, local rebind is intentional
        import matplotlib.colors as mcolors      # noqa: E402
        os.makedirs(image_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Initialise (x, y, lam, rho).  Uniform feasible design satisfies the
    # budget and gives eta_0 = ||x - y||^2 = 0 by construction.
    # ------------------------------------------------------------------
    x = np.full(n, np.clip(budget / n, x_lo, 1.0))
    y = x.copy()
    lam = np.zeros(n)
    rho = float(rho_init)

    # Iteration counts and CPU times, accumulated across all subproblem solves.
    # Initialized here (before the first compute_omega call) so they are in scope
    # for all four compute_omega call sites.
    total_iter_x    = 0      # reciprocal_approximation iters, summed over all x-updates
    total_iter_y    = 0      # Chambolle-Pock iters, summed over all y-updates
    total_iter_prox = 0      # Chambolle-Pock iters inside compute_omega, all calls
    total_time_x    = 0.0    # CPU time for all reciprocal_approximation calls
    total_time_y    = 0.0    # CPU time for all chambolle_pock_graph_tv (y-update) calls
    total_time_prox = 0.0    # CPU time for all compute_omega calls

    eta_k = compute_eta(x, y)
    _t0 = time.perf_counter()
    omega_k, _n_cp = compute_omega(x, y, lam, fem, edges, alpha, rho, budget, x_lo,
                                   tau=omega_tau)
    total_time_prox += time.perf_counter() - _t0
    total_iter_prox += _n_cp
    # Initial filter add: only legal when eta > 0 (Filter.add raises otherwise).
    # With uniform init eta_0 == 0, so the filter starts empty; the inner loop
    # always takes at least one step (see comment below) so this is safe.
    if eta_k > 0:
        flt.add(eta_k, omega_k)

    # ------------------------------------------------------------------
    # History buffers
    # ------------------------------------------------------------------
    obj_hist = []
    eta_hist = []
    omega_hist = []
    rho_hist = []
    filter_size_hist = []
    inner_iter_hist = []
    restoration_count = 0
    suff_dec_failures = 0
    converged = False
    reason = "max_outer"
    _movie_frames = []   # (x, y, lam, k_one_based) per outer iterate; used when movie=True
    _movie_path = None

    # Print the tabular log header once if any per-iteration logging is on.
    # (Per-row prints inside the loop reuse the same _LOG_FMT template so the
    # data columns line up under the header.)
    if verbose or verbose_inner:
        _print_log_header()

    # ==================================================================
    # Outer loop (k)
    # ==================================================================
    k = 0
    for k in range(max_outer):
        # --------------- termination check (eq. (etaOpt), (omegaOpt)) ---
        if eta_k <= eps_opt and omega_k <= eps_opt:
            converged = True
            reason = "converged"
            break

        # --------------- inner-loop working state -----------------------
        x_j = x.copy()
        y_j = y.copy()
        eta_j = eta_k
        omega_j = omega_k
        F_val_j, _ = fem(x_j)
        tv_val_j = _tv_value(y_j, edges)   # TV is on y in the augmented Lagrangian

        n_inner_this = 0
        restoration_failed = False

        # ==============================================================
        # Inner loop (j).  Always takes at least one ADMM step: the
        # acceptance test in the meeting-notes pseudocode is at the loop
        # top, which would short-circuit the loop on an empty filter.
        # We test acceptance AFTER each step so that empty-filter +
        # uniform init (eta_0 == 0) still makes progress.
        # ==============================================================
        for j in range(max_inner):
            n_inner_this += 1

            # ----- ADMM x-update ---------------------------------------
            # min_x F(x) + (rho/2)||x - (y_j + lam/rho)||^2 on X
            # Quadratic data:  a_v = rho/2,  b_v = -rho * (y_j + lam/rho)_v
            y_hat = y_j + lam / rho
            a_v = np.full(n, rho / 2.0)
            b_x = -rho * y_hat

            # Cache pre-step Lagrangian for the sufficient-decrease check.
            L_prev = compute_lagrangian(x_j, y_j, lam, F_val_j, tv_val_j,
                                         alpha, rho)
            omega_prev = omega_j

            _t0 = time.perf_counter()
            x_jp1, _x_info = reciprocal_approximation(
                fem, a_v, b_x, budget,
                x_init=x_j, max_iter=max_iter_x, tol=tol_x, x_lo=x_lo,
                callback=x_inner_callback,
            )
            total_time_x += time.perf_counter() - _t0
            total_iter_x  += _x_info["n_iter"]

            # ----- ADMM y-update ---------------------------------------
            # min_y alpha*TV(y) + (rho/2)||y - (x_jp1 - lam/rho)||^2 on Y
            x_hat = x_jp1 - lam / rho
            b_y = -rho * x_hat

            _t0 = time.perf_counter()
            y_jp1, _y_info = chambolle_pock_graph_tv(
                n, edges, a_v, b_y,
                budget=budget, alpha=alpha, x_lo=x_lo,
                max_iter=max_iter_y, tol=tol_y,
                callback=y_inner_callback, x_init=y_j,
            )
            total_time_y += time.perf_counter() - _t0
            total_iter_y  += _y_info["n_iter"]

            # ----- evaluate the new iterate ----------------------------
            eta_jp1 = compute_eta(x_jp1, y_jp1)
            _t0 = time.perf_counter()
            omega_jp1, _n_cp = compute_omega(x_jp1, y_jp1, lam, fem, edges,
                                             alpha, rho, budget, x_lo, tau=omega_tau)
            total_time_prox += time.perf_counter() - _t0
            total_iter_prox  += _n_cp
            F_jp1, _ = fem(x_jp1)
            tv_jp1 = _tv_value(y_jp1, edges)
            L_new = compute_lagrangian(x_jp1, y_jp1, lam, F_jp1, tv_jp1,
                                       alpha, rho)

            # Sufficient-decrease check (eq. (suffRed)): log only.
            if (L_prev - L_new) < sigma * omega_prev:
                suff_dec_failures += 1

            # ----- restoration triggers -------------------------------
            # eq. (8):  eta >= beta * U
            # eq. (9):  omega <= eps_opt  AND  eta >= beta * eta_min
            # extra :   j+1 == max_inner  (per agreed design)
            eta_min_F = flt.eta_min()  # +inf when filter empty
            trig_8 = eta_jp1 >= beta * U
            trig_9 = (omega_jp1 <= eps_opt) and (eta_jp1 >= beta * eta_min_F)
            trig_M = (j + 1 == max_inner)
            # Single named flag so the inner-row log can mark restoration steps
            # (cleaner than re-evaluating the OR after the if-block runs and
            # potentially mutates rho via the doubling).
            restored_this_inner = trig_8 or trig_9 or trig_M

            if restored_this_inner:
                # Restoration: y_hat_m = x_jp1 + 2^{-m} (y_jp1 - x_jp1)
                # Drives eta -> 0 (since y_hat_m -> x_jp1) so eventually any
                # filter entry is dominated on the eta-branch.
                accepted = False
                for m in range(1, max_restoration + 1):
                    y_hat_m = x_jp1 + (0.5 ** m) * (y_jp1 - x_jp1)
                    eta_hat = compute_eta(x_jp1, y_hat_m)
                    _t0 = time.perf_counter()
                    omega_hat, _n_cp = compute_omega(x_jp1, y_hat_m, lam,
                                                     fem, edges, alpha, rho, budget,
                                                     x_lo, tau=omega_tau)
                    total_time_prox += time.perf_counter() - _t0
                    total_iter_prox  += _n_cp
                    if flt.is_acceptable(eta_hat, omega_hat):
                        y_jp1 = y_hat_m
                        eta_jp1 = eta_hat
                        omega_jp1 = omega_hat
                        tv_jp1 = _tv_value(y_jp1, edges)
                        accepted = True
                        break

                if not accepted:
                    restoration_failed = True
                    # Roll x_jp1, y_jp1 forward as the (failed) candidate so
                    # the outer loop has something to return.
                    pass

                # Double rho whether or not the inner backtracking succeeded
                # (matches the pseudocode which performs the rho update
                # unconditionally inside the restoration branch).
                rho = 2.0 * rho
                restoration_count += 1

            # ----- promote (x_jp1, y_jp1, ...) to working state -------
            x_j = x_jp1
            y_j = y_jp1
            eta_j = eta_jp1
            omega_j = omega_jp1
            F_val_j = F_jp1
            tv_val_j = tv_jp1

            # ----- per-inner-iteration log + plot ---------------------
            # Logged AFTER restoration so the row reflects the values that
            # this inner step actually committed (or, if restoration failed,
            # the failed candidate -- useful for diagnostics).
            #
            # If restoration ran, it may have replaced y_jp1 (and updated
            # eta_jp1/omega_jp1/tv_jp1) and doubled rho.  L_new from above
            # was computed with the pre-restoration values, so we must
            # recompute the Lagrangian here in that case.
            if verbose_inner or plot_inner:
                obj_jp1 = F_jp1 + alpha * tv_jp1
                if restored_this_inner:
                    L_disp = compute_lagrangian(x_jp1, y_jp1, lam,
                                                F_jp1, tv_jp1, alpha, rho)
                else:
                    L_disp = L_new
                r_mark_inner = "R" if restored_this_inner else ""

                if verbose_inner:
                    print(_LOG_FMT.format(
                        io="inner",
                        it=f"{k+1}.{j+1}",
                        obj=f"{obj_jp1:.4f}",
                        F=f"{F_jp1:.4f}",
                        TV=f"{tv_jp1:.4f}",
                        L=f"{L_disp:.4f}",
                        eta=f"{eta_jp1:.2e}",
                        omega=f"{omega_jp1:.2e}",
                        rho=f"{rho:.2e}",
                        nf=str(len(flt)),
                        R=r_mark_inner,
                    ))
                if plot_inner:
                    # lam is the OUTER-loop dual; it doesn't change inside
                    # the inner loop, so plotting it on every inner step
                    # mirrors what the outer plot will eventually capture.
                    _save_iter_heatmap(x_jp1, y_jp1, lam, k + 1, nelx, nely,
                                       image_dir, plt, mcolors,
                                       j_one_based=j + 1)

            # If restoration failed, abort the inner loop.
            if restoration_failed:
                break

            # Filter acceptance check (always after at least one step).
            # After successful restoration the new (eta, omega) was already
            # accepted above, so this exits naturally.
            if flt.is_acceptable(eta_j, omega_j):
                break

        # --------------- accepted iterate -----------------------------
        # Multiplier update: lam <- lam - rho * (x - y)
        # Equivalent to admm.py's `lam += rho * (y - x)` (and matches the
        # sign convention in the meeting-notes algorithm).
        x = x_j
        y = y_j
        lam = lam - rho * (x - y)

        # Recompute (eta, omega) after the multiplier update.  We pass rho=0
        # (NOT the current rho) so this evaluates the first-order error of
        # the ORIGINAL (unpenalized) Lagrangian -- which is what eq. (omegaOpt)
        # actually tests against.  By the identity in §3.3 of the meeting
        # notes,
        #     ω̃_ρ(x^{k+1}, y^{k+1}, λ^k) = ω̃_0(x^{k+1}, y^{k+1}, λ^{k+1})
        # after the multiplier update, so this value also equals the last
        # inner-iteration ω; recomputing both eta and omega here is therefore
        # redundant and could be skipped, but we keep the recompute while
        # validating the algorithm.  The actual rho variable is unchanged --
        # only the argument to this single compute_omega call is zeroed.
        eta_k = compute_eta(x, y)
        _t0 = time.perf_counter()
        omega_k, _n_cp = compute_omega(x, y, lam, fem, edges, alpha, 0.0, budget,
                                       x_lo, tau=omega_tau)
        total_time_prox += time.perf_counter() - _t0
        total_iter_prox  += _n_cp

        # Add accepted iterate to filter (only if infeasible per pseudocode).
        if eta_k > 0:
            flt.add(eta_k, omega_k)

        # Logging
        F_val, _ = fem(x)
        tv_x = _tv_value(x, edges)
        obj = F_val + alpha * tv_x
        obj_hist.append(obj)
        eta_hist.append(eta_k)
        omega_hist.append(omega_k)
        rho_hist.append(rho)
        filter_size_hist.append(len(flt))
        inner_iter_hist.append(n_inner_this)

        if verbose:
            # The augmented Lagrangian uses TV(y), NOT TV(x) -- different
            # from the objective.  Compute it once here so the L column is
            # consistent with the inner rows.  Both calls are pure scalar
            # arithmetic on already-computed quantities (no extra FEM solve).
            tv_y = _tv_value(y, edges)
            L_outer = compute_lagrangian(x, y, lam,
                                         F_val, tv_y, alpha, rho)
            # Mark "R" when this outer iteration triggered restoration.
            # rho only changes via restoration, so a rho-change detection is
            # the authoritative outer-row signal even when inner logging is off.
            rho_changed = (len(rho_hist) >= 2 and rho_hist[-1] != rho_hist[-2]) \
                          or (len(rho_hist) == 1 and rho_hist[-1] != rho_init)
            mark = "R" if rho_changed else ""
            print(_LOG_FMT.format(
                io="outer",
                it=str(k + 1),
                obj=f"{obj:.4f}",
                F=f"{F_val:.4f}",
                TV=f"{tv_x:.4f}",
                L=f"{L_outer:.4f}",
                eta=f"{eta_k:.2e}",
                omega=f"{omega_k:.2e}",
                rho=f"{rho:.2e}",
                nf=str(len(flt)),
                R=mark,
            ))

        if outer_callback is not None:
            outer_callback(x.copy(), y.copy(), k)

        if plot:
            _save_iter_heatmap(x, y, lam, k + 1, nelx, nely,
                               image_dir, plt, mcolors)

        if movie:
            _movie_frames.append((x.copy(), y.copy(), lam.copy(), k + 1))

        if restoration_failed:
            reason = "restoration_failed"
            converged = False
            break

    if plot and len(eta_hist) > 0:
        _save_convergence_plot(eta_hist, omega_hist, rho_hist, rho_init, image_dir, plt)

    if movie and _movie_frames:
        _movie_path = _save_movie(_movie_frames, nelx, nely, image_dir, plt, mcolors)

    _total_time_algo = time.perf_counter() - _t_algo_start

    info = {
        "y":                   y,
        "lam":                 lam,
        "rho":                 rho,
        "n_iter":              k + 1,
        "converged":           converged,
        "reason":              reason,
        "objective":           np.array(obj_hist),
        "eta_history":         np.array(eta_hist),
        "omega_history":       np.array(omega_hist),
        "rho_history":         np.array(rho_hist),
        "filter_size_history": np.array(filter_size_hist),
        "inner_iter_history":  np.array(inner_iter_hist),
        "restoration_count":   restoration_count,
        "suff_dec_failures":   suff_dec_failures,
        "filter_entries":      list(flt),
        "movie_path":          _movie_path,
        "total_iter_x":        total_iter_x,
        "total_iter_y":        total_iter_y,
        "total_iter_prox":     total_iter_prox,
        "total_time_x":        total_time_x,
        "total_time_y":        total_time_y,
        "total_time_prox":     total_time_prox,
        "total_time_pde":      fem.total_time_pde,
        "total_time_adjoint":  fem.total_time_adjoint,
        "n_pde_calls":         fem.n_pde_calls,
        "total_time":          _total_time_algo,
    }
    return x, info


# ---------------------------------------------------------------------------
# Self-test: 30 x 10 default, mirrors admm.py's __main__
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Command-line interface: only the most-tweaked knobs are exposed.
    # All other parameters of filter_admm_compliance_tv (filter constants,
    # restoration caps, tolerances) keep their in-file defaults below; for
    # those, use the programmatic interface (see RASC-MeetingNotes.tex §5.3).
    parser = argparse.ArgumentParser(
        description=(
            "ADMM-Filter for compliance + graph-TV topology optimisation. "
            "Defaults reproduce the 30x10 / 40% / alpha=0.5 self-test."
        )
    )
    parser.add_argument("--nelx",    type=int,   default=30,
                        help="Number of elements in x (default: 30).")
    parser.add_argument("--nely",    type=int,   default=10,
                        help="Number of elements in y (default: 10).")
    parser.add_argument("--volfrac", type=float, default=0.4,
                        help="Volume fraction; budget = volfrac*nelx*nely "
                             "(default: 0.4).")
    parser.add_argument("--penal",   type=float, default=3.0,
                        help="SIMP penalisation exponent (default: 3.0).")
    parser.add_argument("--alpha",   type=float, default=0.5,
                        help="Graph-TV regularisation weight (default: 0.5).")
    parser.add_argument("--plot",    action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Save convergence + per-iter heat-map PDFs to "
                             "images/ (default: --plot).")
    parser.add_argument("--verbose", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Print per-outer-iteration trajectory rows "
                             "(default: --verbose).")
    parser.add_argument("--verbose-inner", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Print per-inner-iteration trajectory rows "
                             "(default: --verbose-inner).")
    parser.add_argument("--plot-inner", action=argparse.BooleanOptionalAction,
                        default=False,
                        help="Save per-inner-iteration heat-map PDFs to "
                             "images/iter_NNNN_jJJ.pdf "
                             "(default: --no-plot-inner).")
    parser.add_argument("--movie", action=argparse.BooleanOptionalAction,
                        default=False,
                        help="Generate images/movie.mp4 (or images/movie.gif if "
                             "ffmpeg is unavailable) from outer-iteration frames "
                             "(default: --no-movie).")
    args = parser.parse_args()

    nelx, nely = args.nelx, args.nely
    n          = nelx * nely
    budget     = args.volfrac * n     # absolute budget derived from volfrac

    print("=" * 72)
    # Banner line is now derived from the actual CLI values so the printout
    # always matches the run.  ":g" formats 0.4 -> 40, 0.333 -> 33.3 cleanly.
    print(f"FilterADMM self-test: {nelx} x {nely} cantilever, "
          f"{args.volfrac * 100:g}% volume fraction")
    print("=" * 72)

    x_opt, info = filter_admm_compliance_tv(
        nelx=nelx, nely=nely,
        penal=args.penal,
        alpha=args.alpha,
        budget=budget,
        rho_init=1.0,
        beta=0.99,
        gamma=1e-5,
        sigma=1e-5,
        U=10.0,
        max_outer=60,
        max_inner=20,
        max_restoration=30,
        eps_opt=1e-2,         # match admm.py's tol_primal/tol_dual default
        omega_tau=1.0,
        x_lo=1e-4,
        verbose=args.verbose,
        verbose_inner=args.verbose_inner,
        plot=args.plot,
        plot_inner=args.plot_inner,
        movie=args.movie,
    )

    print()
    print("-" * 72)
    print(f"Reason             : {info['reason']}")
    print(f"Converged          : {info['converged']}")
    print(f"Outer iterations   : {info['n_iter']}")
    print(f"Total restorations : {info['restoration_count']}")
    print(f"Suff. dec failures : {info['suff_dec_failures']}")
    print(f"Final rho          : {info['rho']:.3e}")
    print(f"Final |F|          : {len(info['filter_entries'])}")
    print(f"Final eta          : {info['eta_history'][-1]:.3e}")
    print(f"Final omega        : {info['omega_history'][-1]:.3e}")
    print(f"sum(x*)            : {x_opt.sum():.3f}  (budget = {budget:.1f})")
    print(f"Final objective    : {info['objective'][-1]:.4f}")

    # ---- Diagnostic: largest eta-jump along the accepted trajectory ------
    # admm.py exhibits a sustained ~70x eta-jump at iter 27 that it does NOT
    # recover from.  Isolated jumps in the FilterADMM trajectory are normal
    # (the filter accepts grown-eta iterates when the omega-branch fires);
    # what matters is that the run terminates with reason='converged'.
    eta = info['eta_history']
    if len(eta) >= 2:
        ratios = eta[1:] / np.maximum(eta[:-1], 1e-300)
        max_jump = float(ratios.max())
        max_jump_idx = int(ratios.argmax())
        print(f"Max eta-jump ratio : {max_jump:.2f}  "
              f"(at outer iter {max_jump_idx+1} -> {max_jump_idx+2})")

    print()
    print("Filter contents at exit:")
    for i, (eta_l, omega_l) in enumerate(info['filter_entries']):
        print(f"  [{i}]  eta = {eta_l:.3e}   omega = {omega_l:.3e}")

    print()
    print("Subproblem statistics:")
    print(f"  x-update  (reciprocal approx) : {info['total_iter_x']:7d} iters   {info['total_time_x']:.3f} s")
    print(f"  y-update  (Chambolle-Pock)    : {info['total_iter_y']:7d} iters   {info['total_time_y']:.3f} s")
    print(f"  prox-grad (CP inside omega)   : {info['total_iter_prox']:7d} iters   {info['total_time_prox']:.3f} s")
    print(f"  PDE solve (K assem + spsolve) : {info['n_pde_calls']:7d} calls   {info['total_time_pde']:.3f} s")
    print(f"  Adjoint   (gradient/sensitiv) :                   {info['total_time_adjoint']:.3f} s")
    print(f"  Total algorithm time          :                   {info['total_time']:.3f} s")
