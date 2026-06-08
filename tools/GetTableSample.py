def _q(name: str) -> str:
    return "[" + name.replace("]", "]]") + "]"


class GetTableSampleMixin:
    def get_table_sample(self, table: str, schema: str = "dbo", limit: int = 10) -> dict:
        """Return a sample of rows from a table (top N rows)."""
        conn = None
        cursor = None
        try:
            limit = max(1, min(int(limit), 100))
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT TOP {limit} * FROM {_q(schema)}.{_q(table)}")

            if cursor.description is None:
                return {"success": True, "rows": [], "row_count": 0, "columns": []}

            columns = [col[0] for col in cursor.description]
            rows = []
            for row in cursor.fetchall():
                rows.append(dict(zip(columns, [
                    str(v) if not isinstance(v, (int, float, bool, type(None))) else v
                    for v in row
                ])))

            return {"success": True, "table": f"{schema}.{table}", "columns": columns, "rows": rows, "row_count": len(rows)}

        except Exception as e:
            return {"success": False, "error": str(e), "rows": []}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
