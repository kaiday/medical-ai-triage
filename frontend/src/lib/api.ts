import type { PatientIntake, Patient } from './types';
import { supabase } from './supabase';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function parseJson<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = body && typeof body === 'object' && 'detail' in body ? String(body.detail) : 'Request failed';
    throw new Error(detail);
  }

  return body as T;
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session?.access_token) return {};
  return { Authorization: `Bearer ${session.access_token}` };
}

export const api = {
  submitIntake: (intake: PatientIntake): Promise<Patient> =>
    fetch(`${BASE_URL}/triage`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(intake) }).then((r) => parseJson<Patient>(r)),

  getQueue: async (): Promise<Patient[]> =>
    fetch(`${BASE_URL}/queue`, { headers: await getAuthHeaders() }).then((r) => parseJson<Patient[]>(r)),

  confirmPatient: async (id: string): Promise<Patient> =>
    fetch(`${BASE_URL}/queue/${id}/status`, { method: 'PATCH', headers: await getAuthHeaders() }).then((r) => parseJson<Patient>(r)),

  overrideUrgency: async (id: string, level: string): Promise<Patient> =>
    fetch(`${BASE_URL}/queue/${id}/override`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...await getAuthHeaders() }, body: JSON.stringify({ level }) }).then((r) => parseJson<Patient>(r)),

  markSeen: async (id: string): Promise<Patient> =>
    fetch(`${BASE_URL}/queue/${id}/seen`, { method: 'POST', headers: await getAuthHeaders() }).then((r) => parseJson<Patient>(r)),
};
