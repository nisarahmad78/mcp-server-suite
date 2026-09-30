"""End-to-end smoke test for the MCP server over stdio.

Spawns the server exactly like a real MCP client would, lists the tools
via the protocol handshake, and calls sqlite_query, file_search and
revenue_stats.

Usage (from the project root, with dependencies installed):

    python scripts/test_server.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _text(result) -> str:
    return "".join(block.text for block in result.content if hasattr(block, "text"))


async def main() -> int:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "server.main"],
        cwd=str(PROJECT_ROOT),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            print("Tools discovered:", ", ".join(names))
            expected = {"sqlite_query", "file_search", "web_fetch", "revenue_stats"}
            missing = expected - set(names)
            if missing:
                print("FAIL: missing tools:", ", ".join(sorted(missing)))
                return 1

            result = await session.call_tool(
                "sqlite_query",
                {"sql": "SELECT name, price FROM products ORDER BY price DESC LIMIT 3"},
            )
            print("\nsqlite_query result:\n" + _text(result))
            assert "Vertex Ultrabook" in _text(result), "unexpected sqlite_query output"

            result = await session.call_tool("file_search", {"keyword": "protocol"})
            print("\nfile_search result (first 400 chars):\n" + _text(result)[:400])
            assert "match" in _text(result).lower(), "unexpected file_search output"

            result = await session.call_tool("revenue_stats", {"limit": 3})
            print("\nrevenue_stats result:\n" + _text(result))

            result = await session.call_tool(
                "sqlite_query", {"sql": "DELETE FROM products"}
            )
            print("\nwrite attempt correctly handled:\n" + _text(result))
            assert "Error" in _text(result), "write query was not rejected"

    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
