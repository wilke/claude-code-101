# Exercise 5 — Wrap a toy QP solver as an MCP server (15 min)

**Goal.** Stand up a Model Context Protocol server that exposes a `solve_qp` tool to Claude Code.

## What ships

```
05-mcp/
├── README.md
├── toy_solver_mcp.py     # the MCP server (~80 lines)
├── problem.json          # a small QP for testing
└── requirements.txt
```

## Setup

```bash
cd exercises/05-mcp
python -m pip install --user -r requirements.txt
```

## Register the server

```bash
claude mcp add toy-solver \
    --command python \
    --args "$(pwd)/toy_solver_mcp.py"

# Verify
claude mcp list
```

## Use it

In a fresh Claude Code session:

```
solve the QP described in problem.json using the toy-solver MCP and
print the optimal value, the solution vector, and the multipliers.
```

Claude should call the `solve_qp` tool, get back a structured result, and report it.

## Stretch goals

1. **Logging.** Add a second MCP tool `log_run(problem_id, result)` that appends a row to a SQLite database. Then ask Claude to run a small parameter sweep and query the database after.
2. **PETSc/TAO.** Replace the cvxpy backend with a `petsc4py` + TAO bound-constrained QP solver. Same MCP shell, different solver — that's the whole point.
3. **Inputs as resources.** Instead of pasting `problem.json` into the prompt, expose it as an MCP *resource* that Claude can list and read. The Python SDK supports both tools and resources.

## Discussion prompts

- When does an MCP beat a plain CLI? (Hint: stateful sessions, structured I/O, cross-tool reuse.)
- When does it lose to a skill?
