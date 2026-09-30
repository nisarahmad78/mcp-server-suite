FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8080

# Default: run the MCP server. docker-compose overrides the command
# per service (server over Streamable HTTP, client as the web app).
CMD ["python", "-m", "server.main"]
