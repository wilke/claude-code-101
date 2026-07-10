<!--slide n=28 layout=section kicker="Part 4 · The diary"-->
# LOGBOOK.md
_Long-running research generates decisions, dead-ends, and parameter folklore. LOGBOOK.md is where those facts live so the next session can use them._


<!--slide n=29 layout=content kicker="LOGBOOK.md"-->
# CLAUDE.md vs LOGBOOK.md
|  | CLAUDE.md | LOGBOOK.md |
|---|---|---|
| Lifespan | Stable across the project | Evolves with the research |
| Content | Conventions, commands, do/don't | Decisions, parameter values, dead-ends |
| Edited by | You, deliberately | You and Claude — at the end of each session |

Small projects: one LOGBOOK.md. As it grows: a `logbook/` directory (`solvers.md`, `experiments.md`, `dead-ends.md`) with an `INDEX.md`; and when a *decision* needs to be cited, reviewed, or reversed, promote it to a numbered ADR in `decisions/`. (See `docs/logbook-to-adrs.md`.)

> We call it `LOGBOOK.md`, not `MEMORY.md`: Claude Code auto-generates its own machine-local `MEMORY.md` — keep the two separate. Full contrast in `docs/native-claude-code-mapping.md`.


<!--slide n=30 layout=content kicker="LOGBOOK.md"-->
# What to record
- **Decisions.** "IPOPT over SNOPT for license reasons — 2026-03-12, issue #41."
- **Parameter folklore.** "`mu_init=1e-2` fastest on our cohort; `1e-4` diverges on the catalysis problem."
- **Dead ends.** "Newton + Tikhonov on inverse Poisson converges but multipliers are noise. Don't repeat."
- **Open questions.** "Is the inertia-correction threshold problem-dependent? Re-check HS071, HS099."
- **Run logs.** "Best so far: `runs/2026-04-22T1430`, ‖∇f‖ = 3.7e-9."

> Keep it append-only and dated — LOGBOOK.md is a log, not a document you rewrite. Capturing these entries is part of the end-of-session ritual (next slide, with STATUS.md).


<!--slide n=31 layout=content kicker="LOGBOOK.md"-->
# Handoff: STATUS.md, not LOGBOOK.md
LOGBOOK.md holds durable knowledge and grows. **Don't put session handoff in it** — "mid-debug on X, next step Y" is true today, noise next week. Use a small, separate, *overwritten* file:

```
# STATUS — 2026-05-07 17:42

## What I'm working on
Filter line search for the IPM driver. PR branch: filter-linesearch.

## Current state
- driver.py and filter.py compile, unit tests pass on synthetic 2D.
- HS071 fails with KeyError: 'theta_max' in filter.accept(...).
- Haven't read filter.py:43-67 yet.

## Next step
Read filter.py:43-67. If theta_max not set in __init__, add it.
Then re-run pytest tests/test_linesearch.py -k HS071.
```

> End-of-session ritual: `append a dated entry to LOGBOOK.md and overwrite STATUS.md with where we are now`. Two minutes. Next session: read STATUS.md and you're back in flight.


<!--slide n=32 layout=content kicker="LOGBOOK.md"-->
# Handoff mechanisms, ordered by reliability
| Mechanism | Reliability | Notes |
|---|---|---|
| STATUS.md you wrote | Highest | You control it; survives anything. |
| Branch name | High | `git branch --show-current` tells you what's in flight. |
| Last commit message | High | A WIP commit is a one-line handoff for free. |
| `claude --continue` | Medium | Brings back the conversation. Brittle: may already be compacted; gone if you switch machines. |

The pattern: rely most on what's in *files* (top three rows). Rely least on what's only in chat state (last row). The deck of files — CLAUDE.md, LOGBOOK.md, STATUS.md — is what survives whatever a session throws at you.


<!--slide n=33 layout=section-->
# Exercise 4
_Please refer to your supplemental slide deck. Open your track's exercise:_

:::columns
### Optimization
- [exercises-opt/04-memory/](exercises-opt/04-memory/)

### PDE / FEM
- [exercises-pde/04-memory/](exercises-pde/04-memory/)

### Linear algebra
- [exercises-lin_alg/04-memory/](exercises-lin_alg/04-memory/)
:::
