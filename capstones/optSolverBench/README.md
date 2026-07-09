# optSolverBench - Optimizer & Solver Benchmarking for PDE-Constrained Optimization

## Purpose

This capstone is a **variation of [SolverBench](../SolverBench/README.md)**. Where
SolverBench benchmarks solver + preconditioner combinations for a *forward* PDE
(Poisson baseline → Stokes deep dive), **optSolverBench focuses on a
PDE-constrained *optimization* problem instead of a Stokes solver**: the inverse
Poisson source-identification problem. The forward Stokes solve is replaced by an
outer optimization loop wrapped around a Poisson solve, and the benchmarking
question moves up a level — from *which linear solver wins* to *which optimizer +
gradient + inner-solve strategy wins, and where*.

Build a small, **reproducible benchmarking study** that answers a question the
inverse-problems literature keeps re-asking without settling: *for a given
PDE-constrained optimization problem, which outer optimizer + inner PDE-solve +
preconditioning strategy is fastest and most robust, and how does that change with
mesh resolution, regularization, noise, and sensor coverage?* There are many good
options and no universal winner — the contribution is a **fair, reproducible map**
of where each one wins, not folklore.

This is a *files, not chats* capstone: you develop the entire project from this
README using the skills from the exercises — a project `CLAUDE.md` for
conventions, plan mode for the harness, `MEMORY.md` for durable findings,
`STATUS.md` for handoffs, and a skill or two for the repetitive parts. Nothing
else ships. The code is yours to write.

- **Scope: two afternoons.** Afternoon 1 → a working harness + the well-posed
  baseline. Afternoon 2 → the ill-posed study + a paper draft. Depth on a narrow,
  honest comparison beats a broad shallow sweep.
- **Deliverable: a publication** — a short, reproducible benchmark/methods note.
  This kind of paper lives or dies on its methodology and its archived,
  re-runnable results. See *Publication outlets* at the end.

## Install

This project runs in **Firedrake**, inside its official Docker image — the same
environment as the PDE track. Firedrake gives you the finite-element forward and
adjoint Poisson solves, PETSc solvers via `solver_parameters` (CG with ILU/AMG, or
MUMPS), and **pyadjoint** for the exact discrete adjoint gradient and the Taylor
test — everything the benchmark needs from a single stack.

**Install Docker and pull the Firedrake image by following the PDE track's install
guide:**
[`../../exercises-pde/01-claude-md/INSTALL.md`](../../exercises-pde/01-claude-md/INSTALL.md).
It walks through installing Docker and running the `firedrakeproject/firedrake`
image with your working folder bind-mounted in. As in the PDE exercises, run
`claude` on the host and run the Python *inside* the container.

## The research gap

"Which optimizer should I use for this inverse problem?" is usually answered by
habit, a neighbor's advice, or the first thing that converged. For reduced-space,
regularized PDE-constrained optimization the honest answer is *it depends* — on
the mesh, the regularization, the noise, how accurately you solve the forward and
adjoint PDEs each iteration, and what you are optimizing (outer iterations, total
PDE solves, wall clock, memory, robustness, reconstruction accuracy). A careful
study that holds everything fixed except one axis, reports **where the winner
changes**, and ships a re-runnable harness is a genuine, publishable contribution.

## A quick PDE-constrained-optimization primer

*Read this if you are not a PDE-constrained-optimization specialist. Experts can
skip to the problem statement.*

The problem has two nested loops. The **inner loop** solves a PDE; the **outer
loop** searches over the unknown you actually want.

**Reduced space.** For each candidate source `f`, you solve the forward PDE to get
`u(f)`, evaluate the objective `J(f)`, and compute the gradient `∇J(f)` with the
**adjoint method** — one extra linear solve, *independent of the number of
unknowns in `f`*. In Firedrake, **pyadjoint** records the forward solve and
produces this exact discrete adjoint for you. The outer optimizer never sees the
PDE; it only sees `f`, `J(f)`, and `∇J(f)`. This is why the adjoint is the whole
game: get it exact and cheap, and the outer loop is a standard optimization.

**Outer optimizers** come in two families — the direct/iterative split of
SolverBench, one level up. All are driven through pyadjoint's `ReducedFunctional`
(which supplies the gradient, and a Hessian action via a second-order adjoint),
using `scipy.optimize`, ROL, or PETSc TAO as the engine.

| Family | Idea | Strengths | Weaknesses |
|---|---|---|---|
| **First-order / quasi-Newton** | use only `J` and `∇J`; build curvature from the gradient history (**L-BFGS**) or take (nonlinear) CG / steepest-descent steps | cheap per outer step; one forward + one adjoint solve per evaluation | outer iteration count can grow with mesh refinement and ill-conditioning |
| **Newton-type (second-order)** | use **Hessian–vector products** (a second adjoint solve, or Gauss–Newton) inside a Krylov inner solve — **Newton-CG** / Gauss–Newton-CG | outer iteration counts can be **mesh-independent**; fast near the optimum | each outer step costs several PDE solves; needs a good inner Krylov solve + preconditioner |

**The inner PDE solve is SolverBench.** Every objective and gradient evaluation
requires a forward Poisson solve and an adjoint Poisson solve — the *same* SPD
elliptic operator SolverBench studies in Phase 1. The solver + preconditioner
choices there reappear here as the **engine inside each outer iteration**, selected
through Firedrake `solver_parameters` (which *are* PETSc options). optSolverBench
asks how that inner choice interacts with the outer optimizer.

| Inner solver | Role here | Notes |
|---|---|---|
| **MUMPS (direct LU)** | robust reference for the forward/adjoint solves | reuse one factorization across every outer iteration — huge amortization |
| **CG + ILU** | cheap iterative inner solve | inner iterations grow as you refine — the "bad" inner baseline |
| **CG + AMG** (GAMG / hypre BoomerAMG) | scalable inner solve | ~mesh-independent inner cost; the honest choice for large meshes |

**Two more knobs that are unique to the optimization setting:**

- **Regularization `α`.** The data-misfit term alone is ill-posed; the Tikhonov
  term `α‖f‖²` makes the reduced problem solvable and controls the
  bias/variance trade-off. It is a *property of the test case*, not a solver tuning
  knob.
- **Inner-solve accuracy (inexactness).** You need not solve the forward/adjoint
  PDEs to machine precision every outer iteration. **Inexact / truncated** schemes
  loosen the inner tolerance early and tighten it near the optimum — a real
  speedup, but only if done as a *declared, controlled axis*, because a sloppy
  inner solve produces a sloppy gradient.

**"Mesh-independent"** is the phrase you'll use most — here it means the *outer*
iteration count stays flat as you refine the mesh. That is the gold standard: it
says the optimizer's cost per unknown is bounded, so the method scales.

## Problem statement

Identify the source term `f` in

```
−Δu = f   on   Ω = (0,1)²,        u = 0   on   ∂Ω
```

from noisy measurements of `u` at sensor points. You solve the reduced-space,
Tikhonov-regularized least-squares problem

```
min_f   ½ ‖ S·u(f) − u_obs ‖₂²  +  α ‖f‖₂²
```

where `u(f)` solves the PDE for the given `f` and `S` is the sensor sampling
operator. The gradient `∇J(f)` is the **exact discrete adjoint** (see the
integrity warning — this is the single most important rule in the project).

You will benchmark across two regimes, in order of difficulty.

| Phase | Regime | Character | The question that matters |
|---|---|---|---|
| **1 — baseline** | well-posed: moderate `α`, low noise, dense sensors | smooth, well-conditioned reduced problem | Can you get **mesh-independent** outer-iteration counts, and does the adjoint gradient pass a **Taylor test**? Validates the harness and the metrics before anything hard. |
| **2 — the study** | ill-posed: small `α`, higher noise, sparse sensors | ill-conditioned, near-singular reduced Hessian | Which optimizer + inner-solve + preconditioner is fastest and most robust across mesh, `α`, and noise? This is where "no clear winner" is real. |

**Optional intermediate bridge (only if you're ahead of schedule).** *Truncated
Newton-CG with adjoint Hessian–vector products* sits between pure first-order and
full second-order methods: it never forms the reduced Hessian, using it only
through second-adjoint matrix–vector products inside an inner CG solve, and
"truncates" that inner solve early far from the optimum. It's the cleanest on-ramp
to second-order behavior and reuses most of the Phase-2 machinery. Put it in your
plan; implement it only if Phase 2 finishes early. (A second natural bridge is a
regularization study: sweep `α` and draw the **L-curve** to pick it honestly.)

### Phase 2 design choice: gradient and Hessian access

The central Phase-2 design choice is *how much derivative information you buy*:

| Access level | What you compute | Trade-off |
|---|---|---|
| **First-order** (L-BFGS) | exact adjoint gradient only | cheapest per step; iteration count degrades as the reduced Hessian conditions worsen (small `α`, fine mesh) |
| **Gauss–Newton** | gradient + Gauss–Newton Hessian–vector products (drops the second-derivative term) | robust curvature for least-squares misfits; great when the residual is small |
| **Full Newton-CG** | gradient + exact Hessian–vector products (second adjoint) | fewest, mesh-independent outer iterations; most PDE solves per step |

Benchmarking these three against a shared set of inner solvers is a clean,
self-contained Phase-2 result. For *why* second-order pays off as the problem
becomes ill-posed, see *Background*.

## Suggested approach

Build the harness for the well-posed case first, get it honest, then turn up the
difficulty. **The harness is the deliverable; the regime is a slot.**

### Afternoon 1 — the harness + the well-posed baseline

**Step 1. Build the benchmarking harness.**
- One driver that runs a single `(regime, optimizer, inner-solver, mesh
  refinement, α)` combination and records a *fixed set of numbers* — so every run
  is comparable.
- Record, per run:
  - **outer iteration count** and the optimizer's convergence reason (did the
    reduced-gradient norm actually reach the tolerance?)
  - the independently recomputed **true reduced-gradient norm `‖∇J(f*)‖`** at
    termination (see the integrity warning)
  - total **forward solves and adjoint solves** — the real cost currency, not
    outer iterations
  - the **reconstruction error `‖f* − f_true‖₂`** (relative L2) — the accuracy
    that actually matters
  - **setup time** vs. **solve time**, separately, and peak memory
  - number of **degrees of freedom** (problem size)
  - the **fully resolved solver options** (the inner `solver_parameters` and
    `-ksp_view` dump; the optimizer options) + **Firedrake/PETSc versions** and the
    noise seed
- Output: one JSON summary per run, written to a dated `runs/<timestamp>/` folder.

**Step 1½. Gate the harness on a Taylor test.** Before trusting *any* benchmark
number, verify the adjoint gradient with a finite-difference **Taylor test**
(pyadjoint's `taylor_test`): the remainder `|J(f+εδf) − J(f) − ε∇J·δf|` must shrink
like `ε²`. A gradient that fails this is descending on a different functional — fix
it before Step 2. (This is the exact analog of SolverBench recomputing
`‖b − Ax‖₂`.)

**Step 2. Solve the well-posed baseline** (moderate `α`, low noise, dense sensors)
and compare these optimizers, all with the *same* inner solver family:

| Label | Outer optimizer | Inner PDE solve | Expectation |
|---|---|---|---|
| `direct_lbfgs` | L-BFGS | MUMPS (direct, reused factorization) | robust reference; watch memory grow |
| `lbfgs_ilu` | L-BFGS | CG + ILU | inner + outer cost grows on refinement — the "bad" baseline |
| `lbfgs_amg` | L-BFGS | CG + AMG (GAMG / hypre) | inner cost ~mesh-independent |
| `newtoncg` *(stretch)* | Newton-CG (adjoint Hessian–vec) | CG + AMG inner | should give ~mesh-independent **outer** iterations |

**Produce:** the **mesh-independence plot** — outer iterations vs. mesh
refinement, one line per optimizer. Flat lines (Newton-CG; well-preconditioned
L-BFGS) = good; rising lines = not scalable.

**Why this matters:** the well-posed regime is where mesh-independence is
*supposed* to work. If your Newton-CG line is not roughly flat here — or the
Taylor test does not show second-order convergence — the bug is in your harness,
adjoint, or setup. Fix it now, before you trust any ill-posed number.

### Afternoon 2 — the ill-posed study + write-up

**Step 3. Set up the ill-posed regime** (small `α`, higher noise, sparse sensors).
- The reduced Hessian becomes **near-singular**; the regularization `α` is what
  keeps the problem solvable. Declare `α`, the sensor operator `S`, the noise
  realization (seed), and the ground truth `f_true` **once**, as fixed properties
  of the test case, and apply them identically to every optimizer (see the
  integrity warning — this is where benchmarks go wrong).

**Step 4. Compare the optimizer families** (all with the *same* stopping
criterion):

| Label | Outer optimizer | Inner PDE solve | What it tests |
|---|---|---|---|
| `direct_lbfgs` | L-BFGS | MUMPS | reference truth |
| `lbfgs_amg` | L-BFGS | CG + AMG | scalable first-order |
| `gauss_newton` | Gauss–Newton-CG | CG + AMG | curvature without the full Hessian |
| `newton_cg` | truncated Newton-CG | CG + AMG | full second-order, mesh-independent outer iters |

**Step 5. Run the robustness sweep.** For the survivors, sweep **mesh
refinement**, **regularization `α`**, and **noise level** (one axis at a time).
Report **where the winner changes** — the honest result is a *map*, not a single
champion. Track both cost (total PDE solves) and accuracy (`‖f* − f_true‖`); the
cheapest optimizer and the most accurate reconstruction need not agree.

**Produce:** outer-iterations-vs-refinement, cost-vs-`α`, and
error-vs-noise plots, plus a summary table of the winning method per regime.

**Step 6. Write it up.** Methodology, the reproducibility manifest, the plots,
the map. Draft the paper.

## Keeping the benchmark sound

A benchmark is only as trustworthy as its methodology. Before you believe any
"X beats Y," check all of these:

| Rule | Why |
|---|---|
| **Same stopping criterion for everyone** — fix the reduced-gradient `rtol`, `atol`, `max_it`, and *which* norm up front; never tune per optimizer | a moved goalpost makes iteration counts meaningless |
| **Report the true reduced-gradient norm `‖∇J(f*)‖`**, recomputed at termination | an optimizer can "converge" on a *scaled* or internally-preconditioned gradient while the true one is large |
| **Count forward + adjoint solves, not just outer iterations** | a method with few outer steps but many inner PDE solves per step may actually lose — the PDE solve is the cost |
| **Split setup from solve time**, and record peak memory | direct inner solvers win reuse and lose memory; the trade-off is the story |
| **Warm vs. cold** — report first-solve cost separately from amortized re-solves when a factorization or preconditioner is reused across outer iterations | otherwise you compare incomparable things |
| **Fix `f_true`, the noise seed, the sensor set `S`, and `α`**; vary exactly one axis at a time | confounded sweeps produce unreadable maps |
| **Archive the environment** — Firedrake/PETSc versions, commit hash, resolved options dict, noise seed — in every `runs/<timestamp>/` | reproducibility *is* the contribution, not a footnote |

## ⚠️ Integrity warning — do NOT let the gradient or optimizer be "quietly fixed"

**This is the single most important thing in this project.** A benchmark measures
whatever problem you *actually* solved with whatever gradient you *actually* used.
Both an eager assistant and the optimizer itself will happily change the gradient,
the regularization, or the stopping rule to make a stalling run "converge" — and
if that happens silently, your numbers are fiction.

Treat every one of these as a **result to record, not a bug to patch**:

- **Finite differences substituted for the adjoint.** The exact discrete adjoint
  gradient is the object under study. Swapping in a finite-difference gradient
  (or handing the problem to a routine with a numerical Jacobian) changes the
  method, costs `O(N)` PDE solves, and *hides* adjoint bugs behind plausible
  numbers. Finite differences are for the **offline Taylor test only**, never the
  production gradient. (This is the Ex06 rule, stated verbatim in its `CLAUDE.md`:
  *don't replace the adjoint with a finite-difference gradient*.)
- **Discretize-then-optimize inconsistency.** If the discrete adjoint is not the
  *exact* gradient of the discrete objective (wrong operator transpose, mishandled
  boundary conditions, quadrature mismatch), the Taylor test fails and you are
  descending on a different functional. Fix it; don't loosen the test.
- **Regularization drift.** Raising `α` to stabilize a stalling optimize changes
  the problem — `α` is a declared, fixed property of each test case, not a knob to
  make a run pass.
- **Inner-solve tolerance drift.** Loosening the forward/adjoint KSP tolerance so
  gradients are cheaper produces an **inexact adjoint** that pollutes the outer
  gradient. If you study inexactness, make it a *declared benchmark axis*, applied
  identically — never a silent patch on one configuration.
- **Test-case swap.** Silently changing the sensor operator `S`, the noise
  realization, or `f_true` between runs — now you are benchmarking different
  problems than the one you named.
- **Stopping-criterion drift.** Loosening the gradient `rtol`, raising `max_it`,
  disabling error-if-not-converged, or reporting the optimizer's scaled/internal
  gradient instead of the true one to make a run "pass."
- **Silent optimizer fallback.** The optimizer switching methods, or the line
  search quietly degrading to steepest descent, so a "converged" flag no longer
  means what you think.

**Defense:** gate every benchmark on a **passing Taylor test** of the adjoint
gradient; after every optimize, independently recompute and log the **true reduced
gradient norm `‖∇J(f*)‖`** next to the optimizer's convergence reason, and log the
reconstruction error `‖f* − f_true‖`; dump the resolved `solver_parameters` and
`-ksp_view` so any injected option is diffable. Use the **kkt-checker** skill (from
Exercise 3) to verify first-order optimality at the reported optimum. A run that
"converged" with a large true gradient — or a failing Taylor test — is the tell
that the gradient or the problem was changed under you. **A stall is a legitimate,
publishable data point.**

## Conventions to put in your project `CLAUDE.md`

Start the project by writing these into a `CLAUDE.md` in this folder (Exercise 01
applied for real). They are the rules most likely to be violated silently.

```markdown
## Stack
- Firedrake (finite elements; PETSc under the hood) for the forward and adjoint
  Poisson solves. Inner linear solvers are chosen via solver_parameters
  (KSP + PC: CG with ILU/AMG, or MUMPS).
- pyadjoint (firedrake.adjoint) supplies the EXACT discrete adjoint gradient and
  the Hessian action, plus the taylor_test used to verify them.
- Outer optimizer via pyadjoint's ReducedFunctional driven by scipy.optimize,
  ROL, or PETSc TAO. matplotlib for figures (saved to figures/, never shown).

## Firedrake / UFL syntax
- When writing Firedrake code, ALWAYS defer to Firedrake/UFL syntax over the
  Python/NumPy equivalent (sin, cos, exp, sqrt, pi, inner, dot, grad, div,
  conditional, Constant, norms, ...). The lookalikes often produce subtly wrong
  results on symbolic objects.
- Mesh: build meshes in code (e.g. UnitSquareMesh) or load pre-compiled .msh
  files. NEVER pass a .geo file to Firedrake's Mesh() constructor.

## Adjoint gradient integrity — never silently "fix" the gradient or optimizer
- The reduced gradient is ALWAYS the exact discrete adjoint gradient (pyadjoint).
  Never replace it with a finite-difference gradient or a numerical Jacobian in
  the production objective. Finite differences are for the offline Taylor test only.
- The discrete adjoint must be the exact gradient of the DISCRETE objective
  (discretize-then-optimize). Gate every benchmark on a Taylor test that shows
  2nd-order convergence before trusting any number.
- Regularization alpha, the sensor operator S, the noise realization (seed), and
  the ground truth f_true are DECLARED, IMMUTABLE properties of each test case,
  applied identically to every optimizer. Never tune them to force convergence.
- The stopping criterion (reduced-gradient norm rtol/atol, max outer iters, and
  the norm used) is fixed for all optimizers. Never loosen it, raise max_it,
  disable error-if-not-converged, or report a scaled gradient to make a run pass.
- The inner forward/adjoint solve tolerance is fixed unless inexactness is an
  explicit benchmark axis. Never loosen it silently to go faster.
- After every optimize, independently recompute and log the true reduced-gradient
  norm ‖∇J(f*)‖ and the reconstruction error ‖f*−f_true‖. A "converged" run with
  a large true gradient is a red flag, not a success. A stall is a result —
  record it.
```

## Background & references

**Problem class — PDE-constrained optimization & inverse problems**
- M. Hinze, R. Pinnau, M. Ulbrich, S. Ulbrich, *Optimization with PDE
  Constraints*, Springer, 2009 — the textbook reference for the reduced-space
  adjoint approach and this problem class.
- V. Akçelik, G. Biros, O. Ghattas, *Parallel Multiscale Gauss–Newton–Krylov
  Methods for Inverse Wave Propagation*, SC'02, 2002 — large-scale
  PDE-constrained inverse problems; closest in structure to this capstone's
  Newton–Krylov Phase 2.
- C. R. Vogel, *Computational Methods for Inverse Problems*, SIAM, 2002 —
  Tikhonov regularization, the L-curve, and the ill-posedness you meet in Phase 2.

**Optimization methods**
- J. Nocedal, S. J. Wright, *Numerical Optimization*, 2nd ed., Springer, 2006 —
  L-BFGS, (Gauss–)Newton-CG, truncated-Newton, and line-search theory.
- C. T. Kelley, *Iterative Methods for Optimization*, SIAM, 1999 — practical
  first- and second-order methods and the mesh-independence idea.

**Adjoints & verification (Firedrake)**
- pyadjoint / dolfin-adjoint: <https://www.dolfin-adjoint.org/> — the automatic
  discrete adjoint behind Firedrake, `ReducedFunctional`, and the `taylor_test`
  your harness must gate on.
- Firedrake adjoint & optimization docs: <https://www.firedrakeproject.org/>.

**Tools & PETSc option dictionaries (via `solver_parameters`)**
- Firedrake solving interface (`solver_parameters` *are* PETSc options):
  <https://www.firedrakeproject.org/solving-interface.html>.
- PETSc/petsc4py: <https://petsc.org/> — the **KSP** chapter
  <https://petsc.org/release/manual/ksp/> (every `ksp_type`, `pc_type`,
  MUMPS/hypre/gamg option for the inner solve) and the **TAO** chapter
  <https://petsc.org/release/manual/tao/> for the outer optimizer.

**Workshop pointers**
- Install (Docker + Firedrake): [`../../exercises-pde/01-claude-md/INSTALL.md`](../../exercises-pde/01-claude-md/INSTALL.md).
- The forward-PDE sibling study: [`../SolverBench/README.md`](../SolverBench/README.md).
- Literature workflow (paper summaries, RAG): `../../LITERATURE.md`.

## Tasks checklist

For fun, you can hand this list to `claude` and let it plan — or work it step by
step.

1. Set up Docker + Firedrake (see *Install* above) and write the project
   `CLAUDE.md` (conventions above).
2. Plan the harness in plan mode; agree on the run-record schema before coding.
3. Implement the harness + the **Taylor-test gate** for the adjoint gradient.
4. Solve the well-posed baseline; produce the mesh-independence plot.
5. Record durable findings in `MEMORY.md` (which optimizers/inner-solvers ruled
   in/out, and why); overwrite `STATUS.md` with the next step at each handoff.
6. Turn on the ill-posed regime; compare the optimizer families; run the
   robustness sweep across mesh, `α`, and noise.
7. (Optional) Add truncated Newton-CG as the bridge case, or an L-curve `α` study.
8. Write the paper: methodology, reproducibility manifest, plots, the map.

## Publication outlets

* [SIAM Journal on Scientific Computing (SISC)](https://www.siam.org/publications/siam-journals/siam-journal-on-scientific-computing/) — software & high-performance computing; a natural home for a solver/optimizer benchmark
* [ACM Transactions on Mathematical Software (TOMS)](https://dl.acm.org/journal/toms) — algorithms & software, benchmarking-friendly
* [Optimization Methods and Software (OMS)](https://www.tandfonline.com/journals/goms20) — method comparisons and reproducible optimization studies
* [Inverse Problems (IOP)](https://iopscience.iop.org/journal/0266-5611) — if the emphasis lands on the reconstruction / regularization side
* [Journal of Open Source Software (JOSS)](https://joss.theoj.org/) — if the harness itself is the contribution
* A reproducible arXiv preprint / workshop proceedings — the fastest honest home for a two-afternoon study

*Good luck — and don't let the gradient lie to you.*

---

*Based on an idea contributed by Rebecca Durst and Sven Leyffer.*
