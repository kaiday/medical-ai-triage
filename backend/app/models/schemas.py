from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

class UrgencyLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNCLASSIFIED = "UNCLASSIFIED"

class PatientStatus(str, Enum):
    WAITING = "waiting"
    CONFIRMED = "confirmed"
    SEEN = "seen"

class StaffRole(str, Enum):
    NURSE = "nurse"
    CHARGE_NURSE = "charge_nurse"
    ADMIN = "admin"

class PatientIntake(BaseModel):
    chief_complaint: str = Field(min_length=5, max_length=500)
    duration: Optional[str] = None
    pain_scale: int = Field(ge=1, le=10)
    age: Optional[int] = Field(default=None, ge=0, le=120)
    conditions: List[str] = Field(default_factory=list)

class TriageResult(BaseModel):
    urgency: UrgencyLevel
    confidence: int = Field(ge=0, le=100)
    reasoning: str
    recommended_actions: List[str] = Field(default_factory=list)
    escalation_flag: bool
    source: str  # 'openai' | 'rule-based' | 'unclassified'

class OverrideRequest(BaseModel):
    level: UrgencyLevel

class StaffUser(BaseModel):
    id: str
    email: Optional[str] = None
    role: StaffRole = StaffRole.NURSE

class PatientRecord(BaseModel):
    id: str
    patient_ref: str
    intake: PatientIntake
    triage: TriageResult
    final_level: UrgencyLevel
    confirmed: bool = False
    submitted_at: str
    status: PatientStatus = PatientStatus.WAITING
    confirmed_by: Optional[str] = None
    confirmed_at: Optional[str] = None
    seen_at: Optional[str] = None

    # Flattened Supabase columns. These mirror `triage` for queue/database rows.
    ai_level: Optional[UrgencyLevel] = None
    ai_confidence: Optional[int] = Field(default=None, ge=0, le=100)
    ai_reasoning: Optional[str] = None
    ai_actions: List[str] = Field(default_factory=list)
    ai_source: Optional[str] = None
