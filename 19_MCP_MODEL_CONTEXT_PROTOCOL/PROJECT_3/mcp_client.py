"""MCP client helpers for PROJECT_3 — same pattern as PROJECT_2."""

from pathlib import Path

from fastmcp import Client

SERVER_SCRIPT = Path(__file__).resolve().parent / "server.py"

async def connect():
    """Connect to the MCP Server."""
    client = Client(SERVER_SCRIPT)
    await client.__aenter__()
    print("Connected to MCP Server.")
    return client

async def disconnect(client):
    """Close the MCP connection."""
    await client.__aexit__(None, None, None)

async def discover_tools(client):
    """Retrieve all tools from the server."""
    tools = await client.list_tools()
    return tools

async def execute_tool(client, tool_name, arguments=None):
    """Execute a tool."""
    if arguments is None:
        arguments = {}
    result = await client.call_tool(tool_name, arguments)
    return result
