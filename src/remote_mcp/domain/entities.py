"""Domain models and value objects for the Expense Tracker."""

from datetime import datetime, timezone
from typing import Self
from pydantic import BaseModel, Field, field_validator


class Expense(BaseModel):
    """Core entity representing a tracked financial expenditure."""

    id: int | None = None
    amount: float = Field(..., gt=0, description="Expense amount in primary currency units")
    category: str = Field(..., min_length=1, max_length=64, description="Expense category")
    description: str = Field(..., min_length=1, max_length=256, description="Short narrative of the expense")
    incurred_at: str = Field(..., description="Date on which the expense occurred (YYYY-MM-DD)")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp when record was entered",
    )

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("Category cannot be empty or solely whitespace.")
        return cleaned

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Description cannot be empty or solely whitespace.")
        return cleaned


class ExpenseSummary(BaseModel):
    """Aggregated financial metrics across stored expenses."""

    total_amount: float = Field(..., ge=0, description="Total amount of recorded expenses")
    expense_count: int = Field(..., ge=0, description="Total number of expenses counted")
    category_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Mapping from category names to sum spent",
    )


class ExpenseFilter(BaseModel):
    """Query parameters used to filter expense records."""

    category: str | None = None
    start_date: str | None = None
    end_date: str | None = None

    @field_validator("category")
    @classmethod
    def sanitize_category(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().lower()
        return cleaned if cleaned else None
