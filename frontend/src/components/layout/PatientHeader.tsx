import { Bell, CalendarDays, Plus } from 'lucide-react';
import { Button } from '../ui/Button';
import { SearchInput } from '../ui/SearchInput';

interface PatientHeaderProps {
  onStartIntake: () => void;
}

export function PatientHeader({ onStartIntake }: PatientHeaderProps) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-5">
      <SearchInput />
      <div className="flex items-center gap-4">
        <Button className="hidden sm:inline-flex" onClick={onStartIntake} type="button">
          <Plus size={18} />
          Start Intake
        </Button>
        <div className="hidden min-h-14 items-center gap-4 rounded-xl border border-clinic-border bg-white px-5 shadow-sm md:flex">
          <span className="grid size-10 place-items-center rounded-full bg-slate-100 text-ink-500">
            <CalendarDays size={22} />
          </span>
          <div>
            <p className="text-xs font-medium text-ink-500">Date</p>
            <p className="text-base font-bold text-ink-700">29th April, 2026</p>
          </div>
        </div>
        <button className="grid size-11 place-items-center rounded-full bg-slate-100 text-ink-700" type="button" aria-label="Notifications">
          <Bell size={20} />
        </button>
        <div className="size-11 rounded-full bg-coral-50 p-1">
          <div className="size-full rounded-full bg-coral-500" aria-label="Profile avatar" />
        </div>
      </div>
    </header>
  );
}
