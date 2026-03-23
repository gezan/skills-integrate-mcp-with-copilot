"""Database helpers for persistent activity storage."""

from __future__ import annotations

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "activities.db"

INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
    },
}


def get_connection() -> sqlite3.Connection:
    """Create a connection to the local SQLite database."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    """Create tables and seed initial data if the database is empty."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS activities (
                name TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                schedule TEXT NOT NULL,
                max_participants INTEGER NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_name TEXT NOT NULL,
                email TEXT NOT NULL,
                UNIQUE(activity_name, email),
                FOREIGN KEY(activity_name) REFERENCES activities(name) ON DELETE CASCADE
            )
            """
        )

        activity_count = connection.execute(
            "SELECT COUNT(*) FROM activities"
        ).fetchone()[0]

        if activity_count == 0:
            seed_initial_data(connection)


def seed_initial_data(connection: sqlite3.Connection) -> None:
    """Populate the database with the original sample activities."""
    for name, details in INITIAL_ACTIVITIES.items():
        connection.execute(
            """
            INSERT INTO activities (name, description, schedule, max_participants)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                details["description"],
                details["schedule"],
                details["max_participants"],
            ),
        )

        for email in details["participants"]:
            connection.execute(
                """
                INSERT INTO registrations (activity_name, email)
                VALUES (?, ?)
                """,
                (name, email),
            )


def list_activities() -> dict[str, dict[str, object]]:
    """Return all activities using the existing API response shape."""
    with get_connection() as connection:
        activities = connection.execute(
            """
            SELECT name, description, schedule, max_participants
            FROM activities
            ORDER BY name
            """
        ).fetchall()

        registrations = connection.execute(
            """
            SELECT activity_name, email
            FROM registrations
            ORDER BY id
            """
        ).fetchall()

    participants_by_activity: dict[str, list[str]] = {
        row["name"]: [] for row in activities
    }
    for row in registrations:
        participants_by_activity[row["activity_name"]].append(row["email"])

    return {
        row["name"]: {
            "description": row["description"],
            "schedule": row["schedule"],
            "max_participants": row["max_participants"],
            "participants": participants_by_activity[row["name"]],
        }
        for row in activities
    }


def activity_exists(activity_name: str) -> bool:
    """Return True when the activity exists."""
    with get_connection() as connection:
        return (
            connection.execute(
                "SELECT 1 FROM activities WHERE name = ?", (activity_name,)
            ).fetchone()
            is not None
        )


def registration_exists(activity_name: str, email: str) -> bool:
    """Return True when the student is already registered."""
    with get_connection() as connection:
        return (
            connection.execute(
                """
                SELECT 1
                FROM registrations
                WHERE activity_name = ? AND email = ?
                """,
                (activity_name, email),
            ).fetchone()
            is not None
        )


def signup_for_activity(activity_name: str, email: str) -> None:
    """Persist a student registration for an activity."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO registrations (activity_name, email)
            VALUES (?, ?)
            """,
            (activity_name, email),
        )


def unregister_from_activity(activity_name: str, email: str) -> bool:
    """Remove a persisted student registration."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM registrations
            WHERE activity_name = ? AND email = ?
            """,
            (activity_name, email),
        )
        return cursor.rowcount > 0
