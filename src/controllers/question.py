from typing import Optional

from rich.console import Console

from src.models.question import Question
from src.repositories.question import QuestionRepository
from src.views.question import QuestionView


class QuestionController:
    """
    Controller for Question operations.
    Orchestrates between QuestionRepository and QuestionView.
    """

    def __init__(
        self, repository: QuestionRepository = None, view: QuestionView = None
    ):
        self.repository = repository or QuestionRepository()
        self.view = view or QuestionView()

    def add_question(self) -> None:
        """
        Handle the complete add question workflow.
        - Prompt user for question details
        - Validate input
        - Save to database
        - Show confirmation
        """
        try:
            question = self.view.prompt_new_question()
            if not question:
                return

            saved_question = self.repository.add(question)
            self.view.show_question_added(saved_question)

        except Exception as e:
            self.view.show_error(f"Failed to add question: {str(e)}")

    def review_questions(self) -> None:
        """
        Handle the complete review workflow.
        - Get due questions
        - Let user select one
        - Open editor for answer
        - Generate evaluation prompt
        - Get grade and update SM-2 values
        """
        try:
            due_questions = self.repository.get_due_questions()
            if not due_questions:
                self.view.show_success(
                    "No questions are due for review today!"
                )
                return

            self.view.show_due_questions(due_questions)
            selected_question = self.view.prompt_question_selection(
                due_questions, "Select a question to answer:"
            )

            if not selected_question:
                return

            question_text, answer_text = self.view.prompt_answer_in_editor(
                selected_question
            )

            self.view.show_evaluation_prompt(question_text, answer_text)
            grade = self.view.prompt_grade_input()
            if grade is None:
                return

            updated_question = self.repository.mark_reviewed(
                selected_question, int(grade)
            )
            self.view.show_question_reviewed(updated_question)

        except Exception as e:
            self.view.show_error(f"Failed to review question: {str(e)}")

    def list_questions(self) -> None:
        """
        Handle listing all questions.
        - Fetch all questions from repository
        - Display via view
        """
        try:
            questions = self.repository.get_all()
            self.view.show_all_questions(questions)

        except Exception as e:
            self.view.show_error(f"Failed to retrieve questions: {str(e)}")

    def update_question(self) -> None:
        """
        Handle the complete update workflow.
        - Get all questions
        - Let user select one
        - Show current values
        - Get new values
        - Save updates
        - Show confirmation
        """
        try:
            questions = self.repository.get_all()
            if not questions:
                self.view.show_info("No questions in the database to update!")
                return

            selected_question = self.view.prompt_question_selection(
                questions, "Select a question to update:"
            )

            if not selected_question:
                return

            new_question_text, new_tags = self.view.prompt_update_fields(
                selected_question
            )

            if new_question_text is None and new_tags is None:
                return

            updated_question = self.repository.update(
                selected_question, new_question_text, new_tags
            )
            self.view.show_question_updated(updated_question)

        except Exception as e:
            self.view.show_error(f"Failed to update question: {str(e)}")

    def delete_question(self) -> None:
        """
        Handle the complete delete workflow.
        - Get all questions
        - Let user select one
        - Confirm deletion
        - Delete from database
        - Show confirmation
        """
        try:
            questions = self.repository.get_all()
            if not questions:
                self.view.show_info("No questions in the database to delete!")
                return

            selected_question = self.view.prompt_question_selection(
                questions, "Select a question to delete:"
            )

            if not selected_question:
                return

            if not self.view.prompt_delete_confirmation(selected_question):
                self.view.show_warning("Deletion cancelled.")
                return

            success = self.repository.delete(selected_question.id)

            if success:
                self.view.show_question_deleted(selected_question.id)
            else:
                self.view.show_error(
                    f"Failed to delete question ID {selected_question.id}"
                )

        except Exception as e:
            self.view.show_error(f"Failed to delete question: {str(e)}")

    def get_question_stats(self) -> Optional[dict]:
        """
        Get statistics about questions for dashboard/reporting.

        Returns:
            Dictionary with question statistics or None if error
        """
        try:
            all_questions = self.repository.get_all()
            due_questions = self.repository.get_due_questions()

            total_count = len(all_questions)
            due_count = len(due_questions)
            reviewed_count = len(
                [q for q in all_questions if q.last_reviewed is not None]
            )
            never_reviewed_count = total_count - reviewed_count

            return {
                "total_questions": total_count,
                "due_for_review": due_count,
                "reviewed_questions": reviewed_count,
                "never_reviewed": never_reviewed_count,
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
                f"Failed to get question statistics: {str(e)}"
            )
            return None
