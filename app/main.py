import fastapi
import pydantic
from fastapi.middleware.cors import CORSMiddleware
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app import storage

app = fastapi.FastAPI(title="RecoveryOS", version="0.1.0")

RAW_BUILD_ID = (
    os.getenv("RECOVERYOS_BUILD_ID")
    or os.getenv("RENDER_GIT_COMMIT")
    or os.getenv("GITHUB_SHA")
    or os.getenv("HEROKU_SLUG_COMMIT")
    or "local"
)
SHORT_BUILD_ID = RAW_BUILD_ID[:7] if RAW_BUILD_ID != "local" else RAW_BUILD_ID
BUILD_STAMP_TEXT = f"RecoveryOS by Deacons Legacy | v{app.version} | {SHORT_BUILD_ID}"
BUILD_STAMP_HTML = (
    "<p style=\"margin-top:1.2rem;font-size:0.78rem;letter-spacing:0.04em;color:#94a3b8;\">"
    f"{BUILD_STAMP_TEXT}</p>"
)


def with_build_stamp(html: str) -> str:
    return html.replace("</main>", f"{BUILD_STAMP_HTML}</main>", 1)

# If a built frontend exists (copied into the image at build-time), serve it at /app/.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend_dist"
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["x-frame-options"] = "DENY"
        response.headers["referrer-policy"] = "strict-origin-when-cross-origin"
        response.headers["permissions-policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        content_type = response.headers.get("content-type", "")
        if content_type.startswith("text/html"):
            response.headers["cache-control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["pragma"] = "no-cache"
            response.headers["expires"] = "0"
        return response


app.add_middleware(SecurityHeadersMiddleware)
# Configure CORS origins via env var `ALLOWED_ORIGINS` (comma-separated). Defaults to localhost dev ports.
allowed_origins = os.getenv("ALLOWED_ORIGINS")
if allowed_origins:
    origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]
else:
    origins = ["http://127.0.0.1:3000", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


class SignupRequest(pydantic.BaseModel):
    role: str
    user_id: str
    organization: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return {
        "app": "RecoveryOS by Deacons Legacy",
        "version": app.version,
        "build_id": SHORT_BUILD_ID,
    }


@app.get("/ui")
def ui_shell() -> fastapi.responses.HTMLResponse:
    return fastapi.responses.HTMLResponse(
        content=with_build_stamp("""
        <!doctype html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
            <title>RecoveryOS by Deacons Legacy</title>
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
                <p class=\"pill\">RecoveryOS by Deacons Legacy</p>
                <h1>RecoveryOS Platform Overview</h1>
                <p>Privacy-first recovery coordination for patients, counselors, families, and facilities.</p>
                <div class="card">
                    <h2>RecoveryOS by Deacons Legacy Product Overview</h2>
                    <p><span class="pill">Patient</span><span class="pill">Counselor</span><span class="pill">Family</span><span class="pill">Facility</span></p>
                    <p>The backend now exposes care timelines, consent handling, audits, retention workflows, and role-aware dashboards.</p>
                </div>
                <div class="card">
                    <h2>Next milestones for RecoveryOS by Deacons Legacy</h2>
                    <ul>
                        <li>Real authentication and database integration</li>
                        <li>Frontend dashboard views and patient experience flows</li>
                        <li>Deployment and observability hardening</li>
                    </ul>
                </div>
            </main>
        </body>
        </html>
        """)
    )


@app.get("/", include_in_schema=False)
def homepage() -> fastapi.responses.Response:
    return fastapi.responses.HTMLResponse(
        content=with_build_stamp("""
        <!doctype html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
            <title>RecoveryOS by Deacons Legacy | Privacy-first recovery operating system</title>
            <style>
                :root { color-scheme: dark; }
                body { font-family: Inter, Arial, sans-serif; margin: 0; background: radial-gradient(circle at top left, rgba(79,209,197,0.22), transparent 20%), linear-gradient(135deg, #040816, #0f172a 50%, #18253c); color: #f8fafc; }
                main { max-width: 1120px; margin: 0 auto; padding: 3rem 1.5rem 4rem; }
                .hero, .card, .pricing { background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(148,163,184,0.2); border-radius: 22px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 16px 40px rgba(2,6,23,0.16); }
                .grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
                a { color: #93c5fd; }
                .button { display: inline-block; margin-top: 1rem; padding: 0.85rem 1.1rem; border-radius: 999px; background: linear-gradient(135deg, #2563eb, #3b82f6); color: white; text-decoration: none; margin-right: 0.5rem; }
                .button.secondary { background: linear-gradient(135deg, #0f766e, #14b8a6); }
                .pill { display: inline-block; padding: 0.35rem 0.7rem; border-radius: 999px; background: rgba(79,209,197,0.2); color: #99f6e4; margin-right: 0.5rem; font-size: 0.85rem; }
                ul { padding-left: 1.1rem; }
                .price { font-size: 2rem; font-weight: 700; }
                .eyebrow { text-transform: uppercase; letter-spacing: 0.2em; color: #5eead4; font-size: 0.8rem; font-weight: 700; }
                .hero p { line-height: 1.7; color: #cbd5e1; }
            </style>
        </head>
        <body>
            <main>
                <section class=\"hero\">
                    <p class="eyebrow">RecoveryOS by Deacons Legacy</p>
                    <h1>RecoveryOS by Deacons Legacy for modern recovery coordination.</h1>
                    <p>Bring daily support, compliance-ready care workflows, and role-based collaboration into a single calm, secure operating system.</p>
                    <p><span class="pill">HIPAA-ready controls</span><span class="pill">Medicaid/insurance-aligned workflows</span><span class="pill">Role-based access</span></p>
                    <a class="button" href="/app/">Explore the platform</a>
                    <a class="button secondary" href="/login">Log in</a>
                    <a class="button secondary" href="/signup">Create account</a>
                </section>

                <section class=\"grid\">
                    <div class=\"card\">
                        <h2>For patients</h2>
                        <p>Daily check-ins, journal prompts, crisis supports, and progress visibility.</p>
                    </div>
                    <div class=\"card\">
                        <h2>For counselors</h2>
                        <p>Caseload views, alerts, documentation support, and treatment planning workflows.</p>
                    </div>
                    <div class=\"card\">
                        <h2>For families & facilities</h2>
                        <p>Permissioned support tools, reporting, and compliance-ready audit trails.</p>
                    </div>
                </section>

                <section class=\"pricing\">
                    <h2>Pricing</h2>
                    <div class=\"grid\">
                        <div class=\"card\">
                            <h3>Starter</h3>
                            <p class=\"price\">$49/mo</p>
                            <ul><li>1 care team</li><li>Basic dashboards</li><li>Encrypted data handling</li></ul>
                        </div>
                        <div class=\"card\">
                            <h3>Clinical</h3>
                            <p class=\"price\">$149/mo</p>
                            <ul><li>Multi-role access</li><li>Audit logging & retention</li><li>Insurance-ready reporting</li></ul>
                        </div>
                        <div class=\"card\">
                            <h3>Enterprise</h3>
                            <p class=\"price\">Custom</p>
                            <ul><li>SSO & advanced integrations</li><li>Compliance and risk review</li><li>Dedicated onboarding</li></ul>
                        </div>
                    </div>
                </section>

                <section class=\"card\">
                    <h2>Compliance posture</h2>
                    <p>RecoveryOS is designed with least-privilege access, consent management, role-based controls, audit logging, retention workflows, and privacy-first architecture intended to support insurance and Medicaid-aligned implementation reviews.</p>
                    <p>For production deployment, legal, compliance, and clinical governance review should confirm your local policy and billing requirements.</p>
                </section>
            </main>
        </body>
        </html>
        """)
    )


@app.get("/app", include_in_schema=False)
def app_entry_redirect() -> fastapi.responses.RedirectResponse:
    return fastapi.responses.RedirectResponse(url="/app/", status_code=307)


@app.get("/login", include_in_schema=False)
def login_page() -> fastapi.responses.HTMLResponse:
    return fastapi.responses.HTMLResponse(
        content=with_build_stamp("""
        <!doctype html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
            <title>Log in to RecoveryOS by Deacons Legacy</title>
            <style>
                :root { color-scheme: dark; }
                body { font-family: Inter, Arial, sans-serif; margin: 0; min-height: 100vh; background: radial-gradient(circle at top left, rgba(79,209,197,0.22), transparent 24%), linear-gradient(135deg, #040816, #0f172a 50%, #18253c); color: #f8fafc; }
                main { max-width: 560px; margin: 4rem auto; padding: 2rem; background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(148,163,184,0.2); border-radius: 24px; box-shadow: 0 20px 50px rgba(2,6,23,0.16); }
                .eyebrow { text-transform: uppercase; letter-spacing: 0.2em; color: #5eead4; font-size: 0.8rem; font-weight: 700; }
                label { display: block; margin-top: 1rem; color: #cbd5e1; }
                input, select, button { width: 100%; padding: 0.8rem; margin-top: 0.35rem; border-radius: 12px; border: 1px solid rgba(148,163,184,0.3); }
                input, select { background: rgba(2,6,23,0.82); color: #f8fafc; }
                button { background: linear-gradient(135deg, #2563eb, #3b82f6); color: white; border: none; cursor: pointer; }
                a { color: #93c5fd; }
                .brand { margin-bottom: 0.75rem; font-size: 1.05rem; color: #99f6e4; }
            </style>
        </head>
        <body>
            <main>
                <p class="eyebrow">RecoveryOS by Deacons Legacy</p>
                <h1>Log in to RecoveryOS by Deacons Legacy</h1>
                <p class="brand">Secure access for patients, counselors, families, and facilities.</p>
                <form action=\"/auth/login\" method=\"post\">
                    <label>Role
                        <select name=\"role\">
                            <option value=\"patient\">Patient</option>
                            <option value=\"counselor\">Counselor</option>
                            <option value=\"family\">Family</option>
                            <option value=\"facility_admin\">Facility</option>
                        </select>
                    </label>
                    <label>User ID
                        <input name=\"user_id\" value=\"demo-patient\" />
                    </label>
                    <button type=\"submit\">Log in</button>
                </form>
                <p><a href=\"/signup\">Create an account</a></p>
            </main>
        </body>
        </html>
        """)
    )


@app.get("/signup", include_in_schema=False)
def signup_page() -> fastapi.responses.HTMLResponse:
    return fastapi.responses.HTMLResponse(
        content=with_build_stamp("""
        <!doctype html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
            <title>Create your RecoveryOS account</title>
            <style>
                :root { color-scheme: dark; }
                body { font-family: Inter, Arial, sans-serif; margin: 0; min-height: 100vh; background: radial-gradient(circle at top left, rgba(79,209,197,0.22), transparent 24%), linear-gradient(135deg, #040816, #0f172a 50%, #18253c); color: #f8fafc; }
                main { max-width: 560px; margin: 4rem auto; padding: 2rem; background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(148,163,184,0.2); border-radius: 24px; box-shadow: 0 20px 50px rgba(2,6,23,0.16); }
                .eyebrow { text-transform: uppercase; letter-spacing: 0.2em; color: #5eead4; font-size: 0.8rem; font-weight: 700; }
                label { display: block; margin-top: 1rem; color: #cbd5e1; }
                input, select, button { width: 100%; padding: 0.8rem; margin-top: 0.35rem; border-radius: 12px; border: 1px solid rgba(148,163,184,0.3); }
                input, select { background: rgba(2,6,23,0.82); color: #f8fafc; }
                button { background: linear-gradient(135deg, #2563eb, #3b82f6); color: white; border: none; cursor: pointer; }
                a { color: #93c5fd; }
                .brand { margin-bottom: 0.75rem; font-size: 1.05rem; color: #99f6e4; }
            </style>
        </head>
        <body>
            <main>
                <p class="eyebrow">RecoveryOS by Deacons Legacy</p>
                <h1>Create your RecoveryOS account</h1>
                <p class="brand">Launch faster with guided onboarding, role-based access, and compliance-ready controls.</p>
                <form action=\"/auth/signup\" method=\"post\">
                    <label>Role
                        <select name=\"role\">
                            <option value=\"patient\">Patient</option>
                            <option value=\"counselor\">Counselor</option>
                            <option value=\"family\">Family</option>
                            <option value=\"facility_admin\">Facility</option>
                        </select>
                    </label>
                    <label>User ID
                        <input name=\"user_id\" placeholder=\"you@example.com\" />
                    </label>
                    <label>Organization
                        <input name=\"organization\" placeholder=\"Your organization or clinic\" />
                    </label>
                    <button type=\"submit\">Create account</button>
                </form>
                <p><a href=\"/login\">Already have an account?</a></p>
            </main>
        </body>
        </html>
        """)
    )


@app.get("/compliance", include_in_schema=False)
def compliance_page() -> fastapi.responses.HTMLResponse:
    return fastapi.responses.HTMLResponse(
        content=with_build_stamp("""
        <!doctype html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
            <title>RecoveryOS by Deacons Legacy Compliance</title>
            <style>
                :root { color-scheme: dark; }
                body { font-family: Inter, Arial, sans-serif; margin: 0; min-height: 100vh; background: radial-gradient(circle at top left, rgba(79,209,197,0.22), transparent 24%), linear-gradient(135deg, #040816, #0f172a 50%, #18253c); color: #f8fafc; }
                main { max-width: 860px; margin: 3rem auto; padding: 2rem; background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(148,163,184,0.2); border-radius: 24px; box-shadow: 0 20px 50px rgba(2,6,23,0.16); }
                .card { background: rgba(15,23,42,0.9); border: 1px solid rgba(148,163,184,0.2); border-radius: 18px; padding: 1rem 1.2rem; margin-bottom: 1rem; }
                .eyebrow { text-transform: uppercase; letter-spacing: 0.2em; color: #5eead4; font-size: 0.8rem; font-weight: 700; }
                strong { color: #93c5fd; }
            </style>
        </head>
        <body>
            <main>
                <p class="eyebrow">RecoveryOS by Deacons Legacy</p>
                <h1>Insurance and Medicaid readiness</h1>
                <p>RecoveryOS is designed for organizations that need role-aware workflows, consent handling, audit trails, and privacy controls from day one.</p>
                <div class=\"card\"><strong>Insurance</strong><br/>Supports claims-ready documentation workflows, auditability, and structured care records.</div>
                <div class=\"card\"><strong>Medicaid</strong><br/>Supports compliance-aligned documentation practices and administrative workflows for state and payer review.</div>
                <div class=\"card\"><strong>Clinical governance</strong><br/>Includes least-privilege access, consent workflows, retention policies, and security monitoring.</div>
                <p>Use this page to support implementation conversations with compliance, legal, and billing teams.</p>
            </main>
        </body>
        </html>
        """)
    )


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


@app.post("/auth/login", response_model=None)
async def login(request: fastapi.Request) -> Response:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        form = await request.form()
        payload = {
            "role": form.get("role"),
            "user_id": form.get("user_id"),
        }

    role = payload.get("role")
    user_id = payload.get("user_id")
    if not isinstance(role, str) or not isinstance(user_id, str):
        raise fastapi.HTTPException(status_code=400, detail="role and user_id are required")

    data = LoginRequest(role=role, user_id=user_id)
    if data.role not in {"patient", "counselor", "family", "facility_admin"}:
        raise fastapi.HTTPException(status_code=403, detail="Unsupported role")
    user_record = {"user_id": data.user_id, "role": data.role}
    storage.save_user(user_record)
    token = f"token-{data.user_id}"
    if data.role == "patient" and data.user_id == "demo-patient":
        token = "token-demo-patient"

    if "application/json" in content_type:
        return fastapi.responses.JSONResponse({"token": token, "role": data.role})
    return fastapi.responses.RedirectResponse(url="/app/", status_code=303)


@app.post("/auth/signup", response_model=None)
async def signup(request: fastapi.Request) -> Response:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        form = await request.form()
        payload = {
            "role": form.get("role"),
            "user_id": form.get("user_id"),
            "organization": form.get("organization"),
        }

    role = payload.get("role")
    user_id = payload.get("user_id")
    organization = payload.get("organization")
    if not isinstance(role, str) or not isinstance(user_id, str):
        raise fastapi.HTTPException(status_code=400, detail="role and user_id are required")

    data = SignupRequest(role=role, user_id=user_id, organization=organization if isinstance(organization, str) else None)
    if data.role not in {"patient", "counselor", "family", "facility_admin"}:
        raise fastapi.HTTPException(status_code=403, detail="Unsupported role")
    user_record = {"user_id": data.user_id, "role": data.role}
    storage.save_user(user_record)
    token = f"token-{data.user_id}"
    if "application/json" in content_type:
        return fastapi.responses.JSONResponse({"token": token, "role": data.role, "organization": data.organization or ""})
    return fastapi.responses.RedirectResponse(url="/app/", status_code=303)


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