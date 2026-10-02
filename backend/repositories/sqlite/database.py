import sqlite3
import contextlib
from backend.core.config.settings import get_settings

def get_db_path() -> str:
    settings = get_settings()
    return settings.DATABASE_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

@contextlib.contextmanager
def db_connection():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize_database() -> bool:
    conn = get_connection()
    try:
        conn.execute("SELECT 1")
        return True
    finally:
        conn.close()
