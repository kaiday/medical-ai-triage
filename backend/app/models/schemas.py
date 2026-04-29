from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class _Base(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # internal code can still use snake_case names
    )


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


class PatientIntake(_Base):
    chief_complaint: str = Field(min_length=5, max_length=500)
    duration: Optional[str] = None
    pain_scale: int = Field(ge=1, le=10)
    age: Optional[int] = Field(default=None, ge=0, le=120)
    conditions: List[str] = Field(default_factory=list)


class TriageResult(_Base):
    urgency: UrgencyLevel
    confidence: int = Field(ge=0, le=100)
    reasoning: str
    recommended_actions: List[str] = Field(default_factory=list)
    escalation_flag: bool
    source: str  # 'openai' | 'rule-based' | 'unclassified'


class OverrideRequest(_Base):
    level: UrgencyLevel


class StaffUser(_Base):
    id: str
    email: Optional[str] = None
    role: StaffRole = StaffRole.NURSE


class PatientRecord(_Base):
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

    # Flattened Supabase columns mirroring triage fields
    ai_level: Optional[UrgencyLevel] = None
    ai_confidence: Optional[int] = Field(default=None, ge=0, le=100)
    ai_reasoning: Optional[str] = None
    ai_actions: List[str] = Field(default_factory=list)
    ai_source: Optional[str] = None
