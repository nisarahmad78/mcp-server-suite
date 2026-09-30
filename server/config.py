"""Shared configuration for the MCP server.

All settings come from environment variables (see .env.example) with
sensible defaults relative to the project root, so the server works
out of the box after running the seed script.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _resolve(path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else PROJECT_ROOT / path


@dataclass(frozen=True)
class Settings:
    db_path: Path
    docs_dir: Path
    web_fetch_timeout: float
    max_query_rows: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=_resolve(os.getenv("SAMPLE_DB_PATH", "data/sample.db")),
            docs_dir=_resolve(os.getenv("DOCS_DIR", "data/docs")),
            web_fetch_timeout=float(os.getenv("WEB_FETCH_TIMEOUT", "15")),
            max_query_rows=int(os.getenv("MAX_QUERY_ROWS", "100")),
        )


settings = Settings.from_env()
