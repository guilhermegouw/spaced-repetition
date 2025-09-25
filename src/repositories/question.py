from datetime import date
from typing import List, Optional

from src.db.database_manager import DatabaseManager
from src.models.question import Question
from src.models.sm2 import SM2Calculator


class QuestionRepository:
    """
    Repository for Question entity.
    Contains all business logic and database operations for questions.
    """

    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
        self.sm2_calculator = SM2Calculator()

    def add(self, question: Question) -> Question:
        """
        Add a new question to the database.

        Args:
            question: Question object to add

        Returns:
            Question object with populated ID

        Raises:
            Exception: If database operation fails
        """
        insert_query = """
        INSERT INTO questions (question, tags)
        VALUES (?, ?);
        """
        try:
            question.id = self.db.execute_query(
                insert_query, (question.question_text, question.tags)
            )
            return question
        except Exception as e:
            raise Exception(f"Error adding question: {e}")

    def get_by_id(self, question_id: int) -> Optional[Question]:
        """
        Retrieve a question by its ID.

        Args:
            question_id: The ID of the question

        Returns:
            Question object if found, None otherwise
        """
        query = """
        SELECT id, question, tags, last_reviewed, interval, ease_factor
        FROM questions WHERE id = ?;
        """
        try:
            result = self.db.fetch_one(query, (question_id,))
            return self._row_to_question(result) if result else None
        except Exception as e:
            raise Exception(f"Error retrieving question {question_id}: {e}")

    def get_all(self) -> List[Question]:
        """
        Retrieve all questions from the database.

        Returns:
            List of all Question objects
        """
        query = """
        SELECT id, question, tags, last_reviewed, interval, ease_factor
        FROM questions;
        """
        try:
            results = self.db.fetch_all(query)
            return [self._row_to_question(row) for row in results]
        except Exception as e:
            raise Exception(f"Error retrieving all questions: {e}")

    def get_due_questions(self) -> List[Question]:
        """
        Retrieve all questions that are due for review.
        Orders by days overdue (most overdue first).

        Returns:
            List of due Question objects
        """
        query = """
        SELECT id, question, tags, last_reviewed, interval, ease_factor
        FROM questions
        WHERE last_reviewed IS NULL
           OR DATE(last_reviewed, '+' || interval || ' days') <= DATE('now')
        ORDER BY 
            CASE 
                WHEN last_reviewed IS NULL THEN 999999
                ELSE julianday('now') - julianday(DATE(last_reviewed, '+' || interval || ' days'))
            END DESC;
        """
        try:
            results = self.db.fetch_all(query)
            return [self._row_to_question(row) for row in results]
        except Exception as e:
            raise Exception(f"Error retrieving due questions: {e}")

    def is_due(self, question: Question) -> bool:
        """
        Check if a question is due for review.

        Args:
            question: Question to check

        Returns:
            True if due for review, False otherwise
        """
        return self.sm2_calculator.is_overdue(
            question.last_reviewed, question.interval, date.today()
        )

    def days_overdue(self, question: Question) -> float:
        """
        Calculate how many days overdue a question is.

        Args:
            question: Question to check

        Returns:
            Number of days overdue (0.0 if not overdue)
        """
        return self.sm2_calculator.days_overdue(
            question.last_reviewed, question.interval, date.today()
        )

    def mark_reviewed(self, question: Question, rating: int) -> Question:
        """
        Mark a question as reviewed and update SM-2 values.

        Args:
            question: Question that was reviewed
            rating: User's performance rating (0-3)

        Returns:
            Updated Question object

        Raises:
            Exception: If database operation fails
        """
        new_interval, new_ease_factor = (
            self.sm2_calculator.calculate_next_review(
                rating, question.interval, question.ease_factor
            )
        )

        question.last_reviewed = date.today()
        question.interval = new_interval
        question.ease_factor = new_ease_factor

        update_query = """
        UPDATE questions
        SET last_reviewed = ?, interval = ?, ease_factor = ?
        WHERE id = ?;
        """
        try:
            rows_affected = self.db.execute_query(
                update_query,
                (
                    question.last_reviewed.isoformat(),
                    question.interval,
                    question.ease_factor,
                    question.id,
                ),
            )

            if rows_affected == 0:
                raise ValueError(f"No question found with ID {question.id}")

            return question
        except Exception as e:
            raise Exception(f"Error marking question as reviewed: {e}")

    def update(
        self,
        question: Question,
        new_question_text: Optional[str] = None,
        new_tags: Optional[str] = None,
    ) -> Question:
        """
        Update an existing question's content.

        Args:
            question: Question to update
            new_question_text: New question text (optional)
            new_tags: New tags (optional)

        Returns:
            Updated Question object
        """
        fields_to_update = []
        params = []

        if new_question_text is not None:
            fields_to_update.append("question = ?")
            params.append(new_question_text)
            question.question_text = new_question_text

        if new_tags is not None:
            fields_to_update.append("tags = ?")
            params.append(new_tags)
            question.tags = new_tags

        if not fields_to_update:
            return question

        query = (
            f"UPDATE questions SET {', '.join(fields_to_update)} WHERE id = ?"
        )
        params.append(question.id)

        try:
            rows_affected = self.db.execute_query(query, tuple(params))

            if rows_affected == 0:
                raise ValueError(f"No question found with ID {question.id}")

            return question
        except Exception as e:
            raise Exception(f"Error updating question: {e}")

    def delete(self, question_id: int) -> bool:
        """
        Delete a question from the database.

        Args:
            question_id: ID of the question to delete

        Returns:
            True if question was deleted, False if not found
        """
        query = "DELETE FROM questions WHERE id = ?"
        try:
            rows_affected = self.db.execute_query(query, (question_id,))
            return rows_affected > 0
        except Exception as e:
            raise Exception(f"Error deleting question: {e}")

    def _row_to_question(self, row) -> Question:
        """
        Convert a database row to a Question object.

        Args:
            row: Database row tuple

        Returns:
            Question object
        """
        last_reviewed = None
        if row[3]:
            last_reviewed = date.fromisoformat(row[3])

        return Question(
            id=row[0],
            question_text=row[1],
            tags=row[2],
            last_reviewed=last_reviewed,
            interval=row[4],
            ease_factor=row[5],
        )
