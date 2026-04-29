export type UrgencyLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'UNCLASSIFIED';

export interface PatientIntake {
  chiefComplaint: string;
  duration?: string;
  painScale: number;
  age?: number;
  conditions: string[];
}

export interface TriageResult {
  urgency: UrgencyLevel;
  confidence: number;
  reasoning: string;
  recommendedActions: string[];
  escalationFlag: boolean;
  source: 'openai' | 'rule-based' | 'unclassified';
}

export interface Patient {
  id: string;
  patientRef: string;
  intake: PatientIntake;
  triage: TriageResult;
  finalLevel: UrgencyLevel;
  confirmed: boolean;
  submittedAt: string;
  status?: 'waiting' | 'confirmed' | 'seen';
  confirmedBy?: string | null;
  confirmedAt?: string | null;
  seenAt?: string | null;
}
