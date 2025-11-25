import os
import re
import shutil
import subprocess
import tempfile
from typing import List, Optional, Tuple

import pyperclip
import questionary
from rich.console import Console

from src.models.challenge import Challenge
from src.templates import CHALLENGE_PROMPT_TEMPLATE


class ChallengeView:
    """
    View layer for Challenge entity.
    Handles all user interface interactions for challenges.
    """

    def __init__(self, console: Console = None):
        self.console = console or Console()

    def prompt_new_challenge(self) -> Optional[Challenge]:
        """
        Prompt user to create a new challenge.

        Returns:
            Challenge object with user input, or None if cancelled
        """
        title = questionary.text("Enter the title of the challenge:").ask()
        if not title:
            self.show_error("Title cannot be empty.")
            return None

        description = questionary.text(
            "Enter the description of the challenge:"
        ).ask()
        if not description:
            self.show_error("Description cannot be empty.")
            return None

        language = questionary.select(
            "Choose the language for the challenge:",
            choices=["python", "javascript"],
        ).ask()
        if not language:
            self.show_warning("No language selected.")
            return None

        testcases = questionary.text("Enter test cases (optional):").ask()
        if not testcases or not testcases.strip():
            testcases = None

        tags = questionary.text(
            "Enter tags (comma-separated, optional):"
        ).ask()
        if not tags or not tags.strip():
            tags = None

        return Challenge(
            title=title.strip(),
            description=description.strip(),
            language=language,
            testcases=testcases,
            tags=tags,
        )

    def prompt_challenge_selection(
        self, challenges: List[Challenge], title: str = "Select a challenge:"
    ) -> Optional[Challenge]:
        """
        Display list of challenges for user selection.

        Args:
            challenges: List of challenges to choose from
            title: Selection prompt title

        Returns:
            Selected challenge or None if cancelled
        """
        if not challenges:
            self.show_info("No challenges available.")
            return None

        challenge_choices = [f"ID: {c.id} - {c.title}" for c in challenges]

        selected = questionary.select(title, choices=challenge_choices).ask()
        if not selected:
            self.show_warning("No challenge selected.")
            return None

        selected_id = int(selected.split(":")[1].strip().split(" ")[0])
        return next(c for c in challenges if c.id == selected_id)

    def show_due_challenges(self, challenges: List[Challenge]) -> None:
        """
        Display list of due challenges with their status.

        Args:
            challenges: List of due challenges to display
        """
        if not challenges:
            self.show_success("No challenges are due for review today!")
            return

        self.console.print("[bold cyan]Challenges due for review:[/bold cyan]")
        for challenge in challenges:
            tags_str = f" [Tags: {challenge.tags}]" if challenge.tags else ""
            self.console.print(
                f"[bold yellow]ID {challenge.id}[/bold yellow]: "
                f"{challenge.title} (Language: {challenge.language}){tags_str}"
            )

    def show_all_challenges(self, challenges: List[Challenge]) -> None:
        """
        Display list of all challenges with their metadata.

        Args:
            challenges: List of challenges to display
        """
        if not challenges:
            self.show_success("No challenges in the database yet!")
            return

        self.console.print("[bold cyan]All Challenges:[/bold cyan]")
        for challenge in challenges:
            tags_str = f", Tags: {challenge.tags}" if challenge.tags else ""
            self.console.print(
                f"[bold yellow]ID {challenge.id}[/bold yellow]: "
                f"{challenge.title} "
                f"(Language: {challenge.language}, "
                f"Interval: {challenge.interval}, "
                f"Last Reviewed: {challenge.last_reviewed}{tags_str})"
            )

    def setup_challenge_workspace(
        self, challenge: Challenge
    ) -> Tuple[str, str]:
        """
        Create a workspace folder and files for the challenge.

        Args:
            challenge: Challenge to set up workspace for

        Returns:
            Tuple of (folder_path, challenge_file_path)
        """
        folder_name = self._sanitize_folder_name(challenge.title)
        os.makedirs(folder_name, exist_ok=True)

        if challenge.language == "python":
            challenge_file_path = self._setup_python_files(
                challenge, folder_name
            )
        elif challenge.language == "javascript":
            challenge_file_path = self._setup_javascript_files(
                challenge, folder_name
            )
        else:
            raise ValueError(f"Unsupported language: {challenge.language}")

        return folder_name, challenge_file_path

    def open_challenge_in_editor(
        self, folder_path: str, challenge_file_path: str
    ) -> None:
        """
        Open the challenge workspace in the appropriate editor.

        Args:
            folder_path: Path to the challenge folder
            challenge_file_path: Path to the main challenge file
        """
        editor = os.getenv("EDITOR", "nvim")

        if editor == "code":
            if os.path.isdir(folder_path):
                subprocess.run(["code", folder_path])
            else:
                self.show_error("Challenge folder does not exist!")
                return

            input("Press ENTER once the challenge is solved...")
        else:
            os.system(f"{editor} {challenge_file_path}")

    def show_evaluation_prompt(self, challenge_file_path: str) -> str:
        """
        Generate and display the evaluation prompt for the challenge.
        Copies the prompt to clipboard.

        Args:
            challenge_file_path: Path to the challenge solution file

        Returns:
            The generated prompt
        """
        try:
            with open(challenge_file_path, "r", encoding="utf-8") as f:
                challenge_content = f.read()

            prompt = CHALLENGE_PROMPT_TEMPLATE.format(
                challenge_content=challenge_content
            )

            pyperclip.copy(prompt)

            self.console.print("[bold cyan]Evaluation Prompt:[/bold cyan]\n")
            self.console.print(prompt.strip())
            self.show_success("Prompt copied to clipboard!")

            return prompt
        except Exception as e:
            self.show_error(f"Error reading challenge file: {e}")
            return ""

    def cleanup_workspace(self, folder_path: str) -> None:
        """
        Clean up the challenge workspace folder.

        Args:
            folder_path: Path to the folder to remove
        """
        try:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
        except Exception as e:
            self.show_warning(f"Could not clean up workspace: {e}")

    def prompt_grade_input(self) -> Optional[float]:
        """
        Prompt user for grade input (0-3).

        Returns:
            Grade as float, or None if invalid/cancelled
        """
        grade_input = questionary.text(
            "Enter your score for this challenge (0-3):"
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
        self, challenge: Challenge
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Prompt user for challenge updates.

        Args:
            challenge: Current challenge object

        Returns:
            Tuple of (new_title, new_description, new_language, new_testcases, new_tags) or (None, None, None, None, None) if no updates
        """
        self.console.print(
            f"[bold cyan]Current title:[/bold cyan] {challenge.title}"
        )
        self.console.print(
            f"[bold cyan]Current description:[/bold cyan] {challenge.description}"
        )
        self.console.print(
            f"[bold cyan]Current language:[/bold cyan] {challenge.language}"
        )
        self.console.print(
            f"[bold cyan]Current tags:[/bold cyan] {challenge.tags or 'None'}"
        )

        update_title = questionary.confirm("Update the title?").ask()
        new_title = None
        if update_title:
            new_title = questionary.text(
                "Enter the new title:", default=challenge.title
            ).ask()

        update_description = questionary.confirm(
            "Update the description?"
        ).ask()
        new_description = None
        if update_description:
            new_description = questionary.text(
                "Enter the new description:", default=challenge.description
            ).ask()

        update_language = questionary.confirm("Update the language?").ask()
        new_language = None
        if update_language:
            new_language = questionary.select(
                "Choose the new language:",
                choices=["python", "javascript"],
                default=challenge.language,
            ).ask()

        update_testcases = questionary.confirm("Update the test cases?").ask()
        new_testcases = None
        if update_testcases:
            new_testcases = questionary.text(
                "Enter the new test cases:", default=challenge.testcases or ""
            ).ask()

        update_tags = questionary.confirm("Update the tags?").ask()
        new_tags = None
        if update_tags:
            new_tags = questionary.text(
                "Enter the new tags (comma-separated):", default=challenge.tags or ""
            ).ask()

        if not any(
            [
                update_title,
                update_description,
                update_language,
                update_testcases,
                update_tags,
            ]
        ):
            self.show_warning("No changes made.")
            return None, None, None, None, None

        return new_title, new_description, new_language, new_testcases, new_tags

    def prompt_testcases_input(self) -> Optional[str]:
        """
        Prompt user for test cases input.

        Returns:
            Test cases string or None if cancelled/empty
        """
        testcases = questionary.text(
            "Enter test cases (format as needed/imports aren't necessary):"
        ).ask()

        if not testcases or not testcases.strip():
            self.show_error("Test cases cannot be empty!")
            return None

        return testcases

    def prompt_delete_confirmation(self, challenge: Challenge) -> bool:
        """
        Prompt user for delete confirmation.

        Args:
            challenge: Challenge to delete

        Returns:
            True if confirmed, False otherwise
        """
        return questionary.confirm(
            f"Are you sure you want to delete this challenge? This action cannot be undone.\n"
            f"Challenge: {challenge.title}"
        ).ask()

    def _sanitize_folder_name(self, title: str) -> str:
        """
        Convert a title into a valid folder name.

        Args:
            title: Challenge title

        Returns:
            Sanitized folder name
        """
        sanitized_name = re.sub(r"[^a-zA-Z0-9\s]", "", title)
        sanitized_name = re.sub(r"\s+", "_", sanitized_name)
        return sanitized_name.lower()

    def _setup_python_files(
        self, challenge: Challenge, folder_name: str
    ) -> str:
        """
        Set up Python challenge files.

        Args:
            challenge: Challenge object
            folder_name: Name of the folder

        Returns:
            Path to the main challenge file
        """
        challenge_path = os.path.join(folder_name, "challenge.py")
        with open(challenge_path, "w", encoding="utf-8") as challenge_file:
            challenge_file.write(
                f'"""\n'
                f"Title: {challenge.title}\n\n"
                f"Description:\n{challenge.description}\n"
                f'"""\n\n\n'
                f"def {folder_name}():\n"
                f"    # Write your solution here...\n"
                f"    pass\n"
            )

        if challenge.testcases:
            test_path = os.path.join(folder_name, "test_challenge.py")
            with open(test_path, "w", encoding="utf-8") as test_file:
                imports = (
                    f"import pytest\n\nfrom challenge import {folder_name}\n"
                )
                test_file.write(imports)
                test_file.write(challenge.testcases)

        return challenge_path

    def _setup_javascript_files(
        self, challenge: Challenge, folder_name: str
    ) -> str:
        """
        Set up JavaScript challenge files.

        Args:
            challenge: Challenge object
            folder_name: Name of the folder

        Returns:
            Path to the main challenge file
        """
        function_name = "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(folder_name.split("_"))
        )

        challenge_path = os.path.join(folder_name, "challenge.js")
        with open(challenge_path, "w", encoding="utf-8") as challenge_file:
            challenge_file.write(
                f"/*\n"
                f"Title: {challenge.title}\n\n"
                f"Description:\n{challenge.description}\n"
                f"*/\n\n"
                f"function {function_name}() {{\n"
                f"    // write your solution here...\n"
                f"}}\n\n"
                f"module.exports = {function_name};"
            )

        if challenge.testcases:
            test_path = os.path.join(folder_name, "challenge.test.js")
            with open(test_path, "w", encoding="utf-8") as test_file:
                test_file.write(
                    f"const {function_name} = require('./challenge');\n\n"
                    f"{challenge.testcases}\n"
                )

        return challenge_path

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

    def show_challenge_added(self, challenge: Challenge) -> None:
        """Show confirmation that challenge was added successfully."""
        self.show_success("Challenge added successfully!")
        self.console.print(f"[bold cyan]Title:[/bold cyan] {challenge.title}")
        self.console.print(
            f"[bold cyan]Language:[/bold cyan] {challenge.language}"
        )

    def show_challenge_updated(self, challenge: Challenge) -> None:
        """Show confirmation that challenge was updated successfully."""
        self.show_success("Challenge updated successfully!")

    def show_challenge_deleted(self, challenge_id: int) -> None:
        """Show confirmation that challenge was deleted successfully."""
        self.show_success(f"Challenge ID {challenge_id} has been deleted.")

    def show_challenge_reviewed(self, challenge: Challenge) -> None:
        """Show confirmation that challenge was reviewed successfully."""
        self.show_success(
            f"Challenge ID {challenge.id} has been reviewed and updated."
        )

    def show_testcases_added(self, challenge_id: int) -> None:
        """Show confirmation that test cases were added successfully."""
        self.show_success(
            f"Test cases added to challenge ID {challenge_id} successfully!"
        )
