from fastapi import APIRouter
from app.models.schemas import PatientIntake, PatientRecord
from app.services.classifier import classify_patient
from app.services.queue_service import save_patient

router = APIRouter(prefix="/triage", tags=["triage"])


@router.post("", response_model=PatientRecord, response_model_by_alias=True)
async def submit_intake(intake: PatientIntake):
    """Receive patient intake, trigger AI classification, persist to queue."""
    record = await classify_patient(intake)
    try:
        await save_patient(record)
    except Exception:
        pass  # DB write failure must never block the patient confirmation
    return record
