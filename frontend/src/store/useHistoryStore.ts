import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { API_BASE } from '@/lib/api'

interface Job {
  id: string
  filename: string
  transcription: string
  createdAt: string
}

interface SavedDocument {
  id: string   // Actualizado a string para consistencia con UUIDs del backend
  title: string
  excerpt: string
  tone_name: string
  created_at: string
}

interface HistoryState {
  jobs: Job[]
  savedDocs: SavedDocument[]
  /** Loading independiente para audio jobs */
  isLoadingJobs: boolean
  /** Loading independiente para documentos guardados */
  isLoadingDocs: boolean
  /** Compatibilidad: true si cualquiera de los dos está cargando */
  isLoading: boolean
  addJob: (job: Job) => void
  fetchHistory: () => Promise<void>
  fetchSavedDocs: () => Promise<void>
  clearHistory: () => void
}

export const useHistoryStore = create<HistoryState>()(
  persist(
    (set) => ({
          jobs: [],
      savedDocs: [],
      isLoadingJobs: false,
      isLoadingDocs: false,
      isLoading: false,
      addJob: (job) => set((state) => ({ jobs: [job, ...state.jobs] })),
      fetchHistory: async () => {
        set({ isLoadingJobs: true, isLoading: true });
        try {
          const res = await fetch(`${API_BASE}/audio/jobs`);
          if (res.ok) {
            const data = await res.json();
            set({ jobs: Array.isArray(data) ? data : [] });
          }
        } catch (e) {
          if (process.env.NODE_ENV === 'development') {
            console.warn("[useHistoryStore] Backend no disponible. Historial vacío.");
          }
        } finally {
          set((state) => ({
            isLoadingJobs: false,
            isLoading: state.isLoadingDocs, // isLoading global solo false cuando ambos terminan
          }));
        }
      },
      fetchSavedDocs: async () => {
        set({ isLoadingDocs: true, isLoading: true });
        try {
          const res = await fetch(`${API_BASE}/docs/list`);
          if (res.ok) {
            const data = await res.json();
            set({ savedDocs: Array.isArray(data) ? data : [] });
          }
        } catch (e) {
          if (process.env.NODE_ENV === 'development') {
            console.warn("[useHistoryStore] Backend no disponible. Documentos vacíos.");
          }
        } finally {
          set((state) => ({
            isLoadingDocs: false,
            isLoading: state.isLoadingJobs, // isLoading global solo false cuando ambos terminan
          }));
        }
      },
      clearHistory: () => set({ jobs: [], savedDocs: [] }),
    }),
    {
      name: 'gema-history-storage',
    }
  )
)
