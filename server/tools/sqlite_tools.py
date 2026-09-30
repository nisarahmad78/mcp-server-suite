"""sqlite_query — run read-only SQL against the sample database."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..config import settings
from ..db import QueryRejected, format_table, run_select


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def sqlite_query(sql: str) -> str:
        """Run a read-only SQL SELECT query against the sample sales database.

        Tables: products(id, name, category, price, stock) and
        orders(id, product_id, quantity, customer, order_date).
        Only a single SELECT statement is allowed; writes are rejected and
        the connection itself is opened read-only.

        Args:
            sql: The SELECT query to run, e.g.
                 "SELECT name, price FROM products ORDER BY price DESC LIMIT 5"
        """
        try:
            columns, rows, truncated = run_select(settings.db_path, sql, settings.max_query_rows)
        except (QueryRejected, FileNotFoundError) as exc:
            return f"Error: {exc}"
        except Exception as exc:  # sqlite errors: bad column, syntax, ...
            return f"SQL error: {exc}"
        return format_table(columns, rows, truncated)
