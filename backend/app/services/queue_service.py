# Queue management service
# Handles Supabase Postgres reads/writes for the patient queue
# Urgency sort order: CRITICAL(4) > HIGH(3) > MEDIUM(2) > LOW(1) > UNCLASSIFIED(0)
# Within same urgency tier: sort by submitted_at ASC (earliest first)

from app.core.supabase import insert, is_configured
from app.models.schemas import PatientRecord


# T-05: persist a classified PatientRecord to Supabase patients table
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
