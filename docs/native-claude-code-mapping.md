# The four-file architecture vs. native Claude Code

How this workshop's opinionated **four-file architecture** (`CLAUDE.md`, `plans/`,
`LOGBOOK.md`, `STATUS.md`) relates to what Claude Code ships natively and to
Anthropic's official best-practices guidance.

> **Naming note.** The durable-knowledge file is called **`LOGBOOK.md`**. Earlier
> revisions of this workshop named it `MEMORY.md`; it was renamed precisely to
> avoid the collision described in the table below — Claude Code ships its own
> machine-local auto-memory file that is *also* called `MEMORY.md`. Wherever this
> doc says `MEMORY.md`, it means Claude Code's native file, not the workshop's.

> **Sources.** Claude Code feature facts below were checked against the official
> docs (`code.claude.com/docs/en/memory`, `.../permission-modes`,
> `.../checkpointing`, `.../sessions`, `.../best-practices`). The mapping and the
> judgements are this workshop's analysis, not official guidance.

## One-line contrast

- **Anthropic's framing:** the binding constraint is the **context window** — "it
  fills fast and performance degrades as it fills." The built-in tools manage
  context *within and across sessions*, and are mostly **ephemeral, automatic, and
  machine-local**.
- **This workshop's framing ("files, not chats"):** the binding constraint is
  **continuity of a long research project** across sessions, machines, and people.
  The remedy is to **externalize durable state into versioned, human-readable files**.

Same diagnosis ("the conversation is scratch paper" ≈ "context degrades"),
**different remedy**: Anthropic says *manage and reset* the session; the deck says
*write it to disk*. The two are layered, not opposed — the deck is a
persistence-and-provenance layer on top of Anthropic's context-management layer.
(The deck says as much: its Resources slide calls the architecture "opinion-laden
extensions" of the official guide.)

## File-by-file mapping

| Deck artifact | Native Claude Code | Best-practices stance | Verdict |
|---|---|---|---|
| **CLAUDE.md** — conventions, "don'ts", pointers | **Native memory system**: enterprise/user/project hierarchy, `@import`, `/memory`, `/init` | Recommended; keep **< 200 lines**; use `.claude/rules/` for path-scoped detail | **Full alignment.** The deck's "Pointers" bullets ≈ `@import`. |
| **plans/** — durable, dated plan files ("evidence") | Plan mode is a **permission mode** — ephemeral, never written to disk; **no native `plans/`** | Explore → Plan → Code → Commit via *ephemeral* plan mode; does **not** recommend persisting plans | **Opinionated extension.** Persists what Claude Code keeps transient. |
| **LOGBOOK.md** — hand-written durable knowledge | CLAUDE.md **is** the memory file. A native **auto-memory `MEMORY.md`** exists but is auto-generated & machine-local (`~/.claude/projects/…/memory/`) — **not** your repo file, which Claude Code will **not** auto-load | No hand-written durable-knowledge file | **Convention, not a feature** — only works if CLAUDE.md points at it. Named `LOGBOOK.md` **specifically to dodge the name collision** with the native auto-memory `MEMORY.md`. |
| **STATUS.md** — overwritten per-session handoff | `--continue` / `--resume` + **checkpoints / `/rewind`** — persistent *within a project* but **machine-local**, don't sync across machines/CI, and only track Claude's own edits | Use checkpoints / `/rewind` and `/clear`; **no STATUS.md** | **Sharpest divergence** — and the deck's strongest point (below). |
| **Skills** | Native, load-on-demand | Recommended | **Full alignment.** |
| **Literature / RAG** | Not native | Not mentioned | **Pure opinion add.** |

## Where the deck genuinely beats the built-ins

The built-in state model is **private, automatic, and machine-local**. The deck's
files are **shared, versioned, and reviewable**. That gap is real:

1. **STATUS.md > checkpoints for the cross-boundary case.** Checkpoints are
   machine-local and don't sync — a new laptop, a collaborator, or a CI run gets
   nothing. A committed STATUS.md survives all of that. (The deck's "handoff
   reliability" slide ranks a hand-written STATUS.md *above* `--continue` for
   exactly this reason, and that ranking is technically correct.)
2. **plans/ + LOGBOOK.md = a git-versioned audit trail.** For reproducible research
   and multi-author labs, "why did we pick IPOPT / abandon Tikhonov" belongs in the
   repo — diffable and code-reviewable — not in a machine-local transcript only one
   person can `--resume`.
3. **The files onboard a human, not just the model.** They double as lab docs.

## Where the deck fights the grain (the costs)

1. **Redundancy.** `plans/` duplicates plan mode; `STATUS.md` duplicates
   `--resume` + checkpoints; `LOGBOOK.md` must be manually wired through CLAUDE.md
   because it isn't auto-loaded. You re-implement, by discipline, what the tool
   does automatically.
2. **Automation → manual ritual.** Auto-memory and checkpoints are free; the deck's
   LOGBOOK.md / STATUS.md depend on the end-of-session ritual actually being
   performed. It trades *automatic* for *durable + controlled*.
3. **The name clash is resolved by the `LOGBOOK.md` name.** Earlier revisions called
   the file `MEMORY.md`, which was a concrete footgun once Claude Code shipped its
   own auto-memory `MEMORY.md`. The rename to `LOGBOOK.md` removes the collision;
   the two files now have distinct names and distinct roles (durable, versioned,
   hand-written vs. ephemeral, machine-local, auto-generated).
4. **Predates newer built-ins.** Best practices now lean on `.claude/rules/`
   (path-scoped), `/goal`, and auto-memory — mechanisms the deck could adopt or at
   least acknowledge. Its dense example CLAUDE.md also runs against the "< 200 lines"
   guidance (though its "Pointers" pattern is the right fix).

## Bottom line

The workshop isn't in conflict with best practices — it's a
**persistence-and-provenance layer stacked on Anthropic's context-management
layer**, tuned for *long-horizon, multi-session, multi-person scientific work*
rather than the single-developer, single-machine loop the built-ins optimize for.
Two of the four files (**CLAUDE.md, skills**) are exactly the official path; the
other two (**plans/, LOGBOOK.md/STATUS.md**) are deliberate, defensible
*reifications of ephemeral built-ins* — strongest when work crosses machines, CI,
or collaborators, and weakest as pure duplication when it doesn't.
