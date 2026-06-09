# Solution — Exercise 4 (MEMORY.md)

## What this exercise is doing

You have three lab notebook entries in `notebooks/`. Each one is the kind of thing you'd jot down at the end of a research day: what worked, what didn't, what the next question is. The exercise is to consolidate them into a structured `MEMORY.md` that Claude can read on every future session.

## A worked MEMORY.md

This is what Claude should produce when you ask it to read `notebooks/` and synthesize a memory file. Edit it down to the point where every line still earns its place.

```markdown
# MEMORY — Inertia-corrected interior-point solver

## Decisions

- **2026-03-12 — Default solver: IPOPT.**
  IPOPT converged on the catalysis benchmark in 47 iterations with KKT
  residual 3e-9. SNOPT was faster (31 iters) but returned multipliers with
  sign errors on 4 of 17 active inequalities — interface bug, not chasing.
  License: IPOPT is EPL-licensed; our SNOPT shared license is saturated.
  Source: `notebooks/2026-03-12-solver-choice.md`.

- **2026-04-08 — Default `mu_init = 1e-2`.**
  Sweep over {1e-6, 1e-4, 1e-2, 1e0} on the seven-problem cohort. 1e-2
  was fastest in mean iterations (52.3) and time (7.8 s) with no
  divergence. 1e0 diverged on catalysis and tube-flow (initial barrier
  too weak). Override to 1e-4 only if the catalysis-style instability
  appears. Source: `notebooks/2026-04-08-mu-init-sweep.md`,
  results in `runs/2026-04-08T0930/summary.csv`.

## Parameters

- `mu_init = 1e-2` (default; see decision 2026-04-08)
- `tol = 1e-8` (project-wide)
- Inertia threshold: still default Wächter–Biegler — flagged as an open
  question on 2026-03-12.

## Dead ends

- **Tikhonov-regularized KKT for the inverse Poisson family — does not work.**
  Primal residual converges, but dual block residual stalls at 1e-2 even
  with `tol=1e-10`. Reason: the dual block is fundamentally indefinite for
  this inverse problem; forcing PD shifts the saddle point. Two days lost;
  do not retry. Source: `notebooks/2026-04-29-tikhonov-deadend.md`.

- **SNOPT for catalysis-class problems.** See solver-choice decision above.

## Open questions

- **Inertia threshold problem-dependence.** Defaults from
  Wächter–Biegler 2006 work on HS071 but not on catalysis. Plan a sweep.
  Raised 2026-03-12, still open.

- **Vermeersch–Anitescu 2019 saddle-point smoothing.** Skim before
  committing time; might offer an alternative to Tikhonov. Raised
  2026-04-29.
```

## What "next experiment" might look like

After this MEMORY.md exists, ask:

```
given MEMORY.md, what's the most informative next experiment to run?
Justify in two sentences.
```

A reasonable answer would be: *"Sweep the inertia threshold across the seven-problem cohort with `mu_init = 1e-2` fixed. The Wächter–Biegler default works on HS071 but stalled on catalysis (2026-03-12), so problem-dependent tuning is the highest-leverage open question; `mu_init` is already pinned, so we change one variable at a time."*

That's the kind of answer you can act on in an afternoon. Not because Claude is clever — because MEMORY.md gave it the context to be specific.

## Where the seam between CLAUDE.md and MEMORY.md sits

These two files are easy to confuse. A working rule:

- **CLAUDE.md** answers *"how does this project work?"* — stack, conventions, commands, do-not-do rules. It changes rarely.
- **MEMORY.md** answers *"what have we learned?"* — decisions with dates and reasons, parameter folklore, dead ends. It grows monotonically.

A test: if a fact would be true in any session of this project regardless of what you've discovered, it belongs in CLAUDE.md. If knowing it depends on having run experiments, it belongs in MEMORY.md.

## The two-minute end-of-session ritual

The single highest-leverage habit from this exercise is: at the end of every session, ask Claude to summarize what was decided and append it to MEMORY.md. Two minutes. Pays back in weeks.

```
summarize what we just did and append a dated entry to MEMORY.md under
Decisions or Open Questions, whichever fits.
```
