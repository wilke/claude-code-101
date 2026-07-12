# Capstone Project: Mixed-Precision Benchmarking for Numerical Linear Algebra

## Purpose

This capstone is a **variation of [SolverBench](../SolverBench/README.md) and
[optSolverBench](../optSolverBench/README.md)**. Those two ask *which solver* and
*which optimizer* wins; **PrecisionBench asks how little precision you can spend at
each stage of an algorithm and still land a double-precision answer.** Treat
precision as a resource you allocate per stage: the **gold standard is fp64**, and
the goal is to **beat it with mixed precision — without reducing solution quality.**

Build a small, **reproducible benchmarking study** that answers a question the
mixed-precision literature keeps re-asking without settling: *for a given problem
class and regime (conditioning, size), which allocation of precisions across the
algorithm's stages preserves fp64-quality solutions — and by how much could it beat
fp64 on supporting hardware?* There are many options and no universal winner — the
contribution is a **fair, reproducible map** of where reduced precision is safe and
where it destroys the answer.

This is a *files, not chats* capstone: you develop the entire project from this
README using the skills from the exercises — a project `CLAUDE.md` for conventions,
plan mode for the harness, `LOGBOOK.md` for durable findings, `STATUS.md` for
handoffs, and a skill or two for the repetitive parts. Nothing else ships. The code
is yours to write.

- **Scope: two afternoons.** Afternoon 1 → a faithful low-precision simulator + a
  working harness + the well-conditioned baseline. Afternoon 2 → the ill-conditioned
  study + a paper draft. Depth on a narrow, honest comparison beats a broad shallow
  sweep.
- **Deliverable: a publication** — a short, reproducible benchmark/methods note.
  This kind of paper lives or dies on its methodology and its archived, re-runnable
  results. See *Publication outlets* at the end.

## No GPU required — and no wall-clock

You do **not** need a GPU, and you will **not** measure wall-clock time. On a CPU,
fp16/bf16 have no native throughput, so timing them is meaningless. Instead:

- **Solution quality is the metric.** Everything is judged by accuracy against a
  validated fp64 reference (see *Accuracy metrics*).
- **Low precision is *simulated*, faithfully.** Because the hardware doesn't run
  fp16/bf16 fast, you must *emulate* their arithmetic correctly (see *Faithfully
  simulating low precision*). Getting this right is the crux of the whole project.
- **Cost is *modeled*, not measured.** A hardware-agnostic model (per-stage
  FLOPs/bytes × a declared precision cost ratio) gives a *projected* speedup, always
  reported as "on hardware with throughput ratio r" — never as measured time.
- **One real, hardware-independent cost survives:** the **iteration count** to reach
  the fixed accuracy. A low-precision preconditioner often needs more iterations —
  record it.

## Packages

Standalone numpy/scipy — no Docker, no Firedrake, no GPU.

```bash
conda create -n precisionbench python=3.11 numpy scipy matplotlib
conda activate precisionbench
pip install pychop ml_dtypes pytest
```

| Package | Why you need it |
|---|---|
| **numpy**, **scipy** | the dense + `scipy.sparse` linear algebra you'll benchmark |
| **matplotlib** | the accuracy/cost figures (saved, never shown) |
| **pychop** | the **chop-style low-precision simulator** — rounds fp64 results to fp16, bf16, fp8, or a custom mantissa/exponent, with correct subnormal + overflow behavior and controllable accumulator precision. The heart of the project. |
| **ml_dtypes** | provides `bfloat16` / `float8_*` as numpy-compatible storage dtypes (bf16 is **not** native to numpy) |
| **pytest** | for the simulator-validation test suite (you must prove your fp16/bf16 emulation is real) |

Verify:

```bash
python3 -c "import numpy, scipy, pychop, ml_dtypes; print('ok')"
```

## The research gap

"Just use single precision, it's twice as fast" is folklore. The honest answer is
*it depends* — on the conditioning, the problem size, which stage you reduce, and
whether an outer correction can clean up the error. A careful study that holds
everything fixed except one axis, reports **where reduced precision stops preserving
the fp64 answer**, and ships a re-runnable harness is a genuine, publishable
contribution.

## A quick mixed-precision primer

New to floating-point formats, unit roundoff, and the **correction-protected vs.
error-anchoring** split across an algorithm's stages? A short primer — plus the
stage-by-stage precision-sensitivity categorization and the strategy menu — is in
[`precision-primer.txt`](precision-primer.txt).

## Faithfully simulating low precision (the crux)

The single biggest way this study goes wrong: **storing values in a low-precision type
is not the same as computing in low precision.** Two things must be controlled
independently — the **rounding of every operation's result** to the target format, and
the **accumulator precision inside reductions** (a fp16 dot product that secretly
accumulates in fp32 is not fp16). Make the accumulator precision an explicit, declared
parameter, handle dynamic range (overflow/underflow), and don't trust numpy's implicit
casts. See [`precision-reference.txt`](precision-reference.txt) for the full discipline.

## Problem statement

Solve `A x = b` for a symmetric positive-definite `A`, in two regimes, in order of
difficulty.

| Phase | Regime | Question | Why |
|---|---|---|---|
| **1 — baseline** | well-conditioned SPD (e.g. a mild 2D Laplacian, modest size) | Can 2-precision IR (fp32) reach the **fp64 forward error**? | Where mixed precision is *supposed* to work — validates the simulator, the harness, and the accuracy metric before anything hard. |
| **2 — the study** | crank up **conditioning** (refine the operator, add anisotropy, shrink a shift) until naive fp32 fails | Where does each strategy stop preserving fp64 quality? GMRES-IR vs 3-precision IR vs inner–outer, across κ, size, and accumulator precision | The "no clear winner" map — the allocation frontier is the result. |

**Optional intermediate bridge (only if you're ahead of schedule).** An **fp16
dynamic-range study**: push magnitudes toward fp16's overflow/underflow limits and
add **scaling / equilibration** as a declared step — a clean on-ramp to why bf16
(wide range, few mantissa bits) and fp16 (narrow range, more mantissa bits) fail
*differently*.

## Suggested approach (adaptable)

Build and *validate the simulator* first, then the harness, then the baseline. **The
simulator and the harness are the deliverable; the problem is a slot.** Design it with
Claude in plan mode — a sketch to adapt, not a recipe.

- **Afternoon 1 — simulator + harness + well-conditioned baseline.** Build the
  low-precision simulator and **gate everything on a validation test** — it must
  reproduce each format's unit roundoff, range, and subnormals (a simulator that quietly
  computes in fp32 makes low precision look free). Then run the harness on the
  well-conditioned baseline, where iterative refinement is *supposed* to recover fp64
  quality — if `ir_fp32` doesn't land on the fp64 line here, the bug is in the simulator
  or harness, not the physics.
- **Afternoon 2 — the ill-conditioned study + write-up.** Raise the conditioning until
  naive fp32 / simple IR stop reaching fp64 quality, compare the survivors, and sweep
  conditioning / stage allocation / accumulator precision one axis at a time — reporting
  *where the winner changes* in delivered accuracy and projected cost. Then draft the
  paper.

Plan the run-record schema (including the precision manifest), the baseline/survivor
configurations, and the sweep axes with Claude — **draw from the reference menu in
[`precision-reference.txt`](precision-reference.txt)**.

## Accuracy metrics

| Metric | Definition | Why |
|---|---|---|
| **Relative forward error** | `‖x − x_fp64‖ / ‖x_fp64‖`, in fp64 | did we land on the same answer? |
| **True residual** | `‖b − A x‖` recomputed in fp64 | backward stability of the mixed-precision solve |
| **Attained vs target tol** | reached the same stopping tol as fp64, or stalled? | equal-accuracy comparison |
| **Iterations to tol** | Krylov / outer count | the real hardware-independent cost |
| **Range events** | count of Inf / NaN / underflow-to-zero | fp16 range failures |

## Keeping the benchmark sound

| Rule | Why |
|---|---|
| **Validate the simulator first** — prove it reproduces each format's unit roundoff, range, and subnormals | otherwise you benchmark a fiction that computes in fp32 |
| **Declare the accumulator precision** of every reduction | "fp16 + fp64 accumulator" is a different experiment from "fp16 throughout" |
| **Compute the accuracy metric in fp64** against a validated-converged fp64 reference | measuring error in the precision under test hides the error |
| **Compare only at equal delivered accuracy** | reaching a looser tol in fp16 is not "beating" fp64 |
| **Cost is modeled, never timed** — report "on hardware with throughput ratio r" | no GPU; wall-clock of emulated fp16 is meaningless |
| **Fix `A`, `b`, the tolerance, and the reference**; vary one axis at a time | confounded sweeps produce unreadable maps |
| **Archive the environment** — numpy/scipy/pychop/ml_dtypes versions, seed, precision manifest — in every `runs/<timestamp>/` | reproducibility *is* the contribution |

## ⚠️ Integrity warning — do NOT let reduced precision be secretly higher than you think

**This is the single most important thing in this project.** A mixed-precision
benchmark measures whatever precision you *actually* computed in — and both an eager
assistant and numpy's implicit type promotion will quietly compute in *higher*
precision than you declared, making reduced precision look free. If that happens
silently, your numbers are fiction.

Treat every one of these as a **result to record, not a bug to patch**:

- **A simulator that isn't faithful.** If your "fp16" path secretly accumulates in
  fp32 (or numpy upcasts a `float16` reduction), you are measuring a rosier format
  than fp16. Validate the simulator against known unit-roundoff/range values before
  trusting anything.
- **Undeclared accumulator precision.** Reporting "fp16" without saying how the dot
  products accumulate is meaningless — state it for every run.
- **Error measured in low precision.** Computing `‖x − x_fp64‖` in fp16 hides the very
  error you're chasing. The metric is always fp64.
- **A reference that isn't converged.** The fp64 "gold standard" must be genuinely
  converged (tighten tol / check) before it can anchor comparisons.
- **Tolerance drift / unequal accuracy.** Loosening the tol, raising `max_it`, or
  comparing a less-accurate fp16 run against a fully-accurate fp64 run to declare a
  win.
- **Hidden range rescue.** Silently rescaling to dodge fp16 overflow/underflow — legit
  as a *declared* equilibration step, fiction as a quiet patch on one configuration.

**Defense:** gate every benchmark on a **passing simulator-validation test**; compute
all accuracy metrics in fp64 against a validated-converged reference; log every
non-finite value and underflow; emit the **precision manifest** so any silent
upcast/downcast is diffable. A "win" that came from computing in higher precision than
declared — or from a looser tolerance — is the tell. **A precision that fails to reach
fp64 quality is a legitimate, publishable data point.**

## Conventions to put in your project `CLAUDE.md`

Start the project by writing these into a `CLAUDE.md` in this folder (Exercise 01
applied for real). They are the rules most likely to be violated silently.

```markdown
## Stack
- numpy / scipy for the linear algebra (dense + scipy.sparse); matplotlib for figures
  (saved to figures/, never shown). No GPU, no Docker.
- Low precision is SIMULATED, not native: use a chop-style rounder (pychop) that
  rounds fp64 results to the target format (fp16, bf16, fp8, or custom) with correct
  subnormal + overflow behavior. ml_dtypes supplies bfloat16 / fp8 storage dtypes.
- We measure SOLUTION QUALITY only — never wall-clock time.

## Precision-simulation integrity — never let reduced precision be secretly higher
- Low precision is simulated. Before trusting any result, VALIDATE the simulator: it
  must reproduce the format's unit roundoff (fp16 ~2^-11, bf16 ~2^-8), overflow /
  underflow thresholds, and subnormal behavior. Ship a pytest that checks this.
- The accumulator precision of every reduction (dot, norm, SpMV, orthogonalization)
  is an EXPLICIT, DECLARED parameter. "fp16 with an fp64 accumulator" is a different
  experiment from "fp16 throughout" — never conflate them; state which for every run.
- The accuracy metric is ALWAYS computed in fp64 against a validated-converged fp64
  gold standard. Never compute error in the reduced precision under test. Never loosen
  the tolerance to declare a win; compare only at EQUAL delivered accuracy.
- Log every non-finite value (Inf/NaN) and underflow-to-zero. fp16 range failures are
  a result to record, not a bug to hide with silent rescaling.
- Emit a precision manifest per run: the storage, operation, and accumulator precision
  of each stage. Any silent upcast/downcast must be diffable after the fact.

## Cost model (no wall-clock)
- Projected cost is MODELED, not measured: per-stage FLOPs/bytes weighted by a
  declared precision cost ratio, reported as "on hardware with throughput ratio r."
  Never presented as measured time.
- Iteration count to reach the fixed tolerance IS measured — it is hardware-independent.
```

## Background & references

**Surveys**
- N. J. Higham, T. Mary, *Mixed precision algorithms in numerical linear algebra*,
  Acta Numerica 31 (2022), 347–414. <https://doi.org/10.1017/S0962492922000022> — the
  definitive survey; read this first.
- A. Abdelfattah et al., *A survey of numerical linear algebra methods utilizing
  mixed-precision arithmetic*, Int. J. High Performance Computing Applications 35(4),
  2021. <https://doi.org/10.1177/10943420211003313>

**Iterative refinement in multiple precisions**
- E. Carson, N. J. Higham, *Accelerating the solution of linear systems by iterative
  refinement in three precisions*, SIAM J. Sci. Comput. 40(2), 2018, A817–A847.
  <https://doi.org/10.1137/17M1140819>
- E. Carson, N. J. Higham, *A new analysis of iterative refinement and its application
  to accurate solution of ill-conditioned sparse linear systems*, SIAM J. Sci.
  Comput. 39(6), 2017, A2834–A2856. <https://doi.org/10.1137/17M1122918>

**Foundations & simulation**
- N. J. Higham, *Accuracy and Stability of Numerical Algorithms*, 2nd ed., SIAM, 2002
  — rounding-error analysis, unit roundoff, and stability, the theory behind the
  metrics.
- N. J. Higham, S. Pranesh, *Simulating low precision floating-point arithmetic*,
  SIAM J. Sci. Comput. 41(5), 2019, C585–C602. <https://doi.org/10.1137/19M1251308> —
  the `chop` method this project's simulator is built on.

**Tools**
- `pychop` — Python low-precision simulator (chop-style rounding to fp16/bf16/fp8/
  custom): <https://pypi.org/project/pychop/>.
- `ml_dtypes` — numpy-compatible `bfloat16` / `float8` dtypes:
  <https://github.com/jax-ml/ml_dtypes>.
- IEEE 754 half / bfloat16 background and the sibling capstones
  [`../SolverBench/README.md`](../SolverBench/README.md) and
  [`../optSolverBench/README.md`](../optSolverBench/README.md).

## Tasks checklist

For fun, you can hand this list to `claude` and let it plan — or work it step by step.

1. Install the packages (see *Packages* above) and write the project `CLAUDE.md`
   (conventions above).
2. Build the low-precision simulator and its **validation test**; do not proceed until
   it passes.
3. Plan the harness in plan mode; agree on the run-record schema (including the
   precision manifest) before coding.
4. Solve the well-conditioned baseline; produce the accuracy plot (IR on the fp64 line).
5. Record durable findings in `LOGBOOK.md` (which allocations preserve fp64 quality, and
   why); overwrite `STATUS.md` with the next step at each handoff.
6. Raise conditioning; compare the strategies; run the sweep over conditioning, stage
   allocation, and accumulator precision.
7. (Optional) Add the fp16 dynamic-range / equilibration bridge study.
8. Write the paper: methodology, simulator validation, reproducibility manifest, plots,
   the map.

## Publication outlets

* [SIAM Journal on Scientific Computing (SISC)](https://www.siam.org/publications/siam-journals/siam-journal-on-scientific-computing/) — the natural home for a mixed-precision numerical study
* [ACM Transactions on Mathematical Software (TOMS)](https://dl.acm.org/journal/toms) — algorithms & software, benchmarking-friendly
* [International Journal of High Performance Computing Applications (IJHPCA)](https://journals.sagepub.com/home/hpc) — where much of the mixed-precision literature lives
* [Journal of Open Source Software (JOSS)](https://joss.theoj.org/) — if the simulator + harness itself is the contribution
* A reproducible arXiv preprint / workshop proceedings — the fastest honest home for a two-afternoon study

*Good luck — and don't let reduced precision pretend to be double.*

---

*Based on an idea contributed by Srinivas Eswar.*
