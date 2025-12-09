from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP


# Create MCP instance
mcp = FastMCP("Expenses-tracker-mcp-server")

# Import your tools AFTER mcp is created
from main import *   # all tools, prompts, resources attach to mcp

# Create ASGI application
app = mcp.http_app()
