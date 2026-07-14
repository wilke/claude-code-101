# Exercise 03 — Package a data profile as a skill (15 min)

**Goal.** See how a **skill** turns a procedure you run on every new dataset —
"profile this CSV before touching it" — into a named artifact Claude invokes for
you. The profile is the pretext; **the skill is the artifact**: Claude routes a
plain-language request ("what's in this file?") to the skill without you naming it,
and the same helper works on *any* CSV, not just this one.

## What ships

```
03-skills/
├── README.md
├── SOLUTION.md
├── experiment.csv            # the messy table to profile
└── skills/
    └── data-profile/
        ├── SKILL.md
        └── data_profile.py   # dtype/missingness/cardinality + suspicion FLAGS
```

Install the skill so Claude can find it:

```bash
mkdir -p .claude
cp -R skills .claude/
```

## Steps

1. `cd exercises-a0/03-skills && claude`
2. Ask — **without naming the skill** (routing is what's being tested):

   ```
   I just got experiment.csv and don't know what's in it. Give me a profile
   of the columns and flag anything that looks wrong.
   ```

   Claude should route this to the **data-profile** skill and run it, then read
   back the flags (inconsistent `treatment_group` labels, the unit-suffixed
   `concentration`, the near-unique `sample_id`, any high-missingness column). If
   it profiles the file inline with a one-off `df.info()` instead, push back:
   "use the skill in `.claude/skills/`."

3. Point the skill at a **different CSV** — any table you have lying around, or a
   copy of `experiment_clean.csv` from Exercise 02. The same helper profiles it and
   flags *its* problems. That reuse is the whole point: a skill is written once and
   pays off on every future dataset.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did Claude *run* the skill, or profile the file inline? | The helper is the source of truth; an inline `df.info()` is just a one-shot. |
| Did the flags catch the unit-suffixed `concentration` and the ID-like `sample_id`? | Those are the two silent traps in this file. |
| Did the top-categories list expose the inconsistent labels? | Seeing `control` and `CTRL` together is your normalize cue. |
| Did it work unchanged on a second CSV? | A skill that only fits one file isn't a skill. |
| On an extension, did it update the skill's `description:`? | A capability the description doesn't mention is invisible to routing. |

## Discussion prompts

- The skill splits "look at the data" from "clean the data". Why is profiling a
  *separate, reusable* step worth keeping — rather than folding it into each clean?
- What's one check specific to *your* field you'd add to `data_profile.py` (e.g. a
  plausible-range check for a physical quantity), and would it go in this shared
  skill or a project-specific one?

## Stretch

Add a `--json` output mode to `data_profile.py` and update its `description:` so a
future session asking "gate the pipeline if any column is >30% missing" routes to
it — a profile you can wire into CI, not just read by eye.
