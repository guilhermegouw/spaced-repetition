from datetime import date
from typing import List, Optional, Tuple

from src.db.database_manager import DatabaseManager
from src.models.mcq import MCQQuestion
from src.models.sm2 import SM2Calculator


class MCQRepository:
    """
    Repository for MCQQuestion entity.
    Contains all business logic and database operations for MCQ questions.
    """

    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
        self.sm2_calculator = SM2Calculator()

    def add(self, mcq_question: MCQQuestion) -> MCQQuestion:
        """
        Add a new MCQ question to the database.

        Args:
            mcq_question: MCQQuestion object to add

        Returns:
            MCQQuestion object with populated ID
        """
        insert_query = """
        INSERT INTO mcq_questions (
            question, question_type, option_a, option_b, option_c, option_d, 
            correct_option, explanation_a, explanation_b, explanation_c, explanation_d,
            tags, last_reviewed, interval, ease_factor
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            mcq_question.id = self.db.execute_query(
                insert_query,
                (
                    mcq_question.question,
                    mcq_question.question_type,
                    mcq_question.option_a,
                    mcq_question.option_b,
                    mcq_question.option_c,
                    mcq_question.option_d,
                    mcq_question.correct_option,
                    mcq_question.explanation_a,
                    mcq_question.explanation_b,
                    mcq_question.explanation_c,
                    mcq_question.explanation_d,
                    mcq_question.tags,
                    mcq_question.last_reviewed.isoformat(),
                    mcq_question.interval,
                    mcq_question.ease_factor,
                ),
            )
            return mcq_question
        except Exception as e:
            raise Exception(f"Error adding MCQ question: {e}")

    def get_by_id(self, mcq_id: int) -> Optional[MCQQuestion]:
        """
        Retrieve an MCQ question by its ID.

        Args:
            mcq_id: The ID of the MCQ question

        Returns:
            MCQQuestion object if found, None otherwise
        """
        query = """
        SELECT id, question, question_type, option_a, option_b, option_c, option_d, 
               correct_option, explanation_a, explanation_b, explanation_c, explanation_d,
               tags, last_reviewed, interval, ease_factor
        FROM mcq_questions WHERE id = ?;
        """
        try:
            result = self.db.fetch_one(query, (mcq_id,))
            return self._row_to_mcq_question(result) if result else None
        except Exception as e:
            raise Exception(f"Error retrieving MCQ question {mcq_id}: {e}")

    def get_all(self) -> List[MCQQuestion]:
        """
        Retrieve all MCQ questions from the database.

        Returns:
            List of all MCQQuestion objects
        """
        query = """
        SELECT id, question, question_type, option_a, option_b, option_c, option_d, 
               correct_option, explanation_a, explanation_b, explanation_c, explanation_d,
               tags, last_reviewed, interval, ease_factor
        FROM mcq_questions;
        """
        try:
            results = self.db.fetch_all(query)
            return [self._row_to_mcq_question(row) for row in results]
        except Exception as e:
            raise Exception(f"Error retrieving all MCQ questions: {e}")

    def get_due_questions(self) -> List[MCQQuestion]:
        """
        Retrieve all MCQ questions that are due for review.
        Orders by days overdue (most overdue first).

        Returns:
            List of due MCQQuestion objects
        """
        query = """
        SELECT id, question, question_type, option_a, option_b, option_c, option_d, 
               correct_option, explanation_a, explanation_b, explanation_c, explanation_d,
               tags, last_reviewed, interval, ease_factor
        FROM mcq_questions
        WHERE julianday('now') - julianday(DATE(last_reviewed, '+' || interval || ' days')) > 0
        ORDER BY julianday('now') - julianday(DATE(last_reviewed, '+' || interval || ' days')) DESC;
        """
        try:
            results = self.db.fetch_all(query)
            return [self._row_to_mcq_question(row) for row in results]
        except Exception as e:
            raise Exception(f"Error retrieving due MCQ questions: {e}")

    def is_due(self, mcq_question: MCQQuestion) -> bool:
        """
        Check if an MCQ question is due for review.

        Args:
            mcq_question: MCQ question to check

        Returns:
            True if due for review, False otherwise
        """
        return self.sm2_calculator.is_overdue(
            mcq_question.last_reviewed, mcq_question.interval, date.today()
        )

    def days_overdue(self, mcq_question: MCQQuestion) -> float:
        """
        Calculate how many days overdue an MCQ question is.

        Args:
            mcq_question: MCQ question to check

        Returns:
            Number of days overdue (0.0 if not overdue)
        """
        return self.sm2_calculator.days_overdue(
            mcq_question.last_reviewed, mcq_question.interval, date.today()
        )

    def get_option_text(
        self, mcq_question: MCQQuestion, option_letter: str
    ) -> Optional[str]:
        """
        Get the text for a specific option letter.

        Args:
            mcq_question: MCQ question
            option_letter: Option letter ('a', 'b', 'c', 'd')

        Returns:
            Option text or None if not found
        """
        option_map = {
            "a": mcq_question.option_a,
            "b": mcq_question.option_b,
            "c": mcq_question.option_c,
            "d": mcq_question.option_d,
        }
        return option_map.get(option_letter.lower())

    def get_explanation(
        self, mcq_question: MCQQuestion, option_letter: str
    ) -> Optional[str]:
        """
        Get the explanation for a specific option letter.

        Args:
            mcq_question: MCQ question
            option_letter: Option letter ('a', 'b', 'c', 'd')

        Returns:
            Explanation text or None if not found
        """
        explanation_map = {
            "a": mcq_question.explanation_a,
            "b": mcq_question.explanation_b,
            "c": mcq_question.explanation_c,
            "d": mcq_question.explanation_d,
        }
        return explanation_map.get(option_letter.lower())

    def get_available_options(
        self, mcq_question: MCQQuestion
    ) -> List[Tuple[str, str]]:
        """
        Get list of available options as (letter, text) tuples.

        Args:
            mcq_question: MCQ question

        Returns:
            List of (option_letter, option_text) tuples
        """
        options = [("a", mcq_question.option_a), ("b", mcq_question.option_b)]

        if mcq_question.question_type == "mcq":
            options.extend(
                [("c", mcq_question.option_c), ("d", mcq_question.option_d)]
            )

        return options

    def is_correct_answer(
        self, mcq_question: MCQQuestion, user_choice: str
    ) -> bool:
        """
        Check if user's choice is correct.

        Args:
            mcq_question: MCQ question
            user_choice: User's selected option letter

        Returns:
            True if correct, False otherwise
        """
        return user_choice.lower() == mcq_question.correct_option.lower()

    def mark_reviewed(
        self,
        mcq_question: MCQQuestion,
        is_correct: bool,
        confidence_level: str,
    ) -> MCQQuestion:
        """
        Mark an MCQ question as reviewed and update SM-2 values with penalty system.

        Args:
            mcq_question: MCQ question that was reviewed
            is_correct: Whether the answer was correct
            confidence_level: Confidence level ('low', 'medium', 'high')

        Returns:
            Updated MCQQuestion object
        """
        new_interval, new_ease_factor = (
            self.sm2_calculator.calculate_mcq_review(
                is_correct,
                confidence_level,
                mcq_question.interval,
                mcq_question.ease_factor,
            )
        )

        mcq_question.last_reviewed = date.today()
        mcq_question.interval = new_interval
        mcq_question.ease_factor = new_ease_factor

        update_query = """
        UPDATE mcq_questions
        SET last_reviewed = ?, interval = ?, ease_factor = ?
        WHERE id = ?;
        """
        try:
            rows_affected = self.db.execute_query(
                update_query,
                (
                    mcq_question.last_reviewed.isoformat(),
                    mcq_question.interval,
                    mcq_question.ease_factor,
                    mcq_question.id,
                ),
            )

            if rows_affected == 0:
                raise ValueError(
                    f"No MCQ question found with ID {mcq_question.id}"
                )

            return mcq_question
        except Exception as e:
            raise Exception(f"Error marking MCQ question as reviewed: {e}")

    def update(
        self,
        mcq_question: MCQQuestion,
        new_question_text: Optional[str] = None,
        new_tags: Optional[str] = None,
    ) -> MCQQuestion:
        """
        Update an existing MCQ question's content.

        Args:
            mcq_question: MCQ question to update
            new_question_text: New question text (optional)
            new_tags: New tags (optional)

        Returns:
            Updated MCQQuestion object
        """
        fields_to_update = []
        params = []

        if new_question_text is not None:
            fields_to_update.append("question = ?")
            params.append(new_question_text)
            mcq_question.question = new_question_text

        if new_tags is not None:
            fields_to_update.append("tags = ?")
            params.append(new_tags)
            mcq_question.tags = new_tags

        if not fields_to_update:
            return mcq_question

        query = f"UPDATE mcq_questions SET {', '.join(fields_to_update)} WHERE id = ?"
        params.append(mcq_question.id)

        try:
            rows_affected = self.db.execute_query(query, tuple(params))

            if rows_affected == 0:
                raise ValueError(
                    f"No MCQ question found with ID {mcq_question.id}"
                )

            return mcq_question
        except Exception as e:
            raise Exception(f"Error updating MCQ question: {e}")

    def delete(self, mcq_id: int) -> bool:
        """
        Delete an MCQ question from the database.

        Args:
            mcq_id: ID of the MCQ question to delete

        Returns:
            True if MCQ question was deleted, False if not found
        """
        query = "DELETE FROM mcq_questions WHERE id = ?"
        try:
            rows_affected = self.db.execute_query(query, (mcq_id,))
            return rows_affected > 0
        except Exception as e:
            raise Exception(f"Error deleting MCQ question: {e}")

    def _row_to_mcq_question(self, row) -> MCQQuestion:
        """
        Convert a database row to an MCQQuestion object.

        Args:
            row: Database row tuple

        Returns:
            MCQQuestion object
        """
        last_reviewed = None
        if row[13]:
            last_reviewed = date.fromisoformat(row[13])

        return MCQQuestion(
            id=row[0],
            question=row[1],
            question_type=row[2],
            option_a=row[3],
            option_b=row[4],
            option_c=row[5],
            option_d=row[6],
            correct_option=row[7],
            explanation_a=row[8],
            explanation_b=row[9],
            explanation_c=row[10],
            explanation_d=row[11],
            tags=row[12],
            last_reviewed=last_reviewed,
            interval=row[14],
            ease_factor=row[15],
        )
