import { Clock } from 'lucide-react';
import type { Patient } from '../../lib/types';
import { StatusChip } from '../ui/StatusChip';
import { UrgencyBadge } from '../ui/UrgencyBadge';

function relativeTime(iso: string): string {
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

interface PatientCardProps {
  patient: Patient;
  isSelected: boolean;
  onSelect: () => void;
}

export function PatientCard({ patient, isSelected, onSelect }: PatientCardProps) {
  return (
    <button
      className={`w-full rounded-xl border p-4 text-left transition ${
        isSelected
          ? 'border-brand-700 bg-clinic-mint'
          : 'border-clinic-border bg-white hover:border-brand-500'
      }`}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <UrgencyBadge level={patient.finalLevel} />
          {patient.confirmed && <StatusChip tone="mint">Confirmed</StatusChip>}
        </div>
        <span className="flex shrink-0 items-center gap-1 text-xs text-ink-400">
          <Clock size={12} />
          {relativeTime(patient.submittedAt)}
        </span>
      </div>
      <p className="mt-2 text-sm font-bold text-ink-900">{patient.patientRef}</p>
      <p className="mt-1 line-clamp-2 text-sm text-ink-500">{patient.intake.chiefComplaint}</p>
      <div className="mt-2 flex flex-wrap gap-3 text-xs text-ink-500">
        <span>Pain: <strong className="text-ink-700">{patient.intake.painScale}/10</strong></span>
        {patient.intake.age != null && (
          <span>Age: <strong className="text-ink-700">{patient.intake.age}</strong></span>
        )}
        {patient.intake.duration && <span>{patient.intake.duration}</span>}
      </div>
    </button>
  );
}
