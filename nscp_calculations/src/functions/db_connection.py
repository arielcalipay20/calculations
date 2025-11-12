# src/functions/db_connection.py
import os
from contextlib import contextmanager
from typing import Iterator, Optional

import mysql.connector
from mysql.connector import pooling, Error
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # load .env once

def _get_required(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val

@st.cache_resource(show_spinner=False)
def get_pool() -> pooling.MySQLConnectionPool:
    cfg = {
        "host": _get_required("DB_HOST"),
        "user": _get_required("DB_USER"),
        "password": _get_required("DB_PASSWORD"),
        "database": _get_required("DB_NAME"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "charset": os.getenv("DB_CHARSET", "utf8mb4"),
        "use_unicode": True,
        "autocommit": False,  # keep explicit control
        "connection_timeout": int(os.getenv("DB_TIMEOUT", "10")),
        # SSL (optional)
        # "ssl_ca": os.getenv("DB_SSL_CA"),
        # "ssl_disabled": os.getenv("DB_SSL_DISABLED", "false").lower() == "true",
    }
    # Remove None keys so mysql-connector doesn't complain
    cfg = {k: v for k, v in cfg.items() if v is not None}

    return pooling.MySQLConnectionPool(
        pool_name="nscp_pool",
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        **cfg,
    )

def get_db_connection():
    """Backwards-compatible: returns a pooled connection."""
    return get_pool().get_connection()

@contextmanager
def db_conn() -> Iterator[mysql.connector.connection.MySQLConnection]:
    """Preferred: context manager that returns a pooled connection."""
    conn = None
    try:
        conn = get_db_connection()
        # Ensure the connection is alive (avoid stale pool sockets)
        try:
            conn.ping(reconnect=True, attempts=1, delay=0)
        except Error:
            conn.reconnect(attempts=1, delay=0)
        yield conn
        # Commit is explicit in callers; no auto-commit here
    finally:
        if conn is not None:
            conn.close()
