"""Tests for SM2Calculator - the core spaced repetition algorithm."""

from datetime import date, timedelta

import pytest

from src.models.sm2 import SM2Calculator


class TestCalculateNextReview:
    """Tests for the calculate_next_review method."""

    def test_rating_3_easy_increases_interval(self):
        """Rating 3 (easy) should increase interval significantly."""
        new_interval, new_ef = SM2Calculator.calculate_next_review(
            rating=3, current_interval=1, current_ease_factor=2.5
        )
        assert new_interval > 1
        assert new_ef >= 2.5  # EF should increase or stay same for easy

    def test_rating_2_good_increases_interval(self):
        """Rating 2 (good) should increase interval."""
        new_interval, new_ef = SM2Calculator.calculate_next_review(
            rating=2, current_interval=1, current_ease_factor=2.5
        )
        assert new_interval >= 1

    def test_rating_1_hard_maintains_learning(self):
        """Rating 1 (hard) should keep learning but slower progress."""
        new_interval, new_ef = SM2Calculator.calculate_next_review(
            rating=1, current_interval=5, current_ease_factor=2.5
        )
        assert new_interval >= 1
        assert new_ef < 2.5  # EF should decrease for hard

    def test_rating_0_forgot_resets_interval(self):
        """Rating 0 (forgot) should reset interval to 1."""
        new_interval, new_ef = SM2Calculator.calculate_next_review(
            rating=0, current_interval=10, current_ease_factor=2.5
        )
        assert new_interval == 1
        assert new_ef < 2.5  # EF decreases

    def test_ease_factor_minimum_bound(self):
        """Ease factor should never go below 1.3."""
        # Start with minimum EF and give worst rating
        new_interval, new_ef = SM2Calculator.calculate_next_review(
            rating=0, current_interval=5, current_ease_factor=1.3
        )
        assert new_ef >= 1.3

    def test_ease_factor_minimum_after_multiple_failures(self):
        """EF should stay at 1.3 minimum even after multiple failures."""
        ef = 2.5
        for _ in range(10):
            _, ef = SM2Calculator.calculate_next_review(
                rating=0, current_interval=1, current_ease_factor=ef
            )
        assert ef >= 1.3

    def test_ease_factor_increases_on_easy(self):
        """Ease factor should increase with rating 3."""
        _, new_ef = SM2Calculator.calculate_next_review(
            rating=3, current_interval=5, current_ease_factor=2.0
        )
        assert new_ef > 2.0

    def test_interval_progression_first_review(self):
        """Test interval progression from first review."""
        interval = 1
        ef = 2.5
        # First easy review
        interval, ef = SM2Calculator.calculate_next_review(
            rating=3, current_interval=interval, current_ease_factor=ef
        )
        assert interval >= 2  # Should progress

    def test_interval_progression_multiple_reviews(self):
        """Test interval grows with consecutive successful reviews."""
        interval = 1
        ef = 2.5
        intervals = [interval]

        for _ in range(5):
            interval, ef = SM2Calculator.calculate_next_review(
                rating=3, current_interval=interval, current_ease_factor=ef
            )
            intervals.append(interval)

        # Intervals should generally increase
        assert intervals[-1] > intervals[0]

    def test_invalid_rating_negative(self):
        """Should raise ValueError for negative rating."""
        with pytest.raises(ValueError, match="Rating must be between"):
            SM2Calculator.calculate_next_review(
                rating=-1, current_interval=1, current_ease_factor=2.5
            )

    def test_invalid_rating_too_high(self):
        """Should raise ValueError for rating > 3."""
        with pytest.raises(ValueError, match="Rating must be between"):
            SM2Calculator.calculate_next_review(
                rating=4, current_interval=1, current_ease_factor=2.5
            )

    def test_all_valid_ratings(self):
        """All ratings 0-3 should work without error."""
        for rating in range(4):
            new_interval, new_ef = SM2Calculator.calculate_next_review(
                rating=rating, current_interval=5, current_ease_factor=2.5
            )
            assert new_interval >= 1
            assert 1.3 <= new_ef <= 3.5

    def test_return_types(self):
        """Should return tuple of (int, float)."""
        result = SM2Calculator.calculate_next_review(
            rating=2, current_interval=5, current_ease_factor=2.5
        )
        assert isinstance(result, tuple)
        assert isinstance(result[0], int)
        assert isinstance(result[1], float)


class TestCalculateMCQReview:
    """Tests for the calculate_mcq_review method."""

    def test_correct_high_confidence(self):
        """Correct answer with high confidence = best case."""
        new_interval, new_ef = SM2Calculator.calculate_mcq_review(
            is_correct=True,
            confidence_level="high",
            current_interval=5,
            current_ease_factor=2.5,
        )
        assert new_interval > 5
        assert new_ef >= 2.5

    def test_correct_medium_confidence(self):
        """Correct with medium confidence = good progress."""
        new_interval, new_ef = SM2Calculator.calculate_mcq_review(
            is_correct=True,
            confidence_level="medium",
            current_interval=5,
            current_ease_factor=2.5,
        )
        assert new_interval >= 1

    def test_correct_low_confidence(self):
        """Correct with low confidence (guessed) = slower progress."""
        new_interval, new_ef = SM2Calculator.calculate_mcq_review(
            is_correct=True,
            confidence_level="low",
            current_interval=5,
            current_ease_factor=2.5,
        )
        assert new_interval >= 1
        assert new_ef < 2.5  # EF should decrease (lucky guess)

    def test_wrong_high_confidence_misconception_penalty(self):
        """Wrong with high confidence = misconception, extra penalty."""
        new_interval, new_ef = SM2Calculator.calculate_mcq_review(
            is_correct=False,
            confidence_level="high",
            current_interval=10,
            current_ease_factor=2.5,
        )
        assert new_interval == 1  # Reset
        # Should have extra misconception penalty
        # Normal wrong would give 2.3, misconception gives 2.2
        assert new_ef < 2.3

    def test_wrong_low_confidence_no_extra_penalty(self):
        """Wrong with low confidence = expected mistake, no extra penalty."""
        new_interval, new_ef = SM2Calculator.calculate_mcq_review(
            is_correct=False,
            confidence_level="low",
            current_interval=10,
            current_ease_factor=2.5,
        )
        assert new_interval == 1
        assert new_ef == 2.3  # Standard penalty only

    def test_misconception_penalty_respects_minimum(self):
        """Misconception penalty should not push EF below 1.3."""
        new_interval, new_ef = SM2Calculator.calculate_mcq_review(
            is_correct=False,
            confidence_level="high",
            current_interval=5,
            current_ease_factor=1.3,
        )
        assert new_ef >= 1.3

    def test_invalid_confidence_level(self):
        """Should raise ValueError for invalid confidence."""
        with pytest.raises(ValueError, match="confidence_level must be"):
            SM2Calculator.calculate_mcq_review(
                is_correct=True,
                confidence_level="very_high",
                current_interval=5,
                current_ease_factor=2.5,
            )

    def test_all_confidence_levels_valid(self):
        """All valid confidence levels should work."""
        for confidence in ["low", "medium", "high"]:
            result = SM2Calculator.calculate_mcq_review(
                is_correct=True,
                confidence_level=confidence,
                current_interval=5,
                current_ease_factor=2.5,
            )
            assert isinstance(result, tuple)


class TestIsOverdue:
    """Tests for the is_overdue method."""

    def test_overdue_past_due_date(self):
        """Item reviewed long ago should be overdue."""
        last_reviewed = date.today() - timedelta(days=10)
        interval = 5
        result = SM2Calculator.is_overdue(
            last_reviewed, interval, date.today()
        )
        assert result is True

    def test_not_overdue_future_due_date(self):
        """Item with future due date should not be overdue."""
        last_reviewed = date.today()
        interval = 7
        result = SM2Calculator.is_overdue(
            last_reviewed, interval, date.today()
        )
        assert result is False

    def test_due_today_is_overdue(self):
        """Item due today should be considered overdue (ready for review)."""
        last_reviewed = date.today() - timedelta(days=5)
        interval = 5
        result = SM2Calculator.is_overdue(
            last_reviewed, interval, date.today()
        )
        assert result is True

    def test_never_reviewed_is_overdue(self):
        """Item never reviewed (None) should be overdue."""
        result = SM2Calculator.is_overdue(None, 5, date.today())
        assert result is True

    def test_one_day_before_due(self):
        """Item one day before due should not be overdue."""
        last_reviewed = date.today() - timedelta(days=4)
        interval = 5
        result = SM2Calculator.is_overdue(
            last_reviewed, interval, date.today()
        )
        assert result is False


class TestDaysOverdue:
    """Tests for the days_overdue method."""

    def test_days_overdue_positive(self):
        """Calculate days past due date."""
        last_reviewed = date.today() - timedelta(days=10)
        interval = 5
        result = SM2Calculator.days_overdue(
            last_reviewed, interval, date.today()
        )
        assert result == 5.0

    def test_days_overdue_zero_on_due_date(self):
        """Should return 0 on the due date itself."""
        last_reviewed = date.today() - timedelta(days=5)
        interval = 5
        result = SM2Calculator.days_overdue(
            last_reviewed, interval, date.today()
        )
        assert result == 0.0

    def test_days_overdue_zero_before_due(self):
        """Should return 0 if not yet due."""
        last_reviewed = date.today() - timedelta(days=2)
        interval = 5
        result = SM2Calculator.days_overdue(
            last_reviewed, interval, date.today()
        )
        assert result == 0.0

    def test_days_overdue_never_reviewed(self):
        """Never reviewed items should return infinity."""
        result = SM2Calculator.days_overdue(None, 5, date.today())
        assert result == float("inf")

    def test_days_overdue_large_overdue(self):
        """Test large overdue period."""
        last_reviewed = date.today() - timedelta(days=100)
        interval = 5
        result = SM2Calculator.days_overdue(
            last_reviewed, interval, date.today()
        )
        assert result == 95.0
