# Expense Tracker Remote MCP Server

A production-grade Model Context Protocol (MCP) server for recording, tracking, filtering, and analyzing personal and organizational expenses. Built with [FastMCP](https://github.com/jlowin/fastmcp) and Clean Architecture principles.

## Architecture Overview

```
src/remote_mcp/
├── domain/                  # Entities, Value Objects, Repository Contracts, Exceptions
│   ├── entities.py          # Expense, ExpenseSummary, ExpenseFilter
│   ├── exceptions.py        # Typed Domain Exceptions
│   └── repository.py        # ExpenseRepository Protocol
├── application/             # Use Case Orchestration & Business Rules
│   └── service.py           # ExpenseTrackerService
└── infrastructure/          # Data Access & External Integrations
    └── sqlite_repository.py # SQLite with WAL mode & parameterized queries
main.py                      # FastMCP Entrypoint exposing Tools & Resources
```

## Available Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `add_expense` | `amount` (float), `category` (str), `description` (str), `date` (str, optional) | Records a new expense with currency validation and category normalization. |
| `list_expenses` | `category` (str, optional), `start_date` (str, optional), `end_date` (str, optional) | Queries stored expenses by category and date range (`YYYY-MM-DD`). |
| `delete_expense` | `expense_id` (int) | Deletes an expense by its unique identifier. |
| `get_expense_summary` | `category` (str, optional) | Computes total spending, record count, and category breakdown. |
| `clear_expenses` | None | Clears all records from the database. |

## Available Resources

- `expenses://summary`: JSON overview of total expenditure, record count, and category breakdown.
- `expenses://categories`: JSON mapping of categories to total spending.
- `info://server`: Server metadata and active capabilities.

## Getting Started

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

### Installation
```bash
uv sync
```

### Running the Server

Run directly with Python (HTTP transport on `0.0.0.0:8080`):
```bash
uv run python main.py
```

Or run via FastMCP CLI:
```bash
uv run fastmcp run main.py --transport http --host 0.0.0.0 --port 8080
```

### Testing & Verification

Run the test suite:
```bash
uv run pytest -v
```

### Using with MCP Inspector

1. Start the inspector:
   ```bash
   npx @modelcontextprotocol/inspector
   ```
2. In the inspector UI:
   - Select **Streamable HTTP**
   - Connect to `http://127.0.0.1:8080/mcp`
