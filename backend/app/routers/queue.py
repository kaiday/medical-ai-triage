from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import require_role
from app.models.schemas import OverrideRequest, PatientRecord, StaffRole, StaffUser
from app.services import queue_service
from app.services.queue_service import (
    PatientNotFoundError,
    QueueConfigurationError,
    QueueDataError,
    QueueDatabaseError,
)

router = APIRouter(prefix="/queue", tags=["queue"])

QUEUE_READER = require_role(StaffRole.NURSE, StaffRole.CHARGE_NURSE, StaffRole.ADMIN)
QUEUE_WRITER = require_role(StaffRole.NURSE, StaffRole.CHARGE_NURSE, StaffRole.ADMIN)
QUEUE_OVERRIDE = require_role(StaffRole.CHARGE_NURSE, StaffRole.ADMIN)


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, PatientNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, QueueDatabaseError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Queue database operation failed.") from exc
    if isinstance(exc, QueueConfigurationError):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Queue database is not configured.") from exc
    if isinstance(exc, QueueDataError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Queue data could not be processed.") from exc
    raise exc


@router.get("", response_model=list[PatientRecord], response_model_by_alias=True)
async def get_queue(_current_user: StaffUser = Depends(QUEUE_READER)):
    """Return active queue sorted CRITICAL → HIGH → MEDIUM → LOW, then by submitted_at."""
    try:
        return await queue_service.get_active_queue()
    except Exception as exc:
        _raise_http_error(exc)


@router.get("/seen-today", response_model=list[PatientRecord], response_model_by_alias=True)
async def get_seen_today(_current_user: StaffUser = Depends(QUEUE_READER)):
    """Return patients marked seen in the current calendar day."""
    try:
        return await queue_service.get_seen_today()
    except Exception as exc:
        _raise_http_error(exc)


@router.patch("/{patient_id}/status", response_model=PatientRecord, response_model_by_alias=True)
async def confirm_patient(
    patient_id: str,
    current_user: StaffUser = Depends(QUEUE_WRITER),
):
    """Nurse confirms AI classification."""
    try:
        return await queue_service.confirm_patient(patient_id, current_user.id)
    except Exception as exc:
        _raise_http_error(exc)


@router.post("/{patient_id}/override", response_model=PatientRecord, response_model_by_alias=True)
async def override_urgency(
    patient_id: str,
    request: OverrideRequest,
    current_user: StaffUser = Depends(QUEUE_OVERRIDE),
):
    """Charge nurse overrides urgency level."""
    try:
        return await queue_service.override_urgency(patient_id, request.level, current_user.id)
    except Exception as exc:
        _raise_http_error(exc)


@router.post("/{patient_id}/seen", response_model=PatientRecord, response_model_by_alias=True)
async def mark_seen(
    patient_id: str,
    _current_user: StaffUser = Depends(QUEUE_WRITER),
):
    """Remove patient from active queue, move to seen-today log."""
    try:
        return await queue_service.mark_seen(patient_id)
    except Exception as exc:
        _raise_http_error(exc)
