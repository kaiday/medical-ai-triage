import type { UrgencyLevel } from '../../lib/types';

const BADGE: Record<UrgencyLevel, string> = {
  CRITICAL:     'bg-coral-500 text-white',
  HIGH:         'bg-amber-500 text-white',
  MEDIUM:       'bg-clinic-orange text-ink-700',
  LOW:          'bg-clinic-green text-brand-700',
  UNCLASSIFIED: 'bg-slate-100 text-ink-500',
};

export function UrgencyBadge({ level }: { level: UrgencyLevel }) {
  return (
    <span className={`inline-flex items-center rounded-md px-2.5 py-1 text-xs font-bold ${BADGE[level]}`}>
      {level}
    </span>
  );
}
