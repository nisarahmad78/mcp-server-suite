"""revenue_stats — sales analytics computed from the sample database."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..config import settings
from ..db import format_table, run_select

_TOP_PRODUCTS_SQL = """
SELECT p.name AS product,
       p.category AS category,
       SUM(o.quantity) AS units_sold,
       ROUND(SUM(o.quantity * p.price), 2) AS revenue
FROM orders o
JOIN products p ON p.id = o.product_id
GROUP BY p.id
ORDER BY revenue DESC
LIMIT ?
"""

_CATEGORY_SQL = """
SELECT p.category AS category,
       SUM(o.quantity) AS units_sold,
       ROUND(SUM(o.quantity * p.price), 2) AS revenue
FROM orders o
JOIN products p ON p.id = o.product_id
GROUP BY p.category
ORDER BY revenue DESC
"""


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def revenue_stats(limit: int = 5, by_category: bool = False) -> str:
        """Compute revenue statistics from the sample sales data.

        By default returns the top products by revenue (units sold and total
        revenue). Set by_category=true to aggregate revenue per category
        instead.

        Args:
            limit: How many top products to return (1-20). Ignored when
                   by_category is true.
            by_category: Aggregate by product category instead of product.
        """
        limit = max(1, min(limit, 20))
        sql = _CATEGORY_SQL if by_category else _TOP_PRODUCTS_SQL
        # LIMIT is interpolated as a validated int; the query itself is fixed.
        query = sql.replace("LIMIT ?", f"LIMIT {limit}") if not by_category else sql
        try:
            columns, rows, truncated = run_select(settings.db_path, query, settings.max_query_rows)
        except FileNotFoundError as exc:
            return f"Error: {exc}"
        except Exception as exc:
            return f"Error computing stats: {exc}"
        title = "Revenue by category:" if by_category else f"Top {limit} products by revenue:"
        return title + "\n" + format_table(columns, rows, truncated)
