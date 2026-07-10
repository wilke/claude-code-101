# Solution — Exercise 03 (singular-value skills)

## What this exercise is doing

Two skills compute singular values, split by **storage**, not by mathematics:

- `qr-iteration` — for a **dense** matrix small enough to factor. Unshifted QR iteration on `AᵀA` drives it to diagonal; singular values are the square roots of the eigenvalues.
- `lanczos` — for a **large sparse** matrix or a **matrix-free operator** (only `apply` available). Wraps the object as a `scipy.sparse.linalg.LinearOperator` and calls `svds` (implicitly restarted Lanczos) for the dominant `k`.

`problem.py` hands each skill the right object via `get_dense()` / `get_sparse()` / `get_operator()` — the three objects from Exercises 01–02. The exercise is really about **routing**: from a plain request, Claude should pick the skill whose `description:` matches the object, and *run* it rather than reimplement it.

## How to invoke

```bash
python3 .claude/skills/qr-iteration/qr_svd.py --problem problem.py --k 6 --check
python3 .claude/skills/lanczos/lanczos_svd.py --problem problem.py --source sparse   --k 6
python3 .claude/skills/lanczos/lanczos_svd.py --problem problem.py --source operator --k 6
```

## What you'd expect to see

```
dense matrix (200, 200): 200 singular values via QR iteration
  largest 6: [27.9731 27.5842 26.8831 26.416  26.2265 25.9595]
  max |QR - numpy.svd| = 4.43e-04

sparse matrix (5000, 5000): dominant 6 singular values via Lanczos (svds)
  [3.8752 3.8681 3.7449 3.7324 3.7207 3.7204]

matrix-free operator (1600, 1600): dominant 6 singular values via Lanczos (svds)
  [0.8352 0.6699 0.6699 0.5593 0.5043 0.5043]
```

The QR `--check` difference (~4e-4) lives in the *smallest* singular values: unshifted QR converges the dominant ones first, the tail slowest. The operator's singular values match Exercise 02's SVD exactly — same object, same answer, reached through the skill.

## Why this is a skill and not an MCP

These checks are stateless, deterministic, and ship in the repo — `git clone` brings the team's QR and Lanczos routines along with no per-developer setup. There is no external system, licensed solver, or persistent state to keep warm, so an MCP would be overkill. Skill = "how to do this recurring computation"; MCP = "an external system Claude must talk to."

## Where it usually goes wrong on the first try

- Claude computes `np.linalg.svd` inline instead of running a skill. **Push back: run the helper; it is the source of truth.**
- Claude runs `qr-iteration` on the sparse matrix (or densifies the operator) — the algorithm no longer matches the storage. The helper's guard catches this; **the routing is the lesson.**
- On the matrix-free operator, Claude forms a dense matrix to call the dense SVD. **`lanczos` wraps `apply` as a `LinearOperator`; never densify.**
- On extending a skill (e.g. adding smallest-singular-values), Claude edits the helper but not the `description:`. **The description is the contract — a capability it doesn't mention is invisible to routing.**
