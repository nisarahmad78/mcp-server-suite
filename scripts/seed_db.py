"""Create and seed the sample sales database.

Creates data/sample.db with two tables:

  products(id, name, category, price, stock)
  orders(id, product_id, quantity, customer, order_date)

Run from the project root:

    python scripts/seed_db.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "sample.db"

PRODUCTS = [
    # name, category, price, stock
    ("Aurora Wireless Headphones", "Audio", 129.99, 340),
    ("Nebula Mechanical Keyboard", "Accessories", 89.50, 520),
    ("Vertex Ultrabook Laptop 14", "Computers", 1199.00, 45),
    ("Pulse Smart Watch Series 5", "Wearables", 249.99, 210),
    ("Echo Chamber Speaker Mini", "Audio", 59.99, 800),
    ("Glide Pro Mouse", "Accessories", 49.99, 640),
    ("Terra 27in 4K Monitor", "Computers", 429.99, 120),
    ("Solstice Desk Lamp", "Home Office", 39.95, 430),
    ("Drift Ergonomic Chair", "Home Office", 349.00, 60),
    ("Orbit USB-C Docking Station", "Accessories", 159.99, 275),
    ("Zephyr Laptop Stand", "Accessories", 69.99, 390),
    ("Halo Noise-Cancel Earbuds", "Audio", 79.99, 710),
]

ORDERS = [
    # product index (1-based into PRODUCTS), quantity, customer, order_date
    (1, 3, "Acme Corp", "2026-01-05"),
    (3, 2, "Northwind Traders", "2026-01-07"),
    (5, 10, "Globex", "2026-01-09"),
    (2, 5, "Initech", "2026-01-12"),
    (4, 4, "Umbrella LLC", "2026-01-15"),
    (12, 8, "Acme Corp", "2026-01-18"),
    (7, 3, "Stark Industries", "2026-01-21"),
    (6, 12, "Globex", "2026-01-25"),
    (10, 6, "Wayne Enterprises", "2026-02-02"),
    (1, 5, "Initech", "2026-02-06"),
    (8, 15, "Hooli", "2026-02-10"),
    (3, 1, "Pied Piper", "2026-02-14"),
    (9, 2, "Northwind Traders", "2026-02-18"),
    (11, 7, "Umbrella LLC", "2026-02-22"),
    (12, 20, "Hooli", "2026-03-01"),
    (5, 6, "Stark Industries", "2026-03-04"),
    (2, 9, "Wayne Enterprises", "2026-03-08"),
    (4, 3, "Acme Corp", "2026-03-11"),
    (7, 2, "Globex", "2026-03-15"),
    (10, 4, "Pied Piper", "2026-03-19"),
    (6, 10, "Northwind Traders", "2026-03-23"),
    (1, 2, "Hooli", "2026-03-27"),
    (8, 11, "Initech", "2026-04-02"),
    (12, 5, "Wayne Enterprises", "2026-04-06"),
    (3, 3, "Acme Corp", "2026-04-10"),
    (9, 1, "Globex", "2026-04-14"),
    (11, 5, "Stark Industries", "2026-04-18"),
    (5, 14, "Umbrella LLC", "2026-04-22"),
    (4, 6, "Pied Piper", "2026-04-26"),
    (2, 4, "Hooli", "2026-04-30"),
]


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(
            """
            CREATE TABLE products (
                id       INTEGER PRIMARY KEY,
                name     TEXT NOT NULL,
                category TEXT NOT NULL,
                price    REAL NOT NULL,
                stock    INTEGER NOT NULL
            );
            CREATE TABLE orders (
                id         INTEGER PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity   INTEGER NOT NULL,
                customer   TEXT NOT NULL,
                order_date TEXT NOT NULL
            );
            """
        )
        conn.executemany(
            "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
            PRODUCTS,
        )
        conn.executemany(
            "INSERT INTO orders (product_id, quantity, customer, order_date) VALUES (?, ?, ?, ?)",
            ORDERS,
        )
    print(f"Seeded {DB_PATH} with {len(PRODUCTS)} products and {len(ORDERS)} orders.")


if __name__ == "__main__":
    sys.exit(main())
