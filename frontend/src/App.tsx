import { useState } from 'react';
import { DashboardPage } from './app/dashboard/DashboardPage';
import { IntakePage } from './app/intake/IntakePage';

type AppView = 'patient' | 'nurse';

export function App() {
  const [view, setView] = useState<AppView>('patient');

  return (
    <>
      <nav className="flex gap-2 border-b border-clinic-border bg-white px-6 py-3">
        <button
          className={`rounded-full px-4 py-1.5 text-sm font-semibold transition ${
            view === 'patient' ? 'bg-brand-700 text-white' : 'text-ink-500 hover:text-ink-900'
          }`}
          onClick={() => setView('patient')}
        >
          Patient Portal
        </button>
        <button
          className={`rounded-full px-4 py-1.5 text-sm font-semibold transition ${
            view === 'nurse' ? 'bg-brand-700 text-white' : 'text-ink-500 hover:text-ink-900'
          }`}
          onClick={() => setView('nurse')}
        >
          Nurse Dashboard
        </button>
      </nav>
      {view === 'patient' ? <IntakePage /> : <DashboardPage />}
    </>
  );
}
