# Capstone — Inverse Poisson with PETSc/TAO (30 min)

**Goal.** End-to-end exercise that uses everything: CLAUDE.md, plan mode, the kkt-checker skill, MEMORY.md, and (optionally) the SQLite MCP from exercise 5.

## The problem

Identify the source term `f` in

$$
-\Delta u = f \text{ on } \Omega = (0, 1)^2, \qquad u = 0 \text{ on } \partial \Omega
$$

from noisy measurements of `u` at sensor points. We solve the reduced-space optimization

$$
\min_{f} \quad \tfrac{1}{2} \|S u(f) - u_{\text{obs}}\|_2^2 + \alpha \|f\|_2^2
$$

where `u(f)` solves the PDE for the given `f`, and `S` is the sensor sampling operator.

A skeleton implementation is in `poisson_inverse.py`. The PDE is discretized with finite differences on a `Nx × Ny` grid; the Poisson solve uses PETSc's `KSP`; the outer optimization uses TAO (`PETSc.TAO`).

## What ships

```
06-capstone/
├── README.md
├── INSTALL.md           # three install paths (pip / conda / docker)
├── CLAUDE.md            # workshop conventions for the capstone
├── MEMORY.md            # durable knowledge; references plan files
├── STATUS.md            # current state; points at the active plan
├── plans/
│   └── 2026-05-07-tao-implementation.md   # the active plan
├── poisson_inverse.py   # skeleton: PDE solve + reduced-space objective
├── requirements.txt     # pip dependencies (numpy backend + tests)
└── environment.yml      # conda environment (recommended for petsc4py)
```

## Install

See `INSTALL.md` for three paths:

- **Path A — native pip, numpy backend.** ~2 min; runs everything except `--backend petsc`.
- **Path B — native conda (recommended).** ~5 min; full PETSc/TAO via prebuilt conda-forge binaries.
- **Path C — Docker container.** ~10 min; for workshop instructors and long-term reproducibility.

For the workshop, pick A (skim) or B (full experience).

The four memory-style artifacts are intentionally separated:

- `CLAUDE.md` — stable conventions, rarely edited.
- `plans/<date>-<slug>.md` — what's going to happen, in what order. Archived after execution; never edited (revisions become `-v2.md` files).
- `MEMORY.md` — append-only durable knowledge; references plan files when a decision comes from a plan or a plan was abandoned.
- `STATUS.md` — overwritten each session; says where you are *right now* and points at the active plan.

See `WORKFLOW.md` at the workshop root for the full pattern and a prompt cookbook.

## Suggested workflow (use plan mode!)

1. `cd exercises/06-capstone && claude`
2. Enter plan mode (`Shift+Tab` twice). Ask:

   ```
   plan an implementation of the inverse Poisson problem in
   poisson_inverse.py using TAO's BLMVM for the outer loop and
   KSP+PCG for the PDE solve. Include adjoint gradient computation,
   convergence logging in our format, and a final figure of recovered f.
   ```

3. Approve the plan (or revise) and let Claude implement.
4. Use the **kkt-checker** skill (from exercise 3 — copy it into `.claude/skills/`) to verify the gradient is consistent with what TAO reports at the optimum.
5. Append the run summary to `MEMORY.md`.

## If PETSc isn't installed

The skeleton has a `--backend numpy` fallback that uses `scipy.sparse.linalg.spsolve` for the PDE and `scipy.optimize.minimize(method="L-BFGS-B")` for the outer problem. It is slower but identical in interface — useful if you don't want to install PETSc just for the workshop.

```bash
python poisson_inverse.py --backend numpy --grid 33 --alpha 1e-3
```

## Things to discuss after

- Where did the plan save you? Where did it cost you?
- Did the kkt-checker skill catch anything?
- What did you append to MEMORY.md? Will future-you thank you?

## Stretch — literature integration

Add a `literature/` directory to this exercise and produce three paper summaries (using the `paper-summary` skill from exercise 3) for the references below. Then cite them from `MEMORY.md`. See `../../LITERATURE.md` for the full pattern.

```bash
mkdir literature
cp -R ../03-skills/skills/paper-summary .claude/skills/
# Drop the PDFs into papers-inbox/, then in a Claude Code session:
> for each PDF in papers-inbox/, run the paper-summary skill and save
  to literature/<bibkey>.md. Verify citations via whatever MCP is
  available; if none, mark unverified.
```

Suggested papers:

- Wächter & Biegler (2006) — IPOPT (the filter line search and inertia correction we'd reuse if we extended the outer optimizer).
- Hinze, Pinnau, M. Ulbrich, S. Ulbrich (2009) — *Optimization with PDE Constraints* (the textbook reference for our problem class).
- Akçelik, Biros, Ghattas (2002) — large-scale inverse problems with PDE constraints (closer to the capstone's structure).

## References

- PETSc TAO manual chapter: <https://petsc.org/release/manual/tao/>
- petsc4py tutorial: <https://petsc.org/release/petsc4py/>
- Inverse problems with PDE constraints: Hinze, Pinnau, Ulbrich, Ulbrich, *Optimization with PDE Constraints* (2009).
- Workshop literature workflow: `../../LITERATURE.md`.
