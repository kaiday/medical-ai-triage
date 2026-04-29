"""
Phase 5 auth tests — T-12 through T-17.

Covers:
  T-12  AUTH_ENABLED=false  → all queue endpoints open (no token needed)
  T-13  AUTH_ENABLED=true, no token  → 401 on all protected endpoints
  T-14  nurse JWT  → GET /queue returns 200
  T-15  nurse JWT  → POST /queue/{id}/override returns 403
  T-16  charge_nurse JWT  → POST /queue/{id}/override returns 200 or 404
  T-17  POST /triage never requires a token (checked both modes)
"""

import time
from unittest.mock import patch, AsyncMock
import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.models.schemas import (
    PatientIntake, PatientRecord, TriageResult, UrgencyLevel, PatientStatus,
)


def _dummy_patient() -> PatientRecord:
    return PatientRecord(
        id="test-id",
        patient_ref="P-TEST",
        intake=PatientIntake(chief_complaint="test complaint", pain_scale=5),
        triage=TriageResult(
            urgency=UrgencyLevel.LOW,
            confidence=50,
            reasoning="test",
            recommended_actions=["monitor"],
            escalation_flag=False,
            source="rule-based",
        ),
        final_level=UrgencyLevel.LOW,
        submitted_at="2026-04-29T00:00:00Z",
    )

TEST_SECRET = "test-secret-unit-tests-only"


def _make_jwt(role: str) -> str:
    return jwt.encode(
        {
            "sub": f"test-{role}-id",
            "email": f"{role}@test.com",
            "role": "authenticated",
            "app_metadata": {"role": role},
            "aud": "authenticated",
            "exp": int(time.time()) + 3600,
        },
        TEST_SECRET,
        algorithm="HS256",
    )


def _bearer(role: str) -> dict:
    return {"Authorization": f"Bearer {_make_jwt(role)}"}


@pytest.fixture()
def client_dev():
    """AUTH_ENABLED=False — dev bypass active."""
    from app.main import app
    from app.core import auth as auth_module

    with patch.object(auth_module.settings, "AUTH_ENABLED", False), \
         patch.object(auth_module.settings, "SUPABASE_JWT_SECRET", None):
        yield TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def client_prod():
    """AUTH_ENABLED=True with a known test secret — full RBAC."""
    from app.main import app
    from app.core import auth as auth_module

    with patch.object(auth_module.settings, "AUTH_ENABLED", True), \
         patch.object(auth_module.settings, "SUPABASE_JWT_SECRET", TEST_SECRET):
        yield TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# T-12: dev mode — no token required anywhere in /queue
# ---------------------------------------------------------------------------

class TestT12AuthDisabled:
    @pytest.fixture(autouse=True)
    def _mock_queue(self, monkeypatch):
        from app.services import queue_service
        monkeypatch.setattr(queue_service, "get_active_queue", AsyncMock(return_value=[]))
        monkeypatch.setattr(queue_service, "confirm_patient", AsyncMock(return_value=_dummy_patient()))
        monkeypatch.setattr(queue_service, "override_urgency", AsyncMock(return_value=_dummy_patient()))
        monkeypatch.setattr(queue_service, "mark_seen", AsyncMock(return_value=_dummy_patient()))
        monkeypatch.setattr(queue_service, "get_seen_today", AsyncMock(return_value=[]))

    def test_get_queue(self, client_dev):
        assert client_dev.get("/queue/").status_code == 200

    def test_patch_status(self, client_dev):
        assert client_dev.patch("/queue/test-id/status").status_code == 200

    def test_post_override(self, client_dev):
        assert client_dev.post("/queue/test-id/override", json={"level": "HIGH"}).status_code == 200

    def test_post_seen(self, client_dev):
        assert client_dev.post("/queue/test-id/seen").status_code == 200

    def test_get_seen_today(self, client_dev):
        assert client_dev.get("/queue/seen-today").status_code == 200


# ---------------------------------------------------------------------------
# T-13: prod mode, no token → 401 on every protected endpoint
# ---------------------------------------------------------------------------

class TestT13NoToken:
    def test_get_queue_401(self, client_prod):
        assert client_prod.get("/queue/").status_code == 401

    def test_patch_status_401(self, client_prod):
        assert client_prod.patch("/queue/test-id/status").status_code == 401

    def test_post_override_401(self, client_prod):
        assert client_prod.post("/queue/test-id/override").status_code == 401

    def test_post_seen_401(self, client_prod):
        assert client_prod.post("/queue/test-id/seen").status_code == 401

    def test_get_seen_today_401(self, client_prod):
        assert client_prod.get("/queue/seen-today").status_code == 401


# ---------------------------------------------------------------------------
# T-14: nurse JWT → GET /queue is allowed
# ---------------------------------------------------------------------------

def test_t14_nurse_can_view_queue(client_prod, monkeypatch):
    from app.services import queue_service
    monkeypatch.setattr(queue_service, "get_active_queue", AsyncMock(return_value=[]))
    r = client_prod.get("/queue/", headers=_bearer("nurse"))
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# T-15: nurse JWT → POST override is forbidden (charge_nurse/admin only)
# ---------------------------------------------------------------------------

def test_t15_nurse_cannot_override(client_prod):
    r = client_prod.post("/queue/test-id/override", headers=_bearer("nurse"))
    assert r.status_code == 403
    assert r.json()["detail"] == "Insufficient role"


# ---------------------------------------------------------------------------
# T-16: charge_nurse JWT → POST override is allowed (stub → 200 null body)
# ---------------------------------------------------------------------------

def test_t16_charge_nurse_can_override(client_prod, monkeypatch):
    from app.services import queue_service
    monkeypatch.setattr(queue_service, "override_urgency", AsyncMock(return_value=_dummy_patient()))
    r = client_prod.post(
        "/queue/test-id/override",
        headers=_bearer("charge_nurse"),
        json={"level": "HIGH"},
    )
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# T-17: POST /triage never requires auth, regardless of AUTH_ENABLED
# ---------------------------------------------------------------------------

_DUMMY_RECORD = {
    "id": "rec-001",
    "patient_ref": "P-001",
    "intake": {
        "chief_complaint": "severe chest pain",
        "pain_scale": 9,
        "conditions": [],
    },
    "triage": {
        "urgency": "CRITICAL",
        "confidence": 95,
        "reasoning": "Chest pain with high pain score.",
        "recommended_actions": ["ECG immediately"],
        "escalation_flag": True,
        "source": "rule-based",
    },
    "final_level": "CRITICAL",
    "confirmed": False,
    "submitted_at": "2026-04-29T00:00:00",
}

_INTAKE_BODY = {"chief_complaint": "severe chest pain", "pain_scale": 9}


class TestT17TriageAlwaysOpen:
    def test_open_in_dev_mode(self, client_dev):
        with patch(
            "app.routers.triage.classify_patient",
            new=AsyncMock(return_value=_DUMMY_RECORD),
        ):
            r = client_dev.post("/triage/", json=_INTAKE_BODY)
        assert r.status_code == 200

    def test_open_in_prod_mode(self, client_prod):
        with patch(
            "app.routers.triage.classify_patient",
            new=AsyncMock(return_value=_DUMMY_RECORD),
        ):
            r = client_prod.post("/triage/", json=_INTAKE_BODY)
        assert r.status_code == 200
