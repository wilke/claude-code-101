# Exercise 04 — Bootstrap a LOGBOOK.md, and reconcile a conflict (12 min)

**Goal.** Turn three dated modeling notes into a structured `LOGBOOK.md` — but two of
the notes **disagree** about the Elo `K` factor, and the consolidation has to *surface*
that conflict rather than quietly pick a side. The synthesis is the pretext; **the file
is the artifact**, and its most valuable line is the honest "these two notes disagree,
here's why, here's what's still open."

**Setup.** This is a *writing* exercise — no code runs, no environment needed. The three
notes are already in `notebooks/`. Just `cd exercises-worldcup/04-logbook && claude`.
Keep the `CLAUDE.md` you wrote for Exercises 01–03.

## The project

The three entries in `notebooks/` (`2026-06-20`, `2026-06-24`, `2026-06-28`) all come
from building the World Cup predictor: choosing the Elo `K`, replacing an
independent-Poisson goal model with Dixon–Coles, and then discovering `K=40` overshoots
early upsets. Two of them **contradict each other**:

- `2026-06-20-elo-k.md` picks **K=40** because it's the FIFA/community *standard*.
- `2026-06-28-upsets.md` finds **K=40 overshoots** the early-round upsets and K≈24 scores
  better on held-out matches.

A consolidation that just writes "K=40" has thrown away the more important finding.

## Steps

1. `cd exercises-worldcup/04-logbook && claude`
2. Paste verbatim:

   ```
   Read everything under notebooks/ and produce LOGBOOK.md with the sections:
   Decisions, Parameters, Dead Ends, Open Questions. Each entry should cite
   the notebook file it came from. If two notes disagree, do NOT silently pick
   one — record the disagreement and what would resolve it.
   ```

3. **Review and trim — and check the conflict.** Read it end-to-end. The `K` question
   must land in **Open Questions** (or a Parameters line explicitly marked *contested*),
   citing **both** notes and stating *why* they differ (standard-for-FIFA-ranking vs
   best-for-our-predictions). If Claude wrote a bare "K=40" in Parameters, push back:
   "06-28 contradicts that — surface the conflict, don't resolve it."

4. **Use the new LOGBOOK.md to pick the next step.** Paste:

   ```
   Given LOGBOOK.md, what is the single most important thing to resolve before
   trusting this predictor through the knockout rounds? Justify in two sentences.
   ```

   A good answer names the **Elo `K` open question** (sweep K / go adaptive) and cites
   the two conflicting notes. If it's generic, push back: "name the entries that
   motivate this."

5. **End with the two-minute ritual:**

   ```
   Summarize what we did in this session, append it as a dated entry to
   LOGBOOK.md, and overwrite STATUS.md with where we are now.
   ```

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did every entry cite its source notebook? | Provenance you can't recover is an entry you can't revise. |
| Did Claude actually *trim*, or is `LOGBOOK.md` longer than the three notes? | Synthesis without trimming is just retyping. |
| **Was the `K=40` vs `K≈24` conflict surfaced, not silently resolved?** | The disagreement (and *why*) is the most valuable line in the file. |
| Did the Poisson Dead End keep its **mechanism**? | "Independent Poisson was wrong" stops nobody; "it overstated 0–0/1–1 because scores correlate" does. |
| Did the next-step answer cite specific entries? | If it doesn't, it could've been written without the file. |

## Discussion prompts

- The `K` conflict is a **contradiction between two of your own notes**, not a gap in
  knowledge. Why is recording "these disagree, and here's the reason" more useful than
  forcing a single value you can't yet justify?
- What goes in `CLAUDE.md` vs `LOGBOOK.md`? "Neutral matches get no home advantage" is
  true every session → `CLAUDE.md`. "K=40 overshoots for *this* tournament" is a
  data-specific finding → `LOGBOOK.md`. Pick one entry and argue where it goes.

## Stretch

The Dixon–Coles-supersedes-independent-Poisson entry is a clean **ADR / supersession**:
one decision explicitly replacing an earlier one, with the reason. Rewrite it in a
`decisions/` log as `0001-independent-poisson.md` (status: *superseded by 0002*) and
`0002-dixon-coles.md` (status: *accepted*), and add a line to your `CLAUDE.md` telling
Claude to record future model changes as numbered, status-tagged ADRs.
