import fastapi
import pydantic

app = fastapi.FastAPI(title="RecoveryOS", version="0.1.0")


class DailyCheckIn(pydantic.BaseModel):
    patient_id: str
    mood: int
    sleep_hours: float
    cravings: int


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/checkin")
def checkin(data: DailyCheckIn) -> dict[str, object]:
    return {
        "message": "Thanks for checking in",
        "patient_id": data.patient_id,
        "mood": data.mood,
        "sleep_hours": data.sleep_hours,
        "cravings": data.cravings,
    }