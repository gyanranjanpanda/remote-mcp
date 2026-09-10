"""Repository interface contract for expense persistence."""

from typing import Protocol, runtime_checkable
from remote_mcp.domain.entities import Expense, ExpenseFilter, ExpenseSummary


@runtime_checkable
class ExpenseRepository(Protocol):
    """Contract for data access operations on Expense entities."""

    def add(self, expense: Expense) -> Expense:
        """Persist a new expense and assign its identifier."""
        ...

    def list(self, filter_criteria: ExpenseFilter) -> list[Expense]:
        """Retrieve stored expenses conforming to filter parameters."""
        ...

    def get_by_id(self, expense_id: int) -> Expense | None:
        """Retrieve an expense record by its unique database primary key."""
        ...

    def delete(self, expense_id: int) -> bool:
        """Remove an expense record by identifier. Returns True if deleted, False otherwise."""
        ...

    def summarize(self, category: str | None = None) -> ExpenseSummary:
        """Calculate aggregated expense metrics across stored records."""
        ...

    def clear(self) -> int:
        """Remove all expense entries. Returns the number of removed rows."""
        ...
