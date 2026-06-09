# Solution — Exercise 05 (MCP server wrapping a Laplace solver)

## What this exercise is doing

The learner installs three pip packages, registers a tiny Python MCP server (`toy-laplace`) with Claude Code, launches `claude` in this directory, and pastes a one-line prompt that asks Claude to solve the Poisson problem described in `problem.json` using the registered MCP. They watch Claude read the JSON, route to the `solve_laplace` tool by name, pass the three arguments over the wire verbatim, and report the structured payload (`status`, `max_u`, `l2_norm`, `dofs`, `grid`). They then edit `problem.json`, re-prompt, and confirm Claude re-calls the MCP instead of recycling the prior answer.

The pedagogy is **the MCP shell**, not the Laplace solver. The shipped main flow is deliberately pure-Python — `numpy` and `scipy` only, no Docker — because the lesson is *what an MCP registration buys you*: a named tool that survives the session and shows up in every future `claude` invocation from this folder. The discretization could be three lines or three hundred and the exercise would teach the same thing. The stretch swaps the numpy backend for a Firedrake-in-Docker call; the MCP shell stays exactly the same, only the body of `call_tool` changes.

## The prompt the learner pastes

```
Solve the Poisson problem described in problem.json using the toy-laplace MCP and print the structured result.
```

Note what the prompt *does not* contain. It does not name the function (`solve_laplace`). It does not list the arguments (`n`, `rhs`, `bc`). It does not describe the schema. Claude routes the call from the descriptions returned by the server's `list_tools` — that text is the contract, which is why the tool description in `laplace_mcp.py` is more carefully worded than the rest of the file.

## What a session with the MCP looks like

The exact wording varies per session; the *shape* below — Claude reading the JSON, calling the tool by name with verbatim arguments, and returning the structured payload without paraphrase — is what to look for.

```
> Solve the Poisson problem described in problem.json using the toy-laplace MCP and print the structured result.

[Reads problem.json]
{
  "n": 32,
  "rhs": "2 * pi**2 * sin(pi*x) * sin(pi*y)",
  "bc": 0.0
}

[Calls toy-laplace:solve_laplace]
  arguments:
    n = 32
    rhs = "2 * pi**2 * sin(pi*x) * sin(pi*y)"
    bc = 0.0

[toy-laplace returns]
{
  "status": "optimal",
  "max_u": <near 1.0>,
  "l2_norm": <near 0.5>,
  "dofs": 961,
  "grid": 33
}

The toy-laplace MCP solved the Poisson problem on a 33×33 grid (961 interior
DOFs). Solver status was optimal. The reported max(u) lands near 1.0, matching
the manufactured solution u_exact = sin(πx)sin(πy), and the L² norm is close
to 0.5 (the integral of sin²(πx)sin²(πy) over the unit square is 1/4, so the
L² norm is its square root).
```

Things to notice in a clean trace:

- The tool was called by name, not by capability. `toy-laplace:solve_laplace` is the routing handle; every future session sees the same name without needing prose framing.
- The arguments crossed the wire verbatim from `problem.json`. No rounding of `n`, no simplification of the RHS string, no swap of `bc = 0` for `bc = 0.0`.
- The structured payload was reported as JSON, then explained — not collapsed into "max ≈ 1, looks fine". The schema is what makes MCP results auditable; paraphrase throws that away.
- The verbal explanation ties the numbers back to the manufactured solution. That is the right level of cross-checking: confirm the magnitude matches what theory says, do not re-derive the magnitude with a parallel inline calculation.

## Why this is an MCP — and when not

The toy here is honestly *skill-shaped*. A 100-line numpy/scipy script could just as easily live as a Claude Code skill or as a snippet in `CLAUDE.md`. The MCP shell is what is being taught — not the choice to use one for this particular workload.

The honest decision rule:

| Mechanism | When it earns its keep |
|-----------|------------------------|
| `CLAUDE.md` note | One-shot conventions ("we use `dx(degree=4)` for non-polynomial integrands"). No code needed; Claude reads `CLAUDE.md` every session anyway. |
| Skill | Stateless, reusable inside this project, ships in the repo. The CFL-check skill from Exercise 03 is the canonical shape — a small Python helper Claude invokes whenever the conversation touches the relevant question. |
| MCP | The capability has *persistent state worth keeping warm across calls* (a loaded JIT cache, an open database connection, a long-running container); or it talks to something Claude Code cannot run inline (a remote cluster, a licensed solver, a service behind auth); or it needs to be available to many sessions across many projects without re-shipping the code. |

The stretch is where the MCP justification for *this* workload starts to bite. A Firedrake backend pays a real cold-start cost — Docker boot plus form-compiler JIT plus solver setup — that dominates the actual solve for small problems. An MCP server is a long-running Python process; once it has paid the cost once, every subsequent call in the same session reuses the warm state. That is the moment "MCP, not skill" stops being a teaching exercise and starts being the design that actually wins.

## What Claude is supposed to do

1. See `toy-laplace` listed on connect and read its tool descriptions (the `list_tools` reply).
2. When the prompt names a Poisson problem and the MCP, route to `solve_laplace` rather than reaching for inline numpy.
3. Read `problem.json` and extract `n`, `rhs`, `bc`.
4. Call the tool with those arguments — exactly those arguments, visible at the tool-call boundary.
5. Report the returned payload faithfully. If summarizing the payload in prose, the structured JSON still appears verbatim alongside.
6. On a re-prompt after `problem.json` is edited, re-call the tool with the new arguments — do not recycle the prior result.

## Where it usually goes wrong on the first try

| What Claude often does | What to push back with |
|------------------------|------------------------|
| Computes the answer inline with scipy instead of calling the MCP. | "Use the toy-laplace MCP. The point is the routing and the audit trail, not the answer itself — inline scipy bypasses both." |
| Paraphrases the structured payload as "max ≈ 1, looks right" without printing the JSON. | "Show the full payload. The structured response is what makes MCP auditable; paraphrase throws that away." |
| Calls the MCP but with arguments that drift from `problem.json` — rounded `n`, simplified RHS, `bc = 0` instead of `bc = 0.0`. | "The arguments must match `problem.json` verbatim. The wire-level call is the contract." |
| Cannot find the MCP after registration. | "Check `claude mcp list` from a shell. If the MCP shows up there but Claude does not see it, restart the `claude` session — tool discovery happens on connect." |
| Registration command runs, but the Python that Claude launches has no `mcp` package. | "The MCP runs in the host Python — `pip install -r requirements.txt` into the same Python you registered with. On macOS with Homebrew, that is `python3`, not `python` (only `python3` exists on PATH)." |
| Treats the MCP's verdict as advisory and second-guesses it with an inline scipy cross-check. | "The MCP is the source of truth for what its tool does. If you disagree, change the server — not the report." |
| Stretch: swaps in a Firedrake backend but quietly broadens the input schema (e.g. accepts a Firedrake mesh object). | "The tool's input schema is the contract every caller in every future session relies on. Backend swaps preserve `n`, `rhs`, `bc` as the inputs; widen the schema only if you are willing to break every existing caller." |
| Stretch: adds a second tool but the description is too vague to route on. | "The description is the routing rule. If two tools have descriptions a model could confuse, future sessions will route wrong — make each tool's description the answer to *when should you call this one and not the other*." |

## Stretch deep-dive — the Firedrake backend

The mechanical part of the swap is small. Inside `call_tool`, replace the numpy/scipy block with a call to a helper that runs Firedrake. The simplest version shells out to a sibling script via `docker run --rm -v "$PWD":/work -w /work firedrakeproject/firedrake:latest python3 /work/solve.py`, passing `n`, `rhs`, `bc` on stdin and reading the payload back on stdout. The MCP shell stays the parent process; nothing about the tool name, the schema, or the response shape changes.

The interesting part is the warm-state variant. A fresh `docker run` per call pays the container-boot cost every time and never amortizes the Firedrake JIT. The slightly larger version keeps a long-lived Firedrake container open with `docker run -d`, then dispatches each call through `docker exec` to a Python process inside it that has already imported Firedrake and warmed its form-compilation cache. The cold start moves from "every call" to "first call of the session"; subsequent calls reuse the JIT and run at roughly numpy-backend speed plus the cost of crossing the container boundary.

That is the design where MCP earns its keep for *this* workload — not the cold-start version, not the toy main flow, but the version where the long-running Python process holding the MCP server is also the one holding the warmth. Mention this in the debrief; it is the bridge from "MCP is a registration mechanism" to "MCP is a place to put state worth keeping."

## The capstone connection

In the capstone, multiple MCPs may be registered simultaneously — a solver, a mesh database, a citation source — and the prompt's tool routing across MCPs is exactly the behavior Exercise 05 sets up.

## How to use this in the workshop

Hand learners the README; the `pip install` and `claude mcp add` steps take two to three minutes (longer if anyone is on a corporate Python with restricted package install), the routing test takes five, the edit-and-re-prompt takes three, leaving roughly five minutes for the discussion prompts or a glance at the stretch. The most common live failure is the wrong Python — registering with `python` on a Homebrew macOS box where only `python3` exists, or registering with system Python while the `mcp` package was pip-installed into a venv. Surface that pitfall first if you see registration silently failing. If `pip install mcp` fails outright (rare, but happens on locked-down corporate Pythons), fall back to walking through the README and the server source from the screen rather than blocking on the install — the *shape* of the MCP shell is teachable from the source code alone, and the routing intuition transfers without the live session.
