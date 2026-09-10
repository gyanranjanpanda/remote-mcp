"""Unit and integration test suite for the Expense Tracker MCP server."""

import pytest
from pathlib import Path
from remote_mcp.application.service import ExpenseTrackerService
from remote_mcp.domain.entities import Expense, ExpenseFilter
from remote_mcp.domain.exceptions import (
    ExpenseNotFoundError,
    InvalidExpenseAmountError,
    InvalidExpenseDateError,
)
from remote_mcp.infrastructure.sqlite_repository import SQLiteExpenseRepository
from main import (
    add_expense,
    clear_expenses,
    delete_expense,
    get_expense_summary,
    list_expenses,
)


@pytest.fixture
def test_database_path(tmp_path: Path) -> Path:
    """Fixture providing an isolated temporary database path."""
    return tmp_path / "test_expenses.db"


@pytest.fixture
def repository(test_database_path: Path) -> SQLiteExpenseRepository:
    """Fixture providing a fresh SQLite repository instance."""
    return SQLiteExpenseRepository(database_path=test_database_path)


@pytest.fixture
def service(repository: SQLiteExpenseRepository) -> ExpenseTrackerService:
    """Fixture providing an ExpenseTrackerService wired to the test repository."""
    return ExpenseTrackerService(repository=repository)


# --------------------------------------------------------------------------
# Domain Entity Tests
# --------------------------------------------------------------------------


def test_expense_entity_normalizes_category() -> None:
    expense = Expense(
        amount=19.99,
        category="  Food & Dining  ",
        description="Lunch meeting",
        incurred_at="2026-09-11",
    )
    assert expense.category == "food & dining"
    assert expense.amount == 19.99


def test_expense_entity_rejects_negative_or_zero_amount() -> None:
    with pytest.raises(ValueError):
        Expense(
            amount=-5.0,
            category="travel",
            description="Ticket",
            incurred_at="2026-09-11",
        )

    with pytest.raises(ValueError):
        Expense(
            amount=0.0,
            category="travel",
            description="Ticket",
            incurred_at="2026-09-11",
        )


def test_expense_entity_rejects_empty_strings() -> None:
    with pytest.raises(ValueError):
        Expense(
            amount=10.0,
            category="   ",
            description="Test",
            incurred_at="2026-09-11",
        )

    with pytest.raises(ValueError):
        Expense(
            amount=10.0,
            category="valid",
            description="   ",
            incurred_at="2026-09-11",
        )


# --------------------------------------------------------------------------
# Repository Integration Tests
# --------------------------------------------------------------------------


def test_repository_add_and_get_by_id(repository: SQLiteExpenseRepository) -> None:
    new_expense = Expense(
        amount=45.50,
        category="groceries",
        description="Weekly grocery shopping",
        incurred_at="2026-09-10",
    )
    saved = repository.add(new_expense)
    assert saved.id is not None
    assert saved.id > 0

    retrieved = repository.get_by_id(saved.id)
    assert retrieved is not None
    assert retrieved.id == saved.id
    assert retrieved.amount == 45.50
    assert retrieved.category == "groceries"
    assert retrieved.description == "Weekly grocery shopping"


def test_repository_list_with_category_filter(repository: SQLiteExpenseRepository) -> None:
    repository.add(Expense(amount=10.0, category="books", description="Python book", incurred_at="2026-09-01"))
    repository.add(Expense(amount=20.0, category="coffee", description="Espresso", incurred_at="2026-09-02"))
    repository.add(Expense(amount=30.0, category="books", description="Go book", incurred_at="2026-09-03"))

    filtered_books = repository.list(ExpenseFilter(category="books"))
    assert len(filtered_books) == 2
    assert all(item.category == "books" for item in filtered_books)


def test_repository_list_with_date_filter(repository: SQLiteExpenseRepository) -> None:
    repository.add(Expense(amount=15.0, category="food", description="Meal 1", incurred_at="2026-09-01"))
    repository.add(Expense(amount=25.0, category="food", description="Meal 2", incurred_at="2026-09-05"))
    repository.add(Expense(amount=35.0, category="food", description="Meal 3", incurred_at="2026-09-10"))

    filtered_dates = repository.list(ExpenseFilter(start_date="2026-09-02", end_date="2026-09-06"))
    assert len(filtered_dates) == 1
    assert filtered_dates[0].amount == 25.0


def test_repository_delete_and_clear(repository: SQLiteExpenseRepository) -> None:
    exp1 = repository.add(Expense(amount=12.0, category="snack", description="Chips", incurred_at="2026-09-01"))
    exp2 = repository.add(Expense(amount=18.0, category="snack", description="Cookies", incurred_at="2026-09-02"))

    assert repository.delete(exp1.id) is True
    assert repository.get_by_id(exp1.id) is None
    assert repository.delete(9999) is False

    cleared_count = repository.clear()
    assert cleared_count == 1
    assert len(repository.list(ExpenseFilter())) == 0


def test_repository_summarize_metrics(repository: SQLiteExpenseRepository) -> None:
    repository.add(Expense(amount=50.0, category="utilities", description="Electricity", incurred_at="2026-09-01"))
    repository.add(Expense(amount=30.0, category="utilities", description="Water", incurred_at="2026-09-02"))
    repository.add(Expense(amount=20.0, category="food", description="Dinner", incurred_at="2026-09-03"))

    summary = repository.summarize()
    assert summary.total_amount == 100.0
    assert summary.expense_count == 3
    assert summary.category_breakdown["utilities"] == 80.0
    assert summary.category_breakdown["food"] == 20.0

    category_summary = repository.summarize(category="utilities")
    assert category_summary.total_amount == 80.0
    assert category_summary.expense_count == 2


# --------------------------------------------------------------------------
# Service Layer Tests
# --------------------------------------------------------------------------


def test_service_record_expense_validates_amount(service: ExpenseTrackerService) -> None:
    with pytest.raises(InvalidExpenseAmountError):
        service.record_expense(amount=-10.0, category="food", description="Negative amount")


def test_service_record_expense_validates_date_format(service: ExpenseTrackerService) -> None:
    with pytest.raises(InvalidExpenseDateError):
        service.record_expense(
            amount=20.0,
            category="food",
            description="Bad date",
            incurred_at="11-09-2026",
        )


def test_service_delete_nonexistent_raises_error(service: ExpenseTrackerService) -> None:
    with pytest.raises(ExpenseNotFoundError):
        service.delete_expense(expense_id=12345)


# --------------------------------------------------------------------------
# MCP Tool Handler Tests
# --------------------------------------------------------------------------


def test_mcp_tool_handlers_end_to_end() -> None:
    clear_expenses()

    add_response = add_expense(
        amount=42.50,
        category="Tech",
        description="USB Cable",
        date="2026-09-11",
    )
    assert add_response["status"] == "success"
    recorded_id = add_response["expense"]["id"]

    expense_list = list_expenses(category="tech")
    assert len(expense_list) >= 1
    assert expense_list[0]["id"] == recorded_id

    summary_response = get_expense_summary()
    assert summary_response["total_amount"] >= 42.50
    assert "tech" in summary_response["category_breakdown"]

    delete_response = delete_expense(expense_id=recorded_id)
    assert delete_response["status"] == "success"
