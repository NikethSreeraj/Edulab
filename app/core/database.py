import hashlib
import hmac
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "edulab.db"


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = _connect()
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                total INTEGER NOT NULL DEFAULT 0,
                completed_lessons TEXT DEFAULT '',
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, subject),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16).hex()
    encoded = (salt + password).encode("utf-8")
    digest = hashlib.pbkdf2_hmac("sha256", encoded, salt.encode("utf-8"), 100_000)
    return digest.hex(), salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    expected_hash, _ = hash_password(password, salt)
    return secrets_compare(expected_hash, stored_hash)


def secrets_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)
