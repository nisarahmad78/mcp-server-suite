"""web_fetch — fetch a URL and return its readable text content."""

from __future__ import annotations

from html.parser import HTMLParser

import httpx
from mcp.server.fastmcp import FastMCP

from ..config import settings

_MAX_CHARS = 8000
_SKIP_TAGS = {"script", "style", "noscript", "svg", "head"}


class _TextExtractor(HTMLParser):
    """Minimal HTML-to-text extractor (no external parser dependency)."""

    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
        if tag in {"p", "br", "div", "li", "h1", "h2", "h3", "tr"}:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            text = data.strip()
            if text:
                self._chunks.append(text + " ")

    def get_text(self) -> str:
        raw = "".join(self._chunks)
        lines = [" ".join(line.split()) for line in raw.splitlines()]
        return "\n".join(line for line in lines if line)


def _clean(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return parser.get_text()


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def web_fetch(url: str) -> str:
        """Fetch a web page and return its main text content.

        HTML is converted to clean plain text (scripts, styles and markup
        removed). Non-HTML responses are returned as-is. Output is truncated
        to a readable length.

        Args:
            url: The full URL to fetch, e.g. "https://example.com".
        """
        if not url.startswith(("http://", "https://")):
            return "Error: URL must start with http:// or https://"
        try:
            with httpx.Client(
                timeout=settings.web_fetch_timeout,
                follow_redirects=True,
                headers={"User-Agent": "mcp-server-suite/1.0"},
            ) as client:
                response = client.get(url)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return f"Error: HTTP {exc.response.status_code} for {url}"
        except httpx.HTTPError as exc:
            return f"Error: could not fetch {url}: {exc}"

        content_type = response.headers.get("content-type", "")
        text = _clean(response.text) if "html" in content_type else response.text.strip()
        if not text:
            return f"No readable text content found at {url}."
        if len(text) > _MAX_CHARS:
            text = text[:_MAX_CHARS] + f"\n... [truncated at {_MAX_CHARS} characters]"
        return f"Content from {url}:\n\n{text}"
