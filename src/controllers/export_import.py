"""Controllers for export and import operations."""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

from src.models.challenge import Challenge
from src.models.mcq import MCQQuestion
from src.models.question import Question
from src.repositories.challenge import ChallengeRepository
from src.repositories.mcq import MCQRepository
from src.repositories.question import QuestionRepository
from src.utils.json_schema import (
    ExportSchema,
    serialize_challenge,
    serialize_mcq,
    serialize_question,
    validate_import_data,
)


class ExportController:
    """
    Controller for exporting questions, challenges, and MCQs to JSON.
    """

    def __init__(
        self,
        question_repo: QuestionRepository = None,
        challenge_repo: ChallengeRepository = None,
        mcq_repo: MCQRepository = None,
        console: Console = None,
    ):
        self.question_repo = question_repo or QuestionRepository()
        self.challenge_repo = challenge_repo or ChallengeRepository()
        self.mcq_repo = mcq_repo or MCQRepository()
        self.console = console or Console()

    def export_all(
        self,
        output_file: Optional[str] = None,
        item_type: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> None:
        """
        Export questions, challenges, and/or MCQs to JSON file.

        Args:
            output_file: Output file path (default: backup_YYYY-MM-DD.json)
            item_type: Filter by type (questions/challenges/mcq)
            tags: Filter by tags (comma-separated)
        """
        try:
            # Determine output file
            if not output_file:
                timestamp = datetime.now().strftime("%Y-%m-%d")
                output_file = f"backup_{timestamp}.json"

            # Fetch data based on filters
            questions = []
            challenges = []
            mcq_questions = []

            if not item_type or item_type == "questions":
                questions = self._get_questions(tags)

            if not item_type or item_type == "challenges":
                challenges = self._get_challenges(tags)

            if not item_type or item_type == "mcq":
                mcq_questions = self._get_mcq_questions(tags)

            # Serialize to JSON
            export_data = ExportSchema(
                questions=[serialize_question(q) for q in questions],
                challenges=[serialize_challenge(c) for c in challenges],
                mcq_questions=[serialize_mcq(m) for m in mcq_questions],
            )

            # Write to file
            output_path = Path(output_file)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data.dict(), f, indent=2, ensure_ascii=False)

            # Show summary
            total = (
                len(questions) + len(challenges) + len(mcq_questions)
            )
            self.console.print(
                f"[bold green]✓ Exported {total} items to {output_file}[/bold green]"
            )
            self.console.print(
                f"  Questions: {len(questions)}, "
                f"Challenges: {len(challenges)}, "
                f"MCQs: {len(mcq_questions)}"
            )

        except Exception as e:
            self.console.print(f"[bold red]✗ Export failed: {e}[/bold red]")

    def _get_questions(self, tags: Optional[str]):
        """Get questions based on tag filter."""
        if tags:
            return self.question_repo.get_by_tags(tags)
        return self.question_repo.get_all()

    def _get_challenges(self, tags: Optional[str]):
        """Get challenges based on tag filter."""
        if tags:
            return self.challenge_repo.get_by_tags(tags)
        return self.challenge_repo.get_all()

    def _get_mcq_questions(self, tags: Optional[str]):
        """Get MCQ questions based on tag filter."""
        if tags:
            return self.mcq_repo.get_by_tags(tags)
        return self.mcq_repo.get_all()


class ImportController:
    """
    Controller for importing questions, challenges, and MCQs from JSON.
    """

    def __init__(
        self,
        question_repo: QuestionRepository = None,
        challenge_repo: ChallengeRepository = None,
        mcq_repo: MCQRepository = None,
        console: Console = None,
    ):
        self.question_repo = question_repo or QuestionRepository()
        self.challenge_repo = challenge_repo or ChallengeRepository()
        self.mcq_repo = mcq_repo or MCQRepository()
        self.console = console or Console()

    def import_from_file(
        self, input_file: str, skip_duplicates: bool = True
    ) -> None:
        """
        Import questions, challenges, and MCQs from JSON file.

        Args:
            input_file: Input file path
            skip_duplicates: If True, skip items with matching content (default: True)
        """
        try:
            # Read and validate JSON
            input_path = Path(input_file)
            if not input_path.exists():
                self.console.print(
                    f"[bold red]✗ File not found: {input_file}[/bold red]"
                )
                return

            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            validated_data = validate_import_data(data)

            # Import each type
            questions_imported = self._import_questions(
                validated_data.questions, skip_duplicates
            )
            challenges_imported = self._import_challenges(
                validated_data.challenges, skip_duplicates
            )
            mcq_imported = self._import_mcq_questions(
                validated_data.mcq_questions, skip_duplicates
            )

            # Show summary
            total = questions_imported + challenges_imported + mcq_imported
            self.console.print(
                f"[bold green]✓ Imported {total} items from {input_file}[/bold green]"
            )
            self.console.print(
                f"  Questions: {questions_imported}, "
                f"Challenges: {challenges_imported}, "
                f"MCQs: {mcq_imported}"
            )

        except ValueError as e:
            self.console.print(f"[bold red]✗ Invalid JSON: {e}[/bold red]")
        except Exception as e:
            self.console.print(f"[bold red]✗ Import failed: {e}[/bold red]")

    def _import_questions(
        self, questions_data: list, skip_duplicates: bool
    ) -> int:
        """Import questions from validated data."""
        count = 0
        existing_texts = set()

        if skip_duplicates:
            existing = self.question_repo.get_all()
            existing_texts = {q.question_text for q in existing}

        for q_data in questions_data:
            if skip_duplicates and q_data.get("question_text") in existing_texts:
                continue

            question = Question(
                question_text=q_data["question_text"],
                tags=q_data.get("tags"),
            )
            self.question_repo.add(question)
            count += 1

        return count

    def _import_challenges(
        self, challenges_data: list, skip_duplicates: bool
    ) -> int:
        """Import challenges from validated data."""
        count = 0
        existing_titles = set()

        if skip_duplicates:
            existing = self.challenge_repo.get_all()
            existing_titles = {c.title for c in existing}

        for c_data in challenges_data:
            if skip_duplicates and c_data.get("title") in existing_titles:
                continue

            challenge = Challenge(
                title=c_data["title"],
                description=c_data["description"],
                language=c_data["language"],
                testcases=c_data.get("testcases"),
                tags=c_data.get("tags"),
            )
            self.challenge_repo.add(challenge)
            count += 1

        return count

    def _import_mcq_questions(
        self, mcq_data: list, skip_duplicates: bool
    ) -> int:
        """Import MCQ questions from validated data."""
        count = 0
        existing_questions = set()

        if skip_duplicates:
            existing = self.mcq_repo.get_all()
            existing_questions = {m.question for m in existing}

        for m_data in mcq_data:
            if skip_duplicates and m_data.get("question") in existing_questions:
                continue

            mcq = MCQQuestion(
                question=m_data["question"],
                question_type=m_data["question_type"],
                option_a=m_data["option_a"],
                option_b=m_data["option_b"],
                option_c=m_data.get("option_c"),
                option_d=m_data.get("option_d"),
                correct_option=m_data["correct_option"],
                explanation_a=m_data.get("explanation_a"),
                explanation_b=m_data.get("explanation_b"),
                explanation_c=m_data.get("explanation_c"),
                explanation_d=m_data.get("explanation_d"),
                tags=m_data.get("tags"),
            )
            self.mcq_repo.add(mcq)
            count += 1

        return count
