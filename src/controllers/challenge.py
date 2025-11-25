from typing import Optional

from src.repositories.challenge import ChallengeRepository
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
        Handle the complete review workflow.
        - Get due challenges
        - Let user select one
        - Set up workspace and open editor
        - Generate evaluation prompt
        - Get grade and update SM-2 values
        - Clean up workspace
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
                return  # User cancelled

            folder_path, challenge_file_path = (
                self.view.setup_challenge_workspace(selected_challenge)
            )

            try:
                self.view.open_challenge_in_editor(
                    folder_path, challenge_file_path
                )

                self.view.show_evaluation_prompt(challenge_file_path)
                grade = self.view.prompt_grade_input()
                if grade is None:
                    return

                updated_challenge = self.repository.mark_reviewed(
                    selected_challenge, int(grade)
                )

                self.view.show_challenge_reviewed(updated_challenge)

            finally:
                self.view.cleanup_workspace(folder_path)

        except Exception as e:
            self.view.show_error(f"Failed to review challenge: {str(e)}")

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
