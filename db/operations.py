import sqlite3
from datetime import datetime

from .connection import get_connection


def add_question(question, tags=None):
    """
    Adds a new question to the database.

    :param question: The text of the question.
    :param tags: Optional comma-separated tags for categorization.
    """
    insert_query = """
    INSERT INTO questions (question, tags)
    VALUES (?, ?);
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(insert_query, (question, tags))

        conn.commit()
        conn.close()
    except Exception:
        raise


def get_due_questions():
    """
    Retrieves all questions that are due for review.
    A question is due if `last_reviewed + interval` is less than or equal to
    today's date or if `last_reviewed` is NULL.

    :return: List of due questions.
    """
    query = """
    SELECT id, question, tags, last_reviewed, interval
    FROM questions
    WHERE last_reviewed IS NULL
       OR DATE(last_reviewed, '+' || interval || ' days') <= DATE('now');
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query)
        results = cursor.fetchall()

        conn.close()

        due_questions = [
            {
                "id": row[0],
                "question": row[1],
                "tags": row[2],
                "last_reviewed": row[3],
                "interval": row[4],
            }
            for row in results
        ]

        return due_questions
    except sqlite3.Error as e:
        print(f"Error retrieving due questions: {e}")
        raise


def get_all_questions():
    """
    Retrieves all questions from the database, regardless of review status.

    :return: List of all questions.
    """
    query = """
    SELECT id, question, tags, last_reviewed, interval, ease_factor
    FROM questions;
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        all_questions = [
            {
                "id": row[0],
                "question": row[1],
                "tags": row[2],
                "last_reviewed": row[3],
                "interval": row[4],
                "ease_factor": row[5],
            }
            for row in results
        ]

        return all_questions
    except sqlite3.Error as e:
        print(f"Error retrieving all questions: {e}")
        raise


def add_challenge(title, description, language, testcases=None):
    """
    Adds a new coding challenge to the database.

    :param title: The title of the challenge.
    :param description: The description of the challenge.
    :param language: The language of the challenge (Python or JavaScript).
    :param testcases: Optional test cases for the challenge.
    """
    insert_query = """
    INSERT INTO challenges (
              title, description, language, testcases,
              last_reviewed, interval, ease_factor
            )
    VALUES (?, ?, ?, ?, DATE('now'), 1, 2.5);
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(insert_query, (title, description, language, testcases))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error adding challenge: {e}")
        raise


def get_all_challenges():
    """
    Retrieves all challenges from the database.

    :return: List of all challenges.
    """
    query = """
    SELECT id, title, description, language, testcases, last_reviewed, interval, ease_factor
    FROM challenges;
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        all_challenges = [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "language": row[3],
                "testcases": row[4],
                "last_reviewed": row[5],
                "interval": row[6],
                "ease_factor": row[7],
            }
            for row in results
        ]

        return all_challenges
    except sqlite3.Error as e:
        print(f"Error retrieving all challenges: {e}")
        raise


def get_due_challenges():
    """
    Retrieves all challenges ordered by days overdue.
    Challenges are due if:
    - days_overdue > 0 (overdue challenges).
    """
    query = """
    SELECT id, title, description, language, testcases, last_reviewed, interval, ease_factor,
           julianday('now') - julianday(DATE(last_reviewed, '+' || interval || ' days')) AS days_overdue
    FROM challenges
    WHERE julianday('now') - julianday(DATE(last_reviewed, '+' || interval || ' days')) > 0
    ORDER BY days_overdue DESC;
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query)
        results = cursor.fetchall()

        conn.close()

        due_challenges = [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "language": row[3],
                "testcases": row[4],
                "last_reviewed": row[5],
                "interval": row[6],
                "ease_factor": row[7],
                "days_overdue": row[8],
            }
            for row in results
        ]

        return due_challenges
    except sqlite3.Error as e:
        print(f"Error retrieving due challenges: {e}")
        raise


def mark_reviewed(question_id, rating):
    """
    Marks a question as reviewed and updates SM-2 values.

    :param question_id: The ID of the question to update.
    :param rating: User's performance rating (0-3).
    """
    if rating < 0 or rating > 3:
        raise ValueError(
            "Rating must be between 0 (forgot) and 3 (easy recall)."
        )

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT interval, ease_factor FROM questions WHERE id = ?",
            (question_id,),
        )
        result = cursor.fetchone()

        if not result:
            raise ValueError(f"No question found with ID {question_id}.")

        current_interval, current_ease_factor = result

        # Update SM-2 values based on rating
        if rating == 0:
            new_interval = 1
            new_ease_factor = max(1.3, current_ease_factor - 0.2)
        else:
            new_ease_factor = current_ease_factor + (
                0.1 - (3 - rating) * (0.08 + (3 - rating) * 0.02)
            )
            new_interval = max(1, round(current_interval * new_ease_factor))

        today = datetime.now().strftime("%Y-%m-%d")

        update_query = """
        UPDATE questions
        SET last_reviewed = ?, interval = ?, ease_factor = ?
        WHERE id = ?;
        """
        cursor.execute(
            update_query,
            (today, new_interval, round(new_ease_factor, 2), question_id),
        )
        conn.commit()
        print(
            f"Question ID {question_id} updated. Last reviewed: {today}, New interval: {new_interval}, New ease factor: {round(new_ease_factor, 2)}"
        )
        conn.close()
    except Exception as e:
        print(f"Error in mark_reviewed: {e}")
        raise


def mark_reviewed_challenge(challenge_id, rating):
    """
    Marks a challenge as reviewed and updates SM-2 values.

    :param challenge_id: The ID of the challenge to update.
    :param rating: User's performance rating (0-3).
    """
    if rating < 0 or rating > 3:
        raise ValueError(
            "Rating must be between 0 (forgot) and 3 (easy recall)."
        )

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch current interval and ease factor for the challenge
        cursor.execute(
            "SELECT interval, ease_factor FROM challenges WHERE id = ?",
            (challenge_id,),
        )
        result = cursor.fetchone()

        if not result:
            raise ValueError(f"No challenge found with ID {challenge_id}.")

        current_interval, current_ease_factor = result

        # Update SM-2 values based on rating
        if rating == 0:
            new_interval = 1
            new_ease_factor = max(1.3, current_ease_factor - 0.2)
        else:
            new_ease_factor = current_ease_factor + (
                0.1 - (3 - rating) * (0.08 + (3 - rating) * 0.02)
            )
            new_interval = max(1, round(current_interval * new_ease_factor))

        # Debugging: Log values
        print(f"Current Interval: {current_interval}")
        print(f"New Interval: {new_interval}")
        print(f"New Ease Factor: {round(new_ease_factor, 2)}")

        # Update the database
        today = datetime.now().strftime("%Y-%m-%d")
        update_query = """
        UPDATE challenges
        SET last_reviewed = ?, interval = ?, ease_factor = ?
        WHERE id = ?;
        """
        cursor.execute(
            update_query,
            (today, new_interval, round(new_ease_factor, 2), challenge_id),
        )
        conn.commit()
        print(
            f"Challenge ID {challenge_id} updated. Last reviewed: {today}, "
            f"New interval: {new_interval}, New ease factor: {round(new_ease_factor, 2)}"
        )
        conn.close()
    except Exception as e:
        print(f"Error in mark_reviewed_challenge: {e}")
        raise


def update_ease_factor(question_id, ease_factor):
    """
    Updates the ease_factor of a question.

    :param question_id: ID of the question to update.
    :param ease_factor: New ease factor to set (0-3).
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        update_query = """
        UPDATE questions
        SET ease_factor = ?
        WHERE id = ?;
        """
        cursor.execute(update_query, (round(ease_factor, 2), question_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating ease factor: {e}")
        raise


def get_challenges_without_testcases():
    """
    Returns a list of challenges that don't have test cases.
    """
    query = """
    SELECT id, title, description, language FROM challenges
    WHERE testcases IS NULL OR testcases = '';
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        challenges = [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "language": row[3],
            }
            for row in results
        ]
        return challenges
    except sqlite3.Error as e:
        print(f"Error retrieving challenges without test cases: {e}")
        raise


def update_challenge_testcases(challenge_id, testcases):
    """
    Updates an existing challenge with new test cases.
    """
    query = "UPDATE challenges SET testcases = ? WHERE id = ?;"
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (testcases, challenge_id))
        conn.commit()
        conn.close()
        print(f"Test cases added to challenge ID {challenge_id}.")
    except sqlite3.Error as e:
        print(f"Error updating test cases for challenge {challenge_id}: {e}")
        raise


if __name__ == "__main__":
    print(get_due_challenges())
