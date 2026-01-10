from typing import Optional

from src.config import get_config
from src.models.evaluation import UserAction
from src.repositories.challenge import ChallengeRepository
from src.services.api_client import APIError
from src.services.evaluator import EvaluationService
from src.views.challenge import ChallengeView


class ChallengeController:
    """
    Controller for Challenge operations.
    Orchestrates between ChallengeRepository and ChallengeView.
    """

    def __init__(
        self,
        repository: ChallengeRepository = None,
        view: ChallengeView = None,
    ):
        self.repository = repository or ChallengeRepository()
        self.view = view or ChallengeView()

    def add_challenge(self) -> None:
        """
        Handle the complete add challenge workflow.
        - Prompt user for challenge details
        - Validate input
        - Save to database
        - Show confirmation
        """
        try:
            challenge = self.view.prompt_new_challenge()
            if not challenge:
                return

            saved_challenge = self.repository.add(challenge)
            self.view.show_challenge_added(saved_challenge)

        except Exception as e:
            self.view.show_error(f"Failed to add challenge: {str(e)}")

    def review_challenges(self) -> None:
        """
        Handle the complete review workflow with API-based evaluation.

        Flow:
        1. Get due challenges, let user select one
        2. Set up workspace and open editor
        3. Send to API for evaluation (or clipboard fallback)
        4. Display evaluation, allow dispute/refactor loop
        5. Update SM-2 with FIRST grade
        6. Clean up workspace
        """
        try:
            due_challenges = self.repository.get_due_challenges()
            if not due_challenges:
                self.view.show_success(
                    "No challenges are due for review today!"
                )
                return

            self.view.show_due_challenges(due_challenges)
            selected_challenge = self.view.prompt_challenge_selection(
                due_challenges, "Select a challenge to review:"
            )

            if not selected_challenge:
                return

            folder_path, challenge_file_path = (
                self.view.setup_challenge_workspace(selected_challenge)
            )

            try:
                self._run_evaluation_loop(
                    selected_challenge,
                    folder_path,
                    challenge_file_path,
                )
            except Exception as e:
                self.view.cleanup_workspace(folder_path)
                raise e

        except Exception as e:
            self.view.show_error(f"Failed to review challenge: {str(e)}")

    def _run_evaluation_loop(
        self,
        challenge,
        folder_path: str,
        challenge_file_path: str,
    ) -> None:
        """
        Run the evaluation loop with API or fallback to clipboard.

        Args:
            challenge: Challenge being reviewed
            folder_path: Path to workspace folder
            challenge_file_path: Path to solution file
        """
        config = get_config()

        self.view.open_challenge_in_editor(folder_path, challenge_file_path)

        if not config.api.is_configured:
            self._fallback_clipboard_evaluation(
                challenge, folder_path, challenge_file_path
            )
            return

        evaluator = None
        try:
            evaluator = EvaluationService()
            session = evaluator.create_session(
                challenge_id=challenge.id,
                challenge_file_path=challenge_file_path,
                folder_path=folder_path,
            )

            self._api_evaluation_loop(
                challenge, session, evaluator, folder_path, challenge_file_path
            )

        except APIError as e:
            self.view.show_api_error(str(e))
            if (
                config.use_clipboard_fallback
                and self.view.prompt_fallback_to_clipboard()
            ):
                self._fallback_clipboard_evaluation(
                    challenge, folder_path, challenge_file_path
                )
            else:
                self.view.cleanup_workspace(folder_path)
        finally:
            if evaluator:
                evaluator.close()

    def _api_evaluation_loop(
        self,
        challenge,
        session,
        evaluator,
        folder_path: str,
        challenge_file_path: str,
    ) -> None:
        """
        Main API evaluation loop with dispute/refactor support.
        """
        with open(challenge_file_path, "r", encoding="utf-8") as f:
            solution_content = f.read()

        self.view.clear_screen()
        with self.view.show_evaluating_spinner():
            evaluation = evaluator.evaluate(session, solution_content)
        self.view.show_evaluation_result(evaluation, session.iteration)

        while True:
            action = self.view.prompt_evaluation_action(
                session.first_grade, session.current_grade
            )

            if action == UserAction.ACCEPT:
                self.view.show_sm2_grade_info(
                    session.first_grade, session.current_grade
                )
                updated_challenge = self.repository.mark_reviewed(
                    challenge, session.get_sm2_grade()
                )
                self.view.show_challenge_reviewed(updated_challenge)

                self.view.cleanup_workspace(folder_path)
                break

            elif action == UserAction.DISPUTE:
                dispute_reason = self.view.prompt_dispute_reason()
                if dispute_reason:
                    try:
                        with self.view.show_evaluating_spinner():
                            evaluation = evaluator.dispute(
                                session, dispute_reason
                            )
                        self.view.show_evaluation_result(
                            evaluation, session.iteration
                        )
                    except APIError as e:
                        self.view.show_api_error(str(e))

            elif action == UserAction.REFACTOR:
                self.view.open_challenge_in_editor(
                    folder_path, challenge_file_path
                )

                with open(challenge_file_path, "r", encoding="utf-8") as f:
                    new_solution = f.read()

                self.view.clear_screen()
                try:
                    with self.view.show_evaluating_spinner():
                        evaluation = evaluator.refactor_evaluate(
                            session, new_solution
                        )
                    self.view.show_evaluation_result(
                        evaluation, session.iteration
                    )
                except APIError as e:
                    self.view.show_api_error(str(e))

    def _fallback_clipboard_evaluation(
        self,
        challenge,
        folder_path: str,
        challenge_file_path: str,
    ) -> None:
        """
        Original clipboard-based evaluation flow (fallback).
        """
        self.view.show_evaluation_prompt(challenge_file_path)
        grade = self.view.prompt_grade_input()

        if grade is not None:
            updated_challenge = self.repository.mark_reviewed(
                challenge, grade
            )
            self.view.show_challenge_reviewed(updated_challenge)

        self.view.cleanup_workspace(folder_path)

    def list_challenges(self) -> None:
        """
        Handle listing all challenges.
        - Fetch all challenges from repository
        - Display via view
        """
        try:
            challenges = self.repository.get_all()
            self.view.show_all_challenges(challenges)

        except Exception as e:
            self.view.show_error(f"Failed to retrieve challenges: {str(e)}")

    def update_challenge(self) -> None:
        """
        Handle the complete update workflow.
        - Get all challenges
        - Let user select one
        - Show current values
        - Get new values
        - Save updates
        - Show confirmation
        """
        try:
            challenges = self.repository.get_all()
            if not challenges:
                self.view.show_info("No challenges in the database to update!")
                return

            selected_challenge = self.view.prompt_challenge_selection(
                challenges, "Select a challenge to update:"
            )

            if not selected_challenge:
                return

            new_title, new_description, new_language, new_testcases, new_tags = (
                self.view.prompt_update_fields(selected_challenge)
            )

            if all(
                x is None
                for x in [
                    new_title,
                    new_description,
                    new_language,
                    new_testcases,
                    new_tags,
                ]
            ):
                return

            updated_challenge = self.repository.update(
                selected_challenge,
                new_title,
                new_description,
                new_language,
                new_testcases,
                new_tags,
            )
            self.view.show_challenge_updated(updated_challenge)

        except Exception as e:
            self.view.show_error(f"Failed to update challenge: {str(e)}")

    def delete_challenge(self) -> None:
        """
        Handle the complete delete workflow.
        - Get all challenges
        - Let user select one
        - Confirm deletion
        - Delete from database
        - Show confirmation
        """
        try:
            challenges = self.repository.get_all()
            if not challenges:
                self.view.show_info("No challenges in the database to delete!")
                return

            selected_challenge = self.view.prompt_challenge_selection(
                challenges, "Select a challenge to delete:"
            )

            if not selected_challenge:
                return

            if not self.view.prompt_delete_confirmation(selected_challenge):
                self.view.show_warning("Deletion cancelled.")
                return

            success = self.repository.delete(selected_challenge.id)
            if success:
                self.view.show_challenge_deleted(selected_challenge.id)
            else:
                self.view.show_error(
                    f"Failed to delete challenge ID {selected_challenge.id}"
                )

        except Exception as e:
            self.view.show_error(f"Failed to delete challenge: {str(e)}")

    def add_testcases(self) -> None:
        """
        Handle adding test cases to challenges that don't have them.
        - Get challenges without test cases
        - Let user select one
        - Get test cases input
        - Update challenge
        - Show confirmation
        """
        try:
            challenges_without_testcases = (
                self.repository.get_challenges_without_testcases()
            )

            if not challenges_without_testcases:
                self.view.show_success(
                    "All challenges already have test cases!"
                )
                return

            selected_challenge = self.view.prompt_challenge_selection(
                challenges_without_testcases,
                "Select a challenge to add testcases:",
            )

            if not selected_challenge:
                return

            testcases = self.view.prompt_testcases_input()
            if not testcases:
                return

            updated_challenge = self.repository.update_testcases(
                selected_challenge, testcases
            )
            self.view.show_testcases_added(updated_challenge.id)

        except Exception as e:
            self.view.show_error(f"Failed to add test cases: {str(e)}")

    def get_challenge_stats(self) -> Optional[dict]:
        """
        Get statistics about challenges for dashboard/reporting.

        Returns:
            Dictionary with challenge statistics or None if error
        """
        try:
            all_challenges = self.repository.get_all()
            due_challenges = self.repository.get_due_challenges()
            challenges_without_testcases = (
                self.repository.get_challenges_without_testcases()
            )

            total_count = len(all_challenges)
            due_count = len(due_challenges)
            without_testcases_count = len(challenges_without_testcases)

            python_count = len(
                [c for c in all_challenges if c.language == "python"]
            )
            javascript_count = len(
                [c for c in all_challenges if c.language == "javascript"]
            )

            return {
                "total_challenges": total_count,
                "due_for_review": due_count,
                "without_testcases": without_testcases_count,
                "python_challenges": python_count,
                "javascript_challenges": javascript_count,
                "average_interval": (
                    sum(c.interval for c in all_challenges) / total_count
                    if total_count > 0
                    else 0
                ),
                "average_ease_factor": (
                    sum(c.ease_factor for c in all_challenges) / total_count
                    if total_count > 0
                    else 0
                ),
            }
        except Exception as e:
            self.view.show_error(
                f"Failed to get challenge statistics: {str(e)}"
            )
            return None
