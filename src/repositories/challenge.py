from datetime import date
from typing import List, Optional

from src.db.database_manager import DatabaseManager
from src.models.challenge import Challenge
from src.models.sm2 import SM2Calculator


class ChallengeRepository:
    """
    Repository for Challenge entity.
    Contains all business logic and database operations for challenges.
    """

    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
        self.sm2_calculator = SM2Calculator()

    def add(self, challenge: Challenge) -> Challenge:
        """
        Add a new challenge to the database.

        Args:
            challenge: Challenge object to add

        Returns:
            Challenge object with populated ID
        """
        insert_query = """
        INSERT INTO challenges (title, description, language, testcases, tags, last_reviewed, interval, ease_factor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            challenge.id = self.db.execute_query(
                insert_query,
                (
                    challenge.title,
                    challenge.description,
                    challenge.language,
                    challenge.testcases,
                    challenge.tags,
                    challenge.last_reviewed.isoformat(),
                    challenge.interval,
                    challenge.ease_factor,
                ),
            )
            return challenge
        except Exception as e:
            raise Exception(f"Error adding challenge: {e}")

    def get_by_id(self, challenge_id: int) -> Optional[Challenge]:
        """
        Retrieve a challenge by its ID.

        Args:
            challenge_id: The ID of the challenge

        Returns:
            Challenge object if found, None otherwise
        """
        query = """
        SELECT id, title, description, testcases, language, tags, last_reviewed, interval, ease_factor
        FROM challenges WHERE id = ?;
        """
        try:
            result = self.db.fetch_one(query, (challenge_id,))
            return self._row_to_challenge(result) if result else None
        except Exception as e:
            raise Exception(f"Error retrieving challenge {challenge_id}: {e}")

    def get_all(self) -> List[Challenge]:
        """
        Retrieve all challenges from the database.

        Returns:
            List of all Challenge objects
        """
        query = """
        SELECT id, title, description, testcases, language, tags, last_reviewed, interval, ease_factor
        FROM challenges;
        """
        try:
            results = self.db.fetch_all(query)
            return [self._row_to_challenge(row) for row in results]
        except Exception as e:
            raise Exception(f"Error retrieving all challenges: {e}")

    def get_due_challenges(self) -> List[Challenge]:
        """
        Retrieve all challenges that are due for review.
        Orders by days overdue (most overdue first).

        Returns:
            List of due Challenge objects
        """
        query = """
        SELECT id, title, description, testcases, language, tags, last_reviewed, interval, ease_factor
        FROM challenges
        WHERE julianday('now') - julianday(DATE(last_reviewed, '+' || interval || ' days')) > 0
        ORDER BY julianday('now') - julianday(DATE(last_reviewed, '+' || interval || ' days')) DESC;
        """
        try:
            results = self.db.fetch_all(query)
            return [self._row_to_challenge(row) for row in results]
        except Exception as e:
            raise Exception(f"Error retrieving due challenges: {e}")

    def get_challenges_without_testcases(self) -> List[Challenge]:
        """
        Retrieve challenges that don't have test cases.

        Returns:
            List of challenges without test cases
        """
        query = """
        SELECT id, title, description, testcases, language, tags, last_reviewed, interval, ease_factor
        FROM challenges
        WHERE testcases IS NULL OR testcases = '';
        """
        try:
            results = self.db.fetch_all(query)
            return [self._row_to_challenge(row) for row in results]
        except Exception as e:
            raise Exception(
                f"Error retrieving challenges without test cases: {e}"
            )

    def is_due(self, challenge: Challenge) -> bool:
        """
        Check if a challenge is due for review.

        Args:
            challenge: Challenge to check

        Returns:
            True if due for review, False otherwise
        """
        return self.sm2_calculator.is_overdue(
            challenge.last_reviewed, challenge.interval, date.today()
        )

    def days_overdue(self, challenge: Challenge) -> float:
        """
        Calculate how many days overdue a challenge is.

        Args:
            challenge: Challenge to check

        Returns:
            Number of days overdue (0.0 if not overdue)
        """
        return self.sm2_calculator.days_overdue(
            challenge.last_reviewed, challenge.interval, date.today()
        )

    def has_testcases(self, challenge: Challenge) -> bool:
        """
        Check if challenge has test cases defined.

        Args:
            challenge: Challenge to check

        Returns:
            True if has test cases, False otherwise
        """
        return (
            challenge.testcases is not None
            and len(challenge.testcases.strip()) > 0
        )

    def mark_reviewed(self, challenge: Challenge, rating: int) -> Challenge:
        """
        Mark a challenge as reviewed and update SM-2 values.

        Args:
            challenge: Challenge that was reviewed
            rating: User's performance rating (0-3)

        Returns:
            Updated Challenge object
        """
        new_interval, new_ease_factor = (
            self.sm2_calculator.calculate_next_review(
                rating, challenge.interval, challenge.ease_factor
            )
        )

        challenge.last_reviewed = date.today()
        challenge.interval = new_interval
        challenge.ease_factor = new_ease_factor

        update_query = """
        UPDATE challenges
        SET last_reviewed = ?, interval = ?, ease_factor = ?
        WHERE id = ?;
        """
        try:
            rows_affected = self.db.execute_query(
                update_query,
                (
                    challenge.last_reviewed.isoformat(),
                    challenge.interval,
                    challenge.ease_factor,
                    challenge.id,
                ),
            )

            if rows_affected == 0:
                raise ValueError(f"No challenge found with ID {challenge.id}")

            return challenge
        except Exception as e:
            raise Exception(f"Error marking challenge as reviewed: {e}")

    def update(
        self,
        challenge: Challenge,
        new_title: Optional[str] = None,
        new_description: Optional[str] = None,
        new_language: Optional[str] = None,
        new_testcases: Optional[str] = None,
        new_tags: Optional[str] = None,
    ) -> Challenge:
        """
        Update an existing challenge's content.

        Args:
            challenge: Challenge to update
            new_title: New title (optional)
            new_description: New description (optional)
            new_language: New language (optional)
            new_testcases: New test cases (optional)
            new_tags: New tags (optional)

        Returns:
            Updated Challenge object
        """
        fields_to_update = []
        params = []

        if new_title is not None:
            fields_to_update.append("title = ?")
            params.append(new_title)
            challenge.title = new_title

        if new_description is not None:
            fields_to_update.append("description = ?")
            params.append(new_description)
            challenge.description = new_description

        if new_language is not None:
            fields_to_update.append("language = ?")
            params.append(new_language)
            challenge.language = new_language

        if new_testcases is not None:
            fields_to_update.append("testcases = ?")
            params.append(new_testcases)
            challenge.testcases = new_testcases

        if new_tags is not None:
            fields_to_update.append("tags = ?")
            params.append(new_tags)
            challenge.tags = new_tags

        if not fields_to_update:
            return challenge

        query = (
            f"UPDATE challenges SET {', '.join(fields_to_update)} WHERE id = ?"
        )
        params.append(challenge.id)

        try:
            rows_affected = self.db.execute_query(query, tuple(params))

            if rows_affected == 0:
                raise ValueError(f"No challenge found with ID {challenge.id}")

            return challenge
        except Exception as e:
            raise Exception(f"Error updating challenge: {e}")

    def update_testcases(
        self, challenge: Challenge, testcases: str
    ) -> Challenge:
        """
        Update test cases for an existing challenge.

        Args:
            challenge: Challenge to update
            testcases: New test cases

        Returns:
            Updated Challenge object
        """
        challenge.testcases = testcases

        query = "UPDATE challenges SET testcases = ? WHERE id = ?"
        try:
            rows_affected = self.db.execute_query(
                query, (testcases, challenge.id)
            )

            if rows_affected == 0:
                raise ValueError(f"No challenge found with ID {challenge.id}")

            return challenge
        except Exception as e:
            raise Exception(f"Error updating challenge test cases: {e}")

    def delete(self, challenge_id: int) -> bool:
        """
        Delete a challenge from the database.

        Args:
            challenge_id: ID of the challenge to delete

        Returns:
            True if challenge was deleted, False if not found
        """
        query = "DELETE FROM challenges WHERE id = ?"
        try:
            rows_affected = self.db.execute_query(query, (challenge_id,))
            return rows_affected > 0
        except Exception as e:
            raise Exception(f"Error deleting challenge: {e}")

    def get_by_tags(self, tags: str) -> List[Challenge]:
        """
        Retrieve challenges that contain any of the specified tags.

        Args:
            tags: Comma-separated tags to filter by

        Returns:
            List of Challenge objects matching the tags
        """
        if not tags:
            return []

        # Split tags and build LIKE clauses for each tag
        tag_list = [tag.strip().lower() for tag in tags.split(",")]
        like_clauses = " OR ".join(
            ["LOWER(tags) LIKE ?" for _ in tag_list]
        )
        query = f"""
        SELECT id, title, description, testcases, language, tags, last_reviewed, interval, ease_factor
        FROM challenges
        WHERE {like_clauses};
        """

        # Create LIKE patterns for each tag
        params = [f"%{tag}%" for tag in tag_list]

        try:
            results = self.db.fetch_all(query, tuple(params))
            return [self._row_to_challenge(row) for row in results]
        except Exception as e:
            raise Exception(f"Error retrieving challenges by tags: {e}")

    def _row_to_challenge(self, row) -> Challenge:
        """
        Convert a database row to a Challenge object.

        Args:
            row: Database row tuple

        Returns:
            Challenge object
        """
        last_reviewed = None
        if row[6]:
            last_reviewed = date.fromisoformat(row[6])

        return Challenge(
            id=row[0],
            title=row[1],
            description=row[2],
            testcases=row[3],
            language=row[4],
            tags=row[5],
            last_reviewed=last_reviewed,
            interval=row[7],
            ease_factor=row[8],
        )
