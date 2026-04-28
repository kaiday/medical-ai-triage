# Medical AI Triage FR Traceability Matrix

This matrix maps the canonical requirements (`FR-01`, `FR-02`, `FR-03`) to current implementation evidence in the repository.

Status legend:
- `implemented`: Requirement is present in code.
- `partial`: Some scaffolding/contract exists, but behavior is incomplete.
- `missing`: No implementation evidence in active code.

## FR-01 Patient Symptom Intake

| Requirement | Status | Evidence | Notes |
|---|---|---|---|
| FR-01.1 Chief complaint (min 5, max 500) | implemented | `backend/app/models/schemas.py` | Enforced via `Field(min_length=5, max_length=500)` on `chief_complaint`. |
| FR-01.2 Symptom duration | partial | `backend/app/models/schemas.py` | `duration` exists in schema, but no patient UI implementation yet. |
| FR-01.3 Pain scale 1-10 | implemented | `backend/app/models/schemas.py` | Enforced with `Field(ge=1, le=10)` on `pain_scale`. |
| FR-01.4 Age capture | implemented | `backend/app/models/schemas.py` | Optional `age` with `0-120` bounds exists in backend model. |
| FR-01.5 Known conditions multi-select | partial | `backend/app/models/schemas.py`, `frontend/src/lib/types.ts` | `conditions` array exists in contracts; UI control not implemented in active code. |
| FR-01.6 Submission validation UX | missing | `frontend/src/app/intake/IntakePage.tsx` | Intake page is currently empty, so inline validation UX is not present. |
| FR-01.7 Confirmation screen (no urgency shown) | missing | `frontend/src/app/intake/IntakePage.tsx` | No confirmation state/page implemented. |
| FR-01.8 Accessibility baseline | missing | `frontend/src/app/intake/IntakePage.tsx` | No rendered intake UI yet to verify 16px/high contrast/tap targets. |
| FR-01.9 Submission timestamp captured | partial | `backend/app/models/schemas.py` | `PatientRecord.submitted_at` exists, but generator/persistence path is still unimplemented. |

## FR-02 AI Triage Classification

| Requirement | Status | Evidence | Notes |
|---|---|---|---|
| FR-02.1 Classification call on submission | partial | `backend/app/routers/triage.py`, `backend/app/services/classifier.py` | Router invokes `classify_patient`, but classifier is still TODO stub. |
| FR-02.2 Structured JSON output contract | partial | `backend/app/models/schemas.py`, `backend/app/services/classifier.py` | Result schema exists and system prompt specifies JSON-only; runtime parsing/validation not implemented. |
| FR-02.3 Four-tier urgency classification | partial | `backend/app/models/schemas.py` | Enum exists (`CRITICAL/HIGH/MEDIUM/LOW`) plus `UNCLASSIFIED`; classification engine missing. |
| FR-02.4 Reasoning summary | partial | `backend/app/models/schemas.py` | Required field exists in model; generation path missing. |
| FR-02.5 Recommended actions | partial | `backend/app/models/schemas.py` | Required field exists in model; generation path missing. |
| FR-02.6 Escalation flag for CRITICAL | partial | `backend/app/models/schemas.py` | Field exists; logic not implemented. |
| FR-02.7 Response within 8 seconds | missing | `backend/app/services/classifier.py` | Timeout/backoff and latency enforcement are only comments. |
| FR-02.8 Fallback to UNCLASSIFIED | partial | `backend/app/models/schemas.py`, `backend/app/services/classifier.py` | `UNCLASSIFIED` enum and fallback design comments exist; no executable fallback chain yet. |
| FR-02.9 Prompt safety constraints | partial | `backend/app/services/classifier.py` | Safety prompt text present; no active OpenAI call currently. |

## FR-03 Nurse Review Dashboard

| Requirement | Status | Evidence | Notes |
|---|---|---|---|
| FR-03.1 Sorted queue by urgency/time | missing | `backend/app/routers/queue.py`, `backend/app/services/queue_service.py` | Endpoints and service are placeholders (`pass`/comments). |
| FR-03.2 Color urgency badges | missing | `frontend/src/app/intake/IntakePage.tsx` | No dashboard component implementation present in active files. |
| FR-03.3 Patient card collapsed view | missing | `frontend/src/app/intake/IntakePage.tsx` | No queue card components in current snapshot. |
| FR-03.4 Expanded patient detail view | missing | `frontend/src/app/intake/IntakePage.tsx` | No dashboard detail panel implemented. |
| FR-03.5 Confirm priority action | partial | `frontend/src/lib/api.ts`, `backend/app/routers/queue.py` | API method exists client-side and route exists server-side, but route handler is placeholder. |
| FR-03.6 Override urgency action | partial | `frontend/src/lib/api.ts`, `backend/app/routers/queue.py` | API method + route shape exist; business logic missing. |
| FR-03.7 CRITICAL escalation alert | missing | `frontend/src/app/intake/IntakePage.tsx` | No clinician dashboard alert UI implemented. |
| FR-03.8 Realtime updates | partial | `frontend/src/lib/supabase.ts`, `README.md` | Supabase client exists and architecture calls for realtime, but subscription wiring not implemented in current UI code. |
| FR-03.9 Live summary counts | missing | `frontend/src/app/intake/IntakePage.tsx` | No dashboard header/count implementation present. |
| FR-03.10 Mark as seen workflow | partial | `frontend/src/lib/api.ts`, `backend/app/routers/queue.py` | API method + endpoint scaffold exist; implementation missing server-side/UI-side. |

## Cross-Cutting Requirements

| Requirement | Status | Evidence | Notes |
|---|---|---|---|
| Human-in-the-loop nurse confirmation | partial | `README.md`, `frontend/src/lib/api.ts` | Product framing and endpoint shape exist; operational confirmation flow not yet implemented. |
| Server-side API key handling | partial | `backend/app/core/config.py`, `backend/app/services/classifier.py` | Config supports server key; classifier does not yet call OpenAI. |
| JWT + RBAC enforcement | missing | `backend/app/core/auth.py`, `backend/app/routers/queue.py` | Auth module is placeholder comments only; role guards absent. |
| Persistence in Supabase Postgres | partial | `supabase/migrations/*.sql`, `backend/app/services/queue_service.py` | Schema exists; service persistence logic not yet implemented in active code. |

## Immediate Implementation Priorities

1. Implement `backend/app/services/classifier.py` end-to-end (OpenAI + validation + fallback chain).
2. Implement `backend/app/services/queue_service.py` and wire `backend/app/routers/queue.py`.
3. Implement frontend intake and dashboard pages/components against existing API/type contracts.
4. Add auth middleware/dependencies in `backend/app/core/auth.py` and apply role guards on queue mutations.
