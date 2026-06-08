import os
import pyodbc
from dotenv import load_dotenv
from tools.ProcessReq import ProcessReqMixin
from tools.ListTables import ListTablesMixin
from tools.DescribeTable import DescribeTableMixin
from tools.ExplainQuery import ExplainQueryMixin
from tools.GetTableSample import GetTableSampleMixin
from tools.GetColumnStats import GetColumnStatsMixin
from tools.CompareTables import CompareTablesMixin

load_dotenv()

# Supported auth types:
#   sql                    - SQL Server login (username + password)
#   windows                - Windows Integrated / Trusted Connection
#   azure_ad_password      - Azure AD username + password
#   azure_ad_integrated    - Azure AD Integrated (SSO / Kerberos)
#   azure_ad_service_principal - Azure AD Service Principal (client_id + client_secret)
#   azure_ad_msi           - Azure AD Managed Identity


class SQLServerConnection(ProcessReqMixin, ListTablesMixin, DescribeTableMixin, ExplainQueryMixin, GetTableSampleMixin, GetColumnStatsMixin, CompareTablesMixin):
    def __init__(self):
        self.host = os.getenv("SQLSERVER_HOST", "localhost")
        self.port = os.getenv("SQLSERVER_PORT", "1433")
        self.database = os.getenv("SQLSERVER_DATABASE")
        self.trust_cert = os.getenv("SQLSERVER_TRUST_SERVER_CERTIFICATE", "yes")
        self.auth_type = os.getenv("SQLSERVER_AUTH_TYPE", "sql").lower()

        if not self.database:
            raise ValueError("SQLSERVER_DATABASE must be set in the environment.")

        if self.auth_type == "sql":
            self.username = os.getenv("SQLSERVER_USERNAME")
            self.password = os.getenv("SQLSERVER_PASSWORD")
            if not all([self.username, self.password]):
                raise ValueError(
                    "SQLSERVER_USERNAME and SQLSERVER_PASSWORD must be set "
                    "when SQLSERVER_AUTH_TYPE=sql."
                )

        elif self.auth_type == "windows":
            pass  # No credentials needed; uses the current OS user

        elif self.auth_type == "azure_ad_password":
            self.username = os.getenv("SQLSERVER_USERNAME")
            self.password = os.getenv("SQLSERVER_PASSWORD")
            if not all([self.username, self.password]):
                raise ValueError(
                    "SQLSERVER_USERNAME and SQLSERVER_PASSWORD must be set "
                    "when SQLSERVER_AUTH_TYPE=azure_ad_password."
                )

        elif self.auth_type == "azure_ad_integrated":
            pass  # Uses ambient Azure AD / Kerberos token

        elif self.auth_type == "azure_ad_service_principal":
            self.username = os.getenv("SQLSERVER_CLIENT_ID")
            self.password = os.getenv("SQLSERVER_CLIENT_SECRET")
            if not all([self.username, self.password]):
                raise ValueError(
                    "SQLSERVER_CLIENT_ID and SQLSERVER_CLIENT_SECRET must be set "
                    "when SQLSERVER_AUTH_TYPE=azure_ad_service_principal."
                )

        elif self.auth_type == "azure_ad_msi":
            # Optionally scope to a specific managed identity via CLIENT_ID
            self.username = os.getenv("SQLSERVER_CLIENT_ID", "")

        else:
            raise ValueError(
                f"Unsupported SQLSERVER_AUTH_TYPE '{self.auth_type}'. "
                "Valid values: sql, windows, azure_ad_password, "
                "azure_ad_integrated, azure_ad_service_principal, azure_ad_msi."
            )

    def get_connection(self) -> pyodbc.Connection:
        base = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.host},{self.port};"
            f"DATABASE={self.database};"
            f"TrustServerCertificate={self.trust_cert};"
        )

        if self.auth_type == "sql":
            conn_str = base + (
                f"UID={self.username};"
                f"PWD={self.password};"
                f"Encrypt=no;"
            )

        elif self.auth_type == "windows":
            conn_str = base + "Trusted_Connection=yes;"

        elif self.auth_type == "azure_ad_password":
            conn_str = base + (
                f"Authentication=ActiveDirectoryPassword;"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"Encrypt=yes;"
            )

        elif self.auth_type == "azure_ad_integrated":
            conn_str = base + (
                "Authentication=ActiveDirectoryIntegrated;"
                "Encrypt=yes;"
            )

        elif self.auth_type == "azure_ad_service_principal":
            conn_str = base + (
                f"Authentication=ActiveDirectoryServicePrincipal;"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"Encrypt=yes;"
            )

        elif self.auth_type == "azure_ad_msi":
            conn_str = base + "Authentication=ActiveDirectoryMsi;Encrypt=yes;"
            if self.username:
                conn_str += f"UID={self.username};"

        return pyodbc.connect(conn_str)
