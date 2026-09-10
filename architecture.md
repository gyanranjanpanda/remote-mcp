# Architecture: Expense Tracker MCP Server

## Domain Entities
- `Expense`: Identity-based core entity (`id: int | None`, `amount: Decimal`, `category: str`, `description: str`, `incurred_at: datetime`, `created_at: datetime`).
- `ExpenseSummary`: Aggregated value object representing total expenses, count, and category breakdown.
- `ExpenseFilter`: Query specification object supporting category filtering and date ranges.

## Use Cases
- `RecordExpenseUseCase`: Validates amount and metadata, persists the expense.
- `ListExpensesUseCase`: Retrieves expenses filtered by category and date interval.
- `DeleteExpenseUseCase`: Removes an expense by its unique identifier.
- `SummarizeExpensesUseCase`: Computes total spending and category metrics.
- `ClearExpensesUseCase`: Resets/clears expense ledger records.

## Layer Map
| Layer | Modules | Depends On | Purpose |
|-------|---------|------------|---------|
| `domain` | `domain.entities`, `domain.interfaces` | None | Pure business logic, entity validation, repository interface |
| `application` | `application.use_cases`, `application.dtos` | `domain` | Orchestrates operations across domain entities and repositories |
| `infrastructure` | `infrastructure.repositories.sqlite` | `domain` | Implements `ExpenseRepository` via standard library SQLite |
| `interfaces` | `main.py` (FastMCP Server) | `application`, `domain` | Exposes MCP tools and resources via FastMCP HTTP transport |

## Interface Contracts

### `ExpenseRepository` (Protocol in `domain.interfaces`)
- `add(expense: Expense) -> Expense`: Persists an expense and assigns identity.
- `list(filter_criteria: ExpenseFilter) -> list[Expense]`: Queries expenses matching criteria.
- `get_by_id(expense_id: int) -> Expense | None`: Retrieves specific expense by ID.
- `delete(expense_id: int) -> bool`: Deletes an expense by ID, returns True if deleted.
- `summarize(category: str | None = None) -> ExpenseSummary`: Computes aggregate metrics.
- `clear() -> int`: Removes all recorded expenses.

## Target Folder Structure
```
/Users/mac/Desktop/remote_mcp/
├── main.py                          # FastMCP entrypoint with MCP tools & resources
├── src/
│   └── remote_mcp/
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── entities.py          # Expense, ExpenseSummary, ExpenseFilter
│       │   └── repository.py        # ExpenseRepository protocol
│       ├── application/
│       │   ├── __init__.py
│       │   └── service.py           # ExpenseTrackerService (orchestration)
│       └── infrastructure/
│           ├── __init__.py
│           └── sqlite_repository.py # SQLite implementation of ExpenseRepository
└── tests/
    └── test_expense_tracker.py      # Unit and integration test suite
```
