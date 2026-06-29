import fastapi
import pydantic
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app import storage

app = fastapi.FastAPI(title="RecoveryOS", version="0.1.0")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["x-frame-options"] = "DENY"
        response.headers["referrer-policy"] = "strict-origin-when-cross-origin"
        response.headers["permissions-policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DailyCheckIn(pydantic.BaseModel):
    patient_id: str
    mood: int
    sleep_hours: float
    cravings: int


class JournalEntry(pydantic.BaseModel):
    patient_id: str
    entry: str


class CrisisSupportRequest(pydantic.BaseModel):
    patient_id: str
    urgency: str


class ConsentRecord(pydantic.BaseModel):
    patient_id: str
    consent_type: str
    granted: bool
    scope: str


class AuditLogEntry(pydantic.BaseModel):
    actor: str
    action: str
    resource: str


class IncidentReport(pydantic.BaseModel):
    severity: str
    summary: str


class DataDeletionRequest(pydantic.BaseModel):
    patient_id: str
    reason: str


class LoginRequest(pydantic.BaseModel):
    role: str
    user_id: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ui")
def ui_shell() -> fastapi.responses.HTMLResponse:
    return fastapi.responses.HTMLResponse(
        content="""
        <!doctype html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
            <title>RecoveryOS</title>
            <style>
                body { font-family: Inter, Arial, sans-serif; margin: 0; background: #0f172a; color: #f8fafc; }
                main { max-width: 960px; margin: 0 auto; padding: 3rem 1.5rem; }
                .card { background: #111827; border: 1px solid #334155; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; }
                .pill { display: inline-block; padding: 0.3rem 0.75rem; border-radius: 999px; background: #2563eb; margin-right: 0.5rem; }
                a { color: #93c5fd; }
            </style>
        </head>
        <body>
            <main>
                <h1>RecoveryOS</h1>
                <p>Privacy-first recovery coordination for patients, counselors, families, and facilities.</p>
                <div class="card">
                    <h2>Product Overview</h2>
                    <p><span class="pill">Patient</span><span class="pill">Counselor</span><span class="pill">Family</span><span class="pill">Facility</span></p>
                    <p>The backend now exposes care timelines, consent handling, audits, retention workflows, and role-aware dashboards.</p>
                </div>
                <div class="card">
                    <h2>Next milestones</h2>
                    <ul>
                        <li>Real authentication and database integration</li>
                        <li>Frontend dashboard views and patient experience flows</li>
                        <li>Deployment and observability hardening</li>
                    </ul>
                </div>
            </main>
        </body>
        </html>
        """
    )


@app.get("/")
def homepage() -> dict[str, object]:
    return {
        "name": "RecoveryOS",
        "vision": "An operating system for recovery.",
        "apps": [
            {
                "slug": "patient",
                "name": "Patient App",
                "description": "AI recovery companion with daily check-ins, journaling, and crisis tools.",
            },
            {
                "slug": "counselor",
                "name": "Counselor Dashboard",
                "description": "Caseload insights, risk alerts, and AI documentation.",
            },
            {
                "slug": "family",
                "name": "Family App",
                "description": "Education, communication tools, and progress updates.",
            },
            {
                "slug": "facility",
                "name": "Facility Dashboard",
                "description": "Analytics, outcomes, compliance, and staff insights.",
            },
            {
                "slug": "intelligence",
                "name": "AI Intelligence Layer",
                "description": "Predictive relapse scoring and personalized recommendations.",
            },
        ],
    }


@app.get("/apps")
def apps_catalog() -> list[dict[str, str]]:
    return [
        {
            "slug": "patient",
            "name": "Patient App",
            "description": "AI recovery companion with daily check-ins, journaling, and crisis tools.",
        },
        {
            "slug": "counselor",
            "name": "Counselor Dashboard",
            "description": "Caseload insights, risk alerts, and AI documentation.",
        },
        {
            "slug": "family",
            "name": "Family App",
            "description": "Education, communication tools, and progress updates.",
        },
        {
            "slug": "facility",
            "name": "Facility Dashboard",
            "description": "Analytics, outcomes, compliance, and staff insights.",
        },
        {
            "slug": "intelligence",
            "name": "AI Intelligence Layer",
            "description": "Predictive relapse scoring and personalized recommendations.",
        },
    ]


@app.get("/privacy/notice")
def privacy_notice() -> dict[str, object]:
    return {
        "summary": "RecoveryOS is designed to collect the minimum necessary data for recovery support and uses consent management, role-based access, and audit logging.",
        "applicable_laws": [
            "HIPAA",
            "42 CFR Part 2",
            "State behavioral health privacy statutes",
        ],
        "required_controls": [
            "Consent management",
            "Role-based access control",
            "Encryption in transit and at rest",
            "Audit logging and monitoring",
        ],
    }


@app.post("/privacy/consent")
def privacy_consent(data: ConsentRecord) -> dict[str, object]:
    consent_record = {
        "patient_id": data.patient_id,
        "consent_type": data.consent_type,
        "granted": data.granted,
        "scope": data.scope,
        "status": "recorded",
    }
    storage.save_consent(consent_record)
    return consent_record


@app.get("/security/access-policy")
def access_policy() -> dict[str, object]:
    return {
        "roles": ["patient", "counselor", "family", "facility_admin"],
        "enforcement": "least_privilege",
        "requirements": [
            "Role-based access control",
            "Authentication required for all sensitive actions",
            "Segregation of duties",
        ],
    }


@app.post("/security/audit-log")
def audit_log(data: AuditLogEntry) -> dict[str, object]:
    event: dict[str, object] = {
        "actor": data.actor,
        "action": data.action,
        "resource": data.resource,
        "status": "recorded",
    }
    storage.save_audit_event(event)
    return event


@app.get("/security/retention-policy")
def retention_policy() -> dict[str, object]:
    return {
        "minimum_retention_days": 2555,
        "deletion_required": True,
        "notes": "Records should be retained according to applicable law and then securely deleted or archived.",
    }


@app.get("/security/data-minimization")
def data_minimization() -> dict[str, object]:
    return {
        "minimum_fields_required": 3,
        "sensitive_data_redaction": True,
        "notes": "Only collect data needed for treatment, safety, and compliance.",
    }


@app.post("/security/delete-data")
def delete_data(data: DataDeletionRequest) -> dict[str, object]:
    deleted_records = 0
    if data.reason == "retention_expired":
        deleted_records = storage.apply_deletion(data.patient_id)
        status = "completed"
    else:
        status = "queued"

    deletion_record = {
        "patient_id": data.patient_id,
        "reason": data.reason,
        "status": status,
        "deleted_records": deleted_records,
        "next_step": "Verify identity and process secure deletion",
    }
    storage.save_deletion(deletion_record)
    return deletion_record


@app.post("/auth/login")
def login(data: LoginRequest) -> dict[str, str]:
    if data.role not in {"patient", "counselor", "family", "facility_admin"}:
        raise fastapi.HTTPException(status_code=403, detail="Unsupported role")
    user_record = {"user_id": data.user_id, "role": data.role}
    storage.save_user(user_record)
    token = f"token-{data.user_id}"
    if data.role == "patient" and data.user_id == "demo-patient":
        token = "token-demo-patient"
    return {"token": token, "role": data.role}


@app.get("/auth/me")
def current_user(request: fastapi.Request) -> dict[str, str]:
    authorization = request.headers.get("authorization", "")
    if not authorization.startswith("Bearer "):
        raise fastapi.HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    if token not in {"token-counselor-1", "token-demo-patient", "token-patient-1", "token-family-1", "token-facility-1"}:
        raise fastapi.HTTPException(status_code=401, detail="Invalid token")
    if token.startswith("token-counselor"):
        role_name = "counselor"
    elif token.startswith("token-demo-patient") or token.startswith("token-patient"):
        role_name = "patient"
    elif token.startswith("token-family"):
        role_name = "family"
    else:
        role_name = "facility_admin"
    return {"token": token, "role": role_name}


@app.post("/security/incident-report")
def incident_report(data: IncidentReport) -> dict[str, object]:
    return {
        "severity": data.severity,
        "summary": data.summary,
        "status": "opened",
        "follow_up": "Notify compliance and security teams immediately",
    }


def require_role(request: fastapi.Request, allowed_roles: set[str]) -> str:
    authorization = request.headers.get("authorization", "")
    if not authorization.startswith("Bearer "):
        raise fastapi.HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    if token not in {"token-counselor-1", "token-demo-patient", "token-patient-1", "token-family-1", "token-facility-1"}:
        raise fastapi.HTTPException(status_code=401, detail="Invalid token")
    if token.startswith("token-counselor"):
        role_name = "counselor"
    elif token.startswith("token-demo-patient") or token.startswith("token-patient"):
        role_name = "patient"
    elif token.startswith("token-family"):
        role_name = "family"
    else:
        role_name = "facility_admin"
    if role_name not in allowed_roles:
        raise fastapi.HTTPException(status_code=403, detail="Forbidden")
    return role_name


@app.get("/patient/dashboard")
def patient_dashboard(request: fastapi.Request) -> dict[str, object]:
    require_role(request, {"patient", "counselor"})
    return {
        "patient_id": "demo-patient",
        "focus": "Stability, connection, and daily progress",
        "daily_goals": [
            "Attend one recovery meeting",
            "Log one reflection",
            "Message a support person",
        ],
    }


@app.post("/patient/journal")
def patient_journal(request: fastapi.Request, data: JournalEntry) -> dict[str, object]:
    require_role(request, {"patient"})
    record = {
        "kind": "journal",
        "patient_id": data.patient_id,
        "entry": data.entry,
        "status": "recorded",
    }
    storage.save_care_record(record)
    return {
        "patient_id": data.patient_id,
        "entry": data.entry,
        "saved": True,
    }


@app.get("/patient/timeline")
def patient_timeline(request: fastapi.Request, patient_id: str) -> dict[str, object]:
    require_role(request, {"patient", "counselor"})
    events = [
        {
            **event,
            "timestamp": event.get("timestamp") or "1970-01-01T00:00:00+00:00",
        }
        for event in storage.load_care_records()
        if event.get("patient_id") == patient_id
    ]
    events = sorted(events, key=lambda event: str(event.get("timestamp", "")), reverse=True)
    return {
        "patient_id": patient_id,
        "events": events,
    }


@app.post("/patient/crisis-support")
def patient_crisis_support(data: CrisisSupportRequest) -> dict[str, object]:
    return {
        "patient_id": data.patient_id,
        "urgency": data.urgency,
        "message": "If you are in immediate danger, call 988 or go to the nearest emergency room.",
    }


class TreatmentPlanRequest(pydantic.BaseModel):
    patient_id: str
    focus: str


class FamilyMessageRequest(pydantic.BaseModel):
    patient_id: str
    message: str


class StaffInsightRequest(pydantic.BaseModel):
    staff_id: str
    focus: str


class IntelligenceSummaryRequest(pydantic.BaseModel):
    patient_id: str
    notes: str


@app.get("/counselor/dashboard")
def counselor_dashboard(request: fastapi.Request) -> dict[str, object]:
    require_role(request, {"counselor"})
    return {
        "caseload_size": 12,
        "high_risk_patients": 2,
        "alerts": [
            {"name": "Demo Patient", "level": "high", "reason": "Missed two check-ins"},
            {"name": "Alex Chen", "level": "medium", "reason": "Low engagement"},
        ],
    }


@app.post("/counselor/treatment-plan")
def counselor_treatment_plan(request: fastapi.Request, data: TreatmentPlanRequest) -> dict[str, object]:
    require_role(request, {"counselor"})
    return {
        "patient_id": data.patient_id,
        "focus": data.focus,
        "status": "draft",
    }


@app.get("/family/dashboard")
def family_dashboard(request: fastapi.Request) -> dict[str, object]:
    require_role(request, {"family"})
    return {
        "patient_id": "demo-patient",
        "resources": [
            {"title": "Recovery Basics", "link": "/resources/recovery-basics"},
            {"title": "Communication Tips", "link": "/resources/communication-tips"},
        ],
        "permissions": {"progress_updates": True, "messages": True},
    }


@app.post("/family/message")
def family_message(request: fastapi.Request, data: FamilyMessageRequest) -> dict[str, object]:
    require_role(request, {"family"})
    return {
        "patient_id": data.patient_id,
        "message": data.message,
        "shared_with_patient": True,
    }


@app.get("/facility/dashboard")
def facility_dashboard(request: fastapi.Request) -> dict[str, object]:
    require_role(request, {"facility_admin"})
    return {
        "program_capacity": 120,
        "completion_rate": 0.86,
        "alerts": [
            {"type": "compliance", "message": "Documentation lag for 3 cases"},
            {"type": "outcome", "message": "Engagement trend improving"},
        ],
    }


@app.post("/facility/staff-insight")
def facility_staff_insight(request: fastapi.Request, data: StaffInsightRequest) -> dict[str, object]:
    require_role(request, {"facility_admin"})
    return {
        "staff_id": data.staff_id,
        "focus": data.focus,
        "recommendation": "Increase outreach to participants with low recent engagement",
    }


@app.get("/intelligence/dashboard")
def intelligence_dashboard() -> dict[str, object]:
    return {
        "patient_id": "demo-patient",
        "relapse_risk": "moderate",
        "recommendations": [
            "Schedule a support call",
            "Review recent journal entries",
            "Increase check-in frequency",
        ],
    }


@app.post("/intelligence/summary")
def intelligence_summary(data: IntelligenceSummaryRequest) -> dict[str, object]:
    return {
        "patient_id": data.patient_id,
        "summary": f"{data.notes} This suggests steady engagement with a manageable risk level.",
        "confidence": 0.82,
    }


@app.post("/checkin")
def checkin(data: DailyCheckIn) -> dict[str, object]:
    record = {
        "kind": "checkin",
        "patient_id": data.patient_id,
        "mood": data.mood,
        "sleep_hours": data.sleep_hours,
        "cravings": data.cravings,
        "status": "recorded",
    }
    storage.save_care_record(record)
    return {
        "message": "Thanks for checking in",
        "patient_id": data.patient_id,
        "mood": data.mood,
        "sleep_hours": data.sleep_hours,
        "cravings": data.cravings,
        "status": "recorded",
    }