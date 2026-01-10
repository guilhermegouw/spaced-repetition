"""
Evaluation service that coordinates API calls and session management.
"""
from typing import Optional

from src.models.evaluation import (
    EvaluationResponse,
    EvaluationSession,
    Message,
)
from src.services.api_client import APIError, ZAIClient
from src.templates import (
    CHALLENGE_EVALUATION_SYSTEM_PROMPT,
    CHALLENGE_PROMPT_TEMPLATE,
)


class EvaluationService:
    """
    Manages the evaluation workflow including:
    - Creating evaluation prompts
    - Calling the API
    - Parsing responses
    - Maintaining conversation history
    """

    def __init__(self, api_client: Optional[ZAIClient] = None):
        """
        Initialize the evaluation service.

        Args:
            api_client: Optional pre-configured API client.
                        If not provided, creates one lazily.
        """
        self._client = api_client

    @property
    def client(self) -> ZAIClient:
        """Lazy initialization of API client."""
        if self._client is None:
            self._client = ZAIClient()
        return self._client

    def create_session(
        self,
        challenge_id: int,
        challenge_file_path: str,
        folder_path: str,
    ) -> EvaluationSession:
        """
        Create a new evaluation session.

        Args:
            challenge_id: ID of the challenge being evaluated
            challenge_file_path: Path to the solution file
            folder_path: Path to the workspace folder

        Returns:
            New EvaluationSession with system prompt initialized
        """
        session = EvaluationSession(
            challenge_id=challenge_id,
            challenge_file_path=challenge_file_path,
            folder_path=folder_path,
        )
        session.add_system_prompt(CHALLENGE_EVALUATION_SYSTEM_PROMPT)
        return session

    def evaluate(
        self,
        session: EvaluationSession,
        solution_content: str,
    ) -> EvaluationResponse:
        """
        Send solution for evaluation.

        Args:
            session: Current evaluation session
            solution_content: The code to evaluate

        Returns:
            Parsed evaluation response
        """
        prompt = CHALLENGE_PROMPT_TEMPLATE.format(
            challenge_content=solution_content
        )
        session.add_user_message(prompt)

        response_text = self.client.chat_completion(session.messages)
        session.add_assistant_response(response_text)

        evaluation = EvaluationResponse.parse_from_response(response_text)
        session.record_evaluation(evaluation.grade)

        return evaluation

    def dispute(
        self,
        session: EvaluationSession,
        dispute_reason: str,
    ) -> EvaluationResponse:
        """
        Submit a dispute with explanation.

        Args:
            session: Current evaluation session
            dispute_reason: User's explanation for disagreement

        Returns:
            New evaluation response
        """
        dispute_prompt = (
            f"I respectfully disagree with your evaluation. "
            f"Here is my reasoning:\n\n{dispute_reason}\n\n"
            f"Please reconsider your evaluation based on this feedback."
        )
        session.add_user_message(dispute_prompt)

        response_text = self.client.chat_completion(session.messages)
        session.add_assistant_response(response_text)

        evaluation = EvaluationResponse.parse_from_response(response_text)
        session.record_evaluation(evaluation.grade)

        return evaluation

    def refactor_evaluate(
        self,
        session: EvaluationSession,
        new_solution_content: str,
    ) -> EvaluationResponse:
        """
        Submit refactored solution for re-evaluation.

        Args:
            session: Current evaluation session
            new_solution_content: The refactored code

        Returns:
            New evaluation response
        """
        refactor_prompt = (
            f"I have refactored my solution based on your feedback. "
            f"Here is my updated code:\n\n{new_solution_content}\n\n"
            f"Please re-evaluate this improved solution."
        )
        session.add_user_message(refactor_prompt)

        response_text = self.client.chat_completion(session.messages)
        session.add_assistant_response(response_text)

        evaluation = EvaluationResponse.parse_from_response(response_text)
        session.record_evaluation(evaluation.grade)

        return evaluation

    def close(self) -> None:
        """Clean up resources."""
        if self._client:
            self._client.close()
