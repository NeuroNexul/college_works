import sqlite3

def create_tables(cursor: sqlite3.Cursor):
    """
    Create the tables in the database if they do not exist
    
    """

    # Users table
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        full_name TEXT NOT NULL,
                        qualification TEXT NOT NULL,
                        dob TEXT NOT NULL
                    )''')

    # Subjects table
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS subjects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT NOT NULL
                    )''')

    # Chapters table
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chapters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT NOT NULL,
                        subject_id INTEGER NOT NULL,
                        FOREIGN KEY (subject_id) REFERENCES subjects (id)
                    )''')

    # Quiz table
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS quiz (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_of_quiz TEXT NOT NULL,
                        time_duration TEXT NOT NULL,
                        remarks TEXT NOT NULL,
                        chapter_id INTEGER NOT NULL,
                        FOREIGN KEY (chapter_id) REFERENCES chapters (id)
                    )''')

    # Questions table
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT NOT NULL,
                        option1 TEXT NOT NULL,
                        option2 TEXT NOT NULL,
                        option3 TEXT NOT NULL,
                        option4 TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        quiz_id INTEGER NOT NULL,
                        FOREIGN KEY (quiz_id) REFERENCES quiz (id)
                    )''')

    # Scores table
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        score INTEGER NOT NULL,
                        time_stamp_of_attempt TEXT NOT NULL,
                        total_scored INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        quiz_id INTEGER NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (quiz_id) REFERENCES quiz (id)
                    )''')
