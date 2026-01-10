"""Tests for evaluation models."""
import pytest

from src.models.evaluation import (
    EvaluationResponse,
    EvaluationSession,
    Message,
    UserAction,
)


class TestMessage:
    """Tests for Message model."""

    def test_valid_user_message(self):
        """Should create valid user message."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_valid_assistant_message(self):
        """Should create valid assistant message."""
        msg = Message(role="assistant", content="Hi there")
        assert msg.role == "assistant"
        assert msg.content == "Hi there"

    def test_valid_system_message(self):
        """Should create valid system message."""
        msg = Message(role="system", content="You are a helpful assistant")
        assert msg.role == "system"

    def test_invalid_role_rejected(self):
        """Should reject invalid role."""
        with pytest.raises(ValueError):
            Message(role="invalid", content="Hello")

    def test_empty_content_rejected(self):
        """Should reject empty content."""
        with pytest.raises(ValueError):
            Message(role="user", content="")

    def test_to_dict(self):
        """Should convert to dictionary correctly."""
        msg = Message(role="assistant", content="Hi")
        assert msg.to_dict() == {"role": "assistant", "content": "Hi"}


class TestEvaluationResponse:
    """Tests for EvaluationResponse parsing."""

    def test_parse_score_with_explicit_format(self):
        """Should parse explicit Score: X/3 format."""
        response = (
            "Correctness: 2/3\nClarity: 3/3\nEfficiency: 2/3\n\n"
            "**Score: 2.33/3**"
        )
        result = EvaluationResponse.parse_from_response(response)
        assert abs(result.grade - 2.33) < 0.01

    def test_parse_score_average_format(self):
        """Should parse average grade format."""
        response = "The average grade is 2.5"
        result = EvaluationResponse.parse_from_response(response)
        assert result.grade == 2.5

    def test_parse_extracts_individual_scores(self):
        """Should extract individual category scores."""
        response = (
            "Correctness: 3/3\nClarity: 2/3\n"
            "Efficiency: 1/3\nScore: 2/3"
        )
        result = EvaluationResponse.parse_from_response(response)
        assert result.correctness_score == 3
        assert result.clarity_score == 2
        assert result.efficiency_score == 1

    def test_grade_clamped_to_valid_range(self):
        """Should clamp grade to 0-3 range."""
        response = "Score: 5/3"
        result = EvaluationResponse.parse_from_response(response)
        assert result.grade == 3.0

    def test_parse_fraction_format(self):
        """Should parse X/3 fraction format."""
        response = "Your solution scores 2.5/3"
        result = EvaluationResponse.parse_from_response(response)
        assert result.grade == 2.5

    def test_parse_with_bold_markdown(self):
        """Should parse score with bold markdown."""
        response = "**Score: 2.7/3**"
        result = EvaluationResponse.parse_from_response(response)
        assert abs(result.grade - 2.7) < 0.01

    def test_raises_on_unparseable_response(self):
        """Should raise ValueError when no grade found."""
        response = "No numbers here at all!"
        with pytest.raises(ValueError, match="Could not extract grade"):
            EvaluationResponse.parse_from_response(response)

    def test_stores_raw_response(self):
        """Should store raw response as feedback."""
        response = "Great work! Score: 3/3"
        result = EvaluationResponse.parse_from_response(response)
        assert result.raw_response == response
        assert result.feedback == response


class TestUserAction:
    """Tests for UserAction enum."""

    def test_action_values(self):
        """Should have correct enum values."""
        assert UserAction.ACCEPT.value == "accept"
        assert UserAction.DISPUTE.value == "dispute"
        assert UserAction.REFACTOR.value == "refactor"


class TestEvaluationSession:
    """Tests for EvaluationSession state management."""

    def test_create_session(self):
        """Should create session with default values."""
        session = EvaluationSession(
            challenge_id=1,
            challenge_file_path="/path/to/file.py",
            folder_path="/path/to",
        )
        assert session.challenge_id == 1
        assert session.first_grade is None
        assert session.current_grade is None
        assert session.iteration == 0
        assert session.messages == []

    def test_add_system_prompt(self):
        """Should add system message."""
        session = EvaluationSession(
            challenge_id=1,
            challenge_file_path="",
            folder_path="",
        )
        session.add_system_prompt("System prompt")

        assert len(session.messages) == 1
        assert session.messages[0].role == "system"
        assert session.messages[0].content == "System prompt"

    def test_add_user_message(self):
        """Should add user message."""
        session = EvaluationSession(
            challenge_id=1,
            challenge_file_path="",
            folder_path="",
        )
        session.add_user_message("User message")

        assert len(session.messages) == 1
        assert session.messages[0].role == "user"

    def test_add_assistant_response(self):
        """Should add assistant message."""
        session = EvaluationSession(
            challenge_id=1,
            challenge_file_path="",
            folder_path="",
        )
        session.add_assistant_response("Assistant response")

        assert len(session.messages) == 1
        assert session.messages[0].role == "assistant"

    def test_record_evaluation_first_grade(self):
        """Should record first evaluation grade."""
        session = EvaluationSession(
            challenge_id=1,
            challenge_file_path="",
            folder_path="",
        )
        session.record_evaluation(2.5)

        assert session.first_grade == 2.5
        assert session.current_grade == 2.5
        assert session.iteration == 1

    def test_first_grade_preserved_on_subsequent_evaluations(self):
        """Should preserve first grade on later evaluations."""
        session = EvaluationSession(
            challenge_id=1,
            challenge_file_path="",
            folder_path="",
        )
        session.record_evaluation(1.5)
        session.record_evaluation(2.5)
        session.record_evaluation(3.0)

        assert session.first_grade == 1.5
        assert session.current_grade == 3.0
        assert session.iteration == 3

    def test_get_sm2_grade_returns_int(self):
        """Should return first grade as integer for SM-2."""
        session = EvaluationSession(
            challenge_id=1,
            challenge_file_path="",
            folder_path="",
        )
        session.record_evaluation(2.7)

        assert session.get_sm2_grade() == 2
        assert isinstance(session.get_sm2_grade(), int)

    def test_get_sm2_grade_raises_if_no_evaluation(self):
        """Should raise error if no evaluation recorded."""
        session = EvaluationSession(
            challenge_id=1,
            challenge_file_path="",
            folder_path="",
        )
        with pytest.raises(ValueError, match="No evaluation recorded"):
            session.get_sm2_grade()

    def test_conversation_history_builds_correctly(self):
        """Should build conversation history in order."""
        session = EvaluationSession(
            challenge_id=1,
            challenge_file_path="",
            folder_path="",
        )
        session.add_system_prompt("System")
        session.add_user_message("User 1")
        session.add_assistant_response("Assistant 1")
        session.add_user_message("User 2")
        session.add_assistant_response("Assistant 2")

        assert len(session.messages) == 5
        assert [m.role for m in session.messages] == [
            "system",
            "user",
            "assistant",
            "user",
            "assistant",
        ]
