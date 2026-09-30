# Getting Started with the MCP Server Suite

The Model Context Protocol (MCP) is an open standard that lets AI
applications connect to external tools and data sources in a uniform way.
This suite ships a small, complete MCP server you can run locally.

## Quick start

1. Create a virtual environment and install the requirements.
2. Run the seed script to create the sample database.
3. Start the server with `python -m server.main` (stdio transport).
4. Connect any MCP client, for example Claude Desktop or Cursor.

## Transports

The server speaks the MCP protocol over stdio by default, which is how
most desktop clients launch local servers. For container deployments it
can also serve over Streamable HTTP — set `MCP_TRANSPORT=http`.

## Safety notes

The sqlite_query tool is read-only by design. The database connection is
opened with SQLite's read-only flag and every statement is validated
before execution, so the protocol tools can never modify the sample data.
