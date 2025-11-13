# src/functions/sessions_mysql.py
import secrets
import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from src.functions.db_connection import db_conn  # Must exist and return a connection context

SESSION_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days


# ----------------- Helpers -----------------
def _new_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)


def _now():
    """Return current UTC datetime with timezone info."""
    return datetime.now(timezone.utc)


# ----------------- CRUD Functions -----------------
def create_session(user_id: int, meta: dict | None = None) -> str:
    """Create a new session in DB and return the token."""
    token = _new_token()
    issued = _now()
    expires = issued + timedelta(seconds=SESSION_TTL_SECONDS)

    with db_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO sessions (token, user_id, issued_at, expires_at, meta)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    token = VALUES(token),
                    issued_at = VALUES(issued_at),
                    expires_at = VALUES(expires_at),
                    meta = VALUES(meta)
                """,
                (token, user_id, issued, expires, json.dumps(meta or {})),
            )
            conn.commit()
        finally:
            cur.close()

    return token


def get_session(token: str) -> Optional[dict]:
    """Retrieve valid session info (if not expired)."""
    if not token:
        return None

    with db_conn() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                """
                SELECT s.token, s.user_id, s.issued_at, s.expires_at, s.meta, u.username
                FROM sessions s
                JOIN users u ON u.id = s.user_id
                WHERE s.token = %s
                  AND s.expires_at > UTC_TIMESTAMP()
                """,
                (token,),
            )
            row = cur.fetchone()
            if row and "meta" in row and row["meta"]:
                try:
                    row["meta"] = json.loads(row["meta"])
                except json.JSONDecodeError:
                    row["meta"] = {}
            return row
        finally:
            cur.close()


def destroy_session(token: str) -> None:
    """Delete a specific session by token."""
    if not token:
        return

    with db_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
            conn.commit()
        finally:
            cur.close()


def cleanup_expired() -> int:
    """Delete expired sessions and return count."""
    with db_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM sessions WHERE expires_at <= UTC_TIMESTAMP()")
            conn.commit()
            return cur.rowcount
        finally:
            cur.close()
