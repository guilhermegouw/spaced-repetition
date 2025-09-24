import random
from typing import List, Optional, Tuple

import questionary
from rich.console import Console

from models.mcq_question import MCQQuestion


class MCQView:
    """
    View layer for MCQ Question entity.
    Handles all user interface interactions for MCQ questions.
    """

    def __init__(self, console: Console = None):
        self.console = console or Console()

    def prompt_new_mcq_question(self) -> Optional[MCQQuestion]:
        """
        Prompt user to create a new MCQ question.

        Returns:
            MCQQuestion object with user input, or None if cancelled
        """
        question = questionary.text("Enter the question:").ask()
        if not question:
            self.show_error("Question cannot be empty.")
            return None

        question_type = questionary.select(
            "What type of question is this?", choices=["mcq", "true_false"]
        ).ask()

        if not question_type:
            self.show_warning("No question type selected.")
            return None

        if question_type == "true_false":
            return self._prompt_true_false_question(question)
        else:
            return self._prompt_mcq_question(question)

    def _prompt_true_false_question(
        self, question: str
    ) -> Optional[MCQQuestion]:
        """
        Prompt for true/false question details.

        Args:
            question: The question text

        Returns:
            MCQQuestion object or None if cancelled
        """
        option_a = "True"
        option_b = "False"

        correct_option = questionary.select(
            "Which is the correct answer?", choices=["a (True)", "b (False)"]
        ).ask()

        if not correct_option:
            self.show_warning("No correct option selected.")
            return None

        correct_option = correct_option[0]

        self.console.print(
            "\n[bold cyan]Now let's add explanations for each option:[/bold cyan]"
        )

        if correct_option == "a":
            explanation_a = questionary.text(
                "Explain why 'True' is correct:"
            ).ask()
            explanation_b = questionary.text(
                "Explain why 'False' is incorrect:"
            ).ask()
        else:
            explanation_a = questionary.text(
                "Explain why 'True' is incorrect:"
            ).ask()
            explanation_b = questionary.text(
                "Explain why 'False' is correct:"
            ).ask()

        tags = questionary.text(
            "Enter tags (comma-separated, optional):"
        ).ask()
        if not tags or not tags.strip():
            tags = None

        return MCQQuestion(
            question=question,
            question_type="true_false",
            option_a=option_a,
            option_b=option_b,
            correct_option=correct_option,
            explanation_a=explanation_a,
            explanation_b=explanation_b,
            tags=tags,
        )

    def _prompt_mcq_question(self, question: str) -> Optional[MCQQuestion]:
        """
        Prompt for MCQ question details.

        Args:
            question: The question text

        Returns:
            MCQQuestion object or None if cancelled
        """
        option_a = questionary.text("Enter option A:").ask()
        option_b = questionary.text("Enter option B:").ask()
        option_c = questionary.text("Enter option C:").ask()
        option_d = questionary.text("Enter option D:").ask()

        if not all([option_a, option_b, option_c, option_d]):
            self.show_error("All four options are required for MCQ questions.")
            return None

        choices = [
            f"a) {option_a}",
            f"b) {option_b}",
            f"c) {option_c}",
            f"d) {option_d}",
        ]

        correct_choice = questionary.select(
            "Which option is correct?", choices=choices
        ).ask()

        if not correct_choice:
            self.show_warning("No correct option selected.")
            return None

        correct_option = correct_choice[0]

        self.console.print(
            "\n[bold cyan]Now let's add explanations for each option:[/bold cyan]"
        )

        explanation_a = questionary.text(
            f"Explain option A ({option_a}) - {'CORRECT' if correct_option == 'a' else 'Why it is wrong'}:"
        ).ask()

        explanation_b = questionary.text(
            f"Explain option B ({option_b}) - {'CORRECT' if correct_option == 'b' else 'Why it is wrong'}:"
        ).ask()

        explanation_c = questionary.text(
            f"Explain option C ({option_c}) - {'CORRECT' if correct_option == 'c' else 'Why it is wrong'}:"
        ).ask()

        explanation_d = questionary.text(
            f"Explain option D ({option_d}) - {'CORRECT' if correct_option == 'd' else 'Why it is wrong'}:"
        ).ask()

        tags = questionary.text(
            "Enter tags (comma-separated, optional):"
        ).ask()
        if not tags or not tags.strip():
            tags = None

        return MCQQuestion(
            question=question,
            question_type="mcq",
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option,
            explanation_a=explanation_a,
            explanation_b=explanation_b,
            explanation_c=explanation_c,
            explanation_d=explanation_d,
            tags=tags,
        )

    def prompt_mcq_selection(
        self,
        mcq_questions: List[MCQQuestion],
        title: str = "Select an MCQ question:",
    ) -> Optional[MCQQuestion]:
        """
        Display list of MCQ questions for user selection.

        Args:
            mcq_questions: List of MCQ questions to choose from
            title: Selection prompt title

        Returns:
            Selected MCQ question or None if cancelled
        """
        if not mcq_questions:
            self.show_info("No MCQ questions available.")
            return None

        question_choices = [
            f"ID: {q.id} - {q.question} (Type: {q.question_type})"
            for q in mcq_questions
        ]

        selected = questionary.select(title, choices=question_choices).ask()
        if not selected:
            self.show_warning("No MCQ question selected.")
            return None

        # Extract ID from selection
        selected_id = int(selected.split(":")[1].strip().split(" ")[0])
        return next(q for q in mcq_questions if q.id == selected_id)

    def show_due_mcq_questions(self, mcq_questions: List[MCQQuestion]) -> None:
        """
        Display list of due MCQ questions with their status.

        Args:
            mcq_questions: List of due MCQ questions to display
        """
        if not mcq_questions:
            self.show_success("No MCQ questions are due for review today!")
            return

        self.console.print(
            "[bold cyan]MCQ Questions due for review (sorted by priority):[/bold cyan]"
        )
        for mcq_question in mcq_questions:
            self.console.print(
                f"[bold yellow]ID {mcq_question.id}[/bold yellow]: "
                f"{mcq_question.question} (Type: {mcq_question.question_type})"
            )

    def show_all_mcq_questions(self, mcq_questions: List[MCQQuestion]) -> None:
        """
        Display list of all MCQ questions with their metadata.

        Args:
            mcq_questions: List of MCQ questions to display
        """
        if not mcq_questions:
            self.show_success("No MCQ questions in the database yet!")
            return

        self.console.print("[bold cyan]All MCQ Questions:[/bold cyan]")
        for mcq_question in mcq_questions:
            self.console.print(
                f"[bold yellow]ID {mcq_question.id}[/bold yellow]: "
                f"{mcq_question.question} "
                f"(Type: {mcq_question.question_type}, "
                f"Tags: {mcq_question.tags or 'None'}, "
                f"Interval: {mcq_question.interval}, "
                f"Last Reviewed: {mcq_question.last_reviewed or 'Never'})"
            )

    def display_mcq_question_for_review(
        self,
        mcq_question: MCQQuestion,
        available_options: List[Tuple[str, str]],
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Display an MCQ question for review with randomized options.

        Args:
            mcq_question: MCQ question to display
            available_options: List of (option_letter, option_text) tuples

        Returns:
            Tuple of (user_choice_original_letter, confidence_level) or (None, None) if cancelled
        """
        self.console.print(
            f"\n[bold cyan]Question:[/bold cyan] {mcq_question.question}"
        )
        self.console.print(
            f"[bold cyan]Type:[/bold cyan] {mcq_question.question_type}"
        )
        if mcq_question.tags:
            self.console.print(
                f"[bold cyan]Tags:[/bold cyan] {mcq_question.tags}"
            )

        randomized_options = available_options.copy()
        random.shuffle(randomized_options)
        self.console.print("\n[bold yellow]Options:[/bold yellow]")
        display_choices = []
        option_mapping = {}

        for i, (original_letter, option_text) in enumerate(randomized_options):
            display_letter = chr(ord("a") + i)  # a, b, c, d for display
            option_mapping[display_letter] = original_letter
            self.console.print(f"  {display_letter}) {option_text}")
            display_choices.append(f"{display_letter}) {option_text}")

        user_choice = questionary.select(
            "\nWhat is your answer?", choices=display_choices
        ).ask()

        if not user_choice:
            self.show_warning("No answer selected.")
            return None, None

        user_answer_display = user_choice[0]
        user_answer_original = option_mapping[user_answer_display]

        confidence = questionary.select(
            "How confident are you in your answer?",
            choices=["low", "medium", "high"],
        ).ask()

        if not confidence:
            self.show_warning("No confidence level selected.")
            return None, None

        return user_answer_original, confidence

    def show_mcq_feedback(
        self,
        mcq_question: MCQQuestion,
        user_choice: str,
        confidence: str,
        is_correct: bool,
        get_option_text_func,
        get_explanation_func,
    ) -> None:
        """
        Display feedback after MCQ question review.

        Args:
            mcq_question: The MCQ question that was answered
            user_choice: User's selected option letter
            confidence: User's confidence level
            is_correct: Whether the answer was correct
            get_option_text_func: Function to get option text
            get_explanation_func: Function to get explanation
        """
        self.console.print(f"\n[bold cyan]=== FEEDBACK ===[/bold cyan]")

        user_option_text = get_option_text_func(mcq_question, user_choice)
        user_explanation = get_explanation_func(mcq_question, user_choice)

        if user_explanation:
            self._display_explanation(
                user_choice,
                user_option_text,
                user_explanation,
                is_correct,
                True,
            )

        if not is_correct:
            correct_option_text = get_option_text_func(
                mcq_question, mcq_question.correct_option
            )
            correct_explanation = get_explanation_func(
                mcq_question, mcq_question.correct_option
            )

            if correct_explanation:
                self._display_explanation(
                    mcq_question.correct_option,
                    correct_option_text,
                    correct_explanation,
                    True,
                    False,
                )

        self.console.print(
            f"\n[bold cyan]Your confidence:[/bold cyan] {confidence}"
        )

        if not is_correct and confidence == "high":
            self.show_warning(
                "⚠️  High confidence with wrong answer detected - applying enhanced penalty to combat misconception."
            )
        elif is_correct and confidence == "low":
            self.show_info(
                "ℹ️  Correct but uncertain - will progress conservatively to build confidence."
            )

    def _display_explanation(
        self,
        option_letter: str,
        option_text: str,
        explanation: str,
        is_correct: bool,
        is_user_choice: bool,
    ) -> None:
        """
        Helper function to display explanations with appropriate formatting.

        Args:
            option_letter: The option letter
            option_text: The option text
            explanation: The explanation text
            is_correct: Whether this option is correct
            is_user_choice: Whether this was the user's choice
        """
        if is_user_choice:
            if is_correct:
                self.console.print(
                    f"\n[bold green]✓ Your choice: {option_letter.upper()}) {option_text}[/bold green]"
                )
                self.console.print(
                    f"[bold green]Why this is correct:[/bold green] {explanation}"
                )
            else:
                self.console.print(
                    f"\n[bold red]✗ Your choice: {option_letter.upper()}) {option_text}[/bold red]"
                )
                self.console.print(
                    f"[bold red]Why this is wrong:[/bold red] {explanation}"
                )
        elif is_correct and not is_user_choice:
            self.console.print(
                f"\n[bold cyan]✓ Correct answer: {option_letter.upper()}) {option_text}[/bold cyan]"
            )
            self.console.print(
                f"[bold cyan]Why this is correct:[/bold cyan] {explanation}"
            )

    def prompt_continue_review(self) -> bool:
        """
        Ask user if they want to review another MCQ question.

        Returns:
            True if user wants to continue, False otherwise
        """
        return questionary.confirm("Review another MCQ question?").ask()

    def prompt_update_fields(
        self, mcq_question: MCQQuestion
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Prompt user for MCQ question updates.

        Args:
            mcq_question: Current MCQ question object

        Returns:
            Tuple of (new_question_text, new_tags) or (None, None) if no updates
        """
        self.console.print(
            f"[bold cyan]Current question:[/bold cyan] {mcq_question.question}"
        )
        self.console.print(
            f"[bold cyan]Current type:[/bold cyan] {mcq_question.question_type}"
        )
        self.console.print(
            f"[bold cyan]Current tags:[/bold cyan] {mcq_question.tags or 'None'}"
        )

        update_question = questionary.confirm(
            "Update the question text?"
        ).ask()
        new_question_text = None
        if update_question:
            new_question_text = questionary.text(
                "Enter the new question text:", default=mcq_question.question
            ).ask()

        update_tags = questionary.confirm("Update the tags?").ask()
        new_tags = None
        if update_tags:
            current_tags = mcq_question.tags or ""
            new_tags = questionary.text(
                "Enter the new tags (comma-separated):", default=current_tags
            ).ask()
            if not new_tags or not new_tags.strip():
                new_tags = None

        if not update_question and not update_tags:
            self.show_warning("No changes made.")
            return None, None

        return new_question_text, new_tags

    def prompt_delete_confirmation(self, mcq_question: MCQQuestion) -> bool:
        """
        Prompt user for delete confirmation.

        Args:
            mcq_question: MCQ question to delete

        Returns:
            True if confirmed, False otherwise
        """
        return questionary.confirm(
            f"Are you sure you want to delete this MCQ question? This action cannot be undone.\n"
            f"Question: {mcq_question.question}"
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

    def show_mcq_question_added(self, mcq_question: MCQQuestion) -> None:
        """Show confirmation that MCQ question was added successfully."""
        self.show_success("MCQ question added successfully!")
        self.console.print(
            f"[bold cyan]Question:[/bold cyan] {mcq_question.question}"
        )
        self.console.print(
            f"[bold cyan]Type:[/bold cyan] {mcq_question.question_type}"
        )
        self.console.print(
            f"[bold cyan]Correct answer:[/bold cyan] {mcq_question.correct_option.upper()}"
        )
        if mcq_question.tags:
            self.console.print(
                f"[bold cyan]Tags:[/bold cyan] {mcq_question.tags}"
            )

    def show_mcq_question_updated(self, mcq_question: MCQQuestion) -> None:
        """Show confirmation that MCQ question was updated successfully."""
        self.show_success("MCQ question updated successfully!")

    def show_mcq_question_deleted(self, mcq_id: int) -> None:
        """Show confirmation that MCQ question was deleted successfully."""
        self.show_success(f"MCQ question ID {mcq_id} has been deleted.")

    def show_mcq_question_reviewed(self, mcq_question: MCQQuestion) -> None:
        """Show confirmation that MCQ question was reviewed successfully."""
        self.show_success("Question updated successfully!")
