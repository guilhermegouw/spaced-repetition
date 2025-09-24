from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, validator


class Question(BaseModel):
    """
    Simple data container for Question entity.
    Contains no business logic - just data attributes with validation.
    """

    id: Optional[int] = None
    question_text: str = Field(
        ..., min_length=1, description="The question text"
    )
    tags: Optional[str] = None
    last_reviewed: Optional[date] = None
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

    @validator("question_text")
    def question_text_not_empty(cls, v):
        """Ensure question text is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Question text cannot be empty")
        return v.strip()

    @validator("tags")
    def clean_tags(cls, v):
        """Clean and normalize tags."""
        if v:
            return v.strip() if v.strip() else None
        return v

    def __str__(self) -> str:
        """String representation for display purposes."""
        text_preview = self.question_text[:50] + (
            "..." if len(self.question_text) > 50 else ""
        )
        return f"Question(id={self.id}, text='{text_preview}')"
