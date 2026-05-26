import json
import logging
import mcp.server
import mcp.types as types
from sqlserver_mcp.connection import SQLServerConnection

logger = logging.getLogger(__name__)


class SQLServerMCPServer(mcp.server.Server):
    def __init__(self):
        super().__init__("sqlserver-mcp-server")
        self.db = SQLServerConnection()
        self._register_handlers()

    def _register_handlers(self):
        @self.list_tools()
        async def list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="process_req",
                    description=(
                        "Execute a SQL query against the connected SQL Server database. "
                        "Supports SELECT, INSERT, UPDATE, DELETE, and DDL statements. "
                        "Returns rows and column names for SELECT queries, or rows_affected "
                        "for DML/DDL statements."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The SQL query to execute.",
                            }
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="list_tables",
                    description=(
                        "List all tables in the connected SQL Server database. "
                        "Optionally filter by schema name. Returns table schema, name, and type."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "schema": {
                                "type": "string",
                                "description": "Optional schema name to filter tables (e.g. 'dbo').",
                            }
                        },
                        "required": [],
                    },
                ),
            ]

        @self.call_tool()
        async def call_tool(
            name: str, arguments: dict
        ) -> list[types.TextContent]:
            logger.debug("Tool called: %s with arguments: %s", name, arguments)

            if name == "process_req":
                query = arguments.get("query", "").strip()
                if not query:
                    result = {"success": False, "error": "No query provided."}
                else:
                    result = self.db.process_req(query)
            elif name == "list_tables":
                result = self.db.list_tables(schema=arguments.get("schema"))
            else:
                result = {"success": False, "error": f"Unknown tool: {name}"}

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
