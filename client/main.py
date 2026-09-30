"""Demo web app: try the MCP Server Suite tools from the browser.

Run from the project root:

    uvicorn client.main:app --port 8080

Then open http://localhost:8080. The page lists the tools the MCP server
advertises (fetched live through the protocol), builds a form from each
tool's JSON schema, and shows the result of calling the tool.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import mcp_client

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="MCP Server Suite — Demo Client")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class RunRequest(BaseModel):
    name: str
    arguments: dict = {}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/tools")
async def tools() -> dict:
    try:
        return {"tools": await mcp_client.list_tools()}
    except Exception as exc:
        return {"tools": [], "error": f"Could not reach the MCP server: {exc}"}


@app.post("/api/run")
async def run(request: RunRequest) -> dict:
    try:
        result = await mcp_client.call_tool(request.name, request.arguments)
        return {"ok": True, "result": result}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
