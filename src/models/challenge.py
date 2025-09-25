from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, validator


class Challenge(BaseModel):
    """
    Simple data container for Challenge entity.
    Contains no business logic - just data attributes with validation.
    """

    id: Optional[int] = None
    title: str = Field(..., min_length=1, description="The challenge title")
    description: str = Field(
        ..., min_length=1, description="The challenge description"
    )
    testcases: Optional[str] = Field(
        None, description="Test cases for the challenge"
    )
    language: str = Field(
        ..., pattern="^(python|javascript)$", description="Programming language"
    )
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

    @validator("title")
    def title_not_empty(cls, v):
        """Ensure title is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @validator("description")
    def description_not_empty(cls, v):
        """Ensure description is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()

    @validator("testcases")
    def clean_testcases(cls, v):
        """Clean and normalize testcases."""
        if v:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return v

    @validator("language")
    def validate_language(cls, v):
        """Ensure language is supported."""
        if v not in ["python", "javascript"]:
            raise ValueError("Language must be either python or javascript")
        return v.lower()

    def __str__(self) -> str:
        """String representation for display purposes."""
        return f"Challenge(id={self.id}, title='{self.title}', language={self.language})"
