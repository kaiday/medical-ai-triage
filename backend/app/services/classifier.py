# AI classification service
#
# Fallback chain:
#   1. OpenAI gpt-4o-mini  (3 retries: 1s / 2s / 4s backoff)
#   2. Rule-based keyword matching
#   3. UNCLASSIFIED + escalation flag for nurse manual review
#
# Payload sent to OpenAI is minimised before dispatch:
#   - Sends: symptom_text, age_range (e.g. "60s"), pain_scale, conditions[]
#   - Strips: exact age, submission timestamp, patient_ref, IP address

import asyncio
import hashlib
import json

from app.core.supabase import insert, is_configured
from app.models.schemas import TriageResult

SYSTEM_PROMPT = """You are a clinical triage assistant helping nurses prioritise patients.
Classify urgency as: CRITICAL, HIGH, MEDIUM, or LOW.
Return ONLY a JSON object: { urgency, confidence, reasoning, recommended_actions, escalation_flag }.
Do NOT provide a diagnosis. Do NOT recommend medications. Nurse actions only."""


# T-07: fire-and-forget audit log write to classification_log table
def _write_audit_log(
    patient_id: str,
    payload: dict,
    result: TriageResult,
    latency_ms: int,
) -> None:
    if not is_configured():
        return

    async def _do_insert() -> None:
        try:
            await insert("classification_log", {
                "patient_id":   patient_id,
                "input_hash":   hashlib.sha256(
                                    json.dumps(payload, sort_keys=True).encode()
                                ).hexdigest(),
                "model":        result.source,
                "raw_response": {
                    "urgency":    result.urgency.value,
                    "confidence": result.confidence,
                    "reasoning":  result.reasoning,
                },
                "latency_ms":   latency_ms,
            })
        except Exception:
            pass  # audit failure must never propagate

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_do_insert())
    except RuntimeError:
        pass  # no running event loop (e.g. sync test context) — skip silently


async def classify_patient(intake):
    # Full implementation lives on feature/backend-classifier.
    # This stub is replaced when that branch merges into main.
    pass
