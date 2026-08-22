import { create } from 'zustand';
import { apiRequest } from '../lib/api';

// Definición estricta de los estados por los que pasa el pipeline local
type RefinementStage = 'idle' | 'lexical_cleaning' | 'semantic_processing' | 'completed';

export interface AIModification {
  id: string;
  timestamp: string;
  type: string;
  original: string;
  replaced: string;
  description: string;
}

interface InferenceState {
  liveBuffer: string;
  currentStage: RefinementStage;
  modifications: AIModification[];
  addModification: (mod: Omit<AIModification, 'id' | 'timestamp'>) => void;
  removeModification: (id: string) => void;
  pendingReplacement: AIModification | null;
  setPendingReplacement: (mod: AIModification | null) => void;
  /** Actualiza el buffer de texto en vivo (interim results del dictado) */
  setLiveBuffer: (text: string) => void;
  /** Actualiza la etapa del pipeline de refinamiento */
  setStage: (stage: RefinementStage) => void;
  clearLog: () => void;
  isProcessing: boolean;
  applyLiteraryStyle: (rawText: string, tone: string) => Promise<void>;
}

export const useInferenceStore = create<InferenceState>((set, get) => ({
  liveBuffer: '',
  currentStage: 'idle',
  modifications: [],
  isProcessing: false,

  addModification: (mod) => set((state) => ({
    modifications: [
      {
        ...mod,
        id: crypto.randomUUID(),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      },
      ...state.modifications
    ]
  })),

  removeModification: (id) => set((state) => ({
    modifications: state.modifications.filter(m => m.id !== id)
  })),

  pendingReplacement: null,
  setPendingReplacement: (mod) => set({ pendingReplacement: mod }),

  setLiveBuffer: (text) => set({ liveBuffer: text }),
  setStage: (stage) => set({ currentStage: stage }),

  clearLog: () => set({ modifications: [], liveBuffer: '', currentStage: 'idle', pendingReplacement: null }),

  applyLiteraryStyle: async (rawText: string, tone: string) => {
    set({ isProcessing: true });
    
    try {
      // Leer outputFormat en el momento de ejecución (evita stale closure)
      const { outputFormat } = (await import('./useToneStore')).useToneStore.getState();

      const response = await apiRequest('/style/process-text', {
        method: 'POST',
        body: JSON.stringify({
          raw_text: rawText,
          tone_name: tone,
          format_type: outputFormat,
        })
      });
      
      const data = await response.json();
      
      // Mapeamos los cambios (suggestions) detectados por el backend (Ollama + FakeAIRulesEngine)
      const newSuggestions: AIModification[] = (data.suggestions || []).map((change: Record<string, string>) => ({
        id: crypto.randomUUID(),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        type: change.rule_id || 'estilo',
        original: change.original,
        replaced: change.replacement,
        description: change.explanation
      }));

      set({
        modifications: newSuggestions,
        // Guardamos el texto refinado para que el componente lo use directamente
        liveBuffer: data.corrected_text || rawText,
        isProcessing: false,
      });
    } catch (error) {
      console.error("[useInferenceStore] Error applying literary style:", error);
      set({ isProcessing: false });
    }
  }
}));
