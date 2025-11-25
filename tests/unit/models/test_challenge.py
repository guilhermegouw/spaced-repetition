"""Tests for the Challenge model."""

from datetime import date

import pytest
from pydantic import ValidationError

from src.models.challenge import Challenge


class TestChallengeCreation:
    """Tests for Challenge model creation and validation."""

    def test_valid_python_challenge(self):
        """Create a valid Python challenge."""
        c = Challenge(
            title="FizzBuzz",
            description="Write a FizzBuzz function",
            language="python",
        )
        assert c.title == "FizzBuzz"
        assert c.description == "Write a FizzBuzz function"
        assert c.language == "python"

    def test_valid_javascript_challenge(self):
        """Create a valid JavaScript challenge."""
        c = Challenge(
            title="Array Sum",
            description="Sum all array elements",
            language="javascript",
        )
        assert c.language == "javascript"

    def test_valid_challenge_with_all_fields(self):
        """Create a challenge with all fields specified."""
        c = Challenge(
            id=1,
            title="Binary Search",
            description="Implement binary search",
            testcases="assert binary_search([1,2,3], 2) == 1",
            language="python",
            tags="algorithms, search",
            last_reviewed=date(2024, 1, 15),
            interval=5,
            ease_factor=2.3,
        )
        assert c.id == 1
        assert c.testcases == "assert binary_search([1,2,3], 2) == 1"
        assert c.tags == "algorithms, search"
        assert c.last_reviewed == date(2024, 1, 15)
        assert c.interval == 5
        assert c.ease_factor == 2.3

    def test_invalid_language_rejected(self):
        """Invalid language should raise ValidationError."""
        with pytest.raises(ValidationError):
            Challenge(
                title="Test",
                description="Test description",
                language="ruby",
            )

    def test_language_case_insensitive(self):
        """Language should be normalized to lowercase."""
        c = Challenge(
            title="Test",
            description="Test description",
            language="python",
        )
        assert c.language == "python"


class TestChallengeTitleDescription:
    """Tests for title and description validation."""

    def test_empty_title_fails(self):
        """Empty title should raise ValidationError."""
        with pytest.raises(ValidationError):
            Challenge(
                title="", description="Valid description", language="python"
            )

    def test_whitespace_only_title_fails(self):
        """Whitespace-only title should raise ValidationError."""
        with pytest.raises(ValidationError):
            Challenge(
                title="   ",
                description="Valid description",
                language="python",
            )

    def test_empty_description_fails(self):
        """Empty description should raise ValidationError."""
        with pytest.raises(ValidationError):
            Challenge(
                title="Valid Title", description="", language="python"
            )

    def test_whitespace_only_description_fails(self):
        """Whitespace-only description should raise ValidationError."""
        with pytest.raises(ValidationError):
            Challenge(
                title="Valid Title", description="   ", language="python"
            )

    def test_title_gets_stripped(self):
        """Title should be stripped of whitespace."""
        c = Challenge(
            title="  FizzBuzz  ",
            description="Description",
            language="python",
        )
        assert c.title == "FizzBuzz"

    def test_description_gets_stripped(self):
        """Description should be stripped of whitespace."""
        c = Challenge(
            title="Title",
            description="  Some description  ",
            language="python",
        )
        assert c.description == "Some description"


class TestChallengeTestcases:
    """Tests for testcases field handling."""

    def test_with_testcases(self):
        """Challenge can have testcases."""
        c = Challenge(
            title="Test",
            description="Description",
            language="python",
            testcases="assert func(1) == 1",
        )
        assert c.testcases == "assert func(1) == 1"

    def test_without_testcases(self):
        """Testcases are optional."""
        c = Challenge(
            title="Test",
            description="Description",
            language="python",
        )
        assert c.testcases is None

    def test_testcases_stripped(self):
        """Testcases should be stripped of whitespace."""
        c = Challenge(
            title="Test",
            description="Description",
            language="python",
            testcases="  assert True  ",
        )
        assert c.testcases == "assert True"

    def test_whitespace_only_testcases_becomes_none(self):
        """Whitespace-only testcases should become None."""
        c = Challenge(
            title="Test",
            description="Description",
            language="python",
            testcases="   ",
        )
        assert c.testcases is None


class TestChallengeTags:
    """Tests for tag handling in Challenge model."""

    def test_tags_normalization(self):
        """Tags should be stripped."""
        c = Challenge(
            title="Test",
            description="Description",
            language="python",
            tags="  algorithms, python  ",
        )
        assert c.tags == "algorithms, python"

    def test_tags_optional(self):
        """Tags are optional."""
        c = Challenge(
            title="Test",
            description="Description",
            language="python",
        )
        assert c.tags is None

    def test_whitespace_only_tags_becomes_none(self):
        """Whitespace-only tags should become None."""
        c = Challenge(
            title="Test",
            description="Description",
            language="python",
            tags="   ",
        )
        assert c.tags is None


class TestChallengeSM2Fields:
    """Tests for SM-2 algorithm fields."""

    def test_default_sm2_values(self):
        """Default SM2 values should be set."""
        c = Challenge(
            title="Test",
            description="Description",
            language="python",
        )
        assert c.interval == 1
        assert c.ease_factor == 2.5

    def test_default_last_reviewed_is_today(self):
        """Default last_reviewed should be today's date."""
        c = Challenge(
            title="Test",
            description="Description",
            language="python",
        )
        assert c.last_reviewed == date.today()

    def test_interval_minimum_bound(self):
        """Interval must be at least 1."""
        with pytest.raises(ValidationError):
            Challenge(
                title="Test",
                description="Description",
                language="python",
                interval=0,
            )

    def test_ease_factor_bounds(self):
        """Ease factor must be between 1.3 and 3.0."""
        with pytest.raises(ValidationError):
            Challenge(
                title="Test",
                description="Description",
                language="python",
                ease_factor=1.2,
            )

        with pytest.raises(ValidationError):
            Challenge(
                title="Test",
                description="Description",
                language="python",
                ease_factor=3.1,
            )


class TestChallengeSerialization:
    """Tests for Challenge model serialization."""

    def test_model_dump(self):
        """model_dump() should return a dictionary."""
        c = Challenge(
            title="Test",
            description="Description",
            language="python",
        )
        data = c.model_dump()
        assert isinstance(data, dict)
        assert data["title"] == "Test"
        assert data["description"] == "Description"
        assert data["language"] == "python"

    def test_str_representation(self):
        """String representation should show key info."""
        c = Challenge(
            id=42,
            title="FizzBuzz",
            description="Description",
            language="python",
        )
        string = str(c)
        assert "42" in string
        assert "FizzBuzz" in string
        assert "python" in string
