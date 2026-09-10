# Decision Log

## 2026-09-11 Decision: Transition from Sample Calculator to Expense Tracker MCP Server
- Context: The user requested replacing sample calculator code with a dedicated Expense Tracker MCP server, removing unnecessary sample code.
- Decision: Adopt Clean Architecture layering (`domain/`, `application/`, `infrastructure/`, `interfaces/`) backed by a persistent SQLite database (`expenses.db`), exposing dedicated MCP tools (`add_expense`, `list_expenses`, `delete_expense`, `get_expense_summary`, `clear_expenses`) and resources (`expenses://summary`, `expenses://categories`).
- Rationale: SQLite provides zero external dependencies while offering reliable local ACID persistence. Clean Architecture keeps business validation decoupled from FastMCP framework specifics.
- Alternatives considered: In-memory dictionary (rejected due to data loss upon server restart), JSON file persistence (rejected due to lack of concurrency and querying capabilities).
