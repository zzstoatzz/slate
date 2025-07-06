"""Entry point for running slate."""

import sys

if "--mcp" in sys.argv:
    # Run as MCP server
    from .mcp_server import mcp
    import asyncio
    asyncio.run(mcp.run())
else:
    # Run as CLI
    from .cli import cli
    cli()