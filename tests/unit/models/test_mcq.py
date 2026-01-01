"""Tests for the MCQQuestion model."""

from datetime import date

import pytest
from pydantic import ValidationError

from src.models.mcq import MCQQuestion


class TestMCQCreation:
    """Tests for MCQ question creation and validation."""

    def test_valid_mcq_four_options(self):
        """Create a valid MCQ with all four options."""
        mcq = MCQQuestion(
            question="What is 2 + 2?",
            question_type="mcq",
            option_a="3",
            option_b="4",
            option_c="5",
            option_d="6",
            correct_option="b",
        )
        assert mcq.question == "What is 2 + 2?"
        assert mcq.question_type == "mcq"
        assert mcq.option_a == "3"
        assert mcq.option_b == "4"
        assert mcq.option_c == "5"
        assert mcq.option_d == "6"
        assert mcq.correct_option == "b"

    def test_valid_true_false(self):
        """Create a valid True/False question."""
        mcq = MCQQuestion(
            question="Python is interpreted",
            question_type="true_false",
            option_a="True",
            option_b="False",
            correct_option="a",
        )
        assert mcq.question_type == "true_false"
        assert mcq.option_c is None
        assert mcq.option_d is None
        assert mcq.correct_option == "a"

    def test_mcq_with_all_fields(self):
        """Create MCQ with all fields specified."""
        mcq = MCQQuestion(
            id=1,
            question="What is Python?",
            question_type="mcq",
            option_a="A snake",
            option_b="A programming language",
            option_c="A movie",
            option_d="A game",
            correct_option="b",
            explanation_a="Partially correct but not in this context",
            explanation_b="Correct! Python is a programming language",
            explanation_c="Incorrect",
            explanation_d="Incorrect",
            tags="python, basics",
            last_reviewed=date(2024, 1, 15),
            interval=3,
            ease_factor=2.3,
        )
        assert mcq.id == 1
        assert mcq.explanation_b == "Correct! Python is a programming language"
        assert mcq.tags == "python, basics"
        assert mcq.interval == 3
        assert mcq.ease_factor == 2.3


class TestMCQTypeValidation:
    """Tests for question type validation."""

    def test_mcq_requires_four_options(self):
        """MCQ type requires all four options."""
        with pytest.raises(ValidationError, match="MCQ questions require"):
            MCQQuestion(
                question="Test",
                question_type="mcq",
                option_a="A",
                option_b="B",
                correct_option="a",
            )

    def test_mcq_requires_option_c(self):
        """MCQ type requires option_c."""
        with pytest.raises(ValidationError):
            MCQQuestion(
                question="Test",
                question_type="mcq",
                option_a="A",
                option_b="B",
                option_d="D",
                correct_option="a",
            )

    def test_mcq_requires_option_d(self):
        """MCQ type requires option_d."""
        with pytest.raises(ValidationError):
            MCQQuestion(
                question="Test",
                question_type="mcq",
                option_a="A",
                option_b="B",
                option_c="C",
                correct_option="a",
            )

    def test_true_false_only_two_options(self):
        """True/False should only have options A and B."""
        with pytest.raises(ValidationError, match="True/False questions"):
            MCQQuestion(
                question="Test",
                question_type="true_false",
                option_a="True",
                option_b="False",
                option_c="Maybe",
                correct_option="a",
            )

    def test_true_false_no_option_d(self):
        """True/False should not have option D."""
        with pytest.raises(ValidationError):
            MCQQuestion(
                question="Test",
                question_type="true_false",
                option_a="True",
                option_b="False",
                option_d="Neither",
                correct_option="a",
            )

    def test_invalid_question_type(self):
        """Invalid question type should fail."""
        with pytest.raises(ValidationError):
            MCQQuestion(
                question="Test",
                question_type="multiple_choice",  # Invalid
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_option="a",
            )


class TestMCQCorrectOption:
    """Tests for correct option validation."""

    def test_valid_correct_options_mcq(self):
        """MCQ accepts a, b, c, d as correct options."""
        for opt in ["a", "b", "c", "d"]:
            mcq = MCQQuestion(
                question="Test",
                question_type="mcq",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_option=opt,
            )
            assert mcq.correct_option == opt

    def test_true_false_only_accepts_a_or_b(self):
        """True/False only accepts a or b as correct option."""
        with pytest.raises(
            ValidationError, match="correct_option must be 'a' or 'b'"
        ):
            MCQQuestion(
                question="Test",
                question_type="true_false",
                option_a="True",
                option_b="False",
                correct_option="c",
            )

    def test_invalid_correct_option_letter(self):
        """Invalid option letter should fail."""
        with pytest.raises(ValidationError):
            MCQQuestion(
                question="Test",
                question_type="mcq",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_option="e",
            )


class TestMCQQuestionText:
    """Tests for question text validation."""

    def test_empty_question_fails(self):
        """Empty question should raise ValidationError."""
        with pytest.raises(ValidationError):
            MCQQuestion(
                question="",
                question_type="mcq",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_option="a",
            )

    def test_whitespace_only_question_fails(self):
        """Whitespace-only question should fail."""
        with pytest.raises(ValidationError):
            MCQQuestion(
                question="   ",
                question_type="mcq",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_option="a",
            )

    def test_question_gets_stripped(self):
        """Question text should be stripped."""
        mcq = MCQQuestion(
            question="  What is Python?  ",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="a",
        )
        assert mcq.question == "What is Python?"


class TestMCQOptions:
    """Tests for option field validation."""

    def test_empty_option_a_fails(self):
        """Empty option A should fail."""
        with pytest.raises(ValidationError):
            MCQQuestion(
                question="Test",
                question_type="mcq",
                option_a="",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_option="a",
            )

    def test_empty_option_b_fails(self):
        """Empty option B should fail."""
        with pytest.raises(ValidationError):
            MCQQuestion(
                question="Test",
                question_type="mcq",
                option_a="A",
                option_b="",
                option_c="C",
                option_d="D",
                correct_option="a",
            )

    def test_options_get_stripped(self):
        """Options should be stripped of whitespace."""
        mcq = MCQQuestion(
            question="Test",
            question_type="mcq",
            option_a="  A  ",
            option_b="  B  ",
            option_c="  C  ",
            option_d="  D  ",
            correct_option="a",
        )
        assert mcq.option_a == "A"
        assert mcq.option_b == "B"
        assert mcq.option_c == "C"
        assert mcq.option_d == "D"


class TestMCQExplanations:
    """Tests for explanation fields."""

    def test_explanations_optional(self):
        """Explanations are optional."""
        mcq = MCQQuestion(
            question="Test",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="a",
        )
        assert mcq.explanation_a is None
        assert mcq.explanation_b is None
        assert mcq.explanation_c is None
        assert mcq.explanation_d is None

    def test_all_explanations(self):
        """All four explanations can be provided."""
        mcq = MCQQuestion(
            question="Test",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="a",
            explanation_a="Why A",
            explanation_b="Why B",
            explanation_c="Why C",
            explanation_d="Why D",
        )
        assert mcq.explanation_a == "Why A"
        assert mcq.explanation_b == "Why B"
        assert mcq.explanation_c == "Why C"
        assert mcq.explanation_d == "Why D"

    def test_partial_explanations(self):
        """Some explanations can be provided."""
        mcq = MCQQuestion(
            question="Test",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="b",
            explanation_b="This is correct",
        )
        assert mcq.explanation_a is None
        assert mcq.explanation_b == "This is correct"

    def test_explanations_get_stripped(self):
        """Explanations should be stripped."""
        mcq = MCQQuestion(
            question="Test",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="a",
            explanation_a="  Explanation  ",
        )
        assert mcq.explanation_a == "Explanation"

    def test_whitespace_only_explanation_becomes_none(self):
        """Whitespace-only explanation becomes None."""
        mcq = MCQQuestion(
            question="Test",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="a",
            explanation_a="   ",
        )
        assert mcq.explanation_a is None


class TestMCQTags:
    """Tests for tag handling in MCQ model."""

    def test_tags_optional(self):
        """Tags are optional."""
        mcq = MCQQuestion(
            question="Test",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="a",
        )
        assert mcq.tags is None

    def test_tags_normalization(self):
        """Tags should be stripped."""
        mcq = MCQQuestion(
            question="Test",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="a",
            tags="  python, oop  ",
        )
        assert mcq.tags == "python, oop"

    def test_whitespace_only_tags_becomes_none(self):
        """Whitespace-only tags becomes None."""
        mcq = MCQQuestion(
            question="Test",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="a",
            tags="   ",
        )
        assert mcq.tags is None


class TestMCQSM2Fields:
    """Tests for SM-2 algorithm fields."""

    def test_default_sm2_values(self):
        """Default SM2 values should be set."""
        mcq = MCQQuestion(
            question="Test",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="a",
        )
        assert mcq.interval == 1
        assert mcq.ease_factor == 2.5

    def test_default_last_reviewed_is_today(self):
        """Default last_reviewed should be today."""
        mcq = MCQQuestion(
            question="Test",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="a",
        )
        assert mcq.last_reviewed == date.today()

    def test_interval_minimum_bound(self):
        """Interval must be at least 1."""
        with pytest.raises(ValidationError):
            MCQQuestion(
                question="Test",
                question_type="mcq",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_option="a",
                interval=0,
            )

    def test_ease_factor_bounds(self):
        """Ease factor must be between 1.3 and 3.0."""
        with pytest.raises(ValidationError):
            MCQQuestion(
                question="Test",
                question_type="mcq",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_option="a",
                ease_factor=1.2,
            )


class TestMCQSerialization:
    """Tests for MCQ model serialization."""

    def test_model_dump(self):
        """model_dump() should return a dictionary."""
        mcq = MCQQuestion(
            question="Test question",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="b",
        )
        data = mcq.model_dump()
        assert isinstance(data, dict)
        assert data["question"] == "Test question"
        assert data["question_type"] == "mcq"
        assert data["correct_option"] == "b"

    def test_str_representation(self):
        """String representation should show key info."""
        mcq = MCQQuestion(
            id=42,
            question="What is Python?",
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="a",
        )
        string = str(mcq)
        assert "42" in string
        assert "mcq" in string

    def test_str_representation_long_question(self):
        """Long question should be truncated in string repr."""
        long_question = "A" * 100
        mcq = MCQQuestion(
            question=long_question,
            question_type="mcq",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_option="a",
        )
        string = str(mcq)
        assert "..." in string
