# Solution — Exercise 5 (MCP)

## What this exercise is doing

An **MCP server** is a small program that exposes capabilities (tools, resources) to an AI client like Claude Code over a standard protocol. We're going to write one that exposes a single tool called `solve_qp` — give it a quadratic program, get back the optimum.

The point isn't this specific solver. The point is the *pattern*: any external solver, database, or service you'd normally have to remember to invoke can be wrapped this way and become a first-class tool in every Claude Code session.

## What the QP looks like

The shipped `problem.json` is:

```
min ½ xᵀ Q x + cᵀ x  s.t.  A x ≤ b
```

with

```
Q = [[2, 0],     c = [-2, -5]    A = [[1, -2], [-1, -2], [-1, 2], [1, 0], [0, 1]]
     [0, 2]]                     b = [2, 6, 2, 4, 4]
```

Geometrically: minimize a circular bowl over a five-sided polygon. The optimum is at one of the polygon's corners. (It's the corner closest to the bowl's center, `[1, 2.5]`.)

If you want to confirm without the MCP, run:

```python
import cvxpy as cp, numpy as np
Q = np.array([[2,0],[0,2]]); c = np.array([-2,-5])
A = np.array([[1,-2],[-1,-2],[-1,2],[1,0],[0,1]]); b = np.array([2,6,2,4,4])
x = cp.Variable(2)
prob = cp.Problem(cp.Minimize(0.5*cp.quad_form(x, Q) + c @ x), [A @ x <= b])
prob.solve()
print(x.value)        # ~ [1.40, 1.70]
print(prob.value)     # ~ -6.45
```

## Registering the MCP

```
$ pip install mcp cvxpy numpy
$ claude mcp add toy-solver --command python --args "$(pwd)/toy_solver_mcp.py"
$ claude mcp list
toy-solver  python /path/to/exercises/05-mcp/toy_solver_mcp.py
```

The server is now available to every new Claude Code session in this project (the registration is stored in `.mcp.json` if the flag is set per-project, or `~/.claude.json` for user-level).

## What a session with the MCP looks like

```
$ claude
> solve the QP described in problem.json using the toy-solver MCP.
  Print the optimal value, the solution vector, and any dual multipliers.

[Claude reads problem.json]
[Claude calls toy-solver:solve_qp with Q, c, A, b from the file]
[toy-solver returns:
  {
    "status": "optimal",
    "optimal_value": -6.45,
    "x": [1.4, 1.7],
    "duals": [..., ..., ..., ..., ...]
  }
]

The QP solved cleanly. Optimal value: -6.45 at x = (1.40, 1.70). The
binding constraints (active inequalities) are #2 (-x₁ - 2x₂ ≤ -6) and
#5 (x₂ ≤ 4)... [etc]
```

The key signal: Claude calls the MCP tool by name and you can see exactly which arguments went over the wire. That makes the boundary auditable — useful when something later goes wrong on a remote MCP and you want to know what was sent.

## Stretch — a logging tool

Add a second tool to `toy_solver_mcp.py` that records solves into SQLite. The change is mechanical: a new `Tool` in the list, a new branch in `call_tool`. Schema:

```sql
CREATE TABLE solves (
  id INTEGER PRIMARY KEY,
  ts TEXT,
  problem_hash TEXT,
  status TEXT,
  optimal_value REAL,
  x_json TEXT
);
```

Then ask Claude:

```
solve problem.json with the toy MCP, log the run, and tell me how many
runs are in the log so far.
```

Claude calls `solve_qp`, then `log_run`, then a hypothetical `count_runs` (or queries by issuing SQL through a separate sqlite MCP). This composition — *one tool's output feeds another tool's input* — is exactly what MCPs are designed for.

## Stretch — PETSc/TAO backend

Replace cvxpy with a TAO bound-constrained QP solve. The MCP shell — server name, tool name, schema — stays the same. Only the inside of `call_tool` changes:

```python
from petsc4py import PETSc
# build Mat from Q, Vec from c, set bounds via TaoSolver, ... solve.
```

A consumer of the MCP doesn't notice the change. That's the value: you can swap solver implementations without touching the prompt that calls it.

## When *not* to reach for an MCP

A skill is simpler. Reach for an MCP when you need:

- **Persistent state.** A database, a long-running solver process, an issue tracker.
- **Cross-session reuse with non-trivial setup.** Authenticated APIs, hosted services.
- **Talk to something Claude Code can't run inline.** A simulator on a cluster, a remote license server.

If none of those apply, write a skill (or just a script Claude can run) instead.
