# SQL Server MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that exposes SQL Server as a tool for AI assistants (Claude, Cursor, etc.).

---

## Prerequisites

### 1. Python 3.10+
Verify with:
```bash
python3 --version
```

### 2. unixODBC (macOS)
Required by `pyodbc`:
```bash
brew install unixodbc
```

### 3. Microsoft ODBC Driver 17 for SQL Server (macOS)
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql17
```

Verify the driver is registered:
```bash
odbcinst -q -d
# Should output: [ODBC Driver 17 for SQL Server]
```

---

## Setup

### 1. Clone the repo
```bash
git clone <repo-url>
cd sql-server-mcp
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Edit `.env` and set the variables for your chosen authentication type.

#### SQL Server Login (default)
```env
SQLSERVER_HOST=your-server.database.windows.net
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=your_database
SQLSERVER_AUTH_TYPE=sql
SQLSERVER_USERNAME=your_username
SQLSERVER_PASSWORD=your_password
SQLSERVER_TRUST_SERVER_CERTIFICATE=yes
```

#### Windows Integrated Authentication
```env
SQLSERVER_HOST=your-server
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=your_database
SQLSERVER_AUTH_TYPE=windows
SQLSERVER_TRUST_SERVER_CERTIFICATE=yes
```
No username or password required — uses the current OS/AD user.

#### Azure AD Password
```env
SQLSERVER_HOST=your-server.database.windows.net
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=your_database
SQLSERVER_AUTH_TYPE=azure_ad_password
SQLSERVER_USERNAME=user@yourtenant.onmicrosoft.com
SQLSERVER_PASSWORD=your_password
SQLSERVER_TRUST_SERVER_CERTIFICATE=yes
```

#### Azure AD Integrated (SSO / Kerberos)
```env
SQLSERVER_HOST=your-server.database.windows.net
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=your_database
SQLSERVER_AUTH_TYPE=azure_ad_integrated
SQLSERVER_TRUST_SERVER_CERTIFICATE=yes
```
No credentials needed — uses the ambient Azure AD / Kerberos token.

#### Azure AD Service Principal
```env
SQLSERVER_HOST=your-server.database.windows.net
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=your_database
SQLSERVER_AUTH_TYPE=azure_ad_service_principal
SQLSERVER_CLIENT_ID=your-app-client-id
SQLSERVER_CLIENT_SECRET=your-client-secret
SQLSERVER_TRUST_SERVER_CERTIFICATE=yes
```

#### Azure AD Managed Identity (MSI)
```env
SQLSERVER_HOST=your-server.database.windows.net
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=your_database
SQLSERVER_AUTH_TYPE=azure_ad_msi
# Optional: only needed when multiple managed identities are assigned
# SQLSERVER_CLIENT_ID=your-managed-identity-client-id
SQLSERVER_TRUST_SERVER_CERTIFICATE=yes
```

#### Authentication type reference

| `SQLSERVER_AUTH_TYPE` | Required vars | Description |
|---|---|---|
| `sql` | `USERNAME`, `PASSWORD` | SQL Server login (default) |
| `windows` | — | Windows Integrated / Trusted Connection |
| `azure_ad_password` | `USERNAME`, `PASSWORD` | Azure AD user credentials |
| `azure_ad_integrated` | — | Azure AD SSO / Kerberos token |
| `azure_ad_service_principal` | `CLIENT_ID`, `CLIENT_SECRET` | App registration / service principal |
| `azure_ad_msi` | `CLIENT_ID` *(optional)* | Azure Managed Identity |

---

## MCP Client Configuration

### Cursor / Claude Desktop

Add the following to your MCP settings (e.g. `~/.cursor/mcp.json` or Claude Desktop config):

```json
{
  "mcpServers": {
    "sqlserver": {
      "command": "/path/to/sqlserver-mcp-server/venv/bin/python",
      "args": ["/path/to/sqlserver-mcp-server/sqlserver_mcp/main.py"]
    }
  }
}
```

Replace `/path/to/sqlserver-mcp-server` with the absolute path on your machine.

---

## Available Tools

### `process_req`
Execute any SQL query against the connected database.

**Input:**
| Parameter | Type   | Required | Description              |
|-----------|--------|----------|--------------------------|
| `query`   | string | Yes      | SQL query to execute     |

**Returns:**
- For `SELECT`: `columns`, `rows`, `row_count`
- For `INSERT` / `UPDATE` / `DELETE` / DDL: `rows_affected`, `message`

**Example:**
```
Query: SELECT TOP 5 * FROM dbo.Customers
```

---

### `list_tables`
List all tables in the connected database, optionally filtered by schema.

**Input:**
| Parameter | Type   | Required | Description                          |
|-----------|--------|----------|--------------------------------------|
| `schema`  | string | No       | Schema name to filter by (e.g. `dbo`) |

**Returns:** `tables` array with `schema`, `table`, and `type` fields, plus `count`.

**Example:**
```
List all tables in the dbo schema
```

---

## Project Structure

```
sqlserver-mcp-server/
├── sqlserver_mcp/
│   ├── main.py           # Entry point
│   ├── server.py         # MCP server + tool registration
│   ├── connection.py     # pyodbc connection management
│   └── tools/
│       ├── ProcessReq.py # process_req tool
│       └── ListTables.py # list_tables tool
├── requirements.txt
├── .env.example
└── README.md
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'sqlserver_mcp'`**
Run the server using the full path to the venv Python binary, not the system Python.

**`Can't open lib 'ODBC Driver 17 for SQL Server'`**
Install `unixodbc` and `msodbcsql17` as described in the Prerequisites section.

**`Library not loaded: libodbc.2.dylib`**
`unixodbc` is not installed. Run `brew install unixodbc`.

**`Connection reset by peer` / TLS handshake error**
- Ensure you are connected to the required VPN (if the server is in a private network)
- Confirm your IP is whitelisted in the server's firewall / AWS Security Group
- For Azure SQL, ensure your client IP is added under *Networking > Firewall rules*
