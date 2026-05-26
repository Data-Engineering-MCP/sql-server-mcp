import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mcp.server.stdio
from sqlserver_mcp.server import SQLServerMCPServer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting SQL Server MCP server...")
    server = SQLServerMCPServer()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
