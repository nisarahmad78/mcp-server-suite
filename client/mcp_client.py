"""MCP client wrapper used by the demo web app.

The client speaks to the server purely through the Model Context
Protocol — it never imports tool code directly.

Two transports are supported, selected by the MCP_TRANSPORT env var:

  stdio (default)  Spawn ``python -m server.main`` as a subprocess and
                   talk over its stdin/stdout, exactly like Claude
                   Desktop or Cursor launch a local MCP server.
  http             Connect to a running server over Streamable HTTP
                   (MCP_SERVER_URL), as in the docker-compose setup.
"""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@asynccontextmanager
async def connect() -> AsyncIterator[ClientSession]:
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    if transport in {"http", "streamable-http"}:
        url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
        async with streamablehttp_client(url) as streams:
            read, write = streams[0], streams[1]
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    else:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "server.main"],
            cwd=str(PROJECT_ROOT),
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session


async def list_tools() -> list[dict]:
    """Return tool metadata (name, description, input schema) via MCP."""
    async with connect() as session:
        result = await session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "inputSchema": tool.inputSchema or {"type": "object", "properties": {}},
            }
            for tool in result.tools
        ]


async def call_tool(name: str, arguments: dict) -> str:
    """Call one tool via MCP and return its text output."""
    async with connect() as session:
        result = await session.call_tool(name, arguments)
        parts = [block.text for block in result.content if hasattr(block, "text")]
        text = "\n".join(parts) if parts else "(no text output)"
        if result.isError:
            raise RuntimeError(text)
        return text
