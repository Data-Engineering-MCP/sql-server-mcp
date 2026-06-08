class CompareTablesMixin:
    def compare_tables(
        self,
        table1: str,
        table2: str,
        schema1: str = "dbo",
        schema2: str = "dbo",
    ) -> dict:
        """Compare schema and row counts of two tables."""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            def get_schema(schema, table):
                cursor.execute(
                    """
                    SELECT COLUMN_NAME, DATA_TYPE,
                           CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE,
                           IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                    ORDER BY ORDINAL_POSITION
                    """,
                    schema, table,
                )
                return {
                    row[0]: {
                        "data_type": row[1],
                        "char_max_length": row[2],
                        "numeric_precision": row[3],
                        "numeric_scale": row[4],
                        "nullable": row[5],
                    }
                    for row in cursor.fetchall()
                }

            def get_row_count(schema, table):
                cursor.execute(
                    f"SELECT COUNT(*) FROM [{schema.replace(']',']]')}].[{table.replace(']',']]')}]"
                )
                return cursor.fetchone()[0]

            cols1 = get_schema(schema1, table1)
            cols2 = get_schema(schema2, table2)

            only_in_1 = [c for c in cols1 if c not in cols2]
            only_in_2 = [c for c in cols2 if c not in cols1]
            in_both = [c for c in cols1 if c in cols2]
            type_mismatches = [
                {
                    "column": c,
                    f"{schema1}.{table1}": cols1[c]["data_type"],
                    f"{schema2}.{table2}": cols2[c]["data_type"],
                }
                for c in in_both
                if cols1[c]["data_type"] != cols2[c]["data_type"]
            ]

            rows1 = get_row_count(schema1, table1)
            rows2 = get_row_count(schema2, table2)

            return {
                "success": True,
                "table1": f"{schema1}.{table1}",
                "table2": f"{schema2}.{table2}",
                "row_counts": {f"{schema1}.{table1}": rows1, f"{schema2}.{table2}": rows2},
                "column_counts": {f"{schema1}.{table1}": len(cols1), f"{schema2}.{table2}": len(cols2)},
                "columns_only_in_table1": only_in_1,
                "columns_only_in_table2": only_in_2,
                "type_mismatches": type_mismatches,
                "schemas_match": not only_in_1 and not only_in_2 and not type_mismatches,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
