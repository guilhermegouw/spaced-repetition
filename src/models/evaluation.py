"""
Pydantic models for evaluation sessions and API communication.
"""
import re
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Message(BaseModel):
    """Single message in conversation history."""

    role: str = Field(...)
    content: str = Field(..., min_length=1)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role is one of the allowed values."""
        allowed = {"system", "user", "assistant"}
        if v not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return v

    def to_dict(self) -> dict:
        """Convert to dictionary for API calls."""
        return {"role": self.role, "content": self.content}


class EvaluationResponse(BaseModel):
    """Parsed evaluation response from API."""

    grade: float = Field(..., ge=0, le=3)
    feedback: str
    correctness_score: Optional[float] = None
    clarity_score: Optional[float] = None
    efficiency_score: Optional[float] = None
    raw_response: str = ""

    @classmethod
    def parse_from_response(cls, response: str) -> "EvaluationResponse":
        """
        Parse API response to extract grade and feedback.

        Tries multiple patterns to extract the numeric grade.
        """
        grade = cls._extract_grade(response)
        feedback = response

        correctness = cls._extract_score(response, "correctness")
        clarity = cls._extract_score(response, "clarity")
        efficiency = cls._extract_score(response, "efficiency")

        return cls(
            grade=grade,
            feedback=feedback,
            correctness_score=correctness,
            clarity_score=clarity,
            efficiency_score=efficiency,
            raw_response=response,
        )

    @staticmethod
    def _extract_grade(text: str) -> float:
        """Extract the final grade from response text."""
        patterns = [
            r"\*\*\s*(?:score|grade|average)[:\s]*(\d+(?:\.\d+)?)\s*(?:/\s*3)?\s*\*\*",
            r"(?:score|grade|average)[:\s]*(\d+(?:\.\d+)?)\s*(?:/\s*3)?",
            r"(\d+(?:\.\d+)?)\s*/\s*3",
            r":\s*(\d+(?:\.\d+)?)\s*$",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                grade = float(matches[-1])
                return min(3.0, max(0.0, grade))

        numbers = re.findall(r"(\d+(?:\.\d+)?)", text)
        for num in reversed(numbers):
            val = float(num)
            if 0 <= val <= 3:
                return val

        raise ValueError("Could not extract grade from API response")

    @staticmethod
    def _extract_score(text: str, category: str) -> Optional[float]:
        """Extract individual category score."""
        pattern = rf"{category}[:\s]*(\d+(?:\.\d+)?)"
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1))
        return None


class UserAction(str, Enum):
    """Actions user can take after seeing evaluation."""

    ACCEPT = "accept"
    DISPUTE = "dispute"
    REFACTOR = "refactor"


class EvaluationSession(BaseModel):
    """
    Manages state for an evaluation session with conversation history.

    Tracks:
    - Challenge being evaluated
    - Conversation history with API
    - First grade (for SM-2, honest assessment)
    - Current iteration number
    """

    challenge_id: int
    challenge_file_path: str
    folder_path: str
    messages: List[Message] = Field(default_factory=list)
    first_grade: Optional[float] = None
    current_grade: Optional[float] = None
    iteration: int = 0
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic model configuration."""

        use_enum_values = True

    def add_system_prompt(self, content: str) -> None:
        """Add system message to conversation."""
        self.messages.append(Message(role="system", content=content))

    def add_user_message(self, content: str) -> None:
        """Add user message to conversation."""
        self.messages.append(Message(role="user", content=content))

    def add_assistant_response(self, content: str) -> None:
        """Add assistant response to conversation."""
        self.messages.append(Message(role="assistant", content=content))

    def record_evaluation(self, grade: float) -> None:
        """Record an evaluation grade."""
        self.iteration += 1
        self.current_grade = grade
        if self.first_grade is None:
            self.first_grade = grade

    def get_sm2_grade(self) -> float:
        """Get the grade to use for SM-2 (always first grade as float 0-3)."""
        if self.first_grade is None:
            raise ValueError("No evaluation recorded yet")
        return self.first_grade
