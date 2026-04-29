import { useCallback, useEffect, useState } from 'react';
import { Loader2, RefreshCw, Users } from 'lucide-react';
import { api } from '../../lib/api';
import type { Patient } from '../../lib/types';
import { useUIStore } from '../../store/ui';
import { PatientCard } from './PatientCard';

interface QueueListProps {
  patients: Patient[];
  onQueueChange?: (patients: Patient[]) => void;
}

export function QueueList({ patients, onQueueChange }: QueueListProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { selectedPatientId, setSelectedPatient } = useUIStore();

  const fetchQueue = useCallback(async () => {
    try {
      const data = await api.getQueue();
      onQueueChange?.(data);
      setError(null);
    } catch {
      setError('Could not load queue.');
    } finally {
      setLoading(false);
    }
  }, [onQueueChange]);

  useEffect(() => {
    fetchQueue();
    const interval = setInterval(fetchQueue, 30_000);
    return () => clearInterval(interval);
  }, [fetchQueue]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-ink-500">
        <Loader2 className="mr-2 animate-spin" size={20} />
        Loading queue…
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl bg-coral-50 p-4 text-center text-sm text-coral-600">
        {error}{' '}
        <button className="font-semibold underline" onClick={fetchQueue}>Retry</button>
      </div>
    );
  }

  if (patients.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center text-ink-500">
        <Users className="mb-3 text-clinic-border" size={36} />
        <p className="font-semibold">No active patients</p>
        <p className="text-sm">New intakes will appear here automatically.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm font-semibold text-ink-500">
          {patients.length} patient{patients.length !== 1 ? 's' : ''} waiting
        </p>
        <button
          className="flex items-center gap-1 text-xs font-semibold text-brand-700 hover:underline"
          onClick={fetchQueue}
        >
          <RefreshCw size={13} />
          Refresh
        </button>
      </div>
      <div className="space-y-2">
        {patients.map(p => (
          <PatientCard
            key={p.id}
            patient={p}
            isSelected={selectedPatientId === p.id}
            onSelect={() => setSelectedPatient(selectedPatientId === p.id ? null : p.id)}
          />
        ))}
      </div>
    </div>
  );
}
