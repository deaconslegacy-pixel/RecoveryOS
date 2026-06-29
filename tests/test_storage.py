from pathlib import Path

from app.storage import Storage


def test_storage_uses_sqlite_for_persistence(tmp_path: Path) -> None:
    storage = Storage(base_path=str(tmp_path))

    storage.save_user({"user_id": "patient-1", "role": "patient"})
    storage.save_care_record({"patient_id": "patient-1", "kind": "checkin", "status": "recorded"})

    users = storage.load_users()
    records = storage.load_care_records()

    assert users[0]["user_id"] == "patient-1"
    assert records[0]["patient_id"] == "patient-1"
    assert records[0]["kind"] == "checkin"
