# Exercise 03 — Package singular-value methods as skills (15 min)

**Goal.** See how a skill packages a recurring computation — here, "find the singular values" — and how the *right algorithm depends on the object*. The check is the pretext; **the skill is the artifact**: Claude routes a plain-language request to the skill whose description matches the object type, without you naming it.

## What ships

```
03-skills/
├── README.md
├── SOLUTION.md
├── problem.py                 # get_dense() / get_sparse() / get_operator()
└── skills/
    ├── qr-iteration/          # singular values of a dense matrix (QR iteration)
    │   ├── SKILL.md
    │   └── qr_svd.py
    ├── lanczos/               # dominant singular values of a sparse matrix or matrix-free operator
    │   ├── SKILL.md
    │   └── lanczos_svd.py
    └── paper-summary/         # bonus: literature-research skill
        ├── SKILL.md
        └── examples/
            └── example-output.md
```

`problem.py` exposes the **three objects from Exercises 01–02**: the dense matrix (`matrix_A.npy`), the sparse matrix (`matrix_B.npz`), and the matrix-free heat-step operator (`heat_operator.py`).

Install the skills so Claude can find them:

```bash
mkdir -p .claude
cp -R skills .claude/
```

## Steps

1. `cd exercises-lin_alg/03-skills && claude`
2. Ask — **without naming a skill** (routing is what's being tested):

   ```
   using problem.py, find the singular values of the dense matrix, the
   sparse matrix, and the operator.
   ```

   Claude should route each object to the algorithm that fits it: **qr-iteration** for the dense matrix, **lanczos** for the sparse matrix and the matrix-free operator. If it computes any of them inline instead of running the skill, push back: "use the skills in `.claude/skills/`."

3. Point the *wrong* skill at an object — e.g. ask Claude to run `qr-iteration` on the sparse matrix. The helper refuses ("this object is sparse — use the lanczos skill"). The guardrail is part of the lesson: the algorithm has to match the storage.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did Claude *run* the skills, or compute the SVD inline? | The helper is the source of truth; an inline `np.linalg.svd` is just a one-shot. |
| Did it pick QR for the dense object and Lanczos for the sparse/operator? | The algorithm must match the storage — that's the whole point. |
| Did it keep the matrix-free operator matrix-free (no densify)? | `lanczos` wraps `apply` as a `LinearOperator`; densifying would defeat it. |
| Did it report the singular values largest-first? | Is this the result you asked for? |
| On an extension, did it update the skill's `description:`? | A capability the description doesn't mention is invisible to routing. |

## Discussion prompts

- The two skills split on **storage**, not on the math. What other recurring checks in your work would you split the same way (dense vs sparse vs matrix-free)?
- `lanczos` assumes the operator is symmetric (`rmatvec = apply`). What would you change in its description and code to handle a nonsymmetric operator?

## Stretch

Add a `--which SM` option to `lanczos` for the *smallest* singular values (a conditioning probe), and update its `description:` so a future session asking "how ill-conditioned is this operator?" routes to it.

The `skills/` folder also ships `paper-summary`, a literature-research skill carried over from the upstream workshop (pre-positioned for the capstone). Note that the `paper-summary` skill was written by Claude, not by a person. Try it out on a paper of your choice. Do you like it? How would you change it to your preferences? Everybody reads and summarizes differently.
