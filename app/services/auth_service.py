import sqlite3

from app.core.database import _connect, hash_password, init_db, verify_password


def create_user(username, email, password, full_name):
    init_db()
    password_hash, salt = hash_password(password)
    connection = _connect()
    try:
        cursor = connection.execute(
            """
            INSERT INTO users (username, email, full_name, password_hash, password_salt)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username.strip(), email.strip(), full_name.strip(), password_hash, salt),
        )
        connection.commit()
        return {
            "id": cursor.lastrowid,
            "username": username.strip(),
            "email": email.strip(),
            "full_name": full_name.strip(),
        }
    except sqlite3.IntegrityError as exc:
        raise ValueError("Username or email already exists.") from exc
    finally:
        connection.close()


def authenticate_user(username, password):
    init_db()
    connection = _connect()
    try:
        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()
        if user is None:
            return None
        if verify_password(password, user["password_hash"], user["password_salt"]):
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
            }
        return None
    finally:
        connection.close()


def get_user_progress(user_id):
    connection = _connect()
    try:
        rows = connection.execute(
            "SELECT * FROM learning_progress WHERE user_id = ? ORDER BY last_updated DESC",
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def save_progress(user_id, subject, score, total, completed_lessons):
    init_db()
    connection = _connect()
    try:
        connection.execute(
            """
            INSERT INTO learning_progress (user_id, subject, score, total, completed_lessons)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, subject) DO UPDATE SET
                score = excluded.score,
                total = excluded.total,
                completed_lessons = excluded.completed_lessons,
                last_updated = CURRENT_TIMESTAMP
            """,
            (user_id, subject, score, total, ",".join(completed_lessons)),
        )
        connection.commit()
    finally:
        connection.close()
