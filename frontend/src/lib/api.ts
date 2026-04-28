// API client — wraps all backend REST calls
// Used with React Query (useQuery / useMutation) throughout the app
import type { PatientIntake, Patient } from './types';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export const api = {
  submitIntake: (intake: PatientIntake) =>
    fetch(`${BASE_URL}/triage`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(intake) }).then(r => r.json()),
  getQueue: (): Promise<Patient[]> =>
    fetch(`${BASE_URL}/queue`).then(r => r.json()),
  confirmPatient: (id: string) =>
    fetch(`${BASE_URL}/queue/${id}/status`, { method: 'PATCH' }).then(r => r.json()),
  overrideUrgency: (id: string, level: string) =>
    fetch(`${BASE_URL}/queue/${id}/override`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ level }) }).then(r => r.json()),
  markSeen: (id: string) =>
    fetch(`${BASE_URL}/queue/${id}/seen`, { method: 'POST' }).then(r => r.json()),
};
