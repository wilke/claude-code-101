# The evolution: one logbook → a directory of ADRs

`LOGBOOK.md` is the workshop's fourth artifact — the durable, hand-maintained
record of what a long-running research project *learned*: decisions, parameter
folklore, dead ends, open questions, run logs. (For where it sits relative to
Claude Code's built-ins — and why it is **not** named `MEMORY.md` — see
[`native-claude-code-mapping.md`](native-claude-code-mapping.md).)

This note is about how that one file **scales**. A logbook does not stay a single
file forever, and it should not collapse into an unstructured wall of prose. It
grows through three stages, and the trigger to move between them is concrete, not
aesthetic.

The through-line:

> **The logbook is append-only *entries*. The ADR directory is append-only
> *files*.** Same discipline, one level up. You graduate a decision to an ADR
> exactly when it earns its own identity — when it needs to be *cited*, *reviewed
> in isolation*, or *reversed cleanly*.

ADRs do **not** replace the logbook. They extract the one subset — decisions —
that benefits from individual identity, while the logbook keeps running as the
diary (run logs, folklore, open questions, the day-to-day narrative).

---

## Stage 1 — One file

`LOGBOOK.md`, append-only, dated entries, everything chronological. This is all a
project needs for a long time. Keep it a *log, not a document you rewrite*.

```
# LOGBOOK

## 2026-03-12
Chose IPOPT over SNOPT — license reasons, see issue #41. plans/solver-eval.md.
mu_init=1e-2 fastest on our cohort; 1e-4 diverges on the catalysis problem.

## 2026-04-22
Dead end: Newton + Tikhonov on inverse Poisson converges but multipliers are
noise. Don't repeat. Best run so far: runs/2026-04-22T1430, ‖∇f‖ = 3.7e-9.
```

**Move on when:** you catch yourself scrolling to find "why did we pick X", or the
file passes a screenful and its structure stops being obvious.

## Stage 2 — A topical directory

Fan the single file out into a `logbook/` directory with one file per topic, plus
an `INDEX.md`. Entries stay chronological *within* each file. This buys
findability without changing the discipline.

```
project/
└── logbook/
    ├── INDEX.md          # contents page — one line per topic file
    ├── solvers.md
    ├── experiments.md
    ├── dead-ends.md
    └── open-questions.md
```

Wire the index into `CLAUDE.md` so Claude maintains it on every append:

```
When you append to any file under logbook/, add or update the matching line in
logbook/INDEX.md.
```

**Move on when:** a *decision* needs to be a first-class object — see the triggers
below. Note you only promote **decisions**; folklore, run logs, and open questions
stay in the logbook.

## Stage 3 — Promote decisions to ADRs

An **Architecture Decision Record (ADR)** is a dated, numbered, version-controlled
record of a single decision plus its context and consequences. It is a
well-established engineering pattern; adopting it gives the logbook's decisions a
recognizable, reviewable shape.

The logbook keeps the running narrative; `decisions/` holds the durable, citable
decisions:

```
project/
├── logbook/              # the running diary — still append-only
│   ├── INDEX.md
│   ├── experiments.md
│   ├── dead-ends.md
│   └── open-questions.md
└── decisions/
    ├── INDEX.md          # number → title → status, one line each
    ├── 0001-ipopt-over-snopt.md
    ├── 0002-mu-init-schedule.md
    └── 0003-adaptive-rho-over-fixed.md
```

### When to graduate a decision to an ADR — the triggers

Pull a decision out of the logbook the moment *any* of these is true:

1. **You want to cite it by name.** "See ADR-0001" beats "scroll to the March 12
   entry."
2. **It might be reversed.** ADRs carry a `Superseded by` field; a chronological
   log does not.
3. **It needs review in isolation.** A PR touching one ADR file is reviewable; a
   decision buried inside a 300-line log diff is not.
4. **The decisions list crosses ~10 entries** and you need a contents page to
   navigate it.

### ADR anatomy — the minimal template

```
# ADR-0001: IPOPT over SNOPT

- Status: Accepted            (Proposed → Accepted → Superseded / Deprecated)
- Date: 2026-03-12
- Context: Need an interior-point NLP solver for the cohort. SNOPT license is
  per-seat and blocks CI; IPOPT is EPL and vendorable. Evidence: issue #41,
  plans/solver-eval.md, literature/wachter-biegler-2006.md.
- Decision: Standardize on IPOPT for all cohort runs.
- Consequences: Lose SNOPT's SQP robustness on a few dense QPs (track in the
  logbook). CI unblocked. Revisit if inertia correction proves problem-dependent.
```

### Two rules that keep it honest

Both preserve the append-only spirit at the *directory* level:

- **Numbers are immutable and sequential** (`0001`, `0002`, …). You never renumber.
- **You never edit an Accepted ADR's decision — you supersede it.** Reversing
  course means a *new* ADR whose Context references the old one; then you flip the
  old ADR's status to `Superseded by ADR-00NN`. The history stays intact, exactly
  like the logbook it grew out of.

A worked supersession:

```
# ADR-0003: Adaptive ρ over fixed ρ for the ADMM-Filter driver

- Status: Accepted
- Date: 2026-06-03
- Context: ADR-0002 fixed ρ for the ADMM outer loop. On the 30×10 cantilever the
  fixed-ρ baseline (admm.py) fails to converge in 30 iterations; the adaptive-ρ
  driver (FilterADMM.py) converges in ~14. Evidence: logbook/experiments.md 2026-06-03.
- Decision: Make adaptive ρ the default; keep fixed ρ behind a flag for comparison.
- Consequences: Supersedes ADR-0002 (fixed ρ). One more tuning knob (the ρ update
  rule) to document.
```

…and in `decisions/0002-mu-init-schedule.md` you set `Status: Superseded by
ADR-0003`. You did **not** delete or rewrite ADR-0002 — its record of *why fixed ρ
seemed right at the time* is exactly what stops someone re-proposing it.

---

## Where this shows up in the workshop

- **Slide deck** — Part 4 (`docs/slides/06-memory.md`) introduces `LOGBOOK.md` and
  points here for the scaling story.
- **Exercise 4** — every track (`exercises-opt/04-logbook/`,
  `exercises-pde/04-logbook/`, `exercises-lin_alg/04-logbook/`) bootstraps a
  `LOGBOOK.md` from raw dated notebook/plan entries (Stage 1), then a stretch splits
  it into a `logbook/` directory (Stage 2) and promotes decisions to ADRs (Stage 3).
