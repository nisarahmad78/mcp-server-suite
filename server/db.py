"""Read-only SQLite access helpers.

Safety model for the sqlite_query tool:
  1. The connection is opened with SQLite's ``mode=ro`` URI flag, so the
     engine itself refuses any write, even if a check below is bypassed.
  2. The statement is validated before execution: it must be a single
     SELECT (or WITH ... SELECT) statement.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

_FORBIDDEN_STARTERS = (
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "replace",
    "truncate",
    "attach",
    "pragma",
    "vacuum",
)


class QueryRejected(ValueError):
    """Raised when a query is not an allowed read-only SELECT."""


def validate_select(sql: str) -> str:
    """Return the cleaned single SELECT statement or raise QueryRejected."""
    cleaned = sql.strip().rstrip(";").strip()
    if not cleaned:
        raise QueryRejected("Query is empty.")
    if ";" in cleaned:
        raise QueryRejected("Only a single statement is allowed.")
    first_word = cleaned.split(None, 1)[0].lower()
    if first_word in _FORBIDDEN_STARTERS:
        raise QueryRejected(f"Statement type '{first_word}' is not allowed. SELECT only.")
    if first_word not in {"select", "with"}:
        raise QueryRejected("Only SELECT queries are allowed.")
    return cleaned


def run_select(
    db_path: Path, sql: str, max_rows: int
) -> tuple[list[str], list[tuple], bool]:
    """Execute a validated SELECT against a read-only connection.

    Returns (columns, rows, truncated).
    """
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found at {db_path}. Run scripts/seed_db.py first."
        )
    query = validate_select(sql)
    uri = f"file:{db_path}?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        cursor = conn.execute(query)
        columns = [col[0] for col in cursor.description or []]
        rows = cursor.fetchmany(max_rows + 1)
    truncated = len(rows) > max_rows
    return columns, rows[:max_rows], truncated


def format_table(columns: list[str], rows: list[tuple], truncated: bool = False) -> str:
    """Render query results as a compact plain-text table."""
    if not columns:
        return "Query returned no columns."
    text_rows = [["" if v is None else str(v) for v in row] for row in rows]
    widths = [len(c) for c in columns]
    for row in text_rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))

    def render(cells: list[str]) -> str:
        return " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    lines = [render(columns), "-+-".join("-" * w for w in widths)]
    lines += [render(row) for row in text_rows]
    lines.append(f"({len(text_rows)} row{'s' if len(text_rows) != 1 else ''})")
    if truncated:
        lines.append("Results truncated at the configured row limit.")
    return "\n".join(lines)
