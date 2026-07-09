# SolverBench - Solver & Preconditioner Benchmarking for PDEs

## Purpose

Build a small, **reproducible benchmarking study** that answers a question the
literature keeps re-asking without settling: *for a given PDE class, which
solver + preconditioner combination is fastest and most robust, and how does
that change with mesh resolution and physical regime?* There are many good
options and no universal winner — the contribution is a **fair, reproducible
map** of where each one wins, not folklore.

This is a *files, not chats* capstone: you develop the entire project from this
README using the skills from the exercises — a project `CLAUDE.md` for
conventions, plan mode for the harness, `MEMORY.md` for durable findings,
`STATUS.md` for handoffs, and a skill or two for the repetitive parts. Nothing
else ships. The code is yours to write.

- **Scope: two afternoons.** Afternoon 1 → a working harness + the Poisson
  baseline. Afternoon 2 → the Stokes comparison + a paper draft. Depth on a
  narrow, honest comparison beats a broad shallow sweep.
- **Deliverable: a publication** — a short, reproducible benchmark/methods note.
  This kind of paper lives or dies on its methodology and its archived,
  re-runnable results. See *Publication outlets* at the end.

## Install

This project runs in **Firedrake** inside its official Docker image. **Install
Docker and pull the Firedrake image by following the PDE track's install guide:**
[`../../exercises-pde/01-claude-md/INSTALL.md`](../../exercises-pde/01-claude-md/INSTALL.md).
It walks through installing Docker and running the `firedrakeproject/firedrake`
image with your working folder bind-mounted in. As in the PDE exercises, run
`claude` on the host and run the Python *inside* the container.

## The research gap

"Which solver should I use for this problem?" is usually answered by habit, a
neighbor's advice, or the first thing that converged. For elliptic and
saddle-point PDEs the honest answer is *it depends* — on the mesh, the physical
parameters, the discretization, and what you are optimizing (iterations, wall
clock, memory, robustness). A careful study that holds everything fixed except
one axis, reports **where the winner changes**, and ships a re-runnable harness
is a genuine, publishable contribution.

## A quick solver primer

*Read this if you are not a numerical-linear-algebra specialist. Experts can
skip to the problem statement.*

Every method here is a way to solve a large linear system `A x = b`, where `A`
comes from discretizing the PDE. There are two families.

| Family | Idea | Strengths | Weaknesses |
|---|---|---|---|
| **Direct solvers** | Factor `A` into simpler pieces (LU / Cholesky), then back-substitute. Essentially "exact." | Robust; no tuning; great for small/medium problems | Memory and time blow up as the mesh grows — do not scale to large 3D problems |
| **Iterative (Krylov) solvers** | Start from a guess and improve it using only matrix–vector products `A·v`. Stop when the residual is small. | Cheap memory; scale to huge problems | Need a good **preconditioner** or they converge slowly (or not at all) |

**MUMPS** is the direct solver you will use as the "ground truth" reference — a
parallel *multifrontal* LU factorization, available through PETSc.

**Krylov methods** differ by what kind of matrix `A` is:

| Method | Use when `A` is… | Typical PDE |
|---|---|---|
| **CG** (Conjugate Gradient) | symmetric **positive-definite** (SPD) | Poisson, compressible elasticity |
| **MINRES** (Minimal Residual) | symmetric but **indefinite** (has +/− eigenvalues) | Stokes (saddle point) |
| **GMRES** / **FGMRES** (Flexible GMRES) | **nonsymmetric**, or when the preconditioner itself changes between iterations | convection–diffusion; Stokes with a variable preconditioner |

A **preconditioner** is a cheap, approximate inverse of `A` that you apply every
iteration to make the Krylov method converge in far fewer steps. Choosing it
*is* the game. The main options:

| Preconditioner | What it does | Notes |
|---|---|---|
| **ILU** (Incomplete LU) | a cheap, approximate LU factorization | generic, easy, but iteration count grows as you refine the mesh |
| **AMG** (Algebraic Multigrid) | builds a hierarchy of coarse problems *from the matrix alone* | for SPD elliptic problems it can give **mesh-independent** iteration counts; implementations: PETSc **GAMG**, **hypre BoomerAMG** |
| **GMG** (Geometric Multigrid) | same multigrid idea, but using the actual mesh hierarchy | Firedrake supports this directly; often the fastest when available |
| **Block / `fieldsplit`** | for multi-field systems (velocity + pressure), preconditions each field and their coupling separately via the **Schur complement** | the only sane option for saddle-point Stokes; variants below |

For Stokes specifically, the block preconditioner must approximate the **Schur
complement** (the pressure part). Common approximations you will compare:

- **mass-matrix** — the simplest; the pressure mass matrix approximates the
  Schur complement for Stokes.
- **PCD** (Pressure Convection–Diffusion) and **LSC** (Least-Squares
  Commutator) — smarter approximations that stay robust as flow is added.
- **Augmented Lagrangian / iterated penalty** — the approach used with
  Scott–Vogelius elements to handle the near-singular pressure block.

**"Mesh-independent"** is the phrase you'll use most: it means the iteration
count *stays flat* as you refine the mesh. That is the gold standard — it says
the cost per unknown is bounded, so the method scales.

## Problem statement

You will benchmark across two PDE classes, in order of difficulty.

| Phase | PDE class | Operator character | The question that matters |
|---|---|---|---|
| **1 — baseline** | Poisson / Darcy on the unit square | SPD, elliptic | Can you get **mesh-independent** iteration counts? Validates the harness and the metrics before anything hard. |
| **2 — the study** | Stokes (steady, linear) | saddle point, symmetric indefinite | How do you precondition the Schur complement, and how robust is each choice across mesh and viscosity? This is where "no clear winner" is real. |

**Optional intermediate bridge (only if you're ahead of schedule).** *Linear
elasticity* sits between the two: compressible elasticity is SPD like Poisson
(CG + AMG, but you must supply the **six rigid-body modes** as the AMG
near-nullspace), and as the material nears incompressibility (Poisson ratio
ν → ½) it *locks* and behaves like Stokes. It's the cleanest on-ramp to the
saddle-point difficulty and reuses most of the Phase-2 machinery. Put it in your
plan; implement it only if Phase 2 finishes early.

### Phase 2 discretization: Scott–Vogelius vs. Taylor–Hood

The central Phase-2 design choice is the velocity/pressure element pair:

| Element pair | Divergence | Trade-off |
|---|---|---|
| **Taylor–Hood** (`P2`–`P1`) | only *weakly* divergence-free — discrete velocity has nonzero divergence that pollutes the solution | the easy workhorse; inf-sup stable on any mesh |
| **Scott–Vogelius** (`Pk`–disc. `P(k-1)`) | *exactly* divergence-free, pressure-robust | needs a special mesh (e.g. barycentric refinement) and a solver that copes with the near-singular pressure block (augmented Lagrangian / iterated penalty) |

Benchmarking these two against a shared set of preconditioners is a clean,
self-contained Phase-2 result. For *why* the difference matters, see
*Background*.

## Suggested approach

Build the harness for Poisson first, get it honest, then swap in Stokes. **The
harness is the deliverable; the PDE is a slot.**

### Afternoon 1 — the harness + the Poisson baseline

**Step 1. Build the benchmarking harness.**
- One driver that runs a single `(problem, solver, mesh refinement, parameter)`
  combination and records a *fixed set of numbers* — so every run is comparable.
- Record, per run:
  - Krylov **iteration count** and `KSPConvergedReason` (did it actually converge?)
  - the independently recomputed **true residual `‖b − Ax‖₂`** (see the integrity warning)
  - **setup time** vs. **solve time**, separately
  - number of **degrees of freedom** (problem size)
  - the **fully resolved PETSc options** (`-ksp_view` dump) + PETSc/Firedrake versions
- Output: one JSON summary per run, written to a dated `runs/<timestamp>/` folder.

**Step 2. Solve the Poisson baseline** (`−Δu = f` on the unit square, `u = 0` on
the boundary) and compare these solvers:

| Label | Solver | Preconditioner | Expectation |
|---|---|---|---|
| `direct` | MUMPS (direct LU) | — | robust reference; watch memory grow |
| `cg_ilu` | CG | ILU | iterations grow as you refine — the "bad" baseline |
| `cg_gamg` | CG | PETSc GAMG (AMG) | should be ~mesh-independent |
| `cg_hypre` | CG | hypre BoomerAMG (AMG) | should be ~mesh-independent |
| `cg_gmg` *(stretch)* | CG | geometric multigrid | often the fastest |

**Produce:** the **mesh-independence plot** — iterations vs. mesh refinement, one
line per solver. Flat lines (AMG, GMG) = good; rising lines (ILU) = not scalable.

**Why this matters:** Poisson is the problem where mesh-independence is *supposed*
to work. If your AMG line is not roughly flat here, the bug is in your harness or
setup — fix it now, before you trust any Stokes number.

### Afternoon 2 — the Stokes study + write-up

**Step 3. Set up steady linear Stokes** (e.g. lid-driven cavity or a channel).
- Pick an element pair (start with Taylor–Hood; add Scott–Vogelius if time).
- Note the structure: it's a **saddle-point** system, and for *enclosed* flow the
  pressure is defined only up to a constant — the operator has a **nullspace**.
  Declare how you handle that nullspace **once**, and apply it identically to
  every solver (see the integrity warning — this is where benchmarks go wrong).

**Step 4. Compare the solver families** (all with the *same* stopping criterion):

| Label | Solver | Preconditioner | What it tests |
|---|---|---|---|
| `direct` | MUMPS | — | reference truth |
| `minres_mass` | MINRES | block-diagonal, Schur ≈ pressure mass matrix | the classic, simplest block method |
| `fgmres_pcd` / `fgmres_lsc` | FGMRES | `fieldsplit` Schur factorization + PCD or LSC | smarter Schur approximations |
| `sv_al` | FGMRES/MINRES | Scott–Vogelius + augmented-Lagrangian / iterated penalty | the divergence-free approach |

**Step 5. Run the robustness sweep.** For the survivors, sweep **mesh refinement**
*and* **viscosity** (one axis at a time). Report **where the winner changes** —
the honest result is a *map*, not a single champion.

**Produce:** iteration-vs-refinement and iteration-vs-viscosity plots, plus a
summary table of the winning method per regime.

**Step 6. Write it up.** Methodology, the reproducibility manifest, the plots,
the map. Draft the paper.

## Keeping the benchmark sound

A benchmark is only as trustworthy as its methodology. Before you believe any
"X beats Y," check all of these:

| Rule | Why |
|---|---|
| **Same stopping criterion for everyone** — fix `rtol`, `atol`, `max_it`, and residual type up front; never tune per solver | a moved goalpost makes iteration counts meaningless |
| **Report the true, unpreconditioned residual `‖b − Ax‖₂`**, recomputed after the solve | a solver can "converge" on the *preconditioned* residual while the real one is large — or on a *perturbed* system (see below) |
| **Split setup time from solve time**, and record peak memory | direct solvers win iterations and lose memory; the trade-off is the story |
| **Warm vs. cold** — report first-solve cost separately from amortized re-solves if you reuse factorizations | otherwise you compare incomparable things |
| **Fix the RHS and the problem**; vary exactly one axis at a time | confounded sweeps produce unreadable maps |
| **Archive the environment** — PETSc/Firedrake versions, commit hash, resolved options dict — in every `runs/<timestamp>/` | reproducibility *is* the contribution, not a footnote |

## ⚠️ Integrity warning — do NOT let the solver be "quietly fixed"

**This is the single most important thing in this project.** A benchmark
measures whatever system you *actually* solved. Both an eager assistant and the
direct solver itself will happily change the system to make a stalling solve
"converge" — and if that happens silently, your numbers are fiction.

Treat every one of these as a **result to record, not a bug to patch**:

- **Nullspace added or removed.** An enclosed-flow / pure-Neumann Stokes problem
  has a pressure defined only up to a constant — the operator is singular. It is
  legitimate to project out that constant nullspace, **but only as a declared,
  fixed property of the test case, applied identically to every solver** — never
  a patch slipped into one configuration to stop MINRES stalling. If the
  nullspace handling differs between two runs, you are benchmarking two different
  problems.
- **MUMPS perturbs the matrix.** When MUMPS meets a (near-)singular pivot it can
  **add a perturbation to the diagonal** and report success — you factorized
  `A + εI`, not `A`. This is controlled by `-mat_mumps_icntl_24` (with the
  `cntl_*` thresholds). Turn detection **on to *observe*** it and log the INFOG
  null-pivot count — but do not let it silently rescue a singular solve you are
  trying to characterize.
- **Factor shifts.** `-pc_factor_shift_type NONZERO` / `POSITIVE_DEFINITE`
  quietly shifts the diagonal before an ILU/Cholesky factorization — again, a
  different operator.
- **Tolerance / criterion drift.** Loosening `rtol`, raising `max_it`, disabling
  `ksp_error_if_not_converged`, or switching preconditioned ↔ true residual to
  make a run "pass."
- **Discretization swap.** Silently trading Scott–Vogelius for Taylor–Hood, or
  changing polynomial degree / quadrature, to dodge a singular pressure block —
  now you are benchmarking a different problem than the one you named.

**Defense:** after every solve, recompute `‖b − Ax‖₂` yourself and log it next
to `KSPConvergedReason`; dump `-ksp_view` so any injected option is diffable.
A solve that "converged" with a large true residual is the tell that the system
was changed under you. **A stall is a legitimate, publishable data point.**

## Conventions to put in your project `CLAUDE.md`

Start the project by writing these into a `CLAUDE.md` in this folder (Exercise 01
applied for real). They are the two rules most likely to be violated silently:

```markdown
## Firedrake / UFL syntax
- When writing Firedrake code, ALWAYS defer to Firedrake/UFL syntax over the
  Python/NumPy equivalent. Whenever there is a Firedrake/UFL way to express
  something (sin, cos, exp, sqrt, pi, inner, dot, grad, div, conditional,
  Constant, norms, ...), use it even if a Python construct would compile —
  the lookalikes often produce subtly wrong results on symbolic objects.
- Mesh: build meshes in code (e.g. UnitSquareMesh) or load pre-compiled .msh
  files. NEVER pass a .geo file to Firedrake's Mesh() constructor.

## Solver integrity — never silently "fix" a solver
- The nullspace of each test problem is a DECLARED, IMMUTABLE property applied
  identically to every solver. Never add or remove a nullspace to make a solve
  converge.
- Never add a factor shift (-pc_factor_shift_type) or enable MUMPS null-pivot
  perturbation (-mat_mumps_icntl_24) to rescue a singular solve. Use them only
  to OBSERVE singularity, and log when they fire.
- Never change rtol/atol/max_it, disable ksp_error_if_not_converged, or swap
  the residual type to make a run pass. The stopping criterion is fixed for all
  solvers.
- Never swap the discretization (element pair, degree, quadrature) to dodge a
  singular block. That changes the problem being benchmarked.
- After every solve, independently recompute and log the true residual
  ‖b − Ax‖₂. A "converged" solve with a large true residual is a red flag,
  not a success. A stall is a result — record it.
```

## Background & references

**Discretization — Scott–Vogelius vs. Taylor–Hood, and why it matters**
- V. John, A. Linke, C. Merdon, M. Neilan, L. Rebholz, *On the Divergence
  Constraint in Mixed Finite Element Methods for Incompressible Flows*, SIAM
  Review 59(3):492–544, 2017. <https://doi.org/10.1137/15M1047696> — the review
  on pressure-robustness and exactly-divergence-free elements.
- P. Farrell, ICERM 2024 course, Navier–Stokes solvers (Taylor–Hood and
  Scott–Vogelius side by side):
  <https://github.com/pefarrell/icerm2024/tree/main/09_navier_stokes_solvers> —
  your linear-Stokes Phase 2 is a simplification of `03_scott_vogelius_*`.
- V. John, *Finite Element Methods for Incompressible Flow Problems*, Springer,
  2016 — the textbook reference for the problem class.

**Iterative solvers & block preconditioning**
- H. Elman, D. Silvester, A. Wathen, *Finite Elements and Fast Iterative
  Solvers*, 2nd ed., Oxford, 2014 — PCD, LSC, and Schur-complement
  preconditioning for Stokes/Navier–Stokes.
- M. Benzi, M. Olshanskii, *An Augmented Lagrangian-Based Approach to the Oseen
  Problem*, SIAM J. Sci. Comput., 2006 — the augmented-Lagrangian idea behind
  the Scott–Vogelius / grad-div solver.

**Tools & PETSc option dictionaries**
- Firedrake: <https://www.firedrakeproject.org/> — and the solver interface
  (`solver_parameters` *are* PETSc options):
  <https://www.firedrakeproject.org/solving-interface.html>
- PETSc/petsc4py: <https://petsc.org/> — the **KSP** manual chapter
  <https://petsc.org/release/manual/ksp/> lists every `ksp_type`, `pc_type`,
  `fieldsplit`, and MUMPS/hypre/gamg option you will assemble into your solver
  dicts.
- hypre BoomerAMG: <https://hypre.readthedocs.io/>

## Tasks checklist

For fun, you can hand this list to `claude` and let it plan — or work it step by
step.

1. Set up Docker + Firedrake (see *Install* above) and write the project
   `CLAUDE.md` (conventions above).
2. Plan the harness in plan mode; agree on the run-record schema before coding.
3. Implement the harness + Poisson baseline; produce the mesh-independence plot.
4. Record durable findings in `MEMORY.md` (which preconditioners ruled in/out,
   and why); overwrite `STATUS.md` with the next step at each handoff.
5. Swap in Stokes; compare the solver families; run the robustness sweep.
6. (Optional) Add near-incompressible elasticity as the bridge case.
7. Write the paper: methodology, reproducibility manifest, plots, the map.

## Publication outlets

* [ACM Transactions on Mathematical Software (TOMS)](https://dl.acm.org/journal/toms) — algorithms & software, benchmarking-friendly
* [SIAM Journal on Scientific Computing (SISC)](https://www.siam.org/publications/siam-journals/siam-journal-on-scientific-computing/) — software & high-performance computing section
* [Journal of Open Source Software (JOSS)](https://joss.theoj.org/) — if the harness itself is the contribution
* A reproducible arXiv preprint / workshop proceedings — the fastest honest home for a two-afternoon study

*Good luck — and don't let the solver lie to you.*

---

*Based on an idea contributed by Rebecca Durst.*
