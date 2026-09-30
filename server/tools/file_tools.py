"""file_search — keyword search with context across the sample docs folder."""

from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..config import settings

_SEARCHABLE_SUFFIXES = {".txt", ".md"}
_MAX_MATCHES = 25


def _search_file(path: Path, keyword: str, context_lines: int) -> list[str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    hits: list[str] = []
    needle = keyword.lower()
    for idx, line in enumerate(lines):
        if needle in line.lower():
            start = max(0, idx - context_lines)
            end = min(len(lines), idx + context_lines + 1)
            block = []
            for j in range(start, end):
                marker = ">" if j == idx else " "
                block.append(f"  {marker} {j + 1:>4}: {lines[j]}")
            hits.append("\n".join(block))
    return hits


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def file_search(keyword: str, context_lines: int = 1) -> str:
        """Search the sample documentation folder for a keyword.

        Searches all .txt and .md files under the docs directory and returns
        each matching line with surrounding context lines.

        Args:
            keyword: Word or phrase to search for (case-insensitive).
            context_lines: Lines of context to include around each match.
        """
        docs_dir = settings.docs_dir
        if not docs_dir.exists():
            return f"Error: docs directory not found at {docs_dir}."
        if not keyword.strip():
            return "Error: keyword must not be empty."

        results: list[str] = []
        total = 0
        for path in sorted(docs_dir.rglob("*")):
            if path.suffix.lower() not in _SEARCHABLE_SUFFIXES or not path.is_file():
                continue
            for block in _search_file(path, keyword.strip(), max(0, context_lines)):
                total += 1
                if total <= _MAX_MATCHES:
                    results.append(f"{path.relative_to(docs_dir)}:\n{block}")
        if total == 0:
            return f"No matches for '{keyword}' in {docs_dir.name}/."
        header = f"Found {total} match(es) for '{keyword}':"
        if total > _MAX_MATCHES:
            header += f" (showing first {_MAX_MATCHES})"
        return header + "\n\n" + "\n\n".join(results)
