"""Entry point for slate memory MCP server."""

from .mcp_server import mcp
import asyncio

if __name__ == "__main__":
    asyncio.run(mcp.run())