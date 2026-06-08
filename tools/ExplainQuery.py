class ExplainQueryMixin:
    def explain_query(self, query: str) -> dict:
        """Return the estimated execution plan for a query without executing it."""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SET SHOWPLAN_ALL ON")
            cursor.execute(query)

            plan = []
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    plan.append(dict(zip(columns, [
                        str(v) if v is not None else None for v in row
                    ])))

            return {
                "success": True,
                "note": "Estimated execution plan — query was NOT executed.",
                "plan": plan,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "plan": []}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
