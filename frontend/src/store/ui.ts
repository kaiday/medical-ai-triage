// Zustand store — client-only UI state (no server data here, use React Query for that)
import { create } from 'zustand';

interface UIStore {
  selectedPatientId: string | null;
  setSelectedPatient: (id: string | null) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  selectedPatientId: null,
  setSelectedPatient: (id) => set({ selectedPatientId: id }),
}));
