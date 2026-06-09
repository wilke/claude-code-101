"""A minimal MCP server exposing a `solve_laplace` tool.

Solves the Poisson equation

    -div(grad u) = f   on (0, 1)^2,    u = bc on the boundary,

using a 5-point finite-difference stencil on a uniform (n+1) x (n+1)
grid (n cells per side). The backend is numpy/scipy; the MCP shell
itself is the lesson. The stretch swaps the numpy backend for a
Firedrake-in-Docker call - the server name, tool name, and input
schema stay the same; only the body of call_tool changes.

Run as a Claude Code MCP server:

    claude mcp add toy-laplace -- python3 "$(pwd)/laplace_mcp.py"
"""
from __future__ import annotations

import asyncio
import json

import numpy as np

# `mcp` is the Python SDK from modelcontextprotocol.io.
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool


server = Server("toy-laplace")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="solve_laplace",
            description=(
                "Solve the Poisson equation -div(grad u) = f on the unit "
                "square (0,1)^2 with Dirichlet boundary u = bc, using a "
                "5-point finite-difference stencil on a uniform grid. "
                "Returns the maximum value of u, its L2 norm, the DOF "
                "count, the grid resolution, and the solver status."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Number of cells per side (n >= 3). The grid has (n+1)^2 nodes; interior unknowns are (n-1)^2.",
                    },
                    "rhs": {
                        "type": "string",
                        "description": "RHS expression in variables x, y using sin, cos, exp, pi (e.g. '2 * pi**2 * sin(pi*x) * sin(pi*y)').",
                    },
                    "bc": {
                        "type": "number",
                        "description": "Constant Dirichlet boundary value.",
                    },
                },
                "required": ["n", "rhs", "bc"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "solve_laplace":
        raise ValueError(f"Unknown tool: {name}")
    import scipy.sparse as sp
    import scipy.sparse.linalg as spla

    n = int(arguments["n"])
    rhs_expr = str(arguments["rhs"])
    bc = float(arguments["bc"])
    if n < 3:
        raise ValueError("n must be >= 3")

    h = 1.0 / n
    xs = np.linspace(0.0, 1.0, n + 1)
    X, Y = np.meshgrid(xs, xs, indexing="ij")

    # Guarded eval: only the names below are exposed to the user's RHS
    # string. Not raw eval - the empty __builtins__ blocks attribute
    # access into the interpreter.
    rhs_namespace = {
        "__builtins__": {},
        "sin": np.sin, "cos": np.cos, "exp": np.exp, "pi": np.pi,
        "x": X, "y": Y,
    }
    F = eval(rhs_expr, rhs_namespace)
    F = np.broadcast_to(F, X.shape).astype(float)

    # Interior unknowns: index 1..n-1 along each axis, shape (n-1, n-1).
    m = n - 1
    T = sp.diags([-np.ones(m - 1), 2 * np.ones(m), -np.ones(m - 1)],
                 offsets=[-1, 0, 1], format="csr")
    I = sp.eye(m, format="csr")
    A = (sp.kron(I, T) + sp.kron(T, I)) / h**2  # discretizes -Laplacian

    f_int = F[1:n, 1:n].copy()
    # Boundary contribution: for each interior node adjacent to a
    # boundary, add bc/h^2 to the RHS (the boundary value moves to the
    # right-hand side).
    g_bc = np.zeros_like(f_int)
    g_bc[0, :] += bc / h**2
    g_bc[-1, :] += bc / h**2
    g_bc[:, 0] += bc / h**2
    g_bc[:, -1] += bc / h**2

    rhs_vec = (f_int + g_bc).reshape(-1)
    u_int = spla.spsolve(A.tocsc(), rhs_vec).reshape(m, m)

    u = np.full((n + 1, n + 1), bc, dtype=float)
    u[1:n, 1:n] = u_int

    payload = {
        "status": "optimal",
        "max_u": float(u.max()),
        "l2_norm": float(np.sqrt(np.sum(u**2) * h**2)),
        "dofs": int(m * m),
        "grid": int(n + 1),
    }
    return [TextContent(type="text", text=json.dumps(payload, indent=2))]


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
