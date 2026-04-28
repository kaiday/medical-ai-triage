import type { ReactNode } from 'react';
import { PatientHeader } from './PatientHeader';
import { PatientSidebar } from './PatientSidebar';

interface PatientPortalShellProps {
  children: ReactNode;
  onStartIntake: () => void;
}

export function PatientPortalShell({ children, onStartIntake }: PatientPortalShellProps) {
  return (
    <div className="min-h-screen bg-clinic-canvas text-ink-900">
      <div className="flex">
        <PatientSidebar onStartIntake={onStartIntake} />
        <main className="min-w-0 flex-1 px-5 py-6 sm:px-8 lg:px-9">
          <PatientHeader onStartIntake={onStartIntake} />
          {children}
        </main>
      </div>
    </div>
  );
}
