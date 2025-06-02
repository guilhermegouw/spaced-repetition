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


def update_question(question_id, new_question=None, new_tags=None):
    """
    Updates an existing question with new content.
    :param question_id: The ID of the question to update.
    :param new_question: New text for the question (optional).
    :param new_tags: New tags for the question (optional).
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        fields_to_update = []
        params = []
        if new_question is not None:
            fields_to_update.append("question = ?")
            params.append(new_question)
        if new_tags is not None:
            fields_to_update.append("tags = ?")
            params.append(new_tags)
        if not fields_to_update:
            return  # Nothing to update
        query = f"UPDATE questions SET {', '.join(fields_to_update)} WHERE id = ?"
        params.append(question_id)
        cursor.execute(query, params)
        if cursor.rowcount == 0:
            raise ValueError(f"No question found with ID {question_id}.")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating question: {e}")
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


def delete_question(question_id):
    """
    Deletes a question from the database.
    :param question_id: The ID of the question to delete.
    :return: True if the question was deleted, False otherwise.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM questions WHERE id = ?", (question_id,))
        if not cursor.fetchone():
            raise ValueError(f"No question found with ID {question_id}.")
        query = "DELETE FROM questions WHERE id = ?"
        cursor.execute(query, (question_id,))
        if cursor.rowcount == 0:
            return False
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting question: {e}")
        raise


def add_mcq_question(question, question_type, option_a, option_b, correct_option, option_c=None, option_d=None, tags=None, explanation_a=None, explanation_b=None, explanation_c=None, explanation_d=None):
    """
    Adds a new multiple choice question to the database.

    :param question: The text of the question.
    :param question_type: Type of question ('mcq' or 'true_false').
    :param option_a: First option text.
    :param option_b: Second option text.
    :param option_c: Third option text (required for 'mcq', should be None for 'true_false').
    :param option_d: Fourth option text (required for 'mcq', should be None for 'true_false').
    :param correct_option: The correct option ('a', 'b', 'c', or 'd').
    :param tags: Optional comma-separated tags for categorization.
    :param explanation_a: Explanation for option A.
    :param explanation_b: Explanation for option B.
    :param explanation_c: Explanation for option C.
    :param explanation_d: Explanation for option D.
    """
    if question_type == 'true_false':
        if option_c is not None or option_d is not None:
            raise ValueError("True/False questions should only have option_a and option_b.")
        if correct_option not in ['a', 'b']:
            raise ValueError("For True/False questions, correct_option must be 'a' or 'b'.")
    elif question_type == 'mcq':
        if option_c is None or option_d is None:
            raise ValueError("MCQ questions require all four options (a, b, c, d).")
        if correct_option not in ['a', 'b', 'c', 'd']:
            raise ValueError("For MCQ questions, correct_option must be 'a', 'b', 'c', or 'd'.")
    else:
        raise ValueError("question_type must be either 'mcq' or 'true_false'.")

    insert_query = """
    INSERT INTO mcq_questions (
        question, question_type, option_a, option_b, option_c, option_d, 
        correct_option, explanation_a, explanation_b, explanation_c, explanation_d,
        tags, last_reviewed, interval, ease_factor
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, DATE('now'), 1, 2.5);
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(insert_query, (
            question, question_type, option_a, option_b, option_c, option_d, 
            correct_option, explanation_a, explanation_b, explanation_c, explanation_d, tags
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error adding MCQ question: {e}")
        raise


def get_all_mcq_questions():
    """
    Retrieves all MCQ questions from the database, regardless of review status.
    Returns essential information for listing/management purposes.

    :return: List of all MCQ questions with essential fields.
    """
    query = """
    SELECT id, question, question_type, tags, last_reviewed, interval, ease_factor
    FROM mcq_questions;
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        all_mcq_questions = [
            {
                "id": row[0],
                "question": row[1],
                "question_type": row[2],
                "tags": row[3],
                "last_reviewed": row[4],
                "interval": row[5],
                "ease_factor": row[6],
            }
            for row in results
        ]
        return all_mcq_questions
    except sqlite3.Error as e:
        print(f"Error retrieving all MCQ questions: {e}")
        raise


def get_due_mcq_questions():
    """
    Retrieves all MCQ questions ordered by days overdue.
    MCQ questions are due if:
    - days_overdue > 0 (overdue questions).
    
    :return: List of due MCQ questions with all fields needed for review.
    """
    query = """
    SELECT id, question, question_type, option_a, option_b, option_c, option_d, 
           correct_option, explanation_a, explanation_b, explanation_c, explanation_d,
           tags, last_reviewed, interval, ease_factor,
           julianday('now') - julianday(DATE(last_reviewed, '+' || interval || ' days')) AS days_overdue
    FROM mcq_questions
    WHERE julianday('now') - julianday(DATE(last_reviewed, '+' || interval || ' days')) > 0
    ORDER BY days_overdue DESC;
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query)
        results = cursor.fetchall()

        conn.close()

        due_mcq_questions = [
            {
                "id": row[0],
                "question": row[1],
                "question_type": row[2],
                "option_a": row[3],
                "option_b": row[4],
                "option_c": row[5],
                "option_d": row[6],
                "correct_option": row[7],
                "explanation_a": row[8],
                "explanation_b": row[9],
                "explanation_c": row[10],
                "explanation_d": row[11],
                "tags": row[12],
                "last_reviewed": row[13],
                "interval": row[14],
                "ease_factor": row[15],
                "days_overdue": row[16],
            }
            for row in results
        ]

        return due_mcq_questions
    except sqlite3.Error as e:
        print(f"Error retrieving due MCQ questions: {e}")
        raise


def get_mcq_question_by_id(question_id):
    """
    Retrieves a single MCQ question with all options for review.
    Used when user selects a specific question to answer.
    
    :param question_id: The ID of the MCQ question to retrieve.
    :return: Dictionary with complete question data, or None if not found.
    """
    query = """
    SELECT id, question, question_type, option_a, option_b, option_c, option_d, 
           correct_option, explanation_a, explanation_b, explanation_c, explanation_d,
           tags, last_reviewed, interval, ease_factor
    FROM mcq_questions
    WHERE id = ?;
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (question_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        mcq_question = {
            "id": result[0],
            "question": result[1],
            "question_type": result[2],
            "option_a": result[3],
            "option_b": result[4],
            "option_c": result[5],
            "option_d": result[6],
            "correct_option": result[7],
            "explanation_a": result[8],
            "explanation_b": result[9],
            "explanation_c": result[10],
            "explanation_d": result[11],
            "tags": result[12],
            "last_reviewed": result[13],
            "interval": result[14],
            "ease_factor": result[15],
        }
        return mcq_question
    except sqlite3.Error as e:
        print(f"Error retrieving MCQ question with ID {question_id}: {e}")
        raise


def update_mcq_question(mcq_id, new_question=None, new_tags=None):
    """
    Updates an existing MCQ question with new content.
    
    :param mcq_id: The ID of the MCQ question to update.
    :param new_question: New text for the question (optional).
    :param new_tags: New tags for the question (optional).
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        fields_to_update = []
        params = []
        if new_question is not None:
            fields_to_update.append("question = ?")
            params.append(new_question)
        if new_tags is not None:
            fields_to_update.append("tags = ?")
            params.append(new_tags)
        if not fields_to_update:
            return
        query = f"UPDATE mcq_questions SET {', '.join(fields_to_update)} WHERE id = ?"
        params.append(mcq_id)
        cursor.execute(query, params)
        if cursor.rowcount == 0:
            raise ValueError(f"No MCQ question found with ID {mcq_id}.")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating MCQ question: {e}")
        raise


def mark_reviewed_mcq(mcq_id, is_correct, confidence_level):
    """
    Marks an MCQ question as reviewed and updates SM-2 values with penalty system.
    
    :param mcq_id: The ID of the MCQ question to update.
    :param is_correct: Boolean indicating if the answer was correct.
    :param confidence_level: String indicating confidence ('low', 'medium', 'high').
    """
    if confidence_level not in ['low', 'medium', 'high']:
        raise ValueError("confidence_level must be 'low', 'medium', or 'high'.")
    
    if is_correct:
        if confidence_level == 'high':
            sm2_rating = 3
        elif confidence_level == 'medium':
            sm2_rating = 2
        else:  # low confidence
            sm2_rating = 1
    else:
        sm2_rating = 0
    
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT interval, ease_factor FROM mcq_questions WHERE id = ?",
            (mcq_id,),
        )
        result = cursor.fetchone()

        if not result:
            raise ValueError(f"No MCQ question found with ID {mcq_id}.")

        current_interval, current_ease_factor = result

        if sm2_rating == 0:
            new_interval = 1
            base_penalty = 0.2
            
            if confidence_level == 'high':
                penalty = base_penalty * 1.5
                print(f"Applying misconception penalty: -{penalty}")
            else:
                penalty = base_penalty
            
            new_ease_factor = max(1.3, current_ease_factor - penalty)
        else:
            if confidence_level == 'low':
                ease_adjustment = 0.05
            elif confidence_level == 'medium':
                ease_adjustment = 0.1
            else:  # high confidence
                ease_adjustment = 0.1 - (3 - sm2_rating) * (0.08 + (3 - sm2_rating) * 0.02)
            
            new_ease_factor = current_ease_factor + ease_adjustment
            new_interval = max(1, round(current_interval * new_ease_factor))

        today = datetime.now().strftime("%Y-%m-%d")
        update_query = """
        UPDATE mcq_questions
        SET last_reviewed = ?, interval = ?, ease_factor = ?
        WHERE id = ?;
        """
        cursor.execute(
            update_query,
            (today, new_interval, round(new_ease_factor, 2), mcq_id),
        )
        conn.commit()
        status = "correct" if is_correct else "incorrect"
        print(
            f"MCQ ID {mcq_id} updated ({status}, {confidence_level} confidence). "
            f"Last reviewed: {today}, New interval: {new_interval}, "
            f"New ease factor: {round(new_ease_factor, 2)}"
        )
        conn.close()
    except Exception as e:
        print(f"Error in mark_reviewed_mcq: {e}")
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

        if rating == 0:
            new_interval = 1
            new_ease_factor = max(1.3, current_ease_factor - 0.2)
        else:
            new_ease_factor = current_ease_factor + (
                0.1 - (3 - rating) * (0.08 + (3 - rating) * 0.02)
            )
            new_interval = max(1, round(current_interval * new_ease_factor))

        print(f"Current Interval: {current_interval}")
        print(f"New Interval: {new_interval}")
        print(f"New Ease Factor: {round(new_ease_factor, 2)}")

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


def update_challenge(challenge_id, new_title=None, new_description=None, new_language=None, new_testcases=None):
    """
    Updates an existing challenge with new content.
    :param challenge_id: The ID of the challenge to update.
    :param new_title: New title for the challenge (optional).
    :param new_description: New description for the challenge (optional).
    :param new_language: New language for the challenge (optional).
    :param new_testcases: New test cases for the challenge (optional).
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        fields_to_update = []
        params = []
        if new_title is not None:
            fields_to_update.append("title = ?")
            params.append(new_title)
        if new_description is not None:
            fields_to_update.append("description = ?")
            params.append(new_description)
        if new_language is not None:
            fields_to_update.append("language = ?")
            params.append(new_language)
        if new_testcases is not None:
            fields_to_update.append("testcases = ?")
            params.append(new_testcases)
        if not fields_to_update:
            return  # Nothing to update
        query = f"UPDATE challenges SET {', '.join(fields_to_update)} WHERE id = ?"
        params.append(challenge_id)
        cursor.execute(query, params)
        if cursor.rowcount == 0:
            raise ValueError(f"No challenge found with ID {challenge_id}.")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating challenge: {e}")
        raise


def delete_challenge(challenge_id):
    """
    Deletes a challenge from the database.
    :param challenge_id: The ID of the challenge to delete.
    :return: True if the challenge was deleted, False otherwise.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM challenges WHERE id = ?", (challenge_id,))
        if not cursor.fetchone():
            raise ValueError(f"No challenge found with ID {challenge_id}.")
        query = "DELETE FROM challenges WHERE id = ?"
        cursor.execute(query, (challenge_id,))
        if cursor.rowcount == 0:
            return False

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting challenge: {e}")
        raise


if __name__ == "__main__":
    print(get_due_challenges())
