<!--slide n=43 layout=section kicker="Part 7 · Habits"-->
# Working sustainably
_Version control, reverting, and recognizing when you're whack-a-mole-ing your own code. The unglamorous habits that make the rest of the workshop pay off._


<!--slide n=44 layout=content kicker="Working sustainably"-->
# Git hygiene with an AI collaborator
- **Start every session with a clean working tree** (or a fresh branch). You want any change Claude makes to be visible in `git diff`.
- **Commit small, atomic changes.** One logical step per commit makes reverting precise.
- **Review the diff before continuing.** If you keep prompting on top of code you haven't read, you lose track of what's in your repo.
- **Branch for risky work.** A solver rewrite or a new formulation goes on its own branch — easy to throw away if it doesn't pan out.

```
# Before a session
git status                       # confirm clean
git checkout -b filter-linesearch  # branch for this task

# After Claude makes changes
git diff                         # always read this
git add -p                       # stage hunks selectively
git commit -m "Add filter line search; HS071 test passes"
```


<!--slide n=45 layout=content kicker="Working sustainably"-->
# Reverting when Claude went the wrong way
```
# Undo edits to one file (uncommitted)
git restore path/to/file.py

# Undo all uncommitted changes
git restore .

# Set aside half-baked work for later
git stash push -m "WIP filter rewrite"
git stash pop

# Throw away the last commit but keep its changes
git reset --soft HEAD~1

# Nuclear: drop the last commit and its changes (only if pushed nowhere)
git reset --hard HEAD~1

# Try a different approach in parallel without disturbing main
git worktree add ../alt-approach
cd ../alt-approach && claude
```

Worktrees are particularly useful with Claude: you can have one tree exploring a regularization scheme and another exploring an SQP variant, without merge headaches.


<!--slide n=46 layout=content kicker="Working sustainably"-->
# Verification first — tests are how Claude checks itself
_The highest-leverage thing you can do is give Claude a way to verify its own work. Without it, you are the only feedback loop; tests let Claude run, see, and fix. For a mathematician, they do double duty:_

|  | As a programmer | As a co-scientist |
|---|---|---|
| What it checks | Code does what it's supposed to | Results haven't degraded |
| Example | `assert filter.accept(x) == True` | "On HS071, IPOPT converges in ≤ 50 iters with `mu_init=1e-2`" |
| Frequency | Every commit | Nightly, or before a paper |
| Lives in | `tests/` | `bench/` (or `tests/` with a marker) |

Both protect future-you. Both let Claude prove a change is correct without you reading every diff.

> Skills as oracles: the `kkt-checker`, `perf-profile`, and `convergence-rate-fitter` skills aren't only one-off tools — they're the predicate that powers an entire family of tests. One predicate, many invocations.


<!--slide n=47 layout=content kicker="Working sustainably"-->
# Test patterns with Claude in the loop
- **Test-first prompting.** "Write the test for X first, confirm it fails, then implement X." Forces specification before code.
- **Hard rule in CLAUDE.md.** "Run `pytest -q` after every edit; surface failures before continuing." Removes the most common failure mode — claimed success without verification.
- **Test the dead end, not just the success.** Assert the failure mode (e.g. Tikhonov) so a well-meaning future fix can't silently re-enable the bug.
- **Cite tests in commits and decisions.** LOGBOOK.md decisions reference the test that catches their regression.

```
# In CLAUDE.md
## Conventions
- After any code edit: run `pytest -q tests/`. Surface failures
  in the next reply; don't claim done.
- For changes touching solver behavior, also run
  `python bench/run.py --suite cohort_smoke` and report iters/time.
```


<!--slide n=48 layout=content kicker="Working sustainably"-->
# The whack-a-mole loop — how to spot it
Symptom: every fix breaks something else. Fix A → B fails → fix B → C fails → fix C → A fails again.

:::columns
### Signs to watch for
- The same files reappear in `git status` across attempts.
- Tests flip between passing and failing on essentially the same code.
- Claude proposes a fix you remember rejecting two turns ago.
- Diffs grow but the bug count is stable.

### Underlying causes
- A missing invariant — e.g., "the multipliers should always sum to zero" — that no test enforces.
- Conflicting requirements between two modules.
- Silent fallback paths (a try/except hiding the actual failure).
:::

```
git log --oneline -20            # any file touched repeatedly?
git log -p path/to/disputed.py   # are the same lines flipping back?
```


<!--slide n=49 layout=content kicker="Working sustainably"-->
# Breaking out of a stuck session
1. **Stop prompting "fix this too."** More turns won't help; you need to step back.
2. **Ask Claude to summarize.** `summarize everything we've tried in this session and why each attempt failed.` Read the summary.
3. **Step away from the keyboard.** Write down — on paper — the actual invariants the code must satisfy.
4. **Reset.** `/clear`. Open a fresh session with the invariants explicit in the prompt or appended to CLAUDE.md.
5. **Re-plan.** Plan mode, with the new invariants. Don't accept a plan that doesn't address them.
6. **Test the invariants.** Add a regression test for each one. Now the loop becomes a stable solution: future sessions can't re-break what's tested.

> Mathematician's variant: the loop usually means you haven't formalized something. Once you write the invariant in math, the fix becomes obvious — even to you.
