# Workshop Solutions — overview

These are walkthroughs of the exercises with the math explained gently for non-mathematicians. Each exercise has its own `SOLUTION.md` inside its folder; this file is the index plus the running themes. The workshop ships three parallel tracks — optimization, PDE/FEM, and numerical linear algebra — each with the same numbered progression.

### Optimization track (`exercises-opt/`)

| # | Exercise | Solution file |
|---|---|---|
| 1 | Write a CLAUDE.md | [exercises-opt/01-claude-md/SOLUTION.md](exercises-opt/01-claude-md/SOLUTION.md) |
| 2 | Plan a cardinality-constrained portfolio NLP | [exercises-opt/02-planning/solution/SOLUTION.md](exercises-opt/02-planning/solution/SOLUTION.md) |
| 3 | Verify a KKT point | [exercises-opt/03-skills/SOLUTION.md](exercises-opt/03-skills/SOLUTION.md) |
| 4 | Bootstrap LOGBOOK.md | [exercises-opt/04-logbook/SOLUTION.md](exercises-opt/04-logbook/SOLUTION.md) |

### PDE / FEM track (`exercises-pde/`)

| # | Exercise | Solution file |
|---|---|---|
| 1 | Write a CLAUDE.md (FEM convergence) | [exercises-pde/01-claude-md/SOLUTION.md](exercises-pde/01-claude-md/SOLUTION.md) |
| 2 | Plan a fix for a broken convergence test | [exercises-pde/02-planning/SOLUTION.md](exercises-pde/02-planning/SOLUTION.md) |
| 3 | Verify a CFL condition with a skill | [exercises-pde/03-skills/SOLUTION.md](exercises-pde/03-skills/SOLUTION.md) |
| 4 | Bootstrap LOGBOOK.md from lab notebooks | [exercises-pde/04-logbook/SOLUTION.md](exercises-pde/04-logbook/SOLUTION.md) |

### Numerical linear algebra track (`exercises-lin_alg/`)

| # | Exercise | Solution file |
|---|---|---|
| 1 | Write a CLAUDE.md (matrix spectra) | [exercises-lin_alg/01-claude-md/SOLUTION.md](exercises-lin_alg/01-claude-md/SOLUTION.md) |
| 2 | Plan an SVD of a matrix-free operator | [exercises-lin_alg/02-planning/SOLUTION.md](exercises-lin_alg/02-planning/SOLUTION.md) |
| 3 | QR / Lanczos singular-value skills | [exercises-lin_alg/03-skills/SOLUTION.md](exercises-lin_alg/03-skills/SOLUTION.md) |
| 4 | Bootstrap LOGBOOK.md | [exercises-lin_alg/04-logbook/SOLUTION.md](exercises-lin_alg/04-logbook/SOLUTION.md) |

## A glossary for non-mathematicians

The exercises sit on top of a few math terms. You don't need to be fluent — these short translations are enough to follow what's happening.

- **Optimization problem.** Find the inputs that minimize (or maximize) some quantity, possibly subject to rules called *constraints*. "Find the cheapest portfolio that returns at least 5%" is one.
- **Nonlinear / convex / nonconvex.** A problem is nonlinear if its math involves products or powers of variables. Convex problems have a single bottom; nonconvex ones can have multiple local bottoms.
- **MINLP.** Mixed-integer nonlinear program. Some variables must be whole numbers (e.g., "buy a stock or don't"); the rest are real-valued; the objective or constraints are nonlinear. These are usually hard.
- **PDE-constrained optimization.** The constraint isn't an equation, it's a *partial differential equation* — the kind that describes heat flow, fluids, or electromagnetic fields.
- **KKT conditions.** First-order optimality conditions for constrained problems — basically: "is this point actually a candidate solution?" Exercise 3 verifies them.
- **Multiplier (Lagrange / dual variable).** An auxiliary variable that captures how much a constraint "matters" at the optimum. Multipliers come along with primal solutions; KKT conditions tie them together.
- **Adjoint method.** A clever way to compute gradients of objectives that involve solving a PDE.
- **CUTEst.** A standard test set of optimization problems researchers use to compare solvers — like a benchmark suite for compilers.

The PDE track adds a few numerical-PDE terms:

- **Finite differences / finite elements (FEM).** Two standard ways to turn a PDE on a continuous domain into a big system of linear equations a computer can solve — by sampling on a grid (finite differences) or tiling the domain with small elements (FEM).
- **Mesh.** The grid or tiling the domain is broken into. Finer meshes are more accurate but cost more; refining only where the solution is hard (e.g. near a corner) is often the win.
- **Convergence rate.** How fast the error shrinks as the mesh is refined — "L² error ~ O(h²)" means halving the spacing `h` cuts the error ~4×.
- **Manufactured solution.** A testing trick: pick the answer first, plug it into the equation to see what right-hand side it needs, then check the solver recovers the answer you picked.
- **CFL condition.** A stability limit for explicit time-stepping: the time step must be small enough relative to the mesh, or the simulation blows up.

The linear algebra track adds a few more:

- **Eigenvalues / eigenvectors.** Directions a matrix only stretches (not rotates), and the stretch factors — a matrix's "natural modes."
- **Singular values / SVD.** The singular value decomposition factors any matrix into rotation–stretch–rotation; the singular values are the stretch factors. For nonsymmetric matrices they differ from the eigenvalues.
- **Spectrum.** Loosely, the set of a matrix's eigenvalues (or singular values) — which one you mean is exactly the ambiguity the linear algebra Exercise 1 makes you pin down.
- **Dense vs sparse matrix.** Dense stores every entry; sparse stores only the nonzeros. The storage choice dictates which algorithms are sane — densifying a large sparse matrix is a classic mistake.
- **Matrix-free / linear operator.** An object you can only *apply* to a vector (matrix–vector products), never see as a stored matrix — e.g. a PDE solve. Its SVD needs iterative methods, not a dense factorization.
- **QR iteration / Lanczos.** Two workhorse algorithms for spectra: QR iteration for the full spectrum of a small dense matrix; Lanczos for the dominant few of a large sparse or matrix-free one.
- **Condition number / preconditioner.** The condition number measures how sensitive a linear solve is (large = hard); a preconditioner is an approximation applied to make an iterative solver converge faster.

## Common themes across the solutions

1. **Claude Code amplifies what you put into it.** A blank session asking for "a convergence plot" gives you a generic answer; the same prompt with a CLAUDE.md gives you what you wanted. Every exercise is a variant of this lesson.
2. **The plan is the deliverable.** Especially in exercise 2 and the capstone — what Claude writes into `plan.md` is often more valuable than the code that follows.
3. **Friction kills the loop.** If summarizing into LOGBOOK.md takes ten minutes, you won't do it. The exercises pick conventions short enough that the ritual fits in two minutes.
4. **MCP at the seams, skills inside the project.** Recurring domain logic (KKT check) goes in a skill. External systems (databases, custom solvers) go behind an MCP. Don't mix the two.
