from datetime import datetime, timezone
from typing import Any, Dict, List

from app.core.supabase import SupabaseConfigurationError, get_supabase_client, insert, is_configured
from app.models.schemas import (
    PatientIntake,
    PatientRecord,
    PatientStatus,
    TriageResult,
    UrgencyLevel,
)


class QueueServiceError(RuntimeError):
    """Base error for queue service failures."""


class PatientNotFoundError(QueueServiceError):
    """Raised when a patient row does not exist."""


class QueueDatabaseError(QueueServiceError):
    """Raised when Supabase rejects or fails a queue operation."""


class QueueConfigurationError(QueueServiceError):
    """Raised when queue infrastructure is not configured."""


class QueueDataError(QueueServiceError):
    """Raised when stored queue data cannot be mapped to API models."""


PATIENT_SELECT = (
    "id,patient_ref,age,chief_complaint,pain_scale,duration,conditions,"
    "submitted_at,ai_level,ai_confidence,ai_reasoning,ai_actions,ai_source,"
    "final_level,confirmed_by,confirmed_at,seen_at,status"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_urgency(value: Any) -> UrgencyLevel:
    if not value:
        return UrgencyLevel.UNCLASSIFIED
    return UrgencyLevel(str(value))


def _coerce_status(value: Any) -> PatientStatus:
    if not value:
        return PatientStatus.WAITING
    return PatientStatus(str(value))


def _row_to_patient_record(row: Dict[str, Any]) -> PatientRecord:
    try:
        ai_level = _coerce_urgency(row.get("ai_level"))
        final_level = _coerce_urgency(row.get("final_level") or ai_level)
        actions = row.get("ai_actions") or []

        intake = PatientIntake(
            chief_complaint=row.get("chief_complaint") or "",
            duration=row.get("duration"),
            pain_scale=row.get("pain_scale") or 1,
            age=row.get("age"),
            conditions=row.get("conditions") or [],
        )
        triage = TriageResult(
            urgency=ai_level,
            confidence=row.get("ai_confidence") or 0,
            reasoning=row.get("ai_reasoning") or "",
            recommended_actions=actions,
            escalation_flag=ai_level in (UrgencyLevel.CRITICAL, UrgencyLevel.UNCLASSIFIED),
            source=row.get("ai_source") or "unclassified",
        )

        return PatientRecord(
            id=str(row["id"]),
            patient_ref=row.get("patient_ref") or "",
            intake=intake,
            triage=triage,
            final_level=final_level,
            confirmed=bool(row.get("confirmed_at")),
            submitted_at=str(row.get("submitted_at") or ""),
            status=_coerce_status(row.get("status")),
            confirmed_by=row.get("confirmed_by"),
            confirmed_at=row.get("confirmed_at"),
            seen_at=row.get("seen_at"),
            ai_level=ai_level,
            ai_confidence=row.get("ai_confidence"),
            ai_reasoning=row.get("ai_reasoning"),
            ai_actions=actions,
            ai_source=row.get("ai_source"),
        )
    except Exception as exc:
        raise QueueDataError("Queue row could not be mapped to a patient record.") from exc


def _extract_single_patient(rows: Any, patient_id: str) -> PatientRecord:
    if not rows:
        raise PatientNotFoundError(f"Patient {patient_id} was not found.")
    return _row_to_patient_record(rows[0])


async def _request(method: str, path: str, **kwargs: Any) -> Any:
    try:
        client = get_supabase_client()
        return await client.request(method, path, **kwargs)
    except SupabaseConfigurationError as exc:
        raise QueueConfigurationError("Queue database is not configured.") from exc
    except Exception as exc:
        raise QueueDatabaseError("Queue database operation failed.") from exc


async def get_active_queue() -> List[PatientRecord]:
    rows = await _request("POST", "/rpc/get_active_queue", json={})
    return [_row_to_patient_record(row) for row in rows or []]


async def confirm_patient(patient_id: str, nurse_id: str) -> PatientRecord:
    rows = await _request(
        "PATCH",
        "/patients",
        params={
            "id": f"eq.{patient_id}",
            "select": PATIENT_SELECT,
        },
        json={
            "status": PatientStatus.CONFIRMED.value,
            "confirmed_by": nurse_id,
            "confirmed_at": _utc_now(),
        },
        headers={"Prefer": "return=representation"},
    )
    return _extract_single_patient(rows, patient_id)


async def override_urgency(
    patient_id: str,
    new_level: UrgencyLevel,
    nurse_id: str,
) -> PatientRecord:
    # The current schema has no override audit fields. Keep nurse_id in the
    # service contract so a later override_log migration can use it directly.
    _ = nurse_id
    rows = await _request(
        "PATCH",
        "/patients",
        params={
            "id": f"eq.{patient_id}",
            "select": PATIENT_SELECT,
        },
        json={"final_level": new_level.value},
        headers={"Prefer": "return=representation"},
    )
    return _extract_single_patient(rows, patient_id)


async def mark_seen(patient_id: str) -> PatientRecord:
    rows = await _request(
        "PATCH",
        "/patients",
        params={
            "id": f"eq.{patient_id}",
            "select": PATIENT_SELECT,
        },
        json={
            "status": PatientStatus.SEEN.value,
            "seen_at": _utc_now(),
        },
        headers={"Prefer": "return=representation"},
    )
    return _extract_single_patient(rows, patient_id)


async def save_patient(record: PatientRecord) -> None:
    if not is_configured():
        return
    row = {
        "id":              record.id,
        "patient_ref":     record.patient_ref,
        "age":             record.intake.age,
        "chief_complaint": record.intake.chief_complaint,
        "pain_scale":      record.intake.pain_scale,
        "duration":        record.intake.duration,
        "conditions":      record.intake.conditions,
        "submitted_at":    record.submitted_at,
        "ai_level":        record.triage.urgency.value,
        "ai_confidence":   record.triage.confidence,
        "ai_reasoning":    record.triage.reasoning,
        "ai_actions":      record.triage.recommended_actions,
        "ai_source":       record.triage.source,
        "final_level":     record.final_level.value,
        "status":          "waiting",
    }
    await insert("patients", row)


async def get_seen_today() -> List[PatientRecord]:
    today_utc = datetime.now(timezone.utc).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    rows = await _request(
        "GET",
        "/patients",
        params={
            "select": PATIENT_SELECT,
            "status": f"eq.{PatientStatus.SEEN.value}",
            "seen_at": f"gte.{today_utc.isoformat()}",
            "order": "seen_at.desc",
        },
    )
    return [_row_to_patient_record(row) for row in rows or []]
