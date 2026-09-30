# Frequently Asked Questions

## What is MCP?

MCP (Model Context Protocol) is a standard protocol for connecting AI
models to tools, databases, and services. A server exposes tools; a
client (an AI app) discovers and calls them through the protocol.

## Which tools does this server provide?

- sqlite_query: read-only SQL against the sample sales database.
- file_search: keyword search across this docs folder.
- web_fetch: fetch a page and return clean text.
- revenue_stats: top products and categories by revenue.

## Can the tools modify the database?

No. The database connection is read-only and only SELECT statements are
accepted. The protocol surface is intentionally small and safe to expose
to an AI client.

## How do I add my own tool?

Create a module under server/tools/, define a register(mcp) function,
decorate functions with @mcp.tool(), and add the module to register_all.
The demo client will pick the new tool up automatically because it reads
the tool list from the protocol handshake.
