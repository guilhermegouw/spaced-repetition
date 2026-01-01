import sqlite3
from contextlib import contextmanager

from src.db.connection import get_connection


class DatabaseManager:
    """
    Database manager providing context manager for database operations.
    Handles connection lifecycle, transactions, and error handling.
    """

    @contextmanager
    def get_cursor(self):
        """
        Context manager for database operations.
        Automatically handles connection, commit, rollback, and cleanup.

        Usage:
            with db_manager.get_cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> int:
        """
        Execute a query that doesn't return data (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            Number of affected rows or lastrowid for INSERT
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    def fetch_one(self, query: str, params: tuple = ()):
        """
        Execute a query and return a single row.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            Single row or None if no results
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = ()):
        """
        Execute a query and return all rows.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            List of rows
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
