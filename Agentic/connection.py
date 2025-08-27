# project_saab/db/connection.py

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from config import CONFIG

logger = logging.getLogger("CONNECTION")


# ─── Database Connection Context Manager ──────────────────────────────


@contextmanager
def get_output_connection():
    """Context-managed connection to the output database."""
    with get_db_connection(CONFIG["output_db"]) as conn:
        yield conn


@contextmanager
def get_agentic_connection():
    """Context-managed connection to the agentic database."""
    with get_db_connection(CONFIG["agentic_db"]) as conn:
        yield conn


@contextmanager
def get_temp_connection():
    """Context-managed connection to the temporary database."""
    with get_db_connection(CONFIG["temp_db"]) as conn:
        yield conn


@contextmanager
def get_db_connection(db):
    db_path = Path(db)
    db_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure parent folders exist
    logger.debug(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()
        logger.debug("Database connection closed.")


# ─── Database Initialization (sanity check)──────────────────────────────────────────
if __name__ == "__main__":
    with get_output_connection() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        table_names = [row["name"] for row in rows]
        logger.info(f"Tables in database: {table_names}")
