# Exercise 03 — Package team ratings as a skill (15 min)

**Goal.** See how a **skill** turns the procedure you run *every* session — "rate the
teams from the match table" — into a named artifact Claude invokes for you. Ratings are
the pretext; **the skill is the artifact**: Claude routes a plain-language request
("who's strongest?") to the skill without you naming it, and the same helper rates any
match set — heuristically (Elo) or by maximum likelihood (Bradley–Terry).

## What ships

```
03-skills/
├── README.md
├── SOLUTION.md
├── matches.csv               # the match-results table to rate
└── skills/
    └── rating-fit/
        ├── SKILL.md
        └── rating_fit.py     # Elo pass + Bradley-Terry MLE (scipy.optimize)
```

Install the skill so Claude can find it:

```bash
mkdir -p .claude
cp -R skills .claude/
```

## Setup

Re-use the track environment (pandas / numpy / scipy), activated **before you start
`claude`**:

```bash
conda activate worldcup            # conda
# or:  source .venv/bin/activate   # pip + venv
```

## Steps

1. `cd exercises-worldcup/03-skills && claude`
2. Ask — **without naming the skill** (routing is what's being tested):

   ```
   From matches.csv, which national teams are strongest right now? Give me a
   ratings table, and use maximum likelihood, not just a win-percentage.
   ```

   Claude should route this to the **rating-fit** skill and run it (Bradley–Terry for
   the MLE ask), then read back the top teams and the fitted home advantage. If it
   hand-rolls a win-percentage table inline instead, push back: "use the skill in
   `.claude/skills/`, and use the MLE method."

3. Point the skill at a **different question or slice** — run the Elo method (`--method
   elo`), or filter to recent matches, and compare the orderings. The same helper rates
   whatever you give it. That reuse is the whole point: a skill is written once and pays
   off every time you need a ratings table (including as input to the bracket
   simulation).

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did Claude *run* the skill, or hand-roll a win-% table inline? | The helper is the source of truth; an inline table has no home-advantage handling. |
| Did it use the **MLE (Bradley–Terry)** method when asked, not just Elo? | The two methods are different claims; the request named one. |
| Did the ratings **respect `neutral`** (no home bonus on neutral matches)? | Ignoring it inflates whoever happens to be listed as `home_team`. |
| Did it read the ratings as **relative** (differences), not absolute? | Bradley–Terry is only identifiable up to a constant. |
| On an extension, did it update the skill's `description:`? | A capability the description doesn't mention is invisible to routing. |

## Discussion prompts

- Elo (an online heuristic) and Bradley–Terry (a likelihood) usually agree on the
  ordering but disagree on the edges. Which would you trust to seed a bracket
  simulation, and why?
- The skill exposes `K` as a knob. Is "use K=32" house style for `CLAUDE.md`, or a
  per-tournament decision for the plan/`LOGBOOK.md`? (Exercise 04 turns this exact
  question into a conflict to reconcile.)

## Stretch

Add the companion **`simulate-bracket`** skill the SKILL.md points to: Monte-Carlo the
knockout tree from a ratings table to get each team's advance/win probabilities, and
update the `description:` so "what are each team's chances of winning?" routes to it.
That's the on-ramp to the BracketSim capstone.
