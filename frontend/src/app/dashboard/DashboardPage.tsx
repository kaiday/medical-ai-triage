import { useState } from 'react';
import type { Patient } from '../../lib/types';
import { useUIStore } from '../../store/ui';
import { EscalationBanner } from '../../components/dashboard/EscalationBanner';
import { QueueList } from '../../components/dashboard/QueueList';
import { ReviewPanel } from '../../components/dashboard/ReviewPanel';

export function DashboardPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const { selectedPatientId, setSelectedPatient } = useUIStore();

  const selectedPatient = patients.find(p => p.id === selectedPatientId) ?? null;
  const criticalCount  = patients.filter(p => p.finalLevel === 'CRITICAL').length;
  const confirmedCount = patients.filter(p => p.confirmed).length;

  function handleUpdated(updated: Patient) {
    setPatients(prev => {
      if (updated.status === 'seen') {
        return prev.filter(p => p.id !== updated.id);
      }

      return prev.map(p => (p.id === updated.id ? updated : p));
    });

    if (updated.status === 'seen') {
      setSelectedPatient(null);
    }
  }

  return (
    <div className="min-h-screen bg-clinic-canvas p-6">
      <div className="mx-auto max-w-6xl space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-ink-900">Triage Queue</h1>
            <p className="mt-0.5 text-sm text-ink-500">Active patients requiring nurse review</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-xl border border-clinic-border bg-white p-4">
            <p className="text-xs font-bold uppercase text-ink-500">Waiting</p>
            <p className="mt-1 text-3xl font-bold text-ink-900">{patients.length}</p>
          </div>
          <div className="rounded-xl border border-coral-50 bg-coral-50 p-4">
            <p className="text-xs font-bold uppercase text-coral-600">Critical</p>
            <p className="mt-1 text-3xl font-bold text-coral-600">{criticalCount}</p>
          </div>
          <div className="rounded-xl border border-brand-100 bg-brand-50 p-4">
            <p className="text-xs font-bold uppercase text-brand-700">Confirmed</p>
            <p className="mt-1 text-3xl font-bold text-brand-700">{confirmedCount}</p>
          </div>
        </div>

        <EscalationBanner patients={patients} />

        <div className={`grid gap-5 ${selectedPatient ? 'lg:grid-cols-[1fr_400px]' : ''}`}>
          <QueueList patients={patients} onQueueChange={setPatients} />
          {selectedPatient && (
            <ReviewPanel
              patient={selectedPatient}
              onUpdated={handleUpdated}
              onClose={() => setSelectedPatient(null)}
            />
          )}
        </div>
      </div>
    </div>
  );
}
