# Status — capstone, in progress

(Overwrite this file at the end of each session. Keep it under one screen.)

## Active plan
plans/2026-05-07-tao-implementation.md — step 3 of 7 (TAO context)

## Current state
- Steps 1–2 complete: PETSc Laplacian Mat verified against scipy version
  to 1e-13; KSP+PCG+ICC solver built and tested on a random RHS.
- Step 3 in progress: TAO BLMVM context constructed but `setObjectiveGradient`
  callback signature needs the right Vec adapter (step 4 idea).
- numpy backend still works; `--check-grad` passes at rel error ~3e-10.

## Next step
Read plan step 4. Implement the Vec-to-numpy adapter using
`vec.getArray(readonly=True)` for input and `vec.array[:] = grad_np` for
output. Then return to step 3 and finish wiring the TAO callback.

## Open questions still in MEMORY.md
- DMDA vs. flat AIJ matrix for parallel solves — deferred (see plan).
- Block-preconditioning the KKT matrix vs. reduced-space — separate study.
