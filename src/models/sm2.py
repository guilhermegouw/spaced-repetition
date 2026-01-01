from datetime import timedelta
from typing import Tuple


class SM2Calculator:
    """
    Pure SM-2 (SuperMemo 2) algorithm implementation.
    Contains no state - just static methods for calculations.
    """

    @staticmethod
    def calculate_next_review(
        rating: int, current_interval: int, current_ease_factor: float
    ) -> Tuple[int, float]:
        """
        Calculate next review interval and ease factor based on SM-2 algorithm.

        Args:
            rating: User's performance rating (0-3)
                   0 = forgot/incorrect
                   1 = hard/low confidence
                   2 = good/medium confidence
                   3 = easy/high confidence
            current_interval: Current interval in days
            current_ease_factor: Current ease factor (typically 1.3-3.0)

        Returns:
            Tuple of (new_interval, new_ease_factor)

        Raises:
            ValueError: If rating is not between 0 and 3
        """
        if not 0 <= rating <= 3:
            raise ValueError(
                "Rating must be between 0 (forgot) and 3 (easy recall)"
            )

        if rating == 0:
            new_interval = 1
            new_ease_factor = max(1.3, current_ease_factor - 0.2)
        else:
            ease_adjustment = 0.1 - (3 - rating) * (0.08 + (3 - rating) * 0.02)
            new_ease_factor = current_ease_factor + ease_adjustment
            new_interval = max(1, round(current_interval * new_ease_factor))

        return new_interval, round(new_ease_factor, 2)

    @staticmethod
    def calculate_mcq_review(
        is_correct: bool,
        confidence_level: str,
        current_interval: int,
        current_ease_factor: float,
    ) -> Tuple[int, float]:
        """
        Calculate next review for MCQ questions with penalty system for
        misconceptions.

        Args:
            is_correct: Whether the answer was correct
            confidence_level: 'low', 'medium', or 'high'
            current_interval: Current interval in days
            current_ease_factor: Current ease factor

        Returns:
            Tuple of (new_interval, new_ease_factor)

        Raises:
            ValueError: If confidence_level is not valid
        """
        valid_confidence = ["low", "medium", "high"]
        if confidence_level not in valid_confidence:
            raise ValueError(
                f"confidence_level must be one of {valid_confidence}"
            )

        if is_correct:
            if confidence_level == "high":
                sm2_rating = 3
            elif confidence_level == "medium":
                sm2_rating = 2
            else:
                sm2_rating = 1
        else:
            sm2_rating = 0

        new_interval, new_ease_factor = SM2Calculator.calculate_next_review(
            sm2_rating, current_interval, current_ease_factor
        )

        if not is_correct and confidence_level == "high":
            misconception_penalty = 0.1
            new_ease_factor = max(1.3, new_ease_factor - misconception_penalty)

        return new_interval, round(new_ease_factor, 2)

    @staticmethod
    def is_overdue(last_reviewed_date, interval_days, current_date) -> bool:
        """
        Check if an item is overdue for review.

        Args:
            last_reviewed_date: Date when last reviewed (date object or None)
            interval_days: Interval in days (int)
            current_date: Current date (date object)

        Returns:
            True if overdue or never reviewed, False otherwise
        """
        if last_reviewed_date is None:
            return True

        next_review_date = last_reviewed_date + timedelta(days=interval_days)
        return current_date >= next_review_date

    @staticmethod
    def days_overdue(last_reviewed_date, interval_days, current_date) -> float:
        """
        Calculate how many days overdue an item is.

        Args:
            last_reviewed_date: Date when last reviewed (date object or None)
            interval_days: Interval in days (int)
            current_date: Current date (date object)

        Returns:
            Number of days overdue (0.0 if not overdue, positive if overdue)
        """
        if last_reviewed_date is None:
            return float("inf")

        next_review_date = last_reviewed_date + timedelta(days=interval_days)
        days_diff = (current_date - next_review_date).days
        return max(0.0, float(days_diff))
