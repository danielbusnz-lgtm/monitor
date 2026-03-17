import os
import sqlite3
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "monitor.db")


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS services (
                name             TEXT PRIMARY KEY,
                interval_seconds INTEGER NOT NULL,
                last_ping        REAL,
                alerted          INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


def record_ping(name: str, interval_seconds: int):
    with _conn() as conn:
        conn.execute("""
            INSERT INTO services (name, interval_seconds, last_ping, alerted)
            VALUES (?, ?, ?, 0)
            ON CONFLICT(name) DO UPDATE SET
                interval_seconds = excluded.interval_seconds,
                last_ping        = excluded.last_ping,
                alerted          = 0
        """, (name, interval_seconds, time.time()))
        conn.commit()


def get_all_services():
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM services").fetchall()
        return [dict(r) for r in rows]


def set_alerted(name: str):
    with _conn() as conn:
        conn.execute("UPDATE services SET alerted = 1 WHERE name = ?", (name,))
        conn.commit()


def clear_alerted(name: str):
    with _conn() as conn:
        conn.execute("UPDATE services SET alerted = 0 WHERE name = ?", (name,))
        conn.commit()


init_db()
