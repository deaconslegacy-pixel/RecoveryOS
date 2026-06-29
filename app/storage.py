import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "recoveryos.db"


class Storage:
    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = Path(base_path or DATA_DIR)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.base_path / "recoveryos.db"
        self._initialize_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS consents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    consent_type TEXT NOT NULL,
                    granted INTEGER NOT NULL,
                    scope TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS deletions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT NOT NULL,
                    deleted_records INTEGER NOT NULL,
                    next_step TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS care_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    entry TEXT,
                    mood INTEGER,
                    sleep_hours REAL,
                    cravings INTEGER,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def load_users(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT user_id, role, created_at FROM users ORDER BY id"
            ).fetchall()
            return [dict(row) for row in rows]

    def save_user(self, user: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO users (user_id, role, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET role=excluded.role
                """,
                (
                    user["user_id"],
                    user["role"],
                    user.get("created_at") or datetime.now(timezone.utc).isoformat(),
                ),
            )
            connection.commit()

    def load_consents(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT patient_id, consent_type, granted, scope, created_at FROM consents ORDER BY id"
            ).fetchall()
            return [dict(row) for row in rows]

    def save_consent(self, consent: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO consents (patient_id, consent_type, granted, scope, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    consent["patient_id"],
                    consent["consent_type"],
                    int(bool(consent["granted"])),
                    consent["scope"],
                    consent.get("created_at") or datetime.now(timezone.utc).isoformat(),
                ),
            )
            connection.commit()

    def load_audit_log(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT actor, action, resource, created_at FROM audit_log ORDER BY id"
            ).fetchall()
            return [dict(row) for row in rows]

    def save_audit_event(self, event: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO audit_log (actor, action, resource, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    event["actor"],
                    event["action"],
                    event["resource"],
                    event.get("created_at") or datetime.now(timezone.utc).isoformat(),
                ),
            )
            connection.commit()

    def load_deletions(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT patient_id, reason, status, deleted_records, next_step, created_at FROM deletions ORDER BY id"
            ).fetchall()
            return [dict(row) for row in rows]

    def save_deletion(self, deletion: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO deletions (patient_id, reason, status, deleted_records, next_step, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    deletion["patient_id"],
                    deletion["reason"],
                    deletion["status"],
                    deletion["deleted_records"],
                    deletion["next_step"],
                    deletion.get("created_at") or datetime.now(timezone.utc).isoformat(),
                ),
            )
            connection.commit()

    def load_care_records(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT patient_id, kind, entry, mood, sleep_hours, cravings, status, timestamp FROM care_records ORDER BY id"
            ).fetchall()
            return [dict(row) for row in rows]

    def save_care_record(self, record: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO care_records (patient_id, kind, entry, mood, sleep_hours, cravings, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["patient_id"],
                    record["kind"],
                    record.get("entry"),
                    record.get("mood"),
                    record.get("sleep_hours"),
                    record.get("cravings"),
                    record["status"],
                    record.get("timestamp") or datetime.now(timezone.utc).isoformat(),
                ),
            )
            connection.commit()

    def apply_deletion(self, patient_id: str) -> int:
        deleted_records = 0
        with self._connect() as connection:
            user_count = connection.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (patient_id,)).fetchone()[0]
            if user_count:
                connection.execute("DELETE FROM users WHERE user_id = ?", (patient_id,))
                deleted_records += user_count

            consent_count = connection.execute("SELECT COUNT(*) FROM consents WHERE patient_id = ?", (patient_id,)).fetchone()[0]
            if consent_count:
                connection.execute("DELETE FROM consents WHERE patient_id = ?", (patient_id,))
                deleted_records += consent_count

            care_count = connection.execute("SELECT COUNT(*) FROM care_records WHERE patient_id = ?", (patient_id,)).fetchone()[0]
            if care_count:
                connection.execute("DELETE FROM care_records WHERE patient_id = ?", (patient_id,))
                deleted_records += care_count

            audit_count = connection.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
            if audit_count:
                connection.execute("DELETE FROM audit_log")
                deleted_records += audit_count

            connection.commit()
        return deleted_records


storage = Storage()


def load_users() -> list[dict[str, Any]]:
    return storage.load_users()


def save_user(user: dict[str, Any]) -> None:
    storage.save_user(user)


def load_consents() -> list[dict[str, Any]]:
    return storage.load_consents()


def save_consent(consent: dict[str, Any]) -> None:
    storage.save_consent(consent)


def load_audit_log() -> list[dict[str, Any]]:
    return storage.load_audit_log()


def save_audit_event(event: dict[str, Any]) -> None:
    storage.save_audit_event(event)


def load_deletions() -> list[dict[str, Any]]:
    return storage.load_deletions()


def save_deletion(deletion: dict[str, Any]) -> None:
    storage.save_deletion(deletion)


def load_care_records() -> list[dict[str, Any]]:
    return storage.load_care_records()


def save_care_record(record: dict[str, Any]) -> None:
    storage.save_care_record(record)


def apply_deletion(patient_id: str) -> int:
    return storage.apply_deletion(patient_id)
