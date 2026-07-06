import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DEFAULT_DB_PATH = DATA_DIR / "recoveryos.db"

# Use DATABASE_URL env var for production (e.g. postgres://...), otherwise local sqlite
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DEFAULT_DB_PATH}"

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


class Consent(Base):
    __tablename__ = "consents"
    id = Column(Integer, primary_key=True)
    patient_id = Column(String, nullable=False)
    consent_type = Column(String, nullable=False)
    granted = Column(Boolean, nullable=False)
    scope = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    actor = Column(String, nullable=False)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


class Deletion(Base):
    __tablename__ = "deletions"
    id = Column(Integer, primary_key=True)
    patient_id = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, nullable=False)
    deleted_records = Column(Integer, nullable=False)
    next_step = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


class CareRecord(Base):
    __tablename__ = "care_records"
    id = Column(Integer, primary_key=True)
    patient_id = Column(String, nullable=False)
    kind = Column(String, nullable=False)
    entry = Column(Text)
    mood = Column(Integer)
    sleep_hours = Column(Float)
    cravings = Column(Integer)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)


class Storage:
    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or DATABASE_URL
        # engine and SessionLocal are module-level; ensure tables exist
        Base.metadata.create_all(engine)

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def load_users(self) -> list[dict[str, Any]]:
        with SessionLocal() as session:
            rows = session.query(User).order_by(User.id).all()
            return [
                {
                    "user_id": u.user_id,
                    "role": u.role,
                    "created_at": u.created_at.isoformat(),
                }
                for u in rows
            ]

    def save_user(self, user: dict[str, Any]) -> None:
        with SessionLocal() as session:
            now = user.get("created_at")
            if isinstance(now, str):
                now = datetime.fromisoformat(now)
            now = now or self._now()
            obj = session.query(User).filter_by(user_id=user["user_id"]).one_or_none()
            if obj:
                obj.role = user["role"]
                obj.created_at = now
            else:
                obj = User(user_id=user["user_id"], role=user["role"], created_at=now)
                session.add(obj)
            session.commit()

    def load_consents(self) -> list[dict[str, Any]]:
        with SessionLocal() as session:
            rows = session.query(Consent).order_by(Consent.id).all()
            return [
                {
                    "patient_id": c.patient_id,
                    "consent_type": c.consent_type,
                    "granted": bool(c.granted),
                    "scope": c.scope,
                    "created_at": c.created_at.isoformat(),
                }
                for c in rows
            ]

    def save_consent(self, consent: dict[str, Any]) -> None:
        with SessionLocal() as session:
            now = consent.get("created_at")
            if isinstance(now, str):
                now = datetime.fromisoformat(now)
            now = now or self._now()
            obj = Consent(
                patient_id=consent["patient_id"],
                consent_type=consent["consent_type"],
                granted=bool(consent["granted"]),
                scope=consent["scope"],
                created_at=now,
            )
            session.add(obj)
            session.commit()

    def load_audit_log(self) -> list[dict[str, Any]]:
        with SessionLocal() as session:
            rows = session.query(AuditLog).order_by(AuditLog.id).all()
            return [
                {
                    "actor": a.actor,
                    "action": a.action,
                    "resource": a.resource,
                    "created_at": a.created_at.isoformat(),
                }
                for a in rows
            ]

    def save_audit_event(self, event: dict[str, Any]) -> None:
        with SessionLocal() as session:
            now = event.get("created_at")
            if isinstance(now, str):
                now = datetime.fromisoformat(now)
            now = now or self._now()
            obj = AuditLog(
                actor=event["actor"],
                action=event["action"],
                resource=event["resource"],
                created_at=now,
            )
            session.add(obj)
            session.commit()

    def load_deletions(self) -> list[dict[str, Any]]:
        with SessionLocal() as session:
            rows = session.query(Deletion).order_by(Deletion.id).all()
            return [
                {
                    "patient_id": d.patient_id,
                    "reason": d.reason,
                    "status": d.status,
                    "deleted_records": d.deleted_records,
                    "next_step": d.next_step,
                    "created_at": d.created_at.isoformat(),
                }
                for d in rows
            ]

    def save_deletion(self, deletion: dict[str, Any]) -> None:
        with SessionLocal() as session:
            now = deletion.get("created_at")
            if isinstance(now, str):
                now = datetime.fromisoformat(now)
            now = now or self._now()
            obj = Deletion(
                patient_id=deletion["patient_id"],
                reason=deletion["reason"],
                status=deletion["status"],
                deleted_records=deletion["deleted_records"],
                next_step=deletion["next_step"],
                created_at=now,
            )
            session.add(obj)
            session.commit()

    def load_care_records(self) -> list[dict[str, Any]]:
        with SessionLocal() as session:
            rows = session.query(CareRecord).order_by(CareRecord.id).all()
            return [
                {
                    "patient_id": r.patient_id,
                    "kind": r.kind,
                    "entry": r.entry,
                    "mood": r.mood,
                    "sleep_hours": r.sleep_hours,
                    "cravings": r.cravings,
                    "status": r.status,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in rows
            ]

    def save_care_record(self, record: dict[str, Any]) -> None:
        with SessionLocal() as session:
            now = record.get("timestamp")
            if isinstance(now, str):
                now = datetime.fromisoformat(now)
            now = now or self._now()
            obj = CareRecord(
                patient_id=record["patient_id"],
                kind=record["kind"],
                entry=record.get("entry"),
                mood=record.get("mood"),
                sleep_hours=record.get("sleep_hours"),
                cravings=record.get("cravings"),
                status=record["status"],
                timestamp=now,
            )
            session.add(obj)
            session.commit()

    def apply_deletion(self, patient_id: str) -> int:
        deleted_records = 0
        with SessionLocal() as session:
            user_count = session.query(User).filter_by(user_id=patient_id).count()
            if user_count:
                session.query(User).filter_by(user_id=patient_id).delete()
                deleted_records += user_count

            consent_count = session.query(Consent).filter_by(patient_id=patient_id).count()
            if consent_count:
                session.query(Consent).filter_by(patient_id=patient_id).delete()
                deleted_records += consent_count

            care_count = session.query(CareRecord).filter_by(patient_id=patient_id).count()
            if care_count:
                session.query(CareRecord).filter_by(patient_id=patient_id).delete()
                deleted_records += care_count

            audit_count = session.query(AuditLog).count()
            if audit_count:
                session.query(AuditLog).delete()
                deleted_records += audit_count

            session.commit()
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
