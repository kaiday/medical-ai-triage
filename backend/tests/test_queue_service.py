import asyncio
import os

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")

from app.models.schemas import PatientStatus, UrgencyLevel
from app.services import queue_service
from app.services.queue_service import PatientNotFoundError


def _patient_row(**overrides):
    row = {
        "id": "patient-1",
        "patient_ref": "Patient #1",
        "age": 62,
        "chief_complaint": "Crushing chest pain",
        "pain_scale": 9,
        "duration": "Just started",
        "conditions": ["Heart condition"],
        "submitted_at": "2026-04-29T00:00:00+00:00",
        "ai_level": "CRITICAL",
        "ai_confidence": 96,
        "ai_reasoning": "High-risk symptoms.",
        "ai_actions": ["Bring to resus immediately"],
        "ai_source": "openai",
        "final_level": "CRITICAL",
        "confirmed_by": None,
        "confirmed_at": None,
        "seen_at": None,
        "status": "waiting",
    }
    row.update(overrides)
    return row


def test_get_active_queue_uses_postgres_rpc(monkeypatch):
    calls = []

    async def fake_request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        return [
            _patient_row(id="critical", final_level="CRITICAL"),
            _patient_row(id="low", final_level="LOW", ai_level="LOW"),
        ]

    monkeypatch.setattr(queue_service, "_request", fake_request)

    records = asyncio.run(queue_service.get_active_queue())

    assert [record.id for record in records] == ["critical", "low"]
    assert records[0].final_level == UrgencyLevel.CRITICAL
    assert calls == [("POST", "/rpc/get_active_queue", {"json": {}})]


def test_confirm_patient_updates_status_and_nurse(monkeypatch):
    calls = []

    async def fake_request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        return [
            _patient_row(
                status="confirmed",
                confirmed_by="nurse-1",
                confirmed_at="2026-04-29T01:00:00+00:00",
            )
        ]

    monkeypatch.setattr(queue_service, "_request", fake_request)

    record = asyncio.run(queue_service.confirm_patient("patient-1", "nurse-1"))

    assert record.status == PatientStatus.CONFIRMED
    assert record.confirmed_by == "nurse-1"
    assert record.confirmed is True
    assert calls[0][0] == "PATCH"
    assert calls[0][1] == "/patients"
    assert calls[0][2]["json"]["status"] == "confirmed"
    assert calls[0][2]["json"]["confirmed_by"] == "nurse-1"


def test_override_urgency_updates_final_level(monkeypatch):
    calls = []

    async def fake_request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        return [_patient_row(final_level="HIGH")]

    monkeypatch.setattr(queue_service, "_request", fake_request)

    record = asyncio.run(
        queue_service.override_urgency("patient-1", UrgencyLevel.HIGH, "charge-1")
    )

    assert record.final_level == UrgencyLevel.HIGH
    assert calls[0][2]["json"] == {"final_level": "HIGH"}


def test_mark_seen_updates_status_and_seen_at(monkeypatch):
    calls = []

    async def fake_request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        return [
            _patient_row(
                status="seen",
                seen_at="2026-04-29T01:30:00+00:00",
            )
        ]

    monkeypatch.setattr(queue_service, "_request", fake_request)

    record = asyncio.run(queue_service.mark_seen("patient-1"))

    assert record.status == PatientStatus.SEEN
    assert record.seen_at is not None
    assert calls[0][2]["json"]["status"] == "seen"
    assert "seen_at" in calls[0][2]["json"]


def test_unknown_patient_update_raises_not_found(monkeypatch):
    async def fake_request(method, path, **kwargs):
        return []

    monkeypatch.setattr(queue_service, "_request", fake_request)

    with pytest.raises(PatientNotFoundError):
        asyncio.run(queue_service.confirm_patient("missing", "nurse-1"))
