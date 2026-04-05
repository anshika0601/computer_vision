from __future__ import annotations

import sqlite3
from datetime import datetime

from .config import DATABASE_PATH, ensure_directories


def get_connection() -> sqlite3.Connection:
    ensure_directories()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_name TEXT NOT NULL,
                attendance_date TEXT NOT NULL,
                attendance_time TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def upsert_person(name: str) -> None:
    timestamp = datetime.now().isoformat(timespec="seconds")
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO people(name, created_at)
            VALUES (?, ?)
            ON CONFLICT(name) DO NOTHING
            """,
            (name, timestamp),
        )
        connection.commit()


def has_attendance_for_date(name: str, attendance_date: str) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM attendance
            WHERE person_name = ? AND attendance_date = ?
            LIMIT 1
            """,
            (name, attendance_date),
        ).fetchone()
    return row is not None


def mark_attendance(name: str, status: str = "Present") -> tuple[str, str]:
    now = datetime.now()
    attendance_date = now.date().isoformat()
    attendance_time = now.strftime("%H:%M:%S")
    timestamp = now.isoformat(timespec="seconds")

    if has_attendance_for_date(name, attendance_date):
        return attendance_date, attendance_time

    upsert_person(name)
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO attendance(person_name, attendance_date, attendance_time, status, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, attendance_date, attendance_time, status, timestamp),
        )
        connection.commit()

    return attendance_date, attendance_time


def fetch_attendance_rows(limit: int = 200) -> list[sqlite3.Row]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT person_name, attendance_date, attendance_time, status
            FROM attendance
            ORDER BY attendance_date DESC, attendance_time DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return rows


def fetch_summary() -> dict[str, int]:
    with get_connection() as connection:
        people_count = connection.execute("SELECT COUNT(*) FROM people").fetchone()[0]
        attendance_count = connection.execute("SELECT COUNT(*) FROM attendance").fetchone()[0]
        today_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            WHERE attendance_date = DATE('now', 'localtime')
            """
        ).fetchone()[0]

    return {
        "people_count": people_count,
        "attendance_count": attendance_count,
        "today_count": today_count,
    }
