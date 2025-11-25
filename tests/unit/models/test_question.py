"""Tests for the Question model."""

from datetime import date

import pytest
from pydantic import ValidationError

from src.models.question import Question


class TestQuestionCreation:
    """Tests for Question model creation and validation."""

    def test_valid_question_with_all_fields(self):
        """Create a question with all fields specified."""
        q = Question(
            id=1,
            question_text="What is polymorphism?",
            tags="oop, python",
            last_reviewed=date(2024, 1, 15),
            interval=7,
            ease_factor=2.5,
        )
        assert q.id == 1
        assert q.question_text == "What is polymorphism?"
        assert q.tags == "oop, python"
        assert q.last_reviewed == date(2024, 1, 15)
        assert q.interval == 7
        assert q.ease_factor == 2.5

    def test_valid_question_minimal(self):
        """Create a question with only required fields."""
        q = Question(question_text="What is a list?")
        assert q.question_text == "What is a list?"
        assert q.id is None
        assert q.tags is None
        assert q.last_reviewed is None
        assert q.interval == 1
        assert q.ease_factor == 2.5

    def test_empty_question_text_fails(self):
        """Empty question text should raise ValidationError."""
        with pytest.raises(ValidationError):
            Question(question_text="")

    def test_whitespace_only_question_text_fails(self):
        """Whitespace-only question text should raise ValidationError."""
        with pytest.raises(ValidationError):
            Question(question_text="   ")

    def test_question_text_gets_stripped(self):
        """Question text should be stripped of leading/trailing whitespace."""
        q = Question(question_text="  What is Python?  ")
        assert q.question_text == "What is Python?"


class TestQuestionTags:
    """Tests for tag handling in Question model."""

    def test_tags_normalization(self):
        """Tags should be stripped of whitespace."""
        q = Question(question_text="Test", tags="  python, oop  ")
        assert q.tags == "python, oop"

    def test_tags_empty_string_preserved(self):
        """Empty string tags are preserved (validator only strips)."""
        q = Question(question_text="Test", tags="")
        assert q.tags == ""

    def test_tags_none_when_whitespace_only(self):
        """Whitespace-only tags should become None."""
        q = Question(question_text="Test", tags="   ")
        assert q.tags is None

    def test_tags_optional(self):
        """Tags are optional."""
        q = Question(question_text="Test")
        assert q.tags is None


class TestQuestionSM2Fields:
    """Tests for SM-2 algorithm fields."""

    def test_default_interval(self):
        """Default interval should be 1."""
        q = Question(question_text="Test")
        assert q.interval == 1

    def test_default_ease_factor(self):
        """Default ease factor should be 2.5."""
        q = Question(question_text="Test")
        assert q.ease_factor == 2.5

    def test_interval_minimum_bound(self):
        """Interval must be at least 1."""
        with pytest.raises(ValidationError):
            Question(question_text="Test", interval=0)

    def test_ease_factor_minimum_bound(self):
        """Ease factor must be at least 1.3."""
        with pytest.raises(ValidationError):
            Question(question_text="Test", ease_factor=1.2)

    def test_ease_factor_maximum_bound(self):
        """Ease factor must be at most 3.0."""
        with pytest.raises(ValidationError):
            Question(question_text="Test", ease_factor=3.1)

    def test_valid_ease_factor_bounds(self):
        """Ease factor at boundaries should work."""
        q1 = Question(question_text="Test", ease_factor=1.3)
        assert q1.ease_factor == 1.3

        q2 = Question(question_text="Test", ease_factor=3.0)
        assert q2.ease_factor == 3.0


class TestQuestionSerialization:
    """Tests for Question model serialization."""

    def test_model_dump(self):
        """model_dump() should return a dictionary."""
        q = Question(
            question_text="What is Python?",
            tags="basics",
            interval=3,
            ease_factor=2.3,
        )
        data = q.model_dump()
        assert isinstance(data, dict)
        assert data["question_text"] == "What is Python?"
        assert data["tags"] == "basics"
        assert data["interval"] == 3
        assert data["ease_factor"] == 2.3

    def test_str_representation(self):
        """String representation should show id and truncated text."""
        q = Question(id=42, question_text="Short question")
        string = str(q)
        assert "42" in string
        assert "Short question" in string

    def test_str_representation_long_text(self):
        """Long question text should be truncated in string repr."""
        long_text = "A" * 100
        q = Question(question_text=long_text)
        string = str(q)
        assert "..." in string
        assert len(string) < len(long_text) + 50


class TestQuestionWithId:
    """Tests for Question with ID field."""

    def test_question_with_id(self):
        """Question can have an ID."""
        q = Question(id=123, question_text="Test")
        assert q.id == 123

    def test_question_without_id(self):
        """Question ID defaults to None."""
        q = Question(question_text="Test")
        assert q.id is None
