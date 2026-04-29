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
      <div className="flex min-h-screen">
        <PatientSidebar onStartIntake={onStartIntake} />
        <main className="min-w-0 flex-1 px-4 py-5 sm:px-6 lg:px-9 lg:py-6">
          <div className="mx-auto w-full max-w-[1174px]">
            <PatientHeader onStartIntake={onStartIntake} />
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
