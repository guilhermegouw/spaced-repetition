import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "questions.db"


def get_connection():
    """
    Establish and return a connection to the SQLite database.
    If the database file does not exist, it will be created.
    """
    try:
        connection = sqlite3.connect(DB_PATH)
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        raise
