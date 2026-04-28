from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class UrgencyLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNCLASSIFIED = "UNCLASSIFIED"

class PatientIntake(BaseModel):
    chief_complaint: str = Field(min_length=5, max_length=500)
    duration: Optional[str] = None
    pain_scale: int = Field(ge=1, le=10)
    age: Optional[int] = Field(default=None, ge=0, le=120)
    conditions: List[str] = []

class TriageResult(BaseModel):
    urgency: UrgencyLevel
    confidence: int = Field(ge=0, le=100)
    reasoning: str
    recommended_actions: List[str]
    escalation_flag: bool
    source: str  # 'openai' | 'rule-based' | 'unclassified'

class PatientRecord(BaseModel):
    id: str
    patient_ref: str
    intake: PatientIntake
    triage: TriageResult
    final_level: UrgencyLevel
    confirmed: bool = False
    submitted_at: str
