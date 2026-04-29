"""
Phase 10 classifier tests — T-13 through T-18.

Covers:
  T-13  FastAPI app imports and starts without errors
  T-14  CRITICAL path — chest pain + heart condition → CRITICAL within 8s
  T-15  LOW path — mild cold → LOW or MEDIUM
  T-16  Fallback — OPENAI_API_KEY=dummy → source: "rule-based"
  T-17  UNCLASSIFIED — rule-based raises → urgency: UNCLASSIFIED, escalation_flag: True
  T-18  Response time — classify_patient completes within 8 seconds
"""

import asyncio
from datetime import datetime
import time
from unittest.mock import patch, AsyncMock

import pytest

from app.models.schemas import PatientIntake, UrgencyLevel
from app.services.classifier import (
    _build_payload,
    _rule_based_classify,
    _unclassified_result,
    _validate_response,
    classify_patient,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _intake(complaint: str, pain: int = 5, age: int = 40, conditions=None) -> PatientIntake:
    return PatientIntake(
        chief_complaint=complaint,
        pain_scale=pain,
        age=age,
        conditions=conditions or [],
    )


# ---------------------------------------------------------------------------
# T-13: app imports cleanly and router is reachable
# ---------------------------------------------------------------------------

def test_t13_app_starts():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    # health-check via docs endpoint — proves uvicorn would serve it
    r = client.get("/docs")
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# T-14: CRITICAL path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_t14_critical_chest_pain():
    intake = _intake("chest pain radiating to arm", pain=9, age=62, conditions=["Heart condition"])
    record = await classify_patient(intake)
    assert record.triage.urgency == UrgencyLevel.CRITICAL
    assert record.triage.source == "rule-based"
    assert record.patient_ref.startswith("Patient #")
    assert record.id  # UUID present
    assert datetime.fromisoformat(record.submitted_at)


@pytest.mark.asyncio
async def test_t14_critical_keywords():
    for complaint in [
        "patient is unconscious and unresponsive",
        "severe bleeding that won't stop",
        "anaphylaxis after bee sting",
        "suspected stroke slurred speech",
    ]:
        record = await classify_patient(_intake(complaint, pain=8))
        assert record.triage.urgency == UrgencyLevel.CRITICAL, f"Expected CRITICAL for: {complaint!r}"


# ---------------------------------------------------------------------------
# T-15: LOW / MEDIUM path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_t15_low_mild_cold():
    record = await classify_patient(_intake("mild cold and runny nose", pain=2, age=24))
    assert record.triage.urgency in (UrgencyLevel.LOW, UrgencyLevel.MEDIUM)
    assert record.triage.source == "rule-based"


@pytest.mark.asyncio
async def test_t15_low_is_default_for_no_keyword_match():
    record = await classify_patient(_intake("feeling a bit tired today", pain=1))
    assert record.triage.urgency == UrgencyLevel.LOW


# ---------------------------------------------------------------------------
# T-16: rule-based fallback activates when OPENAI_API_KEY is dummy/absent
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_t16_dummy_key_triggers_rule_based():
    # Default .env has OPENAI_API_KEY=dummy → _openai_with_retry raises immediately
    record = await classify_patient(_intake("high fever and difficulty breathing", pain=7))
    assert record.triage.source == "rule-based"


@pytest.mark.asyncio
async def test_t16_openai_timeout_triggers_rule_based():
    with patch(
        "app.services.classifier._call_openai",
        new=AsyncMock(side_effect=TimeoutError("simulated timeout")),
    ):
        with patch("app.services.classifier.asyncio.sleep", new=AsyncMock()):
            with patch.object(
                __import__("app.core.config", fromlist=["settings"]).settings,
                "OPENAI_API_KEY",
                "real-looking-key",
            ):
                record = await classify_patient(_intake("fractured wrist", pain=6))
    assert record.triage.source == "rule-based"


# ---------------------------------------------------------------------------
# T-17: UNCLASSIFIED when rule-based also raises
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_t17_unclassified_when_rule_based_fails():
    with patch(
        "app.services.classifier._openai_with_retry",
        new=AsyncMock(side_effect=RuntimeError("OpenAI down")),
    ):
        with patch(
            "app.services.classifier._rule_based_classify",
            side_effect=RuntimeError("rule-based also broken"),
        ):
            record = await classify_patient(_intake("some complaint here", pain=5))

    assert record.triage.urgency == UrgencyLevel.UNCLASSIFIED
    assert record.triage.escalation_flag is True
    assert record.triage.source == "unclassified"
    assert record.triage.confidence == 0


# ---------------------------------------------------------------------------
# T-18: response time under 8 seconds (rule-based is instant)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_t18_response_within_8_seconds():
    start = time.monotonic()
    await classify_patient(_intake("chest pain and shortness of breath", pain=8))
    elapsed = time.monotonic() - start
    assert elapsed < 8.0, f"classify_patient took {elapsed:.2f}s — exceeds 8s limit"


# ---------------------------------------------------------------------------
# Unit tests for supporting functions
# ---------------------------------------------------------------------------

def test_build_payload_strips_exact_age():
    payload = _build_payload(_intake("some complaint", age=62))
    assert "age" not in payload
    assert payload["age_range"] == "60s"
    assert payload["symptom_text"] == "some complaint"


def test_build_payload_none_age():
    intake = PatientIntake(chief_complaint="some complaint", pain_scale=5)
    payload = _build_payload(intake)
    assert payload["age_range"] == "unknown"


def test_validate_response_rejects_bad_urgency():
    with pytest.raises(ValueError):
        _validate_response({"urgency": "SEVERE", "confidence": 90, "recommended_actions": ["act"]})


def test_validate_response_rejects_confidence_out_of_range():
    with pytest.raises(ValueError):
        _validate_response({"urgency": "HIGH", "confidence": 150, "recommended_actions": ["act"]})


def test_validate_response_rejects_empty_actions():
    with pytest.raises(ValueError):
        _validate_response({"urgency": "LOW", "confidence": 50, "recommended_actions": []})


def test_rule_based_pain_bump_low_to_medium():
    record = _rule_based_classify(_intake("mild discomfort", pain=9))
    assert record.urgency == UrgencyLevel.MEDIUM


def test_rule_based_pain_bump_medium_to_high():
    record = _rule_based_classify(_intake("vomiting and nausea", pain=9))
    assert record.urgency == UrgencyLevel.HIGH


def test_unclassified_result_shape():
    result = _unclassified_result()
    assert result.urgency == UrgencyLevel.UNCLASSIFIED
    assert result.escalation_flag is True
    assert result.confidence == 0
    assert result.source == "unclassified"
