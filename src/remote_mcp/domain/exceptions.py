"""Domain exceptions for expense tracking."""


class ExpenseTrackerDomainError(Exception):
    """Base exception for expense tracker domain errors."""


class InvalidExpenseAmountError(ExpenseTrackerDomainError):
    """Raised when an expense amount is zero or negative."""

    def __init__(self, amount: float) -> None:
        super().__init__(f"Expense amount must be strictly greater than 0. Received: {amount}")


class ExpenseNotFoundError(ExpenseTrackerDomainError):
    """Raised when an expense is not found by ID."""

    def __init__(self, expense_id: int) -> None:
        super().__init__(f"Expense with ID {expense_id} not found.")


class InvalidExpenseDateError(ExpenseTrackerDomainError):
    """Raised when an expense date format is invalid."""

    def __init__(self, date_str: str) -> None:
        super().__init__(f"Invalid date format: '{date_str}'. Expected ISO format (YYYY-MM-DD).")
