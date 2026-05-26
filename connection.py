import os
import pyodbc
from dotenv import load_dotenv
from sqlserver_mcp.tools.ProcessReq import ProcessReqMixin

load_dotenv()


class SQLServerConnection(ProcessReqMixin):
    def __init__(self):
        self.host = os.getenv("SQLSERVER_HOST", "localhost")
        self.port = os.getenv("SQLSERVER_PORT", "1433")
        self.database = os.getenv("SQLSERVER_DATABASE")
        self.username = os.getenv("SQLSERVER_USERNAME")
        self.password = os.getenv("SQLSERVER_PASSWORD")
        self.trust_cert = os.getenv("SQLSERVER_TRUST_SERVER_CERTIFICATE", "yes")

        if not all([self.database, self.username, self.password]):
            raise ValueError(
                "SQLSERVER_DATABASE, SQLSERVER_USERNAME, and SQLSERVER_PASSWORD "
                "must be set in the environment."
            )

    def get_connection(self) -> pyodbc.Connection:
        connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.host},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"TrustServerCertificate={self.trust_cert};"
        )
        return pyodbc.connect(connection_string)
