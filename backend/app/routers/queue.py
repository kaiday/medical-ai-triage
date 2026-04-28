from fastapi import APIRouter

router = APIRouter(prefix="/queue", tags=["queue"])

@router.get("/")
async def get_queue():
    """Return active queue sorted CRITICAL → HIGH → MEDIUM → LOW, then by submitted_at."""
    pass

@router.patch("/{patient_id}/status")
async def confirm_patient(patient_id: str):
    """Nurse confirms AI classification."""
    pass

@router.post("/{patient_id}/override")
async def override_urgency(patient_id: str):
    """Charge nurse overrides urgency level."""
    pass

@router.post("/{patient_id}/seen")
async def mark_seen(patient_id: str):
    """Remove patient from active queue, move to seen-today log."""
    pass

@router.get("/seen-today")
async def get_seen_today():
    """Return patients marked seen in the current calendar day."""
    pass
