import { Bell, CalendarDays, Menu, Plus } from 'lucide-react';
import { Button } from '../ui/Button';
import { SearchInput } from '../ui/SearchInput';

interface PatientHeaderProps {
  onStartIntake: () => void;
}

export function PatientHeader({ onStartIntake }: PatientHeaderProps) {
  return (
    <header className="mb-9 flex flex-wrap items-center justify-between gap-3 lg:flex-nowrap lg:gap-5">
      <div className="flex w-full items-center gap-3 lg:hidden">
        <button className="grid size-11 place-items-center rounded-full bg-brand-700 text-white" type="button" aria-label="Open navigation">
          <Menu size={22} />
        </button>
        <div className="h-12 flex-1 rounded-full bg-white shadow-sm" aria-label="Medical AI Triage logo placeholder" />
      </div>
      <SearchInput />
      <div className="flex flex-1 items-center justify-end gap-3 lg:flex-none lg:gap-3">
        <Button className="hidden min-h-10 px-5 sm:inline-flex" onClick={onStartIntake} type="button">
          <Plus size={18} />
          New Health Activity
        </Button>
        <div className="hidden min-h-14 items-center gap-4 rounded-xl border border-clinic-border bg-white px-5 shadow-sm md:flex">
          <span className="grid size-10 place-items-center rounded-full bg-slate-100 text-ink-500">
            <CalendarDays size={22} />
          </span>
          <div>
            <p className="text-xs font-medium text-ink-500">Date</p>
            <p className="text-base font-bold text-ink-700">24th October, 2023</p>
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
