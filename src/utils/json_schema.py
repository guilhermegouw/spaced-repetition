"""JSON schema utilities for export/import operations."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ExportSchema(BaseModel):
    """
    Schema for exported JSON data.
    Contains all questions, challenges, and MCQ questions.
    """

    version: str = Field(default="1.0", description="Schema version")
    exported_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Timestamp of export",
    )
    questions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Exported questions"
    )
    challenges: List[Dict[str, Any]] = Field(
        default_factory=list, description="Exported challenges"
    )
    mcq_questions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Exported MCQ questions"
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True

    @validator("questions", "challenges", "mcq_questions", pre=True)
    def ensure_list(cls, v):
        """Ensure fields are lists."""
        if v is None:
            return []
        return v


def serialize_question(question) -> Dict[str, Any]:
    """
    Serialize a Question object to JSON-compatible dict.

    Args:
        question: Question object

    Returns:
        Dictionary representation
    """
    return {
        "question_text": question.question_text,
        "tags": question.tags,
    }


def serialize_challenge(challenge) -> Dict[str, Any]:
    """
    Serialize a Challenge object to JSON-compatible dict.

    Args:
        challenge: Challenge object

    Returns:
        Dictionary representation
    """
    return {
        "title": challenge.title,
        "description": challenge.description,
        "language": challenge.language,
        "testcases": challenge.testcases,
        "tags": challenge.tags,
    }


def serialize_mcq(mcq) -> Dict[str, Any]:
    """
    Serialize an MCQ Question object to JSON-compatible dict.

    Args:
        mcq: MCQQuestion object

    Returns:
        Dictionary representation
    """
    data = {
        "question": mcq.question,
        "question_type": mcq.question_type,
        "option_a": mcq.option_a,
        "option_b": mcq.option_b,
        "correct_option": mcq.correct_option,
        "explanation_a": mcq.explanation_a,
        "explanation_b": mcq.explanation_b,
        "tags": mcq.tags,
    }

    # Only include options c/d and their explanations for MCQ type
    if mcq.question_type == "mcq":
        data["option_c"] = mcq.option_c
        data["option_d"] = mcq.option_d
        data["explanation_c"] = mcq.explanation_c
        data["explanation_d"] = mcq.explanation_d

    return data


def validate_import_data(data: Dict[str, Any]) -> ExportSchema:
    """
    Validate imported JSON data against schema.

    Args:
        data: Raw JSON data

    Returns:
        Validated ExportSchema object

    Raises:
        ValueError: If data doesn't match schema
    """
    try:
        return ExportSchema(**data)
    except Exception as e:
        raise ValueError(f"Invalid JSON schema: {e}")
