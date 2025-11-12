import secrets, json
from datetime import datetime, timedelta
from typing import Optional
from src.functions.db_connection import get_db_connection

SESSION_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days

def _new_token() -> str:
    return secrets.token_urlsafe(32)

def _now():
    return datetime.utcnow()

def create_session(user_id: int, meta: dict | None = None) -> str:
    token = _new_token()
    issued = _now()
    expires = issued + timedelta(seconds=SESSION_TTL_SECONDS)
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "REPLACE INTO sessions(token,user_id,issued_at,expires_at,meta) VALUES (%s,%s,%s,%s,%s)",
            (token, user_id, issued, expires, json.dumps(meta or {}))
        )
        conn.commit()
    return token

def get_session(token: str) -> Optional[dict]:
    if not token:
        return None
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT s.token, s.user_id, s.issued_at, s.expires_at, s.meta, u.username "
            "FROM sessions s JOIN users u ON u.id=s.user_id "
            "WHERE s.token=%s AND s.expires_at > UTC_TIMESTAMP()",
            (token,)
        )
        row = cur.fetchone()
    return row

def destroy_session(token: str) -> None:
    if not token:
        return
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM sessions WHERE token=%s", (token,))
        conn.commit()

def cleanup_expired() -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM sessions WHERE expires_at <= UTC_TIMESTAMP()")
        conn.commit()
        return cur.rowcount
