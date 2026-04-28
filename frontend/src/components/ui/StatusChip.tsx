import type { ReactNode } from 'react';

type StatusTone = 'mint' | 'green' | 'coral' | 'orange' | 'neutral';

const toneClasses: Record<StatusTone, string> = {
  mint: 'bg-clinic-mint text-brand-800',
  green: 'bg-clinic-green text-brand-700',
  coral: 'bg-coral-50 text-coral-600',
  orange: 'bg-clinic-orange text-amber-800',
  neutral: 'bg-slate-100 text-ink-500',
};

interface StatusChipProps {
  children: ReactNode;
  tone?: StatusTone;
}

export function StatusChip({ children, tone = 'neutral' }: StatusChipProps) {
  return (
    <span className={`inline-flex items-center rounded-md px-2.5 py-1 text-xs font-semibold ${toneClasses[tone]}`}>
      {children}
    </span>
  );
}
