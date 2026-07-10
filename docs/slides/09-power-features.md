<!--slide n=39 layout=section kicker="Part 6 · Power features"-->
# Beyond the basics
_Four mechanisms that change what's possible: checkpoints for reversible exploration, subagents for context-isolated work, hooks for deterministic enforcement, and non-interactive mode for fan-out at scale._


<!--slide n=40 layout=content kicker="Power features"-->
# Checkpoints — try, rewind, try again
Every action Claude takes creates a checkpoint. Press Esc Esc (or run `/rewind`) to open a menu and restore prior state.

- **Restore conversation only** — get back the chat, keep the code as it is.
- **Restore code only** — undo Claude's file edits, keep the conversation history.
- **Restore both** — full rewind to a prior moment.
- **Persists across sessions** — you can close the terminal and rewind tomorrow.

Two reverting tools at different scales: **git** for committed history, **/rewind** for in-session backtracks. Use them together.

> Practical pattern: have Claude try something risky; if the diff isn't right, rewind and re-ask with the lesson learned. The cost of a wrong direction drops to near zero.

Caveat: `/rewind` tracks changes *made by Claude*. External edits, build artifacts, and database state are out of scope. Don't treat it as a replacement for git.


<!--slide n=41 layout=content kicker="Power features"-->
# Subagents and hooks
|  | Skill | Subagent | Hook |
|---|---|---|---|
| Lives in | `.claude/skills/` | `.claude/agents/` | `.claude/settings.json` |
| Context | Loads into your main session | Runs in a separate window — reports back a summary | None — just runs a script |
| Best for | Recurring domain logic (KKT check) | Investigative reads (research a 200-file solver) | Things that must happen *every time* |
| Trigger | Description-match on the task | You ask Claude to delegate | Specific events (PostToolUse, etc.) |
| Reliability | Advisory — usually loaded | Advisory — when delegated | **Deterministic** — guaranteed to fire |

Mathematician examples:

- **Subagent.** A `solver-archaeologist` (`tools: Read, Grep, Glob`) that reads 200 files of inherited solver code and writes a one-page summary — your main session never sees the 200 files.
- **Hook.** Promote "run `pytest -q` after every edit" from a CLAUDE.md rule (advisory) to a hook (deterministic) — it fires whether Claude remembers or not.


<!--slide n=42 layout=content kicker="Power features"-->
# Non-interactive mode — fan-out at scale
`claude -p "prompt"` runs Claude without a session — single shot, machine-readable output. This is what makes Claude usable as a step in a pipeline rather than a chat partner.

```
# Run a solver across the CUTEst small cohort, log per-problem
for prob in $(cat cutest_small.txt); do
  claude -p "solve $prob with mu_init=1e-2 using our IPM driver. \
             Report status, iters, KKT residual as JSON." \
    --allowedTools "Bash(python *),Read,Write" \
    --output-format json >> runs/cohort_2026-05-07.jsonl
done

# Pipe data in directly
cat error.log | claude -p "extract the failing test names as a list"
```

- **`--allowedTools`** scopes permissions for unattended runs.
- **`--output-format json`** for parseable results; `stream-json` for real-time consumption.
- **`--permission-mode auto`** lets a classifier handle approvals; aborts if it repeatedly blocks (no human to fall back to).

> For optimization research this is the unlock: a parameter sweep that used to take 20 manual steps becomes a shell loop. Combined with the `kkt-checker` skill, you can run a 1300-problem CUTEst study overnight with consistent output.
