from fastapi import APIRouter, Depends
from app.core.auth import require_role, StaffUser

router = APIRouter(prefix="/queue", tags=["queue"])

_ALL_STAFF = ("nurse", "charge_nurse", "admin")
_CHARGE_ONLY = ("charge_nurse", "admin")


@router.get("/")
async def get_queue(user: StaffUser = Depends(require_role(*_ALL_STAFF))):
    """Return active queue sorted CRITICAL → HIGH → MEDIUM → LOW, then by submitted_at."""
    pass


@router.patch("/{patient_id}/status")
async def confirm_patient(patient_id: str, user: StaffUser = Depends(require_role(*_ALL_STAFF))):
    """Nurse confirms AI classification."""
    pass


@router.post("/{patient_id}/override")
async def override_urgency(patient_id: str, user: StaffUser = Depends(require_role(*_CHARGE_ONLY))):
    """Charge nurse overrides urgency level."""
    pass


@router.post("/{patient_id}/seen")
async def mark_seen(patient_id: str, user: StaffUser = Depends(require_role(*_ALL_STAFF))):
    """Remove patient from active queue, move to seen-today log."""
    pass


@router.get("/seen-today")
async def get_seen_today(user: StaffUser = Depends(require_role(*_ALL_STAFF))):
    """Return patients marked seen in the current calendar day."""
    pass
