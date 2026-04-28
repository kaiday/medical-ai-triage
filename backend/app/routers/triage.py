from fastapi import APIRouter
from app.models.schemas import PatientIntake, PatientRecord
from app.services.classifier import classify_patient

router = APIRouter(prefix="/triage", tags=["triage"])

@router.post("/", response_model=PatientRecord)
async def submit_intake(intake: PatientIntake):
    """Receive patient intake, trigger AI classification, persist to queue."""
    return await classify_patient(intake)
