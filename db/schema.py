from db.connection import get_connection


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
    language TEXT CHECK(language IN ('python', 'javascript')) NOT NULL,
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
        tags TEXT,
        last_reviewed DATE,
        interval INTEGER DEFAULT 1,
        ease_factor REAL DEFAULT 2.5
    );
    """

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(create_questions_table_query)
        cursor.execute(create_challenges_table_query)
        cursor.execute(create_mcq_questions_table_query)

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing database schema: {e}")
        raise
