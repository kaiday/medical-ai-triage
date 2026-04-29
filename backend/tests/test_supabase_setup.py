"""
Tests for feature/supabase-setup:
  - T-07: _write_audit_log wired to classification_log insert
  - T-05: save_patient persists PatientRecord to patients table
  - T-06: POST /triage calls save_patient; DB failure does not block response
"""

import asyncio
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import PatientIntake, PatientRecord, TriageResult, UrgencyLevel
from app.services import classifier as clf_mod
from app.services import queue_service as qs_mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_triage_result(**kw) -> TriageResult:
    defaults = dict(
        urgency=UrgencyLevel.HIGH,
        confidence=80,
        reasoning="test reasoning",
        recommended_actions=["call doctor"],
        escalation_flag=False,
        source="rule-based",
    )
    return TriageResult(**(defaults | kw))


def _make_record(**kw) -> PatientRecord:
    intake = PatientIntake(
        chief_complaint="severe headache",
        pain_scale=8,
        age=45,
        duration="2 hours",
        conditions=["hypertension"],
    )
    defaults = dict(
        id=str(uuid.uuid4()),
        patient_ref="P-001",
        intake=intake,
        triage=_make_triage_result(),
        final_level=UrgencyLevel.HIGH,
        submitted_at="2026-04-29T10:00:00Z",
    )
    return PatientRecord(**(defaults | kw))


# ---------------------------------------------------------------------------
# T-07: _write_audit_log
# ---------------------------------------------------------------------------

class TestWriteAuditLog:
    def test_fires_insert_when_configured(self):
        """_write_audit_log creates an async task that inserts into classification_log."""
        captured = []

        async def mock_insert(table, row):
            captured.append({"table": table, "row": row})
            return row

        result = _make_triage_result()
        patient_id = str(uuid.uuid4())
        payload = {"symptom_text": "headache", "pain_scale": 7}

        async def run():
            with patch.object(clf_mod, "insert", side_effect=mock_insert), \
                 patch.object(clf_mod, "is_configured", return_value=True):
                clf_mod._write_audit_log(patient_id, payload, result, 150)
                await asyncio.sleep(0.05)

        asyncio.run(run())

        assert len(captured) == 1
        row = captured[0]["row"]
        assert captured[0]["table"] == "classification_log"
        assert row["patient_id"] == patient_id
        assert row["latency_ms"] == 150
        assert row["model"] == "rule-based"
        assert "input_hash" in row
        assert len(row["input_hash"]) == 64  # sha256 hex

    def test_skips_when_not_configured(self):
        """_write_audit_log is a no-op when Supabase is not configured."""
        captured = []

        async def mock_insert(table, row):
            captured.append(row)

        async def run():
            with patch.object(clf_mod, "insert", side_effect=mock_insert), \
                 patch.object(clf_mod, "is_configured", return_value=False):
                clf_mod._write_audit_log("pid", {}, _make_triage_result(), 10)
                await asyncio.sleep(0.05)

        asyncio.run(run())
        assert captured == []

    def test_insert_exception_is_swallowed(self):
        """Audit insert failure must never propagate."""
        async def boom(table, row):
            raise RuntimeError("db exploded")

        async def run():
            with patch.object(clf_mod, "insert", side_effect=boom), \
                 patch.object(clf_mod, "is_configured", return_value=True):
                clf_mod._write_audit_log("pid", {}, _make_triage_result(), 99)
                await asyncio.sleep(0.05)

        asyncio.run(run())  # must not raise

    def test_raw_response_includes_reasoning(self):
        """raw_response dict includes urgency, confidence, and reasoning."""
        captured = []

        async def mock_insert(table, row):
            captured.append(row)

        result = _make_triage_result(urgency=UrgencyLevel.CRITICAL, confidence=95, reasoning="chest pain")

        async def run():
            with patch.object(clf_mod, "insert", side_effect=mock_insert), \
                 patch.object(clf_mod, "is_configured", return_value=True):
                clf_mod._write_audit_log("pid", {}, result, 50)
                await asyncio.sleep(0.05)

        asyncio.run(run())
        raw = captured[0]["raw_response"]
        assert raw["urgency"] == "CRITICAL"
        assert raw["confidence"] == 95
        assert raw["reasoning"] == "chest pain"


# ---------------------------------------------------------------------------
# T-05: save_patient
# ---------------------------------------------------------------------------

class TestSavePatient:
    def test_inserts_correct_fields(self):
        """save_patient calls insert with all required patient fields."""
        captured = []

        async def mock_insert(table, row):
            captured.append({"table": table, "row": row})
            return row

        record = _make_record()

        async def run():
            with patch.object(qs_mod, "insert", side_effect=mock_insert), \
                 patch.object(qs_mod, "is_configured", return_value=True):
                await qs_mod.save_patient(record)

        asyncio.run(run())

        assert len(captured) == 1
        row = captured[0]["row"]
        assert captured[0]["table"] == "patients"
        assert row["id"] == record.id
        assert row["patient_ref"] == record.patient_ref
        assert row["age"] == 45
        assert row["chief_complaint"] == "severe headache"
        assert row["pain_scale"] == 8
        assert row["ai_level"] == "HIGH"
        assert row["final_level"] == "HIGH"
        assert row["status"] == "waiting"

    def test_skips_when_not_configured(self):
        """save_patient does nothing when Supabase is not configured."""
        captured = []

        async def mock_insert(table, row):
            captured.append(row)

        async def run():
            with patch.object(qs_mod, "insert", side_effect=mock_insert), \
                 patch.object(qs_mod, "is_configured", return_value=False):
                await qs_mod.save_patient(_make_record())

        asyncio.run(run())
        assert captured == []

    def test_conditions_and_actions_lists(self):
        """Array fields are passed through correctly."""
        captured = []

        async def mock_insert(table, row):
            captured.append(row)
            return row

        record = _make_record()

        async def run():
            with patch.object(qs_mod, "insert", side_effect=mock_insert), \
                 patch.object(qs_mod, "is_configured", return_value=True):
                await qs_mod.save_patient(record)

        asyncio.run(run())
        assert captured[0]["conditions"] == ["hypertension"]
        assert captured[0]["ai_actions"] == ["call doctor"]


# ---------------------------------------------------------------------------
# T-06: POST /triage calls save_patient; DB failure does not block response
# ---------------------------------------------------------------------------

class TestTriageRoute:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_triage_calls_save_patient(self, client):
        """POST /triage persists the classified record via save_patient."""
        mock_record = _make_record()

        with patch("app.routers.triage.classify_patient", new_callable=AsyncMock, return_value=mock_record), \
             patch("app.routers.triage.save_patient", new_callable=AsyncMock) as mock_save:
            resp = client.post("/triage/", json={
                "chief_complaint": "severe headache",
                "pain_scale": 8,
                "age": 45,
            })
        assert resp.status_code == 200
        mock_save.assert_awaited_once_with(mock_record)

    def test_triage_returns_200_when_save_fails(self, client):
        """POST /triage returns 200 even if save_patient raises an exception."""
        mock_record = _make_record()

        async def boom(record):
            raise RuntimeError("Supabase unreachable")

        with patch("app.routers.triage.classify_patient", new_callable=AsyncMock, return_value=mock_record), \
             patch("app.routers.triage.save_patient", side_effect=boom):
            resp = client.post("/triage/", json={
                "chief_complaint": "severe headache",
                "pain_scale": 8,
                "age": 45,
            })
        assert resp.status_code == 200
        assert resp.json()["id"] == mock_record.id
