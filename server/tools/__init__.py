"""Tool modules. Each module exposes ``register(mcp)`` to attach its tools."""

from . import file_tools, sqlite_tools, stats_tools, web_tools

__all__ = ["register_all"]


def register_all(mcp) -> None:
    sqlite_tools.register(mcp)
    file_tools.register(mcp)
    web_tools.register(mcp)
    stats_tools.register(mcp)
