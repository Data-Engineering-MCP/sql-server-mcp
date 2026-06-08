import json
import logging
import mcp.server
import mcp.types as types
from connection import SQLServerConnection

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
                types.Tool(
                    name="describe_table",
                    description=(
                        "Return column definitions and primary key info for a table. "
                        "Includes column name, data type, nullability, default value, identity flag, and primary key flag."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table": {
                                "type": "string",
                                "description": "Table name to describe.",
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (default: 'dbo').",
                            },
                        },
                        "required": ["table"],
                    },
                ),
                types.Tool(
                    name="explain_query",
                    description=(
                        "Return the estimated execution plan for a SQL query without executing it. "
                        "Useful for query performance analysis."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The SQL query to explain.",
                            }
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="get_table_sample",
                    description=(
                        "Return a sample of rows from a table (top N rows, max 100). "
                        "Useful for quickly inspecting table contents."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table": {
                                "type": "string",
                                "description": "Table name to sample.",
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (default: 'dbo').",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of rows to return (default: 10, max: 100).",
                            },
                        },
                        "required": ["table"],
                    },
                ),
                types.Tool(
                    name="get_column_stats",
                    description=(
                        "Return statistics for a specific column: total rows, null count, distinct count, "
                        "min, max, and average (for numeric columns)."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table": {
                                "type": "string",
                                "description": "Table name.",
                            },
                            "column": {
                                "type": "string",
                                "description": "Column name to analyse.",
                            },
                            "schema": {
                                "type": "string",
                                "description": "Schema name (default: 'dbo').",
                            },
                        },
                        "required": ["table", "column"],
                    },
                ),
                types.Tool(
                    name="compare_tables",
                    description=(
                        "Compare the schema and row counts of two tables. "
                        "Reports columns only in one table, type mismatches, and whether schemas match."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table1": {
                                "type": "string",
                                "description": "First table name.",
                            },
                            "table2": {
                                "type": "string",
                                "description": "Second table name.",
                            },
                            "schema1": {
                                "type": "string",
                                "description": "Schema for the first table (default: 'dbo').",
                            },
                            "schema2": {
                                "type": "string",
                                "description": "Schema for the second table (default: 'dbo').",
                            },
                        },
                        "required": ["table1", "table2"],
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
            elif name == "describe_table":
                result = self.db.describe_table(
                    table=arguments["table"],
                    schema=arguments.get("schema", "dbo"),
                )
            elif name == "explain_query":
                result = self.db.explain_query(query=arguments["query"])
            elif name == "get_table_sample":
                result = self.db.get_table_sample(
                    table=arguments["table"],
                    schema=arguments.get("schema", "dbo"),
                    limit=arguments.get("limit", 10),
                )
            elif name == "get_column_stats":
                result = self.db.get_column_stats(
                    table=arguments["table"],
                    column=arguments["column"],
                    schema=arguments.get("schema", "dbo"),
                )
            elif name == "compare_tables":
                result = self.db.compare_tables(
                    table1=arguments["table1"],
                    table2=arguments["table2"],
                    schema1=arguments.get("schema1", "dbo"),
                    schema2=arguments.get("schema2", "dbo"),
                )
            else:
                result = {"success": False, "error": f"Unknown tool: {name}"}

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
