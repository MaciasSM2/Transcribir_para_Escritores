import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { API_BASE } from '@/lib/api'

interface ToneState {
  toneName: string
  referenceText: string
  outputFormat: string
  setTone: (name: string, reference: string) => Promise<void>
  setOutputFormat: (format: string) => void
  fetchTones: () => Promise<void>
}

export const useToneStore = create<ToneState>()(
  persist(
    (set, get) => ({
      toneName: 'Narrativa de Ciencia Ficción y Fantasía Épica',
      referenceText: 'Era el mejor de los tiempos, era el peor de los tiempos, la edad de la sabiduría, y también de la locura...',
      outputFormat: 'novel',
      setTone: async (toneName, referenceText) => {
        set({ toneName, referenceText });
        try {
          await fetch(`${API_BASE}/tones/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tone_name: toneName, reference_text: referenceText })
          });
        } catch (e) {
          console.error("Failed to save tone to backend", e);
        }
      },
      setOutputFormat: (format) => set({ outputFormat: format }),
      fetchTones: async () => {
        try {
          const res = await fetch(`${API_BASE}/tones/`);
          if (res.ok) {
            const data = await res.json();
            const currentTone = get().toneName;
            if (data[currentTone]) {
              set({ referenceText: data[currentTone] });
            } else {
              // Fallback: buscar un tono que coincida por substring (case-insensitive)
              const match = Object.keys(data).find(
                (key) => key.toLowerCase().includes(currentTone.toLowerCase())
                  || currentTone.toLowerCase().includes(key.toLowerCase())
              );
              if (match) {
                set({ referenceText: data[match] });
              }
            }
          }
        } catch (e) {
          if (process.env.NODE_ENV === 'development') {
            console.warn("[useToneStore] Backend no disponible. Usando valores por defecto.");
          }
        }
      }
    }),
    {
      name: 'gema-tone-storage',
    }
  )
)
