import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")
os.environ.setdefault("AUTH_ENABLED", "false")

from app.models.schemas import (
    PatientIntake,
    PatientRecord,
    PatientStatus,
    StaffRole,
    StaffUser,
    TriageResult,
    UrgencyLevel,
)
from app.core import auth
from app.routers import queue
from app.services.queue_service import PatientNotFoundError


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(queue.router)
    return TestClient(app)


def _patient(level: UrgencyLevel = UrgencyLevel.LOW) -> PatientRecord:
    return PatientRecord(
        id="patient-1",
        patient_ref="Patient #1",
        intake=PatientIntake(chief_complaint="Mild headache", pain_scale=3),
        triage=TriageResult(
            urgency=level,
            confidence=70,
            reasoning="Low acuity symptoms.",
            recommended_actions=["Monitor symptoms"],
            escalation_flag=False,
            source="rule-based",
        ),
        final_level=level,
        submitted_at="2026-04-29T00:00:00+00:00",
    )


def test_get_queue_returns_records(monkeypatch):
    async def fake_get_active_queue():
        return [_patient(UrgencyLevel.CRITICAL), _patient(UrgencyLevel.LOW)]

    monkeypatch.setattr(queue.queue_service, "get_active_queue", fake_get_active_queue)

    response = _client().get("/queue")

    assert response.status_code == 200
    assert [item["finalLevel"] for item in response.json()] == ["CRITICAL", "LOW"]


def test_confirm_unknown_patient_returns_404(monkeypatch):
    async def fake_confirm_patient(patient_id, nurse_id):
        raise PatientNotFoundError(f"Patient {patient_id} was not found.")

    monkeypatch.setattr(queue.queue_service, "confirm_patient", fake_confirm_patient)

    response = _client().patch("/queue/missing/status")

    assert response.status_code == 404


def test_override_accepts_charge_nurse(monkeypatch):
    async def fake_override(patient_id, new_level, nurse_id):
        assert patient_id == "patient-1"
        assert new_level == UrgencyLevel.HIGH
        assert nurse_id == "charge-1"
        return _patient(UrgencyLevel.HIGH)

    monkeypatch.setattr(queue.queue_service, "override_urgency", fake_override)

    app = FastAPI()
    app.include_router(queue.router)
    app.dependency_overrides[auth.get_current_user] = lambda: StaffUser(
        id="charge-1",
        email="charge@test.com",
        role=StaffRole.CHARGE_NURSE,
    )

    response = TestClient(app).post(
        "/queue/patient-1/override",
        json={"level": "HIGH"},
    )

    assert response.status_code == 200
    assert response.json()["finalLevel"] == "HIGH"


def test_override_rejects_nurse_role(monkeypatch):
    async def fake_override(patient_id, new_level, nurse_id):
        raise AssertionError("Override service should not be called for nurse role")

    monkeypatch.setattr(queue.queue_service, "override_urgency", fake_override)

    app = FastAPI()
    app.include_router(queue.router)
    app.dependency_overrides[auth.get_current_user] = lambda: StaffUser(
        id="nurse-1",
        email="nurse@test.com",
        role=StaffRole.NURSE,
    )

    response = TestClient(app).post(
        "/queue/patient-1/override",
        json={"level": "HIGH"},
    )

    assert response.status_code == 403


def test_override_invalid_level_returns_422():
    response = _client().post(
        "/queue/patient-1/override",
        headers={"X-Staff-Role": "charge_nurse"},
        json={"level": "URGENT"},
    )

    assert response.status_code == 422


def test_mark_seen_returns_updated_record(monkeypatch):
    async def fake_mark_seen(patient_id):
        record = _patient()
        record.status = PatientStatus.SEEN
        record.seen_at = "2026-04-29T02:00:00+00:00"
        return record

    monkeypatch.setattr(queue.queue_service, "mark_seen", fake_mark_seen)

    response = _client().post("/queue/patient-1/seen")

    assert response.status_code == 200
    assert response.json()["status"] == "seen"
