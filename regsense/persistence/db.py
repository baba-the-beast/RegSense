"""SQLite connection and schema.

State lives here, not in Streamlit session_state, so the checklist and its
open/closed/escalated status survive a page refresh.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "regsense.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS circulars (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    issued_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gaps (
    id TEXT PRIMARY KEY,
    circular_id TEXT NOT NULL,
    obligation TEXT NOT NULL,
    status TEXT NOT NULL,
    score REAL NOT NULL,
    matched_clause_id TEXT,
    rationale TEXT NOT NULL,
    FOREIGN KEY (circular_id) REFERENCES circulars(id)
);

CREATE TABLE IF NOT EXISTS checklist_items (
    id TEXT PRIMARY KEY,
    gap_id TEXT NOT NULL,
    description TEXT NOT NULL,
    owner TEXT NOT NULL,
    severity TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (gap_id) REFERENCES gaps(id)
);
"""


def get_connection(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn
