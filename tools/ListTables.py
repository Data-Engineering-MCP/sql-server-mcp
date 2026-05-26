class ListTablesMixin:
    def list_tables(self, schema: str = None) -> dict:
        """List all tables in the database, optionally filtered by schema."""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if schema:
                cursor.execute(
                    """
                    SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = ?
                    ORDER BY TABLE_SCHEMA, TABLE_NAME
                    """,
                    schema,
                )
            else:
                cursor.execute(
                    """
                    SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
                    FROM INFORMATION_SCHEMA.TABLES
                    ORDER BY TABLE_SCHEMA, TABLE_NAME
                    """
                )

            tables = [
                {
                    "schema": row[0],
                    "table": row[1],
                    "type": row[2],
                }
                for row in cursor.fetchall()
            ]

            return {
                "success": True,
                "count": len(tables),
                "tables": tables,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "tables": []}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
