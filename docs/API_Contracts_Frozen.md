# Medical AI Triage API Contracts (Frozen for MVP)

This document defines the authoritative request/response contract for backend/frontend integration of MVP scope (`FR-01` to `FR-03`).

## Version and Rules

- Version: `v1` (current MVP)
- Transport: JSON over HTTPS
- Enum values are case-sensitive and must match exactly.
- Backend canonical field style: `snake_case`
- Frontend canonical field style: `camelCase`
- A mapping layer is required at the frontend boundary.

## Shared Enums

### UrgencyLevel

Allowed values:
- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `LOW`
- `UNCLASSIFIED`

### TriageSource

Allowed values:
- `openai`
- `rule-based`
- `unclassified`

## Canonical Backend Types (snake_case)

### `PatientIntake`

```json
{
  "chief_complaint": "string (5-500 chars)",
  "duration": "string|null",
  "pain_scale": "integer 1..10",
  "age": "integer 0..120|null",
  "conditions": ["string"]
}
```

### `TriageResult`

```json
{
  "urgency": "CRITICAL|HIGH|MEDIUM|LOW|UNCLASSIFIED",
  "confidence": "integer 0..100",
  "reasoning": "string",
  "recommended_actions": ["string"],
  "escalation_flag": "boolean",
  "source": "openai|rule-based|unclassified"
}
```

### `PatientRecord`

```json
{
  "id": "string",
  "patient_ref": "string",
  "intake": { "PatientIntake": "object" },
  "triage": { "TriageResult": "object" },
  "final_level": "CRITICAL|HIGH|MEDIUM|LOW|UNCLASSIFIED",
  "confirmed": "boolean",
  "submitted_at": "ISO-8601 datetime string"
}
```

## Frontend Mapping Contract (camelCase)

Frontend internal shape maps backend keys as follows:

| Backend key | Frontend key |
|---|---|
| `chief_complaint` | `chiefComplaint` |
| `pain_scale` | `painScale` |
| `recommended_actions` | `recommendedActions` |
| `escalation_flag` | `escalationFlag` |
| `patient_ref` | `patientRef` |
| `final_level` | `finalLevel` |
| `submitted_at` | `submittedAt` |

All other keys keep semantic parity and only naming transformation applies.

## Endpoint Contracts

### `POST /triage/`

- Purpose: Submit intake and return queued classified record.
- Auth: anonymous allowed (patient flow).
- Request body: `PatientIntake` (snake_case).
- Response `200`: `PatientRecord`.
- Errors:
  - `422` for schema validation failure (e.g., complaint too short, pain out of range).
  - `500` for unexpected server failure.

### `GET /queue/`

- Purpose: Return active queue ordered by urgency then submission time.
- Auth: nurse/staff required once auth guard is active.
- Request body: none.
- Response `200`: `PatientRecord[]`.
- Errors:
  - `401` when unauthenticated (post-auth implementation).
  - `403` when role denied (post-auth implementation).

### `PATCH /queue/{patient_id}/status`

- Purpose: Confirm AI priority for a patient.
- Auth: nurse/staff required.
- Request body: none.
- Response `200`: updated `PatientRecord`.
- Errors:
  - `404` if patient not found.
  - `401/403` for auth failures.

### `POST /queue/{patient_id}/override`

- Purpose: Override urgency level.
- Auth: charge nurse/admin required.
- Request body:

```json
{
  "level": "CRITICAL|HIGH|MEDIUM|LOW|UNCLASSIFIED"
}
```

- Response `200`: updated `PatientRecord`.
- Errors:
  - `404` if patient not found.
  - `422` if `level` invalid.
  - `403` when role lacks permission.

### `POST /queue/{patient_id}/seen`

- Purpose: Mark patient seen and remove from active queue.
- Auth: nurse/staff required.
- Request body: none.
- Response `200`: updated `PatientRecord`.
- Errors:
  - `404` if patient not found.
  - `401/403` for auth failures.

### `GET /queue/seen-today`

- Purpose: Return patients marked seen in current day window.
- Auth: nurse/staff required.
- Request body: none.
- Response `200`: `PatientRecord[]`.

## Non-Functional Contract Constraints

- Classifier must enforce:
  - JSON-only output format.
  - No diagnosis/no medication recommendations.
  - Fallback to safe queue state (`UNCLASSIFIED`) if AI path fails.
- Classification response target:
  - `<= 8s` normal-path target.
  - Timeout/failure must not drop patient records.

## Frontend Integration Rules (Must Follow)

1. Never call endpoints with camelCase JSON payloads; convert to snake_case first.
2. Never trust `fetch(...).json()` without status checks; treat non-2xx as errors.
3. Normalize backend responses to frontend types in one adapter layer.
4. Keep UI logic keyed off frozen enums only; no free-form urgency strings.

## Change Control

Any contract change must:
1. Update this file.
2. Update backend Pydantic schemas.
3. Update frontend type definitions and adapters.
4. Include migration notes if persistence shape changes.
