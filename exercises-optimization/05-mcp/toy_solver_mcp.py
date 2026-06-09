"""A minimal MCP server exposing a `solve_qp` tool.

Solves problems of the form

    min  0.5 x^T Q x + c^T x   s.t.  A x <= b

using cvxpy. Replace the cvxpy backend with petsc4py/TAO for the
stretch goal — the rest of the file stays the same.

Run as a Claude Code MCP server:

    claude mcp add toy-solver --command python \\
        --args "$(pwd)/toy_solver_mcp.py"
"""
from __future__ import annotations

import asyncio
import json

import numpy as np

# `mcp` is the Python SDK from modelcontextprotocol.io.
# Install with: pip install mcp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool


server = Server("toy-solver")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="solve_qp",
            description=(
                "Solve a convex QP min 0.5 x^T Q x + c^T x s.t. A x <= b. "
                "Returns the optimal x, optimal value, dual multipliers."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "Q": {"type": "array", "description": "Symmetric PSD matrix as nested lists"},
                    "c": {"type": "array", "description": "Linear coefficient vector"},
                    "A": {"type": "array", "description": "Inequality matrix as nested lists"},
                    "b": {"type": "array", "description": "Inequality RHS vector"},
                },
                "required": ["Q", "c", "A", "b"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "solve_qp":
        raise ValueError(f"Unknown tool: {name}")
    import cvxpy as cp

    Q = np.asarray(arguments["Q"], dtype=float)
    c = np.asarray(arguments["c"], dtype=float)
    A = np.asarray(arguments["A"], dtype=float)
    b = np.asarray(arguments["b"], dtype=float)

    n = Q.shape[0]
    x = cp.Variable(n)
    constraints = [A @ x <= b]
    obj = cp.Minimize(0.5 * cp.quad_form(x, cp.psd_wrap(Q)) + c @ x)
    prob = cp.Problem(obj, constraints)
    prob.solve()

    payload = {
        "status": prob.status,
        "optimal_value": float(prob.value) if prob.value is not None else None,
        "x": x.value.tolist() if x.value is not None else None,
        "duals": [d.tolist() for d in (constraints[0].dual_value or [])],
    }
    return [TextContent(type="text", text=json.dumps(payload, indent=2))]


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
