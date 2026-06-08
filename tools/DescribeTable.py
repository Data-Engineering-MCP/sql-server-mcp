def _q(name: str) -> str:
    return "[" + name.replace("]", "]]") + "]"


class DescribeTableMixin:
    def describe_table(self, table: str, schema: str = "dbo") -> dict:
        """Return column definitions and primary key info for a table."""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.CHARACTER_MAXIMUM_LENGTH,
                    c.NUMERIC_PRECISION,
                    c.NUMERIC_SCALE,
                    c.IS_NULLABLE,
                    c.COLUMN_DEFAULT,
                    COLUMNPROPERTY(OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME),
                                   c.COLUMN_NAME, 'IsIdentity') AS is_identity,
                    CASE WHEN kcu.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END AS is_primary_key
                FROM INFORMATION_SCHEMA.COLUMNS c
                LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                    ON tc.TABLE_SCHEMA = c.TABLE_SCHEMA
                    AND tc.TABLE_NAME  = c.TABLE_NAME
                    AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
                LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                    ON kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
                    AND kcu.COLUMN_NAME    = c.COLUMN_NAME
                WHERE c.TABLE_SCHEMA = ? AND c.TABLE_NAME = ?
                ORDER BY c.ORDINAL_POSITION
                """,
                schema,
                table,
            )

            columns = []
            for row in cursor.fetchall():
                col_name, data_type, char_len, num_prec, num_scale, nullable, default, is_identity, is_pk = row
                if char_len is not None:
                    type_str = f"{data_type}({char_len})"
                elif num_prec is not None and num_scale is not None and data_type in ("decimal", "numeric"):
                    type_str = f"{data_type}({num_prec},{num_scale})"
                else:
                    type_str = data_type
                columns.append({
                    "column": col_name,
                    "type": type_str,
                    "nullable": nullable == "YES",
                    "default": default,
                    "is_identity": bool(is_identity),
                    "is_primary_key": bool(is_pk),
                })

            return {"success": True, "table": f"{schema}.{table}", "columns": columns, "column_count": len(columns)}

        except Exception as e:
            return {"success": False, "error": str(e), "columns": []}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
