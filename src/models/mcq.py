from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, root_validator, validator


class MCQQuestion(BaseModel):
    """
    Simple data container for MCQ Question entity.
    Contains no business logic - just data attributes with validation.
    """

    id: Optional[int] = None
    question: str = Field(..., min_length=1, description="The question text")
    question_type: str = Field(
        ..., regex="^(mcq|true_false)$", description="Type of question"
    )
    option_a: str = Field(..., min_length=1, description="Option A text")
    option_b: str = Field(..., min_length=1, description="Option B text")
    option_c: Optional[str] = Field(
        None, description="Option C text (MCQ only)"
    )
    option_d: Optional[str] = Field(
        None, description="Option D text (MCQ only)"
    )
    correct_option: str = Field(
        ..., regex="^[a-d]$", description="Correct option letter"
    )
    explanation_a: Optional[str] = Field(
        None, description="Explanation for option A"
    )
    explanation_b: Optional[str] = Field(
        None, description="Explanation for option B"
    )
    explanation_c: Optional[str] = Field(
        None, description="Explanation for option C"
    )
    explanation_d: Optional[str] = Field(
        None, description="Explanation for option D"
    )
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    last_reviewed: Optional[date] = Field(
        default_factory=lambda: date.today(), description="Last review date"
    )
    interval: int = Field(
        default=1, ge=1, description="Days until next review"
    )
    ease_factor: float = Field(
        default=2.5, ge=1.3, le=3.0, description="SM-2 ease factor"
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        use_enum_values = True

    @validator("question")
    def question_not_empty(cls, v):
        """Ensure question is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()

    @validator("option_a", "option_b")
    def required_options_not_empty(cls, v):
        """Ensure required options are not empty."""
        if not v or not v.strip():
            raise ValueError("Options A and B are required")
        return v.strip()

    @validator("option_c", "option_d")
    def optional_options_clean(cls, v):
        """Clean optional options."""
        if v:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return v

    @validator("tags")
    def clean_tags(cls, v):
        """Clean and normalize tags."""
        if v:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return v

    @validator(
        "explanation_a", "explanation_b", "explanation_c", "explanation_d"
    )
    def clean_explanations(cls, v):
        """Clean explanation fields."""
        if v:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return v

    @root_validator
    def validate_question_consistency(cls, values):
        """Validate that question type matches available options and correct answer."""
        question_type = values.get("question_type")
        option_c = values.get("option_c")
        option_d = values.get("option_d")
        correct_option = values.get("correct_option")

        if question_type == "true_false":
            if option_c is not None or option_d is not None:
                raise ValueError(
                    "True/False questions should only have option_a and option_b"
                )

            if correct_option not in ["a", "b"]:
                raise ValueError(
                    "For True/False questions, correct_option must be 'a' or 'b'"
                )

        elif question_type == "mcq":
            if not option_c or not option_d:
                raise ValueError(
                    "MCQ questions require all four options (a, b, c, d)"
                )

            if correct_option not in ["a", "b", "c", "d"]:
                raise ValueError(
                    "For MCQ questions, correct_option must be 'a', 'b', 'c', or 'd'"
                )

        return values

    def __str__(self) -> str:
        """String representation for display purposes."""
        question_preview = self.question[:50] + (
            "..." if len(self.question) > 50 else ""
        )
        return f"MCQQuestion(id={self.id}, type={self.question_type}, question='{question_preview}')"
