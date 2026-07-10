<!--slide n=50 layout=content kicker="Wrap-up"-->
# Seven habits worth keeping
1. **Set up the four-file architecture early.** `CLAUDE.md` (conventions), `plans/` (forward), `MEMORY.md` (learned), `STATUS.md` (current). One job per file; don't conflate them.
2. **Plan before you build.** Plan mode for anything beyond a one-line edit. Save the plan to `plans/<date>-<slug>.md` before you implement.
3. **Promote recurring tasks to skills.** Anything you do twice — KKT check, perf profile, log parsing — becomes a SKILL.md.
4. **Commit before you prompt.** A clean working tree means every Claude change is visible in `git diff` and reversible in one command.
5. **Test both code and results.** Unit tests in `tests/` for correctness; experimental-regression tests in `bench/` for result quality. A CLAUDE.md rule that says "run pytest after every edit" removes the most common failure mode.
6. **End every session with the two-line ritual.** Append a dated entry to MEMORY.md if anything was decided; overwrite STATUS.md with the next concrete step. Two minutes.
7. **When you're whack-a-mole-ing, stop and formalize.** Loops mean an invariant is unwritten. Write it, test it, and the loop ends.


<!--slide n=51 layout=content kicker="Reference"-->
# Files vs. built-ins: how this maps to Claude Code
_Two of the four files are the official path; two deliberately turn ephemeral built-ins into durable, versioned files._

| This deck | Claude Code natively |
|---|---|
| `CLAUDE.md` | The native memory file — hierarchy + `@import`. **Same thing.** |
| Skills | Native, loaded on demand. **Same thing.** |
| `plans/` | Plan mode is a permission mode — **ephemeral**, never written to disk. We persist it. |
| `MEMORY.md` | CLAUDE.md *is* the memory; we split durable facts into a file it points at. (Name clashes with Claude Code's own auto-memory `MEMORY.md`.) |
| `STATUS.md` | `--resume` / checkpoints are **machine-local** — a committed file crosses machines, CI, and collaborators. |

> Same diagnosis as the official guide — context degrades as it fills — but a different remedy: **write it to disk**. Strongest when work crosses sessions, machines, or people; redundant when it doesn't.

Full comparison: `docs/native-claude-code-mapping.md`. Official guide: `docs.claude.com/en/best-practices`.


<!--slide n=52 layout=content kicker="Resources"-->
# Where to go from here
- **Authoritative reference: `docs.claude.com/en/best-practices`** — Anthropic's official guide. Read it after this workshop; our four-file architecture and literature material are opinion-laden extensions of it.
- Documentation: `docs.claude.com/claude-code`
- Source & issues: `github.com/anthropics/claude-code`
- Skills examples: the `.claude/skills/` in this workshop's exercises folder
- A power-user reference setup: `github.com/affaan-m/everything-claude-code` — heavy on software-engineering skills; useful as a layout example, not a starting point.
- Optimization-specific:
    - PETSc/TAO: `petsc.org` — the user manual chapter on TAO is short and excellent.
    - Pyomo: `pyomo.readthedocs.io`
    - CasADi: `casadi.org`
    - CUTEst: `github.com/ralna/CUTEst`

Questions, or stories of what worked: keep notes in MEMORY.md. The next session will thank you.
