from .connection import get_connection


def initialize_db():
    """
    Initializes the database schema.
    Creates the `questions` table if it does not exist.
    """
    create_questions_table_query = """
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        tags TEXT,
        last_reviewed DATE,
        interval INTEGER DEFAULT 1,
        ease_factor REAL DEFAULT 2.5
    );
    """

    create_challenges_table_query = """
    CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    testcases TEXT,
    language TEXT CHECK(language IN ('python', 'javascript', 'go')) NOT NULL,
    last_reviewed DATE DEFAULT CURRENT_DATE,
    interval INTEGER DEFAULT 1,
    ease_factor REAL DEFAULT 2.5
    );
    """

    create_mcq_questions_table_query = """
    CREATE TABLE IF NOT EXISTS mcq_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        question_type TEXT CHECK(question_type IN ('mcq', 'true_false')) NOT NULL DEFAULT 'mcq',
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT,
        option_d TEXT,
        correct_option TEXT CHECK(correct_option IN ('a', 'b', 'c', 'd')) NOT NULL,
        explanation_a TEXT,
        explanation_b TEXT,
        explanation_c TEXT,
        explanation_d TEXT,
        tags TEXT,
        last_reviewed DATE,
        interval INTEGER DEFAULT 1,
        ease_factor REAL DEFAULT 2.5
    );
    """

    add_explanation_columns_query = """
    ALTER TABLE mcq_questions ADD COLUMN explanation_a TEXT;
    """
    add_explanation_columns_query_b = """
    ALTER TABLE mcq_questions ADD COLUMN explanation_b TEXT;
    """
    add_explanation_columns_query_c = """
    ALTER TABLE mcq_questions ADD COLUMN explanation_c TEXT;
    """
    add_explanation_columns_query_d = """
    ALTER TABLE mcq_questions ADD COLUMN explanation_d TEXT;
    """

    add_tags_to_challenges_query = """
    ALTER TABLE challenges ADD COLUMN tags TEXT;
    """

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(create_questions_table_query)
        cursor.execute(create_challenges_table_query)
        cursor.execute(create_mcq_questions_table_query)

        try:
            cursor.execute(add_explanation_columns_query)
            cursor.execute(add_explanation_columns_query_b)
            cursor.execute(add_explanation_columns_query_c)
            cursor.execute(add_explanation_columns_query_d)
            print("Added explanation columns to existing mcq_questions table")
        except Exception:
            pass

        try:
            cursor.execute(add_tags_to_challenges_query)
            print("Added tags column to existing challenges table")
        except Exception:
            pass

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing database schema: {e}")
        raise
