class ProcessReqMixin:
    def process_req(self, query: str) -> dict:
        """Execute a SQL query against SQL Server and return the results."""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)

            # DDL / DML statements (no result set)
            if cursor.description is None:
                conn.commit()
                return {
                    "success": True,
                    "rows_affected": cursor.rowcount,
                    "message": "Query executed successfully.",
                    "columns": [],
                    "rows": [],
                }

            columns = [col[0] for col in cursor.description]
            rows = []
            for row in cursor.fetchall():
                rows.append(dict(zip(columns, [
                    str(v) if not isinstance(v, (int, float, bool, type(None))) else v
                    for v in row
                ])))

            return {
                "success": True,
                "row_count": len(rows),
                "columns": columns,
                "rows": rows,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "columns": [],
                "rows": [],
            }
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
