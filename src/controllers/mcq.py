from typing import Optional

from src.models.mcq import MCQQuestion
from src.repositories.mcq import MCQRepository
from src.views.mcq import MCQView


class MCQController:
    """
    Controller for MCQ Question operations.
    Orchestrates between MCQRepository and MCQView.
    """

    def __init__(self, repository: MCQRepository = None, view: MCQView = None):
        self.repository = repository or MCQRepository()
        self.view = view or MCQView()

    def add_mcq_question(self) -> None:
        """
        Handle the complete add MCQ question workflow.
        - Prompt user for question details (MCQ or True/False)
        - Handle explanations for each option
        - Validate input
        - Save to database
        - Show confirmation
        """
        try:
            mcq_question = self.view.prompt_new_mcq_question()
            if not mcq_question:
                return

            saved_question = self.repository.add(mcq_question)
            self.view.show_mcq_question_added(saved_question)

        except Exception as e:
            self.view.show_error(f"Failed to add MCQ question: {str(e)}")

    def review_mcq_questions(self) -> None:
        """
        Handle the complete MCQ review workflow with 5-step UI flow:
        1. Get list of due questions (clean display)
        2. User selects question to answer
        3. Display question with randomized options
        4. Get user answer and confidence level
        5. Show feedback and update SM-2 with penalty system
        """
        while True:
            try:
                due_questions = self.repository.get_due_questions()
                if not due_questions:
                    self.view.show_success(
                        "No MCQ questions are due for review today!"
                    )
                    return

                self.view.show_due_mcq_questions(due_questions)
                selected_question = self.view.prompt_mcq_selection(
                    due_questions, "Select a question to review:"
                )

                if not selected_question:
                    return  # User cancelled

                available_options = self.repository.get_available_options(
                    selected_question
                )
                user_choice, confidence = (
                    self.view.display_mcq_question_for_review(
                        selected_question, available_options
                    )
                )

                if not user_choice or not confidence:
                    return  # User cancelled

                is_correct = self.repository.is_correct_answer(
                    selected_question, user_choice
                )

                self.view.show_mcq_feedback(
                    selected_question,
                    user_choice,
                    confidence,
                    is_correct,
                    self.repository.get_option_text,
                    self.repository.get_explanation,
                )

                updated_question = self.repository.mark_reviewed(
                    selected_question, is_correct, confidence
                )

                self.view.show_mcq_question_reviewed(updated_question)
                if not self.view.prompt_continue_review():
                    break

            except Exception as e:
                self.view.show_error(
                    f"Failed to review MCQ question: {str(e)}"
                )
                break

    def list_mcq_questions(self) -> None:
        """
        Handle listing all MCQ questions.
        - Fetch all MCQ questions from repository
        - Display via view
        """
        try:
            mcq_questions = self.repository.get_all()
            self.view.show_all_mcq_questions(mcq_questions)

        except Exception as e:
            self.view.show_error(f"Failed to retrieve MCQ questions: {str(e)}")

    def update_mcq_question(self) -> None:
        """
        Handle the complete update workflow.
        - Get all MCQ questions
        - Let user select one
        - Show current values
        - Get new values
        - Save updates
        - Show confirmation
        """
        try:
            mcq_questions = self.repository.get_all()
            if not mcq_questions:
                self.view.show_info(
                    "No MCQ questions in the database to update!"
                )
                return

            selected_question = self.view.prompt_mcq_selection(
                mcq_questions, "Select an MCQ question to update:"
            )

            if not selected_question:
                return  # User cancelled

            new_question_text, new_tags = self.view.prompt_update_fields(
                selected_question
            )
            if new_question_text is None and new_tags is None:
                return

            updated_question = self.repository.update(
                selected_question, new_question_text, new_tags
            )
            self.view.show_mcq_question_updated(updated_question)

        except Exception as e:
            self.view.show_error(f"Failed to update MCQ question: {str(e)}")

    def delete_mcq_question(self) -> None:
        """
        Handle the complete delete workflow.
        - Get all MCQ questions
        - Let user select one
        - Confirm deletion
        - Delete from database
        - Show confirmation
        """
        try:
            mcq_questions = self.repository.get_all()
            if not mcq_questions:
                self.view.show_info(
                    "No MCQ questions in the database to delete!"
                )
                return

            selected_question = self.view.prompt_mcq_selection(
                mcq_questions, "Select an MCQ question to delete:"
            )

            if not selected_question:
                return
            if not self.view.prompt_delete_confirmation(selected_question):
                self.view.show_warning("Deletion cancelled.")
                return

            success = self.repository.delete(selected_question.id)
            if success:
                self.view.show_mcq_question_deleted(selected_question.id)
            else:
                self.view.show_error(
                    f"Failed to delete MCQ question ID {selected_question.id}"
                )

        except Exception as e:
            self.view.show_error(f"Failed to delete MCQ question: {str(e)}")

    def get_mcq_stats(self) -> Optional[dict]:
        """
        Get statistics about MCQ questions for dashboard/reporting.

        Returns:
            Dictionary with MCQ question statistics or None if error
        """
        try:
            all_questions = self.repository.get_all()
            due_questions = self.repository.get_due_questions()

            total_count = len(all_questions)
            due_count = len(due_questions)

            mcq_count = len(
                [q for q in all_questions if q.question_type == "mcq"]
            )
            true_false_count = len(
                [q for q in all_questions if q.question_type == "true_false"]
            )
            reviewed_count = len(
                [q for q in all_questions if q.last_reviewed is not None]
            )
            never_reviewed_count = total_count - reviewed_count

            return {
                "total_mcq_questions": total_count,
                "due_for_review": due_count,
                "reviewed_questions": reviewed_count,
                "never_reviewed": never_reviewed_count,
                "mcq_questions": mcq_count,
                "true_false_questions": true_false_count,
                "average_interval": (
                    sum(q.interval for q in all_questions) / total_count
                    if total_count > 0
                    else 0
                ),
                "average_ease_factor": (
                    sum(q.ease_factor for q in all_questions) / total_count
                    if total_count > 0
                    else 0
                ),
            }
        except Exception as e:
            self.view.show_error(
                f"Failed to get MCQ question statistics: {str(e)}"
            )
            return None

    def review_single_question(self, question_id: int) -> bool:
        """
        Review a specific MCQ question by ID.
        Useful for targeted review or testing.

        Args:
            question_id: ID of the question to review

        Returns:
            True if review completed successfully, False otherwise
        """
        try:
            question = self.repository.get_by_id(question_id)
            if not question:
                self.view.show_error(
                    f"No MCQ question found with ID {question_id}"
                )
                return False

            available_options = self.repository.get_available_options(question)
            user_choice, confidence = (
                self.view.display_mcq_question_for_review(
                    question, available_options
                )
            )

            if not user_choice or not confidence:
                return False

            is_correct = self.repository.is_correct_answer(
                question, user_choice
            )

            self.view.show_mcq_feedback(
                question,
                user_choice,
                confidence,
                is_correct,
                self.repository.get_option_text,
                self.repository.get_explanation,
            )

            updated_question = self.repository.mark_reviewed(
                question, is_correct, confidence
            )
            self.view.show_mcq_question_reviewed(updated_question)
            return True

        except Exception as e:
            self.view.show_error(f"Failed to review MCQ question: {str(e)}")
            return False
