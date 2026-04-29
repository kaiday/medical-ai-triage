import { AlertTriangle } from 'lucide-react';
import type { Patient } from '../../lib/types';

export function EscalationBanner({ patients }: { patients: Patient[] }) {
  const count = patients.filter(p => p.finalLevel === 'CRITICAL' || p.triage.escalationFlag).length;
  if (count === 0) return null;

  return (
    <div className="flex items-center gap-3 rounded-xl bg-coral-500 px-5 py-3 text-white">
      <AlertTriangle className="shrink-0" size={20} />
      <p className="text-sm font-bold">
        {count} critical {count === 1 ? 'patient requires' : 'patients require'} immediate attention
      </p>
    </div>
  );
}
