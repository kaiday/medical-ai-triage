import { useState } from 'react';
import { CheckCircle2, ChevronDown, Eye, ShieldAlert, X } from 'lucide-react';
import { api } from '../../lib/api';
import type { Patient, UrgencyLevel } from '../../lib/types';
import { Button } from '../ui/Button';
import { StatusChip } from '../ui/StatusChip';
import { UrgencyBadge } from '../ui/UrgencyBadge';

const OVERRIDE_LEVELS: UrgencyLevel[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

interface ReviewPanelProps {
  patient: Patient;
  onUpdated: (updated: Patient) => void;
  onClose: () => void;
}

export function ReviewPanel({ patient, onUpdated, onClose }: ReviewPanelProps) {
  const [busy, setBusy] = useState<'confirm' | 'seen' | 'override' | null>(null);
  const [showOverride, setShowOverride] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isBusy = busy !== null;

  async function handleConfirm() {
    setBusy('confirm');
    setError(null);
    try {
      onUpdated(await api.confirmPatient(patient.id));
    } catch {
      setError('Failed to confirm patient.');
    } finally {
      setBusy(null);
    }
  }

  async function handleSeen() {
    setBusy('seen');
    setError(null);
    try {
      onUpdated(await api.markSeen(patient.id));
    } catch {
      setError('Failed to mark as seen.');
    } finally {
      setBusy(null);
    }
  }

  async function handleOverride(level: UrgencyLevel) {
    setBusy('override');
    setShowOverride(false);
    setError(null);
    try {
      onUpdated(await api.overrideUrgency(patient.id, level));
    } catch {
      setError('Failed to override urgency.');
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-5 rounded-2xl border border-clinic-border bg-white p-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="mb-1 text-xs font-bold uppercase text-ink-500">Patient review</p>
          <h2 className="text-lg font-bold text-ink-900">{patient.patientRef}</h2>
        </div>
        <button className="text-ink-400 transition hover:text-ink-700" onClick={onClose}>
          <X size={20} />
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        <UrgencyBadge level={patient.finalLevel} />
        {patient.triage.urgency !== patient.finalLevel && (
          <StatusChip tone="orange">AI: {patient.triage.urgency}</StatusChip>
        )}
        {patient.confirmed && <StatusChip tone="mint">Confirmed</StatusChip>}
      </div>

      <div className="space-y-3 rounded-xl border border-clinic-border bg-clinic-canvas p-4 text-sm">
        <div>
          <p className="text-xs font-bold uppercase text-ink-500">Chief complaint</p>
          <p className="mt-1 font-medium text-ink-900">{patient.intake.chiefComplaint}</p>
        </div>
        <div className="flex gap-6">
          <div>
            <p className="text-xs font-bold uppercase text-ink-500">Pain</p>
            <p className="mt-1 font-bold text-ink-900">{patient.intake.painScale}/10</p>
          </div>
          {patient.intake.age != null && (
            <div>
              <p className="text-xs font-bold uppercase text-ink-500">Age</p>
              <p className="mt-1 font-bold text-ink-900">{patient.intake.age}</p>
            </div>
          )}
          {patient.intake.duration && (
            <div>
              <p className="text-xs font-bold uppercase text-ink-500">Duration</p>
              <p className="mt-1 font-bold text-ink-900">{patient.intake.duration}</p>
            </div>
          )}
        </div>
        {patient.intake.conditions.length > 0 && (
          <div>
            <p className="text-xs font-bold uppercase text-ink-500">Conditions</p>
            <p className="mt-1 text-ink-900">{patient.intake.conditions.join(', ')}</p>
          </div>
        )}
      </div>

      <div className="space-y-2 rounded-xl border border-brand-100 bg-brand-50 p-4 text-sm">
        <div className="flex items-center justify-between">
          <p className="text-xs font-bold uppercase text-brand-700">AI assessment</p>
          <StatusChip tone="neutral">
            {patient.triage.source} · {patient.triage.confidence}%
          </StatusChip>
        </div>
        <p className="leading-relaxed text-ink-700">{patient.triage.reasoning}</p>
        <ul className="mt-1 space-y-1">
          {patient.triage.recommendedActions.map(action => (
            <li key={action} className="flex items-start gap-2 text-ink-600">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-700" />
              {action}
            </li>
          ))}
        </ul>
      </div>

      {error && (
        <p className="rounded-lg bg-coral-50 px-4 py-2 text-sm font-semibold text-coral-600">{error}</p>
      )}

      <div className="flex flex-wrap gap-2 border-t border-clinic-border pt-4">
        {!patient.confirmed && (
          <Button variant="teal" disabled={isBusy} onClick={handleConfirm}>
            <CheckCircle2 size={16} />
            {busy === 'confirm' ? 'Confirming…' : 'Confirm'}
          </Button>
        )}
        <Button variant="secondary" disabled={isBusy} onClick={handleSeen}>
          <Eye size={16} />
          {busy === 'seen' ? 'Marking…' : 'Mark seen'}
        </Button>
        <div className="relative">
          <Button variant="ghost" disabled={isBusy} onClick={() => setShowOverride(v => !v)}>
            <ShieldAlert size={16} />
            Override
            <ChevronDown size={14} />
          </Button>
          {showOverride && (
            <div className="absolute bottom-full left-0 z-10 mb-1 min-w-[140px] rounded-xl border border-clinic-border bg-white py-1 shadow-card">
              {OVERRIDE_LEVELS.map(level => (
                <button
                  key={level}
                  className="w-full px-4 py-2 text-left text-sm font-semibold text-ink-700 transition hover:bg-clinic-canvas"
                  onClick={() => handleOverride(level)}
                >
                  {level}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
