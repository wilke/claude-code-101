# Capstone Project: VoroMesh2D — Voronoi-Based Interstitial Meshing in 2D

## Purpose

Use **Claude Code as your co-scientist** to build a small, modular **2D mesh
generator** for the interstitial space between packed disks — a laptop-sized, 2D take
on the all-hex packed-sphere mesher of Lan, Fischer, Merzari & Min (disks + quads
instead of spheres + hexes; no Nek5000/spectral elements). The **deliverable is a
self-contained git repository** demonstrating Claude's help with mesh generation: the
code, its tests, a sample mesh, and the files-not-chats artifacts showing *how* you
drove the assistant. The mesh is the vehicle; the reproducible workflow is the product.

## Objective

> The objective is not to reproduce the complete research software described in the
> paper. Instead, participants will use Claude Code to understand an unfamiliar
> scientific algorithm, design a modular implementation, generate and modify code,
> debug numerical issues, build tests, analyze computational results, and document a
> reproducible software workflow.

You are **not** expected to finish the whole pipeline — getting partway with a clean
design, real debugging, tests, and honest analysis is a complete deliverable.

## Background

- **Key reference:** Lan, Fischer, Merzari, Min, *All-Hex Meshing Strategies for
  Densely Packed Spheres* — <https://arxiv.org/abs/2106.00196>.
- **The 2D reduction.** The paper takes a Voronoi diagram of the sphere centers,
  tessellates each convex facet into quads, and sweeps them onto the sphere to fill
  the gap. In 2D: Voronoi diagram of the **disk centers** → each cell is a convex
  polygon around one disk → mesh the gap between the polygon **edges** and the disk
  **arc** by sweeping **quads** across it.
- **Context (not a dependency):** the paper's production example is NekRS `pb146` —
  <https://github.com/Nek5000/nekRS/tree/master/examples/pb146>. You don't need Nek.

## Packages

| Package | Role | Repo |
|---|---|---|
| **scipy** | `scipy.spatial.Voronoi` / `Delaunay` — the geometry engine (don't hand-roll a Voronoi diagram) | <https://github.com/scipy/scipy> |
| **numpy** | mesh coordinates and vectors | — |
| **matplotlib** | quick visualization + before/after quality plots | — |
| **meshio** | read/write `.msh` / `.vtu` / `.xdmf`; the **only** mesh I/O you should write | <https://github.com/nschloe/meshio> |
| **pytest** | tests (validity gate, meshio round-trip) | — |


## Meshing workflow

Summarizing this algorithm from the paper is part of the exercise — have Claude do
it. The high-level workflow (2D form) is all you need to start:

**Disk centers → Voronoi decomposition → edge collapse → vertex insertion → facet
tessellation → sweeping → mesh smoothing → all-quad mesh**

## Suggested approach

**Afternoon 1 — understand, design, decompose.** Have Claude read the paper and
extract the 2D pipeline; in plan mode, design the modules (`packing`, `voronoi`,
`cleanup`, `mesh`, `quality`, `io`, `viz`); implement packing + clipped Voronoi +
cleanup and visualize the cells and flagged edges.

**Afternoon 2 — mesh, measure, export, verify.** Build the gap quad-mesh, the
metrics, and the before/after comparison; export through meshio; add the validity gate
and a round-trip test. Record what Claude got wrong and how you caught it.

## Deliverable — a git repository

Package the work as a **git repo** that demonstrates Claude-assisted mesh generation.
Judged on the **workflow**, not on finishing the pipeline.

| Tier | What the repo contains |
|---|---|
| **Minimum (complete)** | generate/read a packing; compute + visualize the Voronoi decomposition; flag problematic features; apply ≥1 cleanup op; compute quality metrics; **export via meshio**; tests + README |
| **Target** | the above **plus** a conformal **all-quad interstitial mesh** for a ≥20-disk packing, a **before/after** comparison, and a passing **validity gate** |
| **Stretch** | all-quad facet tessellation (even-edge guarantee); a 3D single-cell sweep onto one sphere; Laplacian vs. optimization smoothing; timing vs. #disks |

The `plan.md` / `LOGBOOK.md` / `CLAUDE.md` are the point: they let a reader see how
Claude was used — including a dead end or two and how you debugged it.

## ⚠️ Validity — a picture is not a valid mesh

Claude will happily produce a mesh that *renders* fine in matplotlib but isn't valid —
that's the failure mode to guard against. Before calling a mesh done, verify every
element:

- **No inverted/tangled elements** — positive area and **scaled Jacobian in (0, 1]**.
- **Conformity** — shared edges match; no unintended hanging nodes.
- **No overlaps or gaps** — elements tile the region without self-intersection and
  reach the disk boundary.
- **meshio round-trip** — write → read → assert points/cells survive.

Treat "it looks right" as a hypothesis, not a result — and let Claude help you build
the checks that test it.

## Conventions worth putting in your project `CLAUDE.md`

Consider writing conventions around:

- **Mesh validity** — what Claude must verify before calling a mesh "done," and that a rendering is never proof of validity.
- **Tolerances** — treating geometry-processing tolerances as declared, recorded parameters rather than knobs to tune silently.

## Tasks checklist

1. Use Claude to analyze the paper and translate the 2D algorithm into a modular design.
2. Generate structured and random packings of ~10–100 disks.
3. Compute and visualize the Voronoi decomposition.
4. Flag short edges, long edges, and problematic facets.
5. Implement ≥1 geometry-improvement op (edge collapse / long-edge split / vertex insertion).
6. Generate the gap mesh (quads swept from Voronoi edges to disk arcs).
7. Implement quality metrics: edge-length ratio, aspect ratio, minimum angle, scaled Jacobian.
8. Compare mesh quality before and after the improvement op.
9. Export via **meshio** (metrics as `cell_data`); add a round-trip test, a validity
   gate, a CLI, examples, and docs.
10. Package it as a **git repository** with the plan/LOGBOOK/CLAUDE.md artifacts.

## References

- Lan, Fischer, Merzari, Min, *All-Hex Meshing Strategies for Densely Packed Spheres*,
  arXiv:2106.00196 — <https://arxiv.org/abs/2106.00196>.
- scipy — <https://github.com/scipy/scipy>.
- meshio — <https://github.com/nschloe/meshio>.
- NekRS `pb146` example — <https://github.com/Nek5000/nekRS/tree/master/examples/pb146>.

*Good luck — and remember: if you can't prove the mesh is valid, it isn't.*

---

*Based on ideas contributed by Misun Min and Paul Fischer.*
