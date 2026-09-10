"""Application service orchestrating expense domain operations."""

from datetime import date, datetime
from remote_mcp.domain.entities import Expense, ExpenseFilter, ExpenseSummary
from remote_mcp.domain.exceptions import (
    ExpenseNotFoundError,
    InvalidExpenseAmountError,
    InvalidExpenseDateError,
)
from remote_mcp.domain.repository import ExpenseRepository


class ExpenseTrackerService:
    """Coordinates business logic and data access for expense tracking."""

    def __init__(self, repository: ExpenseRepository) -> None:
        self._repository = repository

    def _validate_date_format(self, date_string: str) -> str:
        try:
            parsed = datetime.strptime(date_string.strip(), "%Y-%m-%d").date()
            return parsed.isoformat()
        except ValueError as err:
            raise InvalidExpenseDateError(date_string) from err

    def record_expense(
        self,
        amount: float,
        category: str,
        description: str,
        incurred_at: str | None = None,
    ) -> Expense:
        if amount <= 0:
            raise InvalidExpenseAmountError(amount)

        resolved_date = (
            self._validate_date_format(incurred_at)
            if incurred_at is not None
            else date.today().isoformat()
        )

        expense = Expense(
            amount=round(float(amount), 2),
            category=category,
            description=description,
            incurred_at=resolved_date,
        )
        return self._repository.add(expense)

    def list_expenses(
        self,
        category: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[Expense]:
        sanitized_start = (
            self._validate_date_format(start_date) if start_date is not None else None
        )
        sanitized_end = (
            self._validate_date_format(end_date) if end_date is not None else None
        )

        filter_criteria = ExpenseFilter(
            category=category,
            start_date=sanitized_start,
            end_date=sanitized_end,
        )
        return self._repository.list(filter_criteria)

    def delete_expense(self, expense_id: int) -> bool:
        deleted = self._repository.delete(expense_id)
        if not deleted:
            raise ExpenseNotFoundError(expense_id)
        return True

    def get_summary(self, category: str | None = None) -> ExpenseSummary:
        return self._repository.summarize(category)

    def clear_all_expenses(self) -> int:
        return self._repository.clear()
