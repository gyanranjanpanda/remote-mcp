"""SQLite persistence implementation of the ExpenseRepository protocol."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from remote_mcp.domain.entities import Expense, ExpenseFilter, ExpenseSummary


class SQLiteExpenseRepository:
    """Thread-safe SQLite storage for expense records."""

    def __init__(self, database_path: Path | str = "expenses.db") -> None:
        self.database_path = Path(database_path)
        self._initialize_database()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        # WAL mode enables concurrent reads and writes
        connection.execute("PRAGMA journal_mode = WAL;")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize_database(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    incurred_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_expenses_category 
                ON expenses(category);
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_expenses_incurred_at 
                ON expenses(incurred_at);
                """
            )

    def add(self, expense: Expense) -> Expense:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO expenses (amount, category, description, incurred_at, created_at)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    expense.amount,
                    expense.category,
                    expense.description,
                    expense.incurred_at,
                    expense.created_at,
                ),
            )
            row_id = cursor.lastrowid
            return expense.model_copy(update={"id": row_id})

    def list(self, filter_criteria: ExpenseFilter) -> list[Expense]:
        clauses: list[str] = []
        parameters: list[str] = []

        if filter_criteria.category:
            clauses.append("category = ?")
            parameters.append(filter_criteria.category)

        if filter_criteria.start_date:
            clauses.append("incurred_at >= ?")
            parameters.append(filter_criteria.start_date)

        if filter_criteria.end_date:
            clauses.append("incurred_at <= ?")
            parameters.append(filter_criteria.end_date)

        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"""
            SELECT id, amount, category, description, incurred_at, created_at
            FROM expenses
            {where_clause}
            ORDER BY incurred_at DESC, id DESC;
        """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            rows = cursor.fetchall()
            return [
                Expense(
                    id=row["id"],
                    amount=row["amount"],
                    category=row["category"],
                    description=row["description"],
                    incurred_at=row["incurred_at"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]

    def get_by_id(self, expense_id: int) -> Expense | None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, amount, category, description, incurred_at, created_at
                FROM expenses
                WHERE id = ?;
                """,
                (expense_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Expense(
                id=row["id"],
                amount=row["amount"],
                category=row["category"],
                description=row["description"],
                incurred_at=row["incurred_at"],
                created_at=row["created_at"],
            )

    def delete(self, expense_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?;", (expense_id,))
            return cursor.rowcount > 0

    def summarize(self, category: str | None = None) -> ExpenseSummary:
        where_clause = "WHERE category = ?" if category else ""
        params = [category.strip().lower()] if category else []

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT COALESCE(SUM(amount), 0.0) as total, COUNT(*) as count
                FROM expenses
                {where_clause};
                """,
                params,
            )
            total_row = cursor.fetchone()
            total_amount = round(float(total_row["total"]), 2)
            expense_count = int(total_row["count"])

            # Category breakdown
            cursor.execute(
                f"""
                SELECT category, ROUND(SUM(amount), 2) as subtotal
                FROM expenses
                {where_clause}
                GROUP BY category
                ORDER BY subtotal DESC;
                """,
                params,
            )
            breakdown_rows = cursor.fetchall()
            category_breakdown = {
                row["category"]: float(row["subtotal"]) for row in breakdown_rows
            }

            return ExpenseSummary(
                total_amount=total_amount,
                expense_count=expense_count,
                category_breakdown=category_breakdown,
            )

    def clear(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses;")
            return cursor.rowcount
