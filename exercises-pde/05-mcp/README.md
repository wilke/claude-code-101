# Exercise 05 — Wrap a small Laplace solver as an MCP server (15 min)

**Goal.** Stand up a Model Context Protocol server that exposes a `solve_laplace` tool to Claude Code, register it, and watch Claude call it by name when you describe a Poisson problem in plain English. MCP is the package format for *"any session in this project can now use this tool"* — register once, invoke by tool name forever. The Laplace solver shipped here is the pretext; the registered tool that survives across sessions is the artifact.

**Setup.** The main flow is pure-Python — install with `pip install -r requirements.txt`. **Docker is not required for this exercise.** (The stretch swaps the backend for a Firedrake-in-Docker call; if you decide to attempt it, see `../01-claude-md/INSTALL.md`.) Keep the `CLAUDE.md` you wrote in Exercises 01-04 — Claude reads it every session. If you find yourself wanting to repeat any convention about *how MCPs are registered or invoked*, add it there.

## The problem

*The shipped `laplace_mcp.py` solves -div(grad u) = f on the unit square (0,1)² with Dirichlet boundary u = bc, using a 5-point finite-difference stencil on a uniform (n+1) × (n+1) grid. The shipped `problem.json` is the manufactured-solution case f = 2π² sin(πx) sin(πy) with bc = 0, whose exact solution is u_exact = sin(πx) sin(πy); the reported max(u) should land near 1.0.*

*The solver is deliberately small. The lesson is not the discretization — it is registering the server, watching Claude route to it by tool name, and seeing the arguments cross the wire.*

## Register the server

From this directory:

```bash
cd exercises-pde/05-mcp
pip install -r requirements.txt
```

Then register the server with Claude Code:

```bash
claude mcp add toy-laplace -- python3 "$(pwd)/laplace_mcp.py"
```

The `--` separates the registration command from the command Claude will run to launch the server. On macOS with Homebrew Python, only `python3` is on PATH (there is no `python` binary), so use `python3` here. Quick sanity check before registering:

```bash
which python3 && python3 -c "import mcp; print('ok')"
```

List the registered MCPs to confirm:

```bash
claude mcp list
```

## Steps

1. Register the server (above).
2. Launch `claude` in this directory.
3. **Paste this prompt verbatim:**

   ```
   Solve the Poisson problem described in problem.json using the toy-laplace MCP and print the structured result.
   ```
4. Watch Claude read `problem.json`, call `toy-laplace:solve_laplace` with the three arguments, and report the payload. The arguments-over-the-wire are the auditable moment — note exactly what was sent.
5. Edit `problem.json` (bump `n` to `64`, or change the RHS) and re-prompt. Confirm Claude re-calls the MCP with the new arguments rather than recycling the prior answer.
6. When you are done: `claude mcp remove toy-laplace` to clean up, or keep it registered if you want it available in future sessions in this folder.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did Claude call the MCP tool by name, or compute the answer inline with numpy? | If Claude computes inline, you have not actually tested the MCP — you have tested Claude's scipy reflex. |
| Did the arguments-over-the-wire match `problem.json` verbatim? | An MCP's auditability comes from exact, visible arguments. A rounded `n` or simplified RHS means the audit trail is broken. |
| Did Claude report the structured payload faithfully, or paraphrase it as "max ≈ 1, looks right"? | The structured response is the whole point — paraphrasing throws away the contract the schema enforces. |
| When you edited `problem.json`, did Claude re-call the MCP, or recycle the prior result? | Recycling means Claude treated the first call as a memo, not a tool. |
| Did Claude treat the MCP as the source of truth, or second-guess the result with its own inline check? | If you disagree with what the MCP returns, change the server — not the report. |
| On the second prompt, did Claude know the tool was available without being reminded? | A registered MCP should appear in the tool list automatically. If Claude asks "what MCP?", the registration did not stick. |

## Discussion prompts

- The wrapped solver is tiny — `pip install scipy` would let any session compute the same answer in three lines. When does that change? What capability would have to be inside the MCP for *"MCP, not skill"* to be the obvious right answer?
- Compare the MCP shell here to the skill from Exercise 03. Both expose a recurring computation to Claude. What makes one feel right for the CFL check and the other feel right for, say, a solver running on a remote cluster?

## Stretch (optional, for experienced learners)

Swap the numpy `spsolve` inside `call_tool` for a Firedrake-in-Docker call — the MCP shell (server name, tool name, input schema) stays the same; only the body of `call_tool` changes. See `../01-claude-md/INSTALL.md` for the Docker install. This is where the *"why MCP, not skill"* question starts to bite: the warm Python process holding the MCP can cache the Firedrake JIT across calls, amortizing the cold start that would otherwise dominate every invocation. As a smaller variant, add a second tool `mesh_info(n)` that reports the grid spacing `h`, the matrix size, and the stencil bandwidth — a multi-tool MCP grows from a single-tool one with one more `Tool(...)` entry in `list_tools` and one more `if name == ...` branch in `call_tool`.
