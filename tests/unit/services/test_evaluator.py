"""Tests for evaluation service."""
from unittest.mock import Mock, patch

import pytest

from src.models.evaluation import EvaluationResponse, EvaluationSession
from src.services.api_client import APIError
from src.services.evaluator import EvaluationService


class TestEvaluationService:
    """Tests for EvaluationService."""

    @pytest.fixture
    def mock_client(self):
        """Create mock API client."""
        client = Mock()
        client.chat_completion.return_value = (
            "Correctness: 3/3\nClarity: 2/3\n"
            "Efficiency: 2/3\n**Score: 2.33/3**"
        )
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create service with mock client."""
        return EvaluationService(api_client=mock_client)

    def test_create_session(self, service):
        """Should create session with system prompt."""
        session = service.create_session(
            challenge_id=1,
            challenge_file_path="/path/file.py",
            folder_path="/path",
        )

        assert session.challenge_id == 1
        assert session.challenge_file_path == "/path/file.py"
        assert session.folder_path == "/path"
        assert len(session.messages) == 1
        assert session.messages[0].role == "system"

    def test_evaluate_sends_prompt_and_records_grade(self, service):
        """Should send solution and record evaluation."""
        session = service.create_session(1, "/path", "/folder")

        result = service.evaluate(session, "def hello(): pass")

        assert len(session.messages) == 3
        assert session.messages[1].role == "user"
        assert session.messages[2].role == "assistant"
        assert session.first_grade is not None
        assert session.iteration == 1
        assert isinstance(result, EvaluationResponse)

    def test_evaluate_includes_solution_in_prompt(self, service, mock_client):
        """Should include solution code in the prompt."""
        session = service.create_session(1, "/path", "/folder")

        service.evaluate(session, "def my_solution(): return 42")

        call_args = mock_client.chat_completion.call_args
        messages = call_args[0][0]
        user_message = messages[1]
        assert "def my_solution(): return 42" in user_message.content

    def test_dispute_adds_to_conversation(self, service):
        """Should add dispute to conversation history."""
        session = service.create_session(1, "/path", "/folder")
        service.evaluate(session, "def hello(): pass")

        service.dispute(session, "I think efficiency is better")

        assert len(session.messages) == 5
        assert "disagree" in session.messages[3].content.lower()
        assert session.iteration == 2

    def test_dispute_preserves_first_grade(self, service, mock_client):
        """Should preserve first grade after dispute."""
        mock_client.chat_completion.side_effect = [
            "Score: 1.5/3",
            "Score: 2.5/3",
        ]
        session = service.create_session(1, "/path", "/folder")
        service.evaluate(session, "def hello(): pass")

        service.dispute(session, "My code is correct")

        assert session.first_grade == 1.5
        assert session.current_grade == 2.5

    def test_refactor_adds_new_code_to_conversation(self, service):
        """Should add refactored code to conversation."""
        session = service.create_session(1, "/path", "/folder")
        service.evaluate(session, "def hello(): pass")

        service.refactor_evaluate(session, "def hello():\n    '''Better'''")

        assert len(session.messages) == 5
        assert "refactored" in session.messages[3].content.lower()
        assert "Better" in session.messages[3].content

    def test_full_conversation_flow(self, service, mock_client):
        """Should maintain full conversation history."""
        mock_client.chat_completion.side_effect = [
            "Score: 1.5/3 - needs improvement",
            "Score: 2.0/3 - valid point",
            "Score: 2.8/3 - much better",
        ]

        session = service.create_session(1, "/path", "/folder")

        service.evaluate(session, "def v1(): pass")
        service.dispute(session, "I handled edge cases")
        service.refactor_evaluate(session, "def v2(): return True")

        assert session.first_grade == 1.5
        assert session.current_grade == 2.8
        assert session.iteration == 3
        assert len(session.messages) == 7

    def test_close_closes_client(self, mock_client):
        """Should close the API client."""
        service = EvaluationService(api_client=mock_client)
        service.close()
        mock_client.close.assert_called_once()

    def test_lazy_client_initialization(self):
        """Should lazily initialize client when needed."""
        service = EvaluationService()
        assert service._client is None

        with patch(
            "src.services.evaluator.ZAIClient"
        ) as mock_client_class:
            mock_instance = Mock()
            mock_instance.chat_completion.return_value = "Score: 2/3"
            mock_client_class.return_value = mock_instance

            session = service.create_session(1, "/path", "/folder")
            service.evaluate(session, "code")

            mock_client_class.assert_called_once()


class TestEvaluationServiceErrorHandling:
    """Tests for error handling in EvaluationService."""

    def test_api_error_propagates(self):
        """Should propagate API errors."""
        mock_client = Mock()
        mock_client.chat_completion.side_effect = APIError("API failed")

        service = EvaluationService(api_client=mock_client)
        session = service.create_session(1, "/path", "/folder")

        with pytest.raises(APIError, match="API failed"):
            service.evaluate(session, "code")

    def test_parse_error_propagates(self):
        """Should propagate parse errors."""
        mock_client = Mock()
        mock_client.chat_completion.return_value = "No grade here!"

        service = EvaluationService(api_client=mock_client)
        session = service.create_session(1, "/path", "/folder")

        with pytest.raises(ValueError, match="Could not extract grade"):
            service.evaluate(session, "code")
