from fastapi.testclient import TestClient

from app import storage
from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version() -> None:
    response = client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert body["app"] == "RecoveryOS by Deacons Legacy"
    assert body["version"] == "0.1.0"
    assert "build_id" in body


def test_security_headers_are_applied() -> None:
    response = client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_privacy_notice_describes_required_controls() -> None:
    response = client.get("/privacy/notice")
    assert response.status_code == 200
    body = response.json()
    assert "hipaa" in " ".join(body["applicable_laws"]).lower()
    assert "consent" in body["required_controls"][0].lower()


def test_consent_record_is_recorded() -> None:
    response = client.post(
        "/privacy/consent",
        json={
            "patient_id": "demo-patient",
            "consent_type": "family_access",
            "granted": True,
            "scope": "progress_updates",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "demo-patient"
    assert body["status"] == "recorded"
    assert body["granted"] is True


def test_access_policy_describes_role_based_controls() -> None:
    response = client.get("/security/access-policy")
    assert response.status_code == 200
    body = response.json()
    assert "patient" in body["roles"]
    assert body["enforcement"] == "least_privilege"


def test_login_persists_a_user_record() -> None:
    response = client.post(
        "/auth/login",
        json={"role": "counselor", "user_id": "counselor-2"},
    )
    assert response.status_code == 200
    users = storage.load_users()
    assert any(user["user_id"] == "counselor-2" and user["role"] == "counselor" for user in users)


def test_signup_persists_a_user_record_and_returns_token() -> None:
    response = client.post(
        "/auth/signup",
        json={"role": "patient", "user_id": "new-patient", "organization": "RecoveryOS Demo"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "patient"
    assert body["token"].startswith("token-")
    users = storage.load_users()
    assert any(user["user_id"] == "new-patient" and user["role"] == "patient" for user in users)


def test_form_login_redirects_to_app_dashboard() -> None:
    response = client.post(
        "/auth/login",
        data={"role": "patient", "user_id": "demo-patient"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/app/"


def test_form_signup_redirects_to_app_dashboard() -> None:
    response = client.post(
        "/auth/signup",
        data={"role": "patient", "user_id": "form-signup", "organization": "RecoveryOS Demo"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/app/"


def test_audit_log_is_recorded_and_persisted() -> None:
    response = client.post(
        "/security/audit-log",
        json={"actor": "counselor", "action": "viewed_treatment_plan", "resource": "patient:demo-patient"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "recorded"
    assert body["actor"] == "counselor"


def test_retention_policy_describes_required_periods() -> None:
    response = client.get("/security/retention-policy")
    assert response.status_code == 200
    body = response.json()
    assert body["minimum_retention_days"] == 2555
    assert body["deletion_required"] is True


def test_data_minimization_policy_is_defined() -> None:
    response = client.get("/security/data-minimization")
    assert response.status_code == 200
    body = response.json()
    assert body["minimum_fields_required"] == 3
    assert body["sensitive_data_redaction"] is True


def test_data_deletion_workflow_is_created() -> None:
    response = client.post(
        "/security/delete-data",
        json={"patient_id": "demo-patient", "reason": "requested_by_patient"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "demo-patient"
    assert body["status"] == "queued"


def test_retention_enforcement_records_and_executes_deletion() -> None:
    response = client.post(
        "/security/delete-data",
        json={"patient_id": "demo-patient", "reason": "retention_expired"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["deleted_records"] >= 1


def test_care_record_is_persisted_when_checkin_is_submitted() -> None:
    response = client.post(
        "/checkin",
        json={"patient_id": "demo-patient", "mood": 4, "sleep_hours": 7.5, "cravings": 1},
    )
    assert response.status_code == 200
    records = storage.load_care_records()
    assert any(record["patient_id"] == "demo-patient" and record["kind"] == "checkin" for record in records)


def test_journal_entry_is_persisted_when_submitted() -> None:
    response = client.post(
        "/patient/journal",
        json={"patient_id": "demo-patient", "entry": "I stayed calm today."},
        headers={"Authorization": "Bearer token-demo-patient"},
    )
    assert response.status_code == 200
    records = storage.load_care_records()
    assert any(record["patient_id"] == "demo-patient" and record["kind"] == "journal" for record in records)


def test_patient_timeline_returns_stored_care_events() -> None:
    response = client.get(
        "/patient/timeline",
        params={"patient_id": "demo-patient"},
        headers={"Authorization": "Bearer token-demo-patient"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "demo-patient"
    assert any(event["kind"] == "checkin" for event in body["events"])
    assert any(event["kind"] == "journal" for event in body["events"])
    assert all("timestamp" in event for event in body["events"])


def test_authentication_token_is_issued_for_valid_role() -> None:
    response = client.post(
        "/auth/login",
        json={"role": "counselor", "user_id": "counselor-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "counselor"
    assert body["token"].startswith("token-")


def test_patient_login_returns_the_expected_demo_token() -> None:
    response = client.post(
        "/auth/login",
        json={"role": "patient", "user_id": "demo-patient"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token"] == "token-demo-patient"


def test_cors_headers_are_present_for_browser_requests() -> None:
    response = client.get("/health", headers={"Origin": "http://127.0.0.1:3000"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"


def test_authorized_endpoint_accepts_valid_token() -> None:
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer token-counselor-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "counselor"


def test_unauthorized_endpoint_rejects_missing_token() -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_patient_data_is_protected_from_non_patient_roles() -> None:
    response = client.get(
        "/patient/dashboard",
        headers={"Authorization": "Bearer token-counselor-1"},
    )
    assert response.status_code == 200

    response = client.get(
        "/patient/dashboard",
        headers={"Authorization": "Bearer token-family-1"},
    )
    assert response.status_code == 403


def test_counselor_dashboard_requires_counselor_role() -> None:
    response = client.get(
        "/counselor/dashboard",
        headers={"Authorization": "Bearer token-counselor-1"},
    )
    assert response.status_code == 200

    response = client.get(
        "/counselor/dashboard",
        headers={"Authorization": "Bearer token-patient-1"},
    )
    assert response.status_code == 403


def test_family_dashboard_requires_family_role() -> None:
    response = client.get(
        "/family/dashboard",
        headers={"Authorization": "Bearer token-family-1"},
    )
    assert response.status_code == 200

    response = client.get(
        "/family/dashboard",
        headers={"Authorization": "Bearer token-patient-1"},
    )
    assert response.status_code == 403


def test_facility_dashboard_requires_facility_role() -> None:
    response = client.get(
        "/facility/dashboard",
        headers={"Authorization": "Bearer token-facility-1"},
    )
    assert response.status_code == 200

    response = client.get(
        "/facility/dashboard",
        headers={"Authorization": "Bearer token-patient-1"},
    )
    assert response.status_code == 403


def test_incident_report_is_created() -> None:
    response = client.post(
        "/security/incident-report",
        json={"severity": "high", "summary": "Potential unauthorized access to treatment notes"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "opened"
    assert body["severity"] == "high"


def test_homepage_promotes_app_access() -> None:
    response = client.get("/")
    assert response.status_code == 200
    body = response.text.lower()
    assert "recoveryos" in body
    assert "/app/" in body


def test_app_route_redirects_to_frontend_entry() -> None:
    response = client.get("/app", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"].startswith("/app/?v=")


def test_root_serves_branded_homepage() -> None:
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 200
    assert "RecoveryOS by Deacons Legacy" in response.text


def test_ui_shell_is_served() -> None:
    response = client.get("/ui")
    assert response.status_code == 200
    assert "RecoveryOS" in response.text


def test_login_page_serves_account_access_form() -> None:
    response = client.get("/login")
    assert response.status_code == 200
    assert "Log in to RecoveryOS" in response.text
    assert "/auth/login" in response.text


def test_signup_page_serves_account_creation_form() -> None:
    response = client.get("/signup")
    assert response.status_code == 200
    assert "Create your RecoveryOS by Deacons Legacy account" in response.text
    assert "/auth/signup" in response.text


def test_compliance_page_highlights_insurance_and_medicaid_readiness() -> None:
    response = client.get("/compliance")
    assert response.status_code == 200
    assert "Insurance" in response.text
    assert "Medicaid" in response.text


def test_apps_catalog_lists_five_integrated_apps() -> None:
    response = client.get("/apps")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 5
    slugs = {item["slug"] for item in body}
    assert slugs == {"patient", "counselor", "family", "facility", "intelligence"}


def test_patient_dashboard_returns_recovery_plan() -> None:
    response = client.get(
        "/patient/dashboard",
        headers={"Authorization": "Bearer token-demo-patient"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "demo-patient"
    assert body["focus"] == "Stability, connection, and daily progress"
    assert len(body["daily_goals"]) == 3


def test_patient_journal_entry_is_recorded() -> None:
    response = client.post(
        "/patient/journal",
        json={"patient_id": "demo-patient", "entry": "Today I stayed grounded and reached out for support."},
        headers={"Authorization": "Bearer token-demo-patient"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "demo-patient"
    assert body["entry"] == "Today I stayed grounded and reached out for support."
    assert body["saved"] is True


def test_patient_crisis_support_returns_resources() -> None:
    response = client.post(
        "/patient/crisis-support",
        json={"patient_id": "demo-patient", "urgency": "high"},
        headers={"Authorization": "Bearer token-demo-patient"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "demo-patient"
    assert body["urgency"] == "high"
    assert "call 988" in body["message"].lower()


def test_counselor_dashboard_returns_risk_and_planning_data() -> None:
    response = client.get(
        "/counselor/dashboard",
        headers={"Authorization": "Bearer token-counselor-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["caseload_size"] == 12
    assert body["high_risk_patients"] == 2
    assert any(item["name"] == "Demo Patient" for item in body["alerts"])


def test_counselor_treatment_plan_is_created() -> None:
    response = client.post(
        "/counselor/treatment-plan",
        json={"patient_id": "demo-patient", "focus": "weekly check-ins and relapse prevention"},
        headers={"Authorization": "Bearer token-counselor-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "demo-patient"
    assert body["focus"] == "weekly check-ins and relapse prevention"
    assert body["status"] == "draft"


def test_family_dashboard_returns_support_resources_and_updates() -> None:
    response = client.get(
        "/family/dashboard",
        headers={"Authorization": "Bearer token-family-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "demo-patient"
    assert any(resource["title"] == "Recovery Basics" for resource in body["resources"])
    assert body["permissions"]["progress_updates"] is True


def test_family_message_is_created_with_permission_check() -> None:
    response = client.post(
        "/family/message",
        json={"patient_id": "demo-patient", "message": "Thinking of you today."},
        headers={"Authorization": "Bearer token-family-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "demo-patient"
    assert body["message"] == "Thinking of you today."
    assert body["shared_with_patient"] is True


def test_facility_dashboard_returns_analytics_and_compliance_data() -> None:
    response = client.get(
        "/facility/dashboard",
        headers={"Authorization": "Bearer token-facility-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["program_capacity"] == 120
    assert body["completion_rate"] == 0.86
    assert any(item["type"] == "compliance" for item in body["alerts"])


def test_facility_staff_insight_is_generated() -> None:
    response = client.post(
        "/facility/staff-insight",
        json={"staff_id": "staff-7", "focus": "engagement"},
        headers={"Authorization": "Bearer token-facility-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["staff_id"] == "staff-7"
    assert body["focus"] == "engagement"
    assert body["recommendation"] == "Increase outreach to participants with low recent engagement"


def test_intelligence_dashboard_returns_risk_and_recommendations() -> None:
    response = client.get("/intelligence/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "demo-patient"
    assert body["relapse_risk"] == "moderate"
    assert len(body["recommendations"]) == 3


def test_intelligence_summary_is_generated() -> None:
    response = client.post(
        "/intelligence/summary",
        json={"patient_id": "demo-patient", "notes": "Patient engaged well this week but missed one check-in."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "demo-patient"
    assert "engaged well" in body["summary"].lower()
    assert body["confidence"] == 0.82
