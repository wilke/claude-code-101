<!--slide n=8 layout=content kicker="Session basics"-->
# How a session works
_Everything Claude reads and writes in a session lives in one finite buffer — the context window._

- Every prompt, file read, and tool output goes into the same window.
- Large but bounded — the context window is model-specific.
- Near the limit, Claude Code **auto-compacts**: older messages are summarized to make room.
- Compaction is lossy — details from early turns can fade. Keep anything that matters on disk.

> Long sessions are fine — but because compaction is lossy, treat the running conversation as ephemeral. Anything that matters belongs on disk.


<!--slide n=9 layout=content kicker="Session basics"-->
# What persists, what doesn't
|  | Survives a new session? | Survives auto-compact? |
|---|---|---|
| Files in your project (code, LOGBOOK.md) | Yes | Yes — they're on disk |
| CLAUDE.md | Yes — auto-loaded each session | Yes — kept in context |
| Skills | Yes — loaded on demand by description match | Re-loaded as needed |
| The conversation itself | Only with `--resume` | Compressed to a summary |
| "Mental notes" Claude has in-conversation | No — they vanish | Often lost |

If a fact matters tomorrow, write it to LOGBOOK.md today. If it's a reusable procedure, lift it into a skill. **The conversation is scratch paper.**


<!--slide n=10 layout=content kicker="Session basics"-->
# Save, resume, clear
```
# Resume the most recent session in this project
claude --continue

# Pick from a list of past sessions
claude --resume

# Inside a session
/clear      # wipe the conversation; keep CLAUDE.md, skills, files
/compact    # manually summarize older turns to free context space
```

Sessions are stored locally under `~/.claude/projects/<hash>/`. They're plain files; you can grep them.

> **Don't lean on `--resume` to remember decisions** — it's brittle. Persist anything that matters to files. We'll cover the end-of-session ritual with LOGBOOK.md and STATUS.md in Part 4.
