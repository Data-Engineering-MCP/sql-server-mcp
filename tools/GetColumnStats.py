def _q(name: str) -> str:
    return "[" + name.replace("]", "]]") + "]"


class GetColumnStatsMixin:
    def get_column_stats(self, table: str, column: str, schema: str = "dbo") -> dict:
        """Return min, max, null count, distinct count, and row count for a column."""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            tbl = f"{_q(schema)}.{_q(table)}"
            col = _q(column)

            cursor.execute(
                f"""
                SELECT
                    COUNT(*)           AS total_rows,
                    COUNT({col})       AS non_null_count,
                    COUNT(*) - COUNT({col}) AS null_count,
                    COUNT(DISTINCT {col})   AS distinct_count,
                    CAST(MIN({col}) AS NVARCHAR(MAX)) AS min_value,
                    CAST(MAX({col}) AS NVARCHAR(MAX)) AS max_value
                FROM {tbl}
                """
            )

            row = cursor.fetchone()
            if row is None:
                return {"success": False, "error": "No data returned."}

            stats = {
                "table": f"{schema}.{table}",
                "column": column,
                "total_rows": row[0],
                "non_null_count": row[1],
                "null_count": row[2],
                "null_pct": round(row[2] / row[0] * 100, 2) if row[0] else 0,
                "distinct_count": row[3],
                "min_value": row[4],
                "max_value": row[5],
            }

            # Try average for numeric columns (fails gracefully for non-numeric)
            try:
                cursor.execute(f"SELECT AVG(CAST({col} AS FLOAT)) FROM {tbl}")
                avg_row = cursor.fetchone()
                stats["avg_value"] = round(avg_row[0], 4) if avg_row and avg_row[0] is not None else None
            except Exception:
                stats["avg_value"] = None

            return {"success": True, **stats}

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
