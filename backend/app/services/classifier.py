import asyncio
import hashlib
import json
import time
import uuid
from datetime import datetime
from typing import Optional

from openai import AsyncOpenAI, APITimeoutError, APIConnectionError, RateLimitError, AuthenticationError

from app.core.config import settings
from app.core.supabase import insert, is_configured
from app.models.schemas import PatientIntake, PatientRecord, TriageResult, UrgencyLevel

SYSTEM_PROMPT = """You are a clinical triage assistant helping nurses prioritise patients.
Classify urgency as: CRITICAL, HIGH, MEDIUM, or LOW.
Return ONLY a JSON object: { urgency, confidence, reasoning, recommended_actions, escalation_flag }.
Do NOT provide a diagnosis. Do NOT recommend medications. Nurse actions only."""

CRITICAL_KEYWORDS = [
    "chest pain", "can't breathe", "cannot breathe", "not breathing",
    "unconscious", "severe bleeding", "stroke", "heart attack", "crushing",
    "radiating arm", "anaphylaxis", "seizure", "overdose", "choking",
    "no pulse", "unresponsive", "stopped breathing",
]
HIGH_KEYWORDS = [
    "high fever", "head injury", "fracture", "broken bone", "severe pain",
    "vomiting blood", "difficulty breathing", "dislocated", "deep cut",
    "head trauma", "intense pain", "coughing blood",
]
MEDIUM_KEYWORDS = [
    "vomiting", "moderate pain", "earache", "laceration", "dizzy",
    "nausea", "swollen", "sprain", "rash with fever", "dizziness",
    "mild fever", "abdominal pain", "stomach pain",
]

FALLBACK_ACTIONS = {
    UrgencyLevel.CRITICAL: [
        "Bring patient to resuscitation area immediately",
        "Check vital signs: BP, HR, SpO2 now",
        "Alert on-call physician",
    ],
    UrgencyLevel.HIGH: [
        "Assess patient within 15 minutes",
        "Check blood pressure and pulse",
        "Prepare examination room",
    ],
    UrgencyLevel.MEDIUM: [
        "Schedule review within 30-60 minutes",
        "Monitor for symptom changes",
        "Take patient history notes",
    ],
    UrgencyLevel.LOW: [
        "Add to standard queue (within 2 hours)",
        "Advise patient to inform staff if symptoms worsen",
        "Record symptoms for physician review",
    ],
    UrgencyLevel.UNCLASSIFIED: [
        "Review patient manually — AI classification unavailable",
        "Check vital signs",
        "Assess urgency in person",
    ],
}

_patient_counter = 0


def _next_patient_ref() -> str:
    global _patient_counter
    _patient_counter += 1
    return f"Patient #{_patient_counter}"


# T-04: payload builder — strips PHI, converts age to decade range
def _build_payload(intake: PatientIntake) -> dict:
    age_range = "unknown"
    if intake.age is not None:
        decade = (intake.age // 10) * 10
        age_range = f"{decade}s"
    return {
        "symptom_text": intake.chief_complaint,
        "age_range": age_range,
        "pain_scale": intake.pain_scale,
        "conditions": intake.conditions,
        "duration": intake.duration,
    }


# T-06: validate OpenAI response shape
def _validate_response(raw: dict) -> TriageResult:
    urgency = str(raw.get("urgency", "")).upper()
    if urgency not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        raise ValueError(f"Invalid urgency value: {urgency!r}")

    confidence = int(raw.get("confidence", 0))
    if not 0 <= confidence <= 100:
        raise ValueError(f"Confidence out of range: {confidence}")

    actions = raw.get("recommended_actions", [])
    if not isinstance(actions, list) or len(actions) == 0:
        raise ValueError("recommended_actions must be a non-empty list")

    return TriageResult(
        urgency=UrgencyLevel(urgency),
        confidence=confidence,
        reasoning=raw.get("reasoning", ""),
        recommended_actions=actions[:3],
        escalation_flag=bool(raw.get("escalation_flag", urgency == "CRITICAL")),
        source="openai",
    )


# T-05: single OpenAI API call
async def _call_openai(payload: dict) -> TriageResult:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_object"},
        timeout=settings.CLASSIFY_TIMEOUT_SECONDS,
    )
    raw = json.loads(response.choices[0].message.content)
    return _validate_response(raw)


# T-07: retry with exponential backoff — 4 attempts (0s, 1s, 2s, 4s)
# AuthenticationError is permanent — break immediately, no retry
async def _openai_with_retry(payload: dict) -> TriageResult:
    if settings.OPENAI_API_KEY == "dummy":
        raise RuntimeError("No OpenAI API key configured — using fallback")

    delays = [0, 1, 2, 4]
    last_error: Optional[Exception] = None
    for delay in delays:
        if delay:
            await asyncio.sleep(delay)
        try:
            return await _call_openai(payload)
        except AuthenticationError as exc:
            raise exc  # permanent failure — skip retries
        except (APITimeoutError, APIConnectionError, RateLimitError, ValueError) as exc:
            last_error = exc
        except Exception as exc:
            last_error = exc
            break
    raise last_error or RuntimeError("All OpenAI attempts exhausted")


# T-08: rule-based keyword fallback
def _rule_based_classify(intake: PatientIntake) -> TriageResult:
    text = intake.chief_complaint.lower()

    if any(kw in text for kw in CRITICAL_KEYWORDS):
        level = UrgencyLevel.CRITICAL
    elif any(kw in text for kw in HIGH_KEYWORDS):
        level = UrgencyLevel.HIGH
    elif any(kw in text for kw in MEDIUM_KEYWORDS):
        level = UrgencyLevel.MEDIUM
    else:
        level = UrgencyLevel.LOW

    # Pain scale 9-10 bumps LOW→MEDIUM and MEDIUM→HIGH
    if intake.pain_scale >= 9:
        if level == UrgencyLevel.LOW:
            level = UrgencyLevel.MEDIUM
        elif level == UrgencyLevel.MEDIUM:
            level = UrgencyLevel.HIGH

    return TriageResult(
        urgency=level,
        confidence=40,
        reasoning=(
            f"Rule-based classification: symptom keywords indicate {level.value}. "
            f"Pain scale {intake.pain_scale}/10."
        ),
        recommended_actions=FALLBACK_ACTIONS[level],
        escalation_flag=(level == UrgencyLevel.CRITICAL),
        source="rule-based",
    )


# T-09: last-resort unclassified result
def _unclassified_result() -> TriageResult:
    return TriageResult(
        urgency=UrgencyLevel.UNCLASSIFIED,
        confidence=0,
        reasoning="Classification failed — both AI and rule-based systems unavailable. Manual nurse review required.",
        recommended_actions=FALLBACK_ACTIONS[UrgencyLevel.UNCLASSIFIED],
        escalation_flag=True,
        source="unclassified",
    )


# T-10: fire-and-forget audit log (silently skips if Supabase not configured)
def _write_audit_log(patient_id: str, payload: dict, result: TriageResult, latency_ms: int) -> None:
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
        pass  # no running event loop (sync test context) — skip silently


# T-11: main entry point — orchestrates the full fallback chain
async def classify_patient(intake: PatientIntake) -> PatientRecord:
    start = time.monotonic()
    patient_id = str(uuid.uuid4())
    payload = _build_payload(intake)

    try:
        result = await _openai_with_retry(payload)
    except Exception:
        try:
            result = _rule_based_classify(intake)
        except Exception:
            result = _unclassified_result()

    latency_ms = int((time.monotonic() - start) * 1000)
    _write_audit_log(patient_id, payload, result, latency_ms)

    return PatientRecord(
        id=patient_id,
        patient_ref=_next_patient_ref(),
        intake=intake,
        triage=result,
        final_level=result.urgency,
        confirmed=False,
        submitted_at=datetime.now().strftime("%H:%M"),
    )
