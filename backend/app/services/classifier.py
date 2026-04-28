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

SYSTEM_PROMPT = """You are a clinical triage assistant helping nurses prioritise patients.
Classify urgency as: CRITICAL, HIGH, MEDIUM, or LOW.
Return ONLY a JSON object: { urgency, confidence, reasoning, recommended_actions, escalation_flag }.
Do NOT provide a diagnosis. Do NOT recommend medications. Nurse actions only."""

async def classify_patient(intake):
    # TODO: implement OpenAI call + fallback chain
    pass
