import sqlite3


DATABASE = "voting.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            has_voted INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            votes INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def add_voter(voter_id, name, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO voters (voter_id, name, password)
            VALUES (?, ?, ?)
            """,
            (voter_id, name, password)
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def get_voter(voter_id, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM voters
        WHERE voter_id = ? AND password = ?
        """,
        (voter_id, password)
    )

    voter = cursor.fetchone()

    conn.close()

    return voter


def get_voter_by_id(voter_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM voters
        WHERE voter_id = ?
        """,
        (voter_id,)
    )

    voter = cursor.fetchone()

    conn.close()

    return voter


def add_candidate(name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO candidates (name) VALUES (?)",
        (name,)
    )

    conn.commit()
    conn.close()


def get_candidates():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM candidates"
    )

    candidates = cursor.fetchall()

    conn.close()

    return candidates


def cast_vote(voter_id, candidate_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT has_voted FROM voters WHERE voter_id = ?",
        (voter_id,)
    )

    voter = cursor.fetchone()

    if voter is None or voter[0] == 1:
        conn.close()
        return False

    cursor.execute(
        """
        UPDATE candidates
        SET votes = votes + 1
        WHERE id = ?
        """,
        (candidate_id,)
    )

    cursor.execute(
        """
        UPDATE voters
        SET has_voted = 1
        WHERE voter_id = ?
        """,
        (voter_id,)
    )

    conn.commit()
    conn.close()

    return True