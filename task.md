# Task Checklist: Expense Tracker MCP Server

## Architecture & Design
- [x] Create Clean Architecture specification (`architecture.md`)
- [x] Define domain entities, repository protocol, and use case boundaries

## Implementation (Ralph)
- [x] Implement domain models and protocol (`src/remote_mcp/domain/entities.py`, `src/remote_mcp/domain/repository.py`, `src/remote_mcp/domain/exceptions.py`)
- [x] Implement SQLite persistence layer (`src/remote_mcp/infrastructure/sqlite_repository.py`)
- [x] Implement application service layer (`src/remote_mcp/application/service.py`)
- [x] Replace calculator sample in `main.py` with Expense Tracker MCP tools and resources
  - Tool: `add_expense(amount, category, description, date)`
  - Tool: `list_expenses(category, start_date, end_date)`
  - Tool: `delete_expense(expense_id)`
  - Tool: `get_expense_summary(category)`
  - Tool: `clear_expenses()`
  - Resource: `expenses://summary`
  - Resource: `expenses://categories`
  - Resource: `info://server`
- [x] Update README with API details and usage instructions

## Verification & Testing (Tester)
- [x] Create unit and integration test suite (`tests/test_expense_tracker.py`)
- [x] Run automated tests via pytest (12/12 passing)
- [x] Verify FastMCP server startup and tool registration

## Review & DevOps
- [x] Human developer code quality & clean architecture boundary review
- [x] Create GitHub Actions CI workflow (`.github/workflows/ci.yml`)
- [x] Update memory log (`memory/decision_log.md`)
