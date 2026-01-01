"""Shared pytest fixtures for all tests."""

import sqlite3
from datetime import date, timedelta

import pytest

from src.models.challenge import Challenge
from src.models.mcq import MCQQuestion
from src.models.question import Question


@pytest.fixture
def test_db():
    """Create an in-memory SQLite database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Create questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            question TEXT NOT NULL,
            tags TEXT,
            last_reviewed DATE,
            interval INTEGER DEFAULT 1,
            ease_factor REAL DEFAULT 2.5
        )
    """)

    # Create challenges table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            testcases TEXT,
            language TEXT NOT NULL CHECK (language IN ('python', 'javascript')),
            tags TEXT,
            last_reviewed DATE DEFAULT CURRENT_DATE,
            interval INTEGER DEFAULT 1,
            ease_factor REAL DEFAULT 2.5
        )
    """)

    # Create mcq_questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mcq_questions (
            id INTEGER PRIMARY KEY,
            question TEXT NOT NULL,
            question_type TEXT DEFAULT 'mcq'
                CHECK (question_type IN ('mcq', 'true_false')),
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT,
            option_d TEXT,
            correct_option TEXT NOT NULL CHECK (correct_option IN ('a','b','c','d')),
            explanation_a TEXT,
            explanation_b TEXT,
            explanation_c TEXT,
            explanation_d TEXT,
            tags TEXT,
            last_reviewed DATE,
            interval INTEGER DEFAULT 1,
            ease_factor REAL DEFAULT 2.5
        )
    """)

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def sample_question():
    """Create a sample Question model."""
    return Question(
        question_text="What is the time complexity of binary search?",
        tags="algorithms, search",
        interval=1,
        ease_factor=2.5,
    )


@pytest.fixture
def sample_challenge():
    """Create a sample Challenge model."""
    return Challenge(
        title="FizzBuzz",
        description="Write a function that prints FizzBuzz",
        language="python",
        tags="loops, conditionals",
        testcases="assert fizzbuzz(15) == 'FizzBuzz'",
    )


@pytest.fixture
def sample_mcq():
    """Create a sample MCQ model."""
    return MCQQuestion(
        question="What is the output of print(2 ** 3)?",
        question_type="mcq",
        option_a="6",
        option_b="8",
        option_c="9",
        option_d="None",
        correct_option="b",
        explanation_a="Incorrect: 2 * 3 = 6, but ** is exponentiation",
        explanation_b="Correct: 2 ** 3 = 2^3 = 8",
        explanation_c="Incorrect: 3 ** 2 = 9",
        explanation_d="Incorrect: The expression returns an integer",
        tags="python, operators",
    )


@pytest.fixture
def sample_true_false():
    """Create a sample True/False MCQ model."""
    return MCQQuestion(
        question="Python is a compiled language",
        question_type="true_false",
        option_a="True",
        option_b="False",
        correct_option="b",
        explanation_a="Incorrect: Python is interpreted",
        explanation_b="Correct: Python is an interpreted language",
        tags="python, basics",
    )


@pytest.fixture
def today():
    """Return today's date."""
    return date.today()


@pytest.fixture
def yesterday():
    """Return yesterday's date."""
    return date.today() - timedelta(days=1)


@pytest.fixture
def one_week_ago():
    """Return date from one week ago."""
    return date.today() - timedelta(days=7)
