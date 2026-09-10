"""Expense Tracker Remote MCP Server."""

import json
from pathlib import Path
from fastmcp import FastMCP
from remote_mcp.application.service import ExpenseTrackerService
from remote_mcp.domain.exceptions import (
    ExpenseNotFoundError,
    ExpenseTrackerDomainError,
)
from remote_mcp.infrastructure.sqlite_repository import SQLiteExpenseRepository

# Initialize persistence and service orchestration
database_file = Path("expenses.db")
repository = SQLiteExpenseRepository(database_path=database_file)
expense_service = ExpenseTrackerService(repository=repository)

# Create FastMCP server instance
mcp = FastMCP("Expense Tracker Server")


@mcp.tool
def add_expense(
    amount: float,
    category: str,
    description: str,
    date: str | None = None,
) -> dict:
    """Record a new financial expense into the tracker.

    Args:
        amount: Numerical cost of the expense (must be greater than 0).
        category: Expense classification (e.g., 'food', 'travel', 'utilities', 'software').
        description: Short explanation or notes about the purchase.
        date: Optional purchase date in 'YYYY-MM-DD' format. Defaults to today.

    Returns:
        Dictionary detailing the newly recorded expense including its unique ID.
    """
    try:
        recorded = expense_service.record_expense(
            amount=amount,
            category=category,
            description=description,
            incurred_at=date,
        )
        return {
            "status": "success",
            "message": "Expense recorded successfully",
            "expense": recorded.model_dump(),
        }
    except ExpenseTrackerDomainError as err:
        return {"status": "error", "message": str(err)}


@mcp.tool
def list_expenses(
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict]:
    """Retrieve filtered expense records from the database.

    Args:
        category: Optional category filter (e.g., 'food').
        start_date: Optional inclusive start date in 'YYYY-MM-DD' format.
        end_date: Optional inclusive end date in 'YYYY-MM-DD' format.

    Returns:
        List of expense dictionaries matching the search criteria.
    """
    try:
        expenses = expense_service.list_expenses(
            category=category,
            start_date=start_date,
            end_date=end_date,
        )
        return [item.model_dump() for item in expenses]
    except ExpenseTrackerDomainError as err:
        return [{"status": "error", "message": str(err)}]


@mcp.tool
def delete_expense(expense_id: int) -> dict:
    """Delete an expense record by its unique database ID.

    Args:
        expense_id: The integer ID of the expense to remove.

    Returns:
        Confirmation status message.
    """
    try:
        expense_service.delete_expense(expense_id=expense_id)
        return {
            "status": "success",
            "message": f"Expense ID {expense_id} deleted successfully",
        }
    except ExpenseNotFoundError as err:
        return {"status": "error", "message": str(err)}


@mcp.tool
def get_expense_summary(category: str | None = None) -> dict:
    """Compute aggregate spending totals and category breakdown.

    Args:
        category: Optional category filter to compute metrics specifically for that category.

    Returns:
        Summary metrics including total amount spent, expense count, and category breakdown.
    """
    summary = expense_service.get_summary(category=category)
    return summary.model_dump()


@mcp.tool
def clear_expenses() -> dict:
    """Permanently delete all recorded expenses from the database.

    Returns:
        Status message with count of cleared records.
    """
    count = expense_service.clear_all_expenses()
    return {
        "status": "success",
        "message": f"All expenses cleared. Total records removed: {count}",
    }


@mcp.resource("expenses://summary")
def get_summary_resource() -> str:
    """Resource returning aggregate financial spending overview."""
    summary = expense_service.get_summary()
    return json.dumps(summary.model_dump(), indent=2)


@mcp.resource("expenses://categories")
def get_categories_resource() -> str:
    """Resource returning category list and subtotal breakdown."""
    summary = expense_service.get_summary()
    return json.dumps(summary.category_breakdown, indent=2)


@mcp.resource("info://server")
def server_info() -> str:
    """Resource returning server metadata and available capabilities."""
    info = {
        "name": "Expense Tracker Server",
        "version": "1.0.0",
        "description": "Production MCP server for tracking and analyzing financial expenditures",
        "tools": [
            "add_expense",
            "list_expenses",
            "delete_expense",
            "get_expense_summary",
            "clear_expenses",
        ],
        "resources": [
            "expenses://summary",
            "expenses://categories",
            "info://server",
        ],
    }
    return json.dumps(info, indent=2)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8080)
