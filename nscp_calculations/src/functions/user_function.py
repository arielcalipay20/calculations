# src/functions/user_function.py
from typing import Optional, Dict
import mysql.connector
import bcrypt

from src.functions.db_connection import db_conn  # <- use the context manager version I shared

def register_user(username: str, password: str) -> bool:
    """Create a user with a salted bcrypt hash. Returns True on success, False if username exists."""
    # Normalize
    username = username.strip()
    if not username or not password:
        return False

    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        with db_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, pw_hash),
            )
            conn.commit()
            cur.close()
        return True
    except mysql.connector.IntegrityError as e:
        # Likely duplicate username (UNIQUE constraint)
        return False
    except mysql.connector.Error:
        # Log if you have logging; avoid crashing the app
        return False


def login_user(username: str, password: str) -> Optional[Dict]:
    """
    Returns {'id': int, 'username': str} on success, otherwise None.
    """
    username = username.strip()
    if not username or not password:
        return None

    try:
        with db_conn() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, username, password_hash FROM users WHERE username = %s",
                (username,),
            )
            user = cur.fetchone()
            cur.close()
    except mysql.connector.Error:
        return None

    if not user:
        return None

    if bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        # Return only the fields you need downstream
        return {"id": user["id"], "username": user["username"]}
    return None
