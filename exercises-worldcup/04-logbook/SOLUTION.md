# Solution — Exercise 04 (World Cup LOGBOOK.md + conflict)

## What this exercise is doing

The learner consolidates three dated modeling notes into a `LOGBOOK.md`. The twist,
carried from the optimization track's memory exercise, is a **built-in contradiction**:
two of the notes disagree about the Elo `K` factor. The whole point is whether the
consolidation *surfaces* that conflict — with the reason and what would resolve it —
instead of silently writing one value and discarding the more important finding.

The model file below is *not* shipped — the learner produces it. It is a **reference**
to compare against, not an answer key; a good student version may be shorter.

## A worked LOGBOOK.md

```markdown
# LOGBOOK — World Cup predictor

## Decisions
- Rate teams with Elo, home advantage on non-neutral matches only. Every World
  Cup match is neutral, so no team (host nations included) gets a home bonus
  inside the tournament. [2026-06-20]
- Goal model is Poisson with the Dixon–Coles low-score correction, not
  independent Poisson. The correction fixes the overstated 0–0/1–1 rates. [2026-06-24]

## Parameters
- Elo `home_adv = 65` (non-neutral only), base 1500. [2026-06-20]
- Elo `K`: **contested** — 40 (per 06-20) vs ≈24 (per 06-28). See Open Questions;
  do not treat 40 as settled. [2026-06-20, 2026-06-28]
- Dixon–Coles `ρ` ≈ −0.05 (small, negative). [2026-06-24]

## Dead Ends
- Independent-Poisson goal model. Assumed home/away goals independent →
  overstated 0–0 and 1–1 versus the observed historical rates, because low scores
  are correlated. Superseded by the Dixon–Coles `ρ` correction; kept only as the
  "before" illustration. [2026-06-24]

## Open Questions
- What Elo `K` should the predictor use? 06-20 chose K=40 because it's the FIFA/
  community *standard*; 06-28 found K=40 **overshoots early-round upsets** and
  K≈24 scored better on held-out R32 log-loss. The conflict: "standard for the
  official ranking" optimizes a stable published ranking, while we optimize
  per-match predictive accuracy through a short, upset-heavy tournament.
  **Unresolved:** drop to K≈24, or make `K` adaptive. Needs a K-sweep against
  held-out matches before committing. [2026-06-20, 2026-06-28]
- Is Poisson+Dixon–Coles enough, or is a negative-binomial needed for
  over-dispersion in blowouts? Deferred. [2026-06-24]
```

## The conflict is the payload

- `2026-06-20-elo-k.md`: **K=40**, chosen because it's the FIFA/community *standard*.
- `2026-06-28-upsets.md`: **K=40 overshoots** early-round upsets; K≈24 scored better on
  held-out R32 log-loss.

These aren't a knowledge gap — they're two of the learner's own notes contradicting each
other. A good `LOGBOOK.md` records the disagreement in **Open Questions** (or a
Parameters line explicitly tagged *contested*), cites **both** notes, and states *why*
they differ: "standard for the official ranking" optimizes a stable published ranking,
while the predictor optimizes per-match accuracy through a short, upset-heavy tournament.
The resolution path (sweep `K`, or make it adaptive) is recorded as still-open.

**Failure mode to catch:** Claude writes `K = 40` in Parameters and moves on. Push back
exactly as the README says — 06-28 contradicts it; the file must hold the tension, not
hide it.

## The Poisson dead end must keep its mechanism

The `2026-06-24` note is a clean supersession: independent Poisson → Dixon–Coles. The
consolidation must keep *why* independent Poisson failed ("overstated 0–0/1–1 because low
scores are correlated"), not just "it was wrong." That mechanism is what stops a future
session re-deriving it. It's also the cleanest ADR in the set — one decision explicitly
replacing another — which is why it's the stretch's supersession example.

## What a good consolidation keeps (and cuts)

**Keeps:**

- **Decisions** with reasons: Elo + home-advantage-only-when-not-neutral; Poisson **with
  Dixon–Coles**.
- **Parameters** you'd re-tune: `home_adv=65`, `ρ≈−0.05`, and `K` **marked contested**.
- **Dead Ends** with mechanism: independent Poisson overstates low-score draws.
- **Open Questions** left open: the `K` conflict, and Poisson-vs-negative-binomial.

**Cuts:** "ratings look sensible", the play-by-play of each re-run, restating the
CLAUDE.md rules. If `LOGBOOK.md` is longer than the three notes, no trimming happened.

## Step 4 — a good next-step answer

Expected: names the **Elo `K` open question** (run a K-sweep against held-out matches, or
adopt an adaptive K) and cites `2026-06-20` **and** `2026-06-28`. The tell of a weak
answer is genericness ("gather more data", "try a neural net") untethered to the
conflict. Push back: "name the entries that motivate this."

## Step 5 — the ritual

The dated append + `STATUS.md` overwrite is the four-file habit: `LOGBOOK.md` accretes
durable knowledge (including unresolved conflicts); `STATUS.md` is overwritten with just
"where we are now" (e.g. "predictor rated through R32; K unresolved; final pending"). A
good append is 3–5 dated bullets on what changed this session.

## Discussion: why record a conflict instead of resolving it

Forcing `K=40` because a note said "standard" would bury a measured finding that it's
wrong for this objective. Recording "these two notes disagree, here's the reason, here's
the sweep that settles it" is strictly more useful than a confident wrong number — and it
is exactly the kind of thing a future session (or a teammate) needs inherited, not
re-discovered.
