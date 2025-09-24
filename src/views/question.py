import os
import tempfile
from typing import List, Optional, Tuple

import pyperclip
import questionary
from rich.console import Console

from models.question import Question
from templates import QUESTION_PROMPT_TEMPLATE


class QuestionView:
    """
    View layer for Question entity.
    Handles all user interface interactions for questions.
    """

    def __init__(self, console: Console = None):
        self.console = console or Console()

    def prompt_new_question(self) -> Optional[Question]:
        """
        Prompt user to create a new question.

        Returns:
            Question object with user input, or None if cancelled
        """
        question_text = questionary.text("Enter the question:").ask()
        if not question_text:
            self.show_error("Question cannot be empty.")
            return None

        tags = questionary.text(
            "Enter tags (comma-separated, optional):"
        ).ask()
        if not tags or not tags.strip():
            tags = None

        return Question(question_text=question_text.strip(), tags=tags)

    def prompt_question_selection(
        self, questions: List[Question], title: str = "Select a question:"
    ) -> Optional[Question]:
        """
        Display list of questions for user selection.

        Args:
            questions: List of questions to choose from
            title: Selection prompt title

        Returns:
            Selected question or None if cancelled
        """
        if not questions:
            self.show_info("No questions available.")
            return None

        question_choices = [
            f"ID: {q.id} - {q.question_text}" for q in questions
        ]

        selected = questionary.select(title, choices=question_choices).ask()
        if not selected:
            self.show_warning("No question selected.")
            return None

        selected_id = int(selected.split(":")[1].strip().split(" ")[0])
        return next(q for q in questions if q.id == selected_id)

    def show_due_questions(self, questions: List[Question]) -> None:
        """
        Display list of due questions with their status.

        Args:
            questions: List of due questions to display
        """
        if not questions:
            self.show_success("No questions are due for review today!")
            return

        self.console.print("[bold cyan]Questions due for review:[/bold cyan]")
        for question in questions:
            self.console.print(
                f"[bold yellow]ID {question.id}[/bold yellow]: "
                f"{question.question_text}"
            )

    def show_all_questions(self, questions: List[Question]) -> None:
        """
        Display list of all questions with their metadata.

        Args:
            questions: List of questions to display
        """
        if not questions:
            self.show_success("No questions in the database yet!")
            return

        self.console.print("[bold cyan]All Questions:[/bold cyan]")
        for question in questions:
            self.console.print(
                f"[bold yellow]ID {question.id}[/bold yellow]: "
                f"{question.question_text} "
                f"(Tags: {question.tags or 'None'}, "
                f"Interval: {question.interval}, "
                f"Last Reviewed: {question.last_reviewed or 'Never'})"
            )

    def prompt_answer_in_editor(self, question: Question) -> Tuple[str, str]:
        """
        Open editor for user to answer the question.

        Args:
            question: Question to answer

        Returns:
            Tuple of (question_text, answer_text)
        """
        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False
        ) as temp_file:
            temp_file.write(
                f"Question: {question.question_text}\n\n".encode("utf-8")
            )
            temp_path = temp_file.name

        os.system(f"{os.getenv('EDITOR', 'nvim')} {temp_path}")

        with open(temp_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        os.unlink(temp_path)

        lines = content.split("\n")
        question_text = lines[0].replace("Question: ", "").strip()
        answer_text = "\n".join(lines[2:]).strip()

        return question_text, answer_text

    def show_evaluation_prompt(
        self, question_text: str, answer_text: str
    ) -> str:
        """
        Generate and display the evaluation prompt for Claude.
        Copies the prompt to clipboard.

        Args:
            question_text: The question text
            answer_text: The user's answer

        Returns:
            The generated prompt
        """
        prompt = QUESTION_PROMPT_TEMPLATE.format(
            question=question_text, answer=answer_text
        )

        pyperclip.copy(prompt)

        self.console.print("[bold cyan]Evaluation Prompt:[/bold cyan]\n")
        self.console.print(prompt.strip())
        self.show_success("Prompt copied to clipboard!")

        return prompt

    def prompt_grade_input(self) -> Optional[float]:
        """
        Prompt user for grade input (0-3).

        Returns:
            Grade as float, or None if invalid/cancelled
        """
        grade_input = questionary.text(
            "Enter the average grade (0-3) received:"
        ).ask()

        if not grade_input:
            self.show_warning("No grade entered.")
            return None

        try:
            grade = float(grade_input)
            if not 0 <= grade <= 3:
                self.show_error(
                    "Invalid grade. Please enter a value between 0 and 3."
                )
                return None
            return grade
        except ValueError:
            self.show_error("Invalid input. Please enter a numeric value.")
            return None

    def prompt_update_fields(
        self, question: Question
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Prompt user for question updates.

        Args:
            question: Current question object

        Returns:
            Tuple of (new_question_text, new_tags) or (None, None) if no updates
        """
        self.console.print(
            f"[bold cyan]Current question:[/bold cyan] {question.question_text}"
        )
        self.console.print(
            f"[bold cyan]Current tags:[/bold cyan] {question.tags or 'None'}"
        )

        update_question = questionary.confirm(
            "Update the question text?"
        ).ask()
        new_question_text = None
        if update_question:
            new_question_text = questionary.text(
                "Enter the new question text:", default=question.question_text
            ).ask()

        update_tags = questionary.confirm("Update the tags?").ask()
        new_tags = None
        if update_tags:
            current_tags = question.tags or ""
            new_tags = questionary.text(
                "Enter the new tags (comma-separated):", default=current_tags
            ).ask()
            if not new_tags or not new_tags.strip():
                new_tags = None

        if not update_question and not update_tags:
            self.show_warning("No changes made.")
            return None, None

        return new_question_text, new_tags

    def prompt_delete_confirmation(self, question: Question) -> bool:
        """
        Prompt user for delete confirmation.

        Args:
            question: Question to delete

        Returns:
            True if confirmed, False otherwise
        """
        return questionary.confirm(
            f"Are you sure you want to delete this question? This action cannot be undone.\n"
            f"Question: {question.question_text}"
        ).ask()

    def show_success(self, message: str) -> None:
        """Display success message."""
        self.console.print(f"[bold green]{message}[/bold green]")

    def show_error(self, message: str) -> None:
        """Display error message."""
        self.console.print(f"[bold red]{message}[/bold red]")

    def show_warning(self, message: str) -> None:
        """Display warning message."""
        self.console.print(f"[bold yellow]{message}[/bold yellow]")

    def show_info(self, message: str) -> None:
        """Display info message."""
        self.console.print(f"[bold cyan]{message}[/bold cyan]")

    def show_question_added(self, question: Question) -> None:
        """Show confirmation that question was added successfully."""
        self.show_success("Question added successfully!")
        self.console.print(
            f"[bold cyan]Question:[/bold cyan] {question.question_text}"
        )
        if question.tags:
            self.console.print(f"[bold cyan]Tags:[/bold cyan] {question.tags}")

    def show_question_updated(self, question: Question) -> None:
        """Show confirmation that question was updated successfully."""
        self.show_success("Question updated successfully!")

    def show_question_deleted(self, question_id: int) -> None:
        """Show confirmation that question was deleted successfully."""
        self.show_success(f"Question ID {question_id} has been deleted.")

    def show_question_reviewed(self, question: Question) -> None:
        """Show confirmation that question was reviewed successfully."""
        self.show_success(
            f"Question ID {question.id} has been reviewed and updated."
        )
