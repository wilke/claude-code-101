# Workflow guide — sessions, version control, and breaking loops

Backs the *Session basics* and *Working sustainably* sections of the deck. This is the practical companion to the conceptual material on CLAUDE.md, planning, skills, LOGBOOK.md, and MCP — i.e., *how to keep doing this for months without your repo going sideways.*

## 1. How a session works

When you run `claude`, you start a *session*. Everything Claude reads and writes — your prompts, file contents it loads, command outputs, tool results — accumulates in a single buffer called the **context window**.

- The context window is large but bounded. Modern Claude models support around 200,000 tokens (roughly 150,000 words, or ~600 pages of text). That's plenty for most work, but not infinite.
- When the buffer fills, Claude Code performs **auto-compaction**: older messages are replaced with a summary so newer work has room.
- Auto-compaction is lossy. Specific facts from the early part of a long session can become "we discussed X" in the summary — accurate at the level of topic, vague at the level of detail.

**Mental model.** The conversation is a whiteboard, not a notebook. Anything you'd want to read tomorrow goes into a file (CLAUDE.md, LOGBOOK.md, source code, a comment), not into the chat.

## 2. What persists across sessions

| Item | Reloaded on next session? | Survives auto-compact within a session? |
|---|---|---|
| Files in your repo (code, LOGBOOK.md, runs/) | Yes — they're on disk | Yes |
| `CLAUDE.md` | Yes — auto-loaded at session start | Yes — kept in context |
| Skills under `.claude/skills/` | Yes — loaded on demand by description match | Re-loaded as needed |
| Registered MCP servers | Yes — config persists | Connection persists |
| The chat transcript | Only with `--resume` / `--continue` | Compressed to a summary |
| Mid-conversation working memory ("remember to also fix that") | No — vanishes | Often lost |

The single most important rule: **if a fact matters tomorrow, write it to LOGBOOK.md today**. Don't trust the conversation to remember it.

## 3. Save, resume, clear

```
claude --continue          # resume the most recent session in this project
claude --resume            # pick from a list of past sessions
```

Sessions are stored locally in `~/.claude/projects/<project-hash>/`. They're plain JSON files; you can grep them, copy them between machines, archive them.

Inside a session:

```
/clear      wipe the conversation; CLAUDE.md, skills, files all stay
/compact    manually summarize older turns to free context space
```

Useful patterns:

- **Long focused work.** Use `/compact` at natural break points (e.g., after finishing a feature) so the model keeps space for the next phase.
- **Switching topics.** Use `/clear` rather than letting the conversation drift across unrelated topics. Each topic gets a clean window.
- **End of day.** Always end with `summarize what we did and append a dated entry to LOGBOOK.md`. Two minutes; pays back in weeks.

## 4. Claude Code vs. Cowork

Both are interfaces to the same model family with the same skills system, but they're optimized for different work.

| | **Claude Code** | **Cowork** |
|---|---|---|
| **Surface** | Terminal CLI, IDE plugins | Desktop app feature |
| **Centered on** | A project folder of code, data, papers | Cross-tool workflows on your computer |
| **Reads / writes** | Files in the project; runs shell commands | Files + connectors (Slack, Gmail, Notion, Calendar, Drive) |
| **Audience** | Developers, researchers writing code | Knowledge workers including non-developers |
| **Strong fit** | Solver development, experiments, paper LaTeX, anything in a git repo | Grant admin, email triage, briefings that pull from multiple SaaS tools |
| **Plugins / skills / memory** | Yes — `.claude/skills/`, CLAUDE.md, LOGBOOK.md | Yes — same conventions; plus connector-aware skills |

**For optimization research, Claude Code is the workhorse.** It's where you write the solver, run experiments, build CUTEst harnesses, generate paper figures, manage LOGBOOK.md.

**Where Cowork helps an optimization researcher.** When the work crosses tools your terminal can't reach: drafting a referee reply that pulls from your Calendar (when's my response due?), Gmail (what did the editor actually ask?), and a Notion outline of your prior responses, in one chat. Or weekly grant-admin work — pulling spend tracking from Drive, due dates from your calendar, status from email.

The two complement each other. You don't pick one.

## 4b. Session handoff: STATUS.md vs. LOGBOOK.md

A common early mistake is to use `LOGBOOK.md` for session-to-session handoff: "I'm in the middle of debugging X; next step is Y." Don't. The two have different lifecycles, and mixing them makes both worse.

| | **LOGBOOK.md** | **STATUS.md** |
|---|---|---|
| Purpose | Durable knowledge | Where you are right now |
| Lifecycle | Append-only; rarely consolidated | Overwritten each session |
| Lifespan of an entry | Months to years | Hours to days |
| Length | Grows; index it past ~200 lines | One screen, always |
| Read by | Claude every session, future-you, future-collaborator | You, at the start of the next session |

A typical `STATUS.md` answers exactly three questions:

```markdown
# Status — 2026-05-07 17:42

## What I'm working on
Filter line search for the IPM driver. Branch: filter-linesearch.

## Current state
- driver.py and filter.py compile; synthetic 2D tests pass.
- HS071 fails with KeyError: 'theta_max' inside filter.accept(...).
- Haven't read filter.py:43-67 yet.

## Next step
Read filter.py:43-67. If theta_max isn't set in __init__, add it.
Then re-run pytest tests/test_linesearch.py -k HS071.
```

The split end-of-session ritual:

```
> append a dated entry to LOGBOOK.md with what we decided in this session
> overwrite STATUS.md with where we are now and the next step
```

Then the next session starts with:

```
> read STATUS.md and tell me what the next concrete action is.
```

### Handoff mechanisms ranked by reliability

1. **STATUS.md you wrote.** Highest reliability. You control it; nothing about session boundaries can break it.
2. **Branch name.** `git branch --show-current` tells you "I'm on `filter-linesearch`" — coarse but durable.
3. **Last commit message.** A WIP commit (`git commit -m "WIP: theta_max init missing"`) is a one-line handoff that costs nothing if you commit anyway.
4. **`claude --continue`.** Brings back the conversation. Brittle for two reasons: the conversation may have already auto-compacted (so detail is fuzzy), and it's tied to your machine.

The pattern is simple: rely most on what you write into files; rely least on what lives only in chat state.

### Why not put a "currently working on" header in LOGBOOK.md?

Small projects can get away with it. Two failure modes show up at scale:

- The handoff section grows because nobody prunes it. Stale TODOs accumulate.
- You start scanning LOGBOOK.md for current state and conflating it with durable decisions, which is exactly what the file structure is trying to prevent.

Keep them separate. STATUS.md is cheap.

## 4c. Plans as artifacts — the four-file architecture

A plan from plan mode is a third long-lived file type, distinct from CLAUDE.md, LOGBOOK.md, and STATUS.md. Give plans a directory of their own and have the other files reference them by filename.

```
project/
├── CLAUDE.md          conventions; rarely edited
├── LOGBOOK.md          durable knowledge; references plan outcomes
├── STATUS.md          current state; points at the active plan
└── plans/
    ├── 2026-04-08-filter-linesearch.md   executed
    ├── 2026-04-22-tikhonov.md            abandoned
    └── 2026-05-07-tao-implementation.md  active
```

The lifecycle of a plan file is: created → active → one of {executed, abandoned, revised}. Each transition has a corresponding update to STATUS.md or LOGBOOK.md.

| File | Says | Updated when |
|---|---|---|
| `CLAUDE.md` | How the project works | A convention changes |
| `plans/<date>-<slug>.md` | What's going to happen next | Plan created, revised, or marked abandoned |
| `LOGBOOK.md` | What's been learned | A plan executes or is abandoned, producing a decision or a dead end |
| `STATUS.md` | Where I am right now | Every session, at minimum |

### How the files reference plans

**STATUS.md points at the *active* plan.** That's its main job: tell the next session exactly where to pick up.

```markdown
# Status — 2026-05-07 17:42

## Active plan
plans/2026-05-07-tao-implementation.md — step 3 of 7

## Current state
- Steps 1–2 complete: TAO context built; objective+gradient registered.
- Step 3 in progress: BLMVM bounds setup. Stuck on PETSc Vec ↔ numpy
  conversion.

## Next step
Read plan step 3.b. Use VecGetArray for the conversion, not VecCopy.
```

**LOGBOOK.md references plans selectively** — when a plan made a decision worth remembering, or when a plan was abandoned and you want future-you to skip it.

```markdown
## Decisions
- **2026-04-08 — Default solver IPOPT.**
  Outcome of plans/2026-04-08-filter-linesearch.md. Reasoning is in
  the plan's "Open questions" section, settled there.

## Dead ends
- **Tikhonov-regularized KKT for inverse Poisson.**
  See plans/2026-04-22-tikhonov.md (abandoned 2026-04-29 after two days
  of effort). Reason summarized in
  notebooks/2026-04-29-tikhonov-deadend.md.
```

The pattern: **plan files are evidence; LOGBOOK.md is the index.** Reasoning lives in the plan, the fact lives in LOGBOOK.md, the filename ties them together.

### Two operational rules

- **A plan revised mid-execution becomes a new plan file, not an edit.** `2026-05-07-tao-implementation.md` becomes `2026-05-07-tao-implementation-v2.md`. The diff between them is itself instructive.
- **Commit messages can reference plan steps.** `git commit -m "Implements step 3 of plans/2026-05-07-tao-implementation.md"` ties git history to the plan, which makes whack-a-mole loops easier to spot — three commits against the same step is a problem.

### Prompt cookbook

These are the operational moves that keep the architecture honest. Copy them into your sessions; tweak the dates and slugs.

```
# Set up the structure in a fresh project
> create CLAUDE.md, LOGBOOK.md, STATUS.md, and a plans/ directory in
  this project. Use the workshop conventions from WORKFLOW.md if
  present, otherwise leave each file as a clearly marked template.

# At the end of a planning session — promote the plan to a file
> save the plan to plans/$(date +%Y-%m-%d)-<short-slug>.md and update
  STATUS.md to point to it as the active plan. Do not implement yet.

# At the start of the next session — pick up where you left off
> read STATUS.md and tell me what the next concrete action is.
  Then read the active plan it references.

# After a step of the plan executes
> append the run summary to LOGBOOK.md if anything was decided.
  Then overwrite STATUS.md with the next concrete step inside the
  active plan.

# When you need to revise a plan mid-flight
> save the revised plan as plans/<existing-date>-<slug>-v2.md, leaving
  the v1 in place as history. Update STATUS.md to point to v2.

# When you decide to abandon a plan
> add an "Abandoned: <today>, reason: <one line>" header to the top
  of plans/<filename>.md. Then append a Dead Ends entry to LOGBOOK.md
  that references it.

# Reorganize an old project that already has a flat plan.md
> move ./plan.md to plans/$(date +%Y-%m-%d)-<inferred-slug>.md and
  update STATUS.md to point to it. Leave the old path as a one-line
  redirect note for two weeks.
```

A short habit that pays off: at the end of every session, ask Claude `is anything in STATUS.md or LOGBOOK.md still referencing a stale plan filename?` Half a second; catches the broken link the day it happens, not three months later.

## 4d. Literature research — the fifth artifact

For mathematicians working on optimization, literature reading is *the* highest-leverage place where Claude as a co-scientist outperforms Claude as a programmer. The literature is paper-dense and notation-fragmented; an assistant that pulls equations out of PDFs, translates between conventions, and ties your code to its source paper is genuinely useful. An assistant that hallucinates bibliographies is genuinely dangerous. The architecture below is structured to use the first while neutralizing the second.

### What Claude does well, and badly

| | Does well | Does badly |
|---|---|---|
| PDFs | Extracts text, equations, tables via the built-in `pdf` skill | Decides what a result "really means" — that's still you |
| Notation | Translates between Nocedal–Wright / Conn–Gould–Toint / Boyd–Vandenberghe / Bertsekas | Catches subtle distinctions (B- vs. M- vs. S-stationarity) without verification |
| Citations | Resolves fragments via an `arxiv` or `semantic-scholar` MCP | Emits citations from memory — plausible-looking and often wrong |
| Cross-refs | Ties a method in your code to its source paper section | Maintains coherent literature picture across hundreds of papers without your editorial hand |

Bottom line: useful augmentation, not automation. The verification step is non-negotiable for citations.

### A `literature/` directory parallel to `plans/`

Add a fifth conventional artifact to the four-file architecture:

```
project/
├── CLAUDE.md
├── LOGBOOK.md         # cites both plans/ AND literature/
├── STATUS.md
├── plans/
│   └── 2026-05-07-tao-implementation.md
└── literature/
    ├── wachter-biegler-2006.md
    ├── nocedal-wright-12.md
    ├── conn-gould-toint-2000.md
    └── INDEX.md      # contents page; helpful past ~10 entries
```

Each paper becomes one markdown file, named by BibTeX key. The file follows a consistent template (the `paper-summary` skill enforces this — see below) so the directory is searchable and grep-able.

`LOGBOOK.md` decisions cite both layers:

```markdown
## Decisions
- **Filter line search.**
  Outcome of plans/2026-04-08-filter-linesearch.md.
  Source: literature/wachter-biegler-2006.md §4.2.
```

This gives you a bibliography that emerges from the work, rather than a separate parallel artifact you have to maintain.

### Skills for literature work

Three skills earn their keep:

- **`paper-summary`** — given a PDF, produce a structured summary (contribution / theorem / assumptions / limitations / fit-to-our-problem / pull-quotes). Output goes to `literature/<bibkey>.md`. The template-driven format makes the directory searchable.
- **`citation-resolver`** — given a fragment ("the Wächter–Biegler filter"), return the BibTeX entry. The skill *must verify via an MCP* (arXiv, Semantic Scholar) rather than emit from training data. This is the only way to defeat citation hallucination.
- **`tex-equation-extractor`** — pull display math out of a paper PDF into LaTeX you can paste into your derivations.

The `paper-summary` skill ships with the workshop in `exercises/03-skills/skills/paper-summary/`. The other two are sketched in `LITERATURE.md`.

### MCPs at the seams

Three are common for optimization researchers:

- **arXiv MCP** — preprints, BibTeX, abstracts.
- **Semantic Scholar MCP** — citation graph, related papers, paper IDs.
- **Zotero or filesystem MCP scoped to your library** — your personal corpus of PDFs.

A locally-hosted RAG (next section) is a fourth option when the personal corpus outgrows context.

### The CLAUDE.md verification rule

The single change with the largest payoff for literature work. Add to CLAUDE.md:

```markdown
## Literature
- Never emit a citation from memory. For every paper claim:
  1. Resolve the citation via the arxiv or semantic-scholar MCP.
  2. Quote the relevant passage from the local PDF if available.
  3. If neither is possible, mark the claim as `[citation needed]`.
- Treat any citation lacking (1) or (2) as unverified.
- When summarizing a paper, prefer literal quotes from the PDF over
  paraphrase. Paraphrase drops the qualifier that matters.
```

This turns Claude from a confident bibliographer into a verifying research aid.

### RAG: when the corpus outgrows your context window

Your group's PDFs, lab wiki, and shared notes don't fit in one session. **Retrieval-Augmented Generation** is the standard answer: index the corpus into a vector database (chunked text + embeddings); for each question, retrieve the most relevant chunks; feed only those into the model. Three properties matter:

1. You stop relying on what the model was trained on, and start relying on what you actually have.
2. Citations come back as document IDs you can verify, not paraphrases of training data.
3. The corpus can grow without inflating your context window.

For mathematicians, RAG is the right tool when:

- You have a group wiki / Notion / Confluence with operational knowledge.
- You have a folder of >50 PDFs that no longer fits in context.
- You want collaborators to ask questions of your group's institutional knowledge in chat.

### `moodlehq/wiki-rag` — a concrete example

`moodlehq/wiki-rag` is an experimental RAG specialized for **MediaWiki sites** (consumed via API, not web crawling). Worth knowing about because:

- It's open source and Docker-runnable.
- Uses Milvus for vector storage with hybrid retrieval (vector + keyword + fusion reranking) — the configuration the literature recommends for technical content.
- Exposes an **OpenAI-compatible API** at `/v1/chat/completions`, which means it can be wrapped as an MCP tool in a few lines.

If your group keeps documentation in MediaWiki (some labs do — Moodle's wiki, math-department wikis, internal documentation sites), wiki-rag is a starting point. If you keep it elsewhere, the architecture transfers: any RAG with an OpenAI-compatible endpoint can become an MCP tool.

The wrapper pattern:

```python
# An MCP tool that proxies to wiki-rag's OpenAI API.
@server.call_tool()
async def call_tool(name, arguments):
    if name == "query_lab_wiki":
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{WIKI_RAG_URL}/v1/chat/completions",
                json={"model": "wiki-rag",
                      "messages": [{"role": "user", "content": arguments["question"]}]},
                timeout=60.0,
            )
        return [TextContent(type="text", text=r.json()["choices"][0]["message"]["content"])]
```

Once registered, Claude Code can ask your wiki questions like any other tool. The retrieved passages come with source-document IDs you can spot-check.

### The end-to-end flow for a mathematician

1. Find a candidate paper (arXiv MCP, Semantic Scholar MCP, your reading queue).
2. Drop the PDF into `papers-inbox/`. Run `paper-summary` skill.
3. Review the resulting `literature/<bibkey>.md`. Edit ruthlessly. Verify pull-quotes against the PDF.
4. If a decision is being made, append to `LOGBOOK.md` citing both the active plan and the new literature entry.
5. For "what does the field say about X" questions, ask the literature MCP (or a wiki-rag MCP) — never the model from memory.

A small habit that scales: at the end of every session, ask `is anything I cited today still unverified? List unresolved [citation needed] markers.` Half a second; catches sloppy citation early.

## 5. Git hygiene with an AI collaborator

The single biggest mistake is letting Claude edit code without git in the loop. With git, every change is visible, named, and undoable. Without it, you're flying blind.

The minimal practice:

```
# Before any session
git status          # confirm a clean tree (or accept a known WIP)
git checkout -b filter-linesearch   # branch for this task

# Mid-session, after each significant change
git diff            # always read this before continuing
git add -p          # stage hunks selectively
git commit -m "Add filter line search; HS071 test passes"
```

Smaller patterns that pay off:

- **One commit per logical step.** Easier to revert precisely. "Refactor solver" → bad. "Move convergence check out of inner loop" → good.
- **Read the diff before prompting again.** If you keep prompting on top of code you haven't read, you lose track of what's in your repo. This is the most common cause of whack-a-mole loops.
- **Branch for risky work.** A solver rewrite or a new formulation is a branch. If it doesn't pan out, `git checkout main; git branch -D experiment` and you're done.

## 6. Reverting when Claude went the wrong way

Some things — wrong refactor, deleted code, broken merge — are easier to revert than to fix. Cheat sheet:

```
# Undo edits to one file (uncommitted)
git restore path/to/file.py

# Undo all uncommitted changes
git restore .

# Set aside half-baked work for later
git stash push -m "WIP filter rewrite"
git stash pop

# Drop the last commit but keep its changes in your tree
git reset --soft HEAD~1

# Drop the last commit AND its changes (only if not pushed anywhere)
git reset --hard HEAD~1

# Try a different approach in parallel without disturbing main
git worktree add ../alt-approach
cd ../alt-approach
claude
```

**Worktrees deserve a special mention.** With Claude Code, worktrees are excellent: you can have one tree exploring a Tikhonov regularization scheme and another exploring an SQP variant, in parallel sessions, with no merge headaches. When one wins, you discard the other.

```
# Set up two parallel experiments
git worktree add ../tikhonov-experiment
git worktree add ../sqp-experiment

# In each, run claude separately. Each has its own CLAUDE.md
# (you can fork the file if needed) and its own LOGBOOK.md.
```

## 6b. Testing for code and for results

For a mathematician using Claude Code, tests do double duty: they catch programming bugs *and* they catch experimental regressions. Both belong in the same suite; only the cadence differs.

### Two layers of tests

| | **Tests as a programmer** | **Tests as a co-scientist** |
|---|---|---|
| Question answered | Does the code do what it's supposed to? | Have our results degraded? |
| Example | `assert filter.accept(x) == True` | "IPOPT on HS071 converges in ≤ 50 iters with `mu_init=1e-2`" |
| Failure means | Bug | Method or parameter regression |
| Cadence | Every commit | Nightly, or before a paper |
| Typical home | `tests/` | `bench/` (or `tests/` with a `slow` marker) |

The second layer is where Claude as a co-scientist pays off. Encoding "the recovered source on the inverse Poisson at α = 1e-5, grid 65 has rel L2 error ≤ 0.6" as a test is exactly the same shape as encoding "this function returns 42." Both are oracles; both belong in the suite; both protect future-you.

### Skills as oracles

Many of the verification skills suggested in the deck — `kkt-checker`, `strong-stationarity-checker`, `convergence-rate-fitter`, `perf-profile-regression` — are essentially *test predicates packaged as skills*. The KKT checker isn't just a one-off verification tool; it's the kernel of every test in `tests/test_solver_*.py`. The same is true for any predicate that returns a residual or a comparison: encode it once as a skill, invoke it from many tests.

### How tests fit the four-file architecture

- **CLAUDE.md** says how to run them. Make it a hard rule:
  > After any code edit: run `pytest -q tests/`. Surface failures in the next reply; don't claim done. For changes touching solver behavior, also run `python bench/run.py --suite cohort_smoke` and report iters/time.
- **LOGBOOK.md decisions** should cite the test that would catch the regression:
  > Decision: `mu_init = 1e-2`. Test: `tests/test_mu_default.py::test_no_divergence_on_cohort`.
- **plans/** — every step that changes solver behavior pairs with a test step. The capstone plan follows this pattern (step 6 is "smoke test").
- **STATUS.md** — the *Current state* block should list which tests pass and which fail. That's the single most useful piece of state to hand off.

### Patterns that pay off

1. **Test-first prompting.** *"Write the test for X first, run it, confirm it fails. Then implement X and run the test again."* The conversation produces the test as evidence before any production code is touched. TDD with Claude doing both ends works well.
2. **Test the dead end.** When the Tikhonov approach failed (see `notebooks/2026-04-29`), don't just write it down — add a test like `test_tikhonov_disabled_or_mode_mismatch_raises` so a well-meaning future fix can't silently re-enable the bug. Encoding *what shouldn't work* is as valuable as encoding what should.
3. **Two cadences, one suite.** Fast unit tests run on every commit; benchmarks run nightly or before a deadline. Use `pytest` markers (`@pytest.mark.slow`) so the same harness runs both. Don't duplicate test infrastructure.
4. **Cite tests in commits and decisions.** `git commit -m "Step 3 of plans/2026-05-07-tao.md; tests/test_petsc_smoke.py passes"`. Ties the four-file architecture to git history. Makes whack-a-mole loops easier to see — three commits against the same step with the same test failing means the test is wrong, the invariant is wrong, or both.
5. **Add a regression test for every loop you escape.** Per the previous section: when you finally fix a loop by formalizing an invariant, write the test that enforces it. Now the loop becomes a stable solution.

## 7. The whack-a-mole loop — how to spot it

You're in a loop when fixes don't accumulate. Fix A breaks B; fix B breaks C; fix C breaks A. The session feels productive because Claude is making changes, but progress is illusory.

**Symptoms.**

- The same files keep appearing in `git status` across multiple attempts.
- Tests flip between passing and failing on essentially the same code.
- Claude proposes a fix you remember rejecting two turns ago.
- Diffs grow but the bug count is stable.
- You feel a vague sense of treading water.

**Underlying causes.** Almost always one of:

1. **A missing invariant.** Some property of the data, types, or solver state must hold but isn't tested or asserted anywhere. Each fix happens to satisfy it locally and break it elsewhere.
2. **Conflicting requirements.** Module A expects multipliers in convention X; module B expects convention Y. The fix oscillates between conventions.
3. **A silent fallback.** A try/except, a default argument, or a numpy broadcasting rule is hiding the real failure mode.

**Diagnosis tools.**

```
git log --oneline -20            # any file touched repeatedly?
git log -p path/to/disputed.py   # are the same lines flipping back?
git log --stat -10               # which files have churned the most?
```

If a file has been edited five times in twenty commits, you have a loop.

## 8. Breaking out of a stuck session

A six-step recipe. The hard part is *step one* — stopping when the loop is fresh in your mind and you "just want to fix this last thing."

1. **Stop prompting.** "Fix this too" never works on a real loop. The next turn is not the answer.

2. **Ask Claude to summarize.**

   ```
   summarize everything we've tried in this session and why each
   attempt failed. List the files modified, the tests that passed,
   and the tests that failed.
   ```

   Read the summary. Often you'll see the conflict yourself.

3. **Step away from the keyboard.** Write down on paper or in a scratch file:

   - What invariants must hold?
   - Which two requirements are conflicting? (There are usually two.)
   - What test would have caught the original mistake?

4. **Reset.** `/clear` the conversation. Optionally close the terminal — fresh process, fresh state.

5. **Re-plan.** Open a new session. Append the invariants you wrote down to CLAUDE.md (or to a temporary `INVARIANTS.md`). Enter plan mode and ask:

   ```
   plan a fix that satisfies the invariants in INVARIANTS.md.
   Identify which existing files violate them.
   ```

   Don't accept a plan that doesn't address them.

6. **Test the invariants.** Add a regression test for each. Now the loop becomes a stable solution — future sessions can't re-break what's tested.

**Mathematician's variant.** A loop usually means you haven't formalized something. Maybe the multiplier sign convention. Maybe the active-set definition. Once you write it in math — `μᵢ ≥ 0 for active, μᵢ = 0 for inactive` — the conflict becomes visible and the fix becomes obvious. The discipline that keeps your proofs honest is the same one that gets you out of code loops.

## 9. A short checklist

Print this. Stick it next to your monitor.

```
Before a session:
  □  Clean `git status` (or known WIP on a branch)
  □  CLAUDE.md still reflects the project? Quick read.
  □  Anything in LOGBOOK.md from last session that's relevant? Skim.

During a session:
  □  Read every git diff before continuing
  □  Commit small, atomic changes
  □  Use plan mode for anything > a one-line edit
  □  /compact at natural break points on long sessions

If you suspect a loop:
  □  git log --oneline -20: any file touched repeatedly?
  □  Ask Claude to summarize what's been tried
  □  Step away. Write the invariants on paper.
  □  /clear, re-plan with invariants explicit, add tests

End of session:
  □  Append a dated entry to LOGBOOK.md
  □  Commit. Push if appropriate.
  □  Note any open questions (in LOGBOOK.md, not in your head)
```
