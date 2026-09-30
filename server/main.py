"""MCP Server Suite — entrypoint.

Run locally over stdio (default, for Claude Desktop / Cursor / the demo
client):

    python -m server.main

Run over Streamable HTTP (used by docker-compose):

    MCP_TRANSPORT=http MCP_PORT=8000 python -m server.main
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from .tools import register_all

INSTRUCTIONS = (
    "Sample-data tools for demos and development: query a read-only sales "
    "database, search bundled documentation, fetch web pages as clean text, "
    "and compute revenue statistics."
)


def create_server() -> FastMCP:
    mcp = FastMCP("mcp-server-suite", instructions=INSTRUCTIONS)
    register_all(mcp)
    return mcp


def main() -> None:
    mcp = create_server()
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    if transport in {"http", "streamable-http"}:
        mcp.settings.port = int(os.getenv("MCP_PORT", "8000"))
        mcp.settings.host = os.getenv("MCP_HOST", "0.0.0.0")
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
