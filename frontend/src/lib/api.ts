// API client — wraps all backend REST calls
// Used with React Query (useQuery / useMutation) throughout the app
import type { PatientIntake, Patient } from './types';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function parseJson<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = body && typeof body === 'object' && 'detail' in body ? String(body.detail) : 'Request failed';
    throw new Error(detail);
  }

  return body as T;
}

export const api = {
  submitIntake: (intake: PatientIntake): Promise<Patient> =>
    fetch(`${BASE_URL}/triage`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(intake) }).then((r) => parseJson<Patient>(r)),
  getQueue: (): Promise<Patient[]> =>
    fetch(`${BASE_URL}/queue`).then((r) => parseJson<Patient[]>(r)),
  confirmPatient: (id: string) =>
    fetch(`${BASE_URL}/queue/${id}/status`, { method: 'PATCH' }).then((r) => parseJson<Patient>(r)),
  overrideUrgency: (id: string, level: string) =>
    fetch(`${BASE_URL}/queue/${id}/override`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ level }) }).then((r) => parseJson<Patient>(r)),
  markSeen: (id: string) =>
    fetch(`${BASE_URL}/queue/${id}/seen`, { method: 'POST' }).then((r) => parseJson<Patient>(r)),
};
