import { create } from 'zustand'

interface DictationState {
  isRecording: boolean
  isWhisperMode: boolean
  isProcessingAudio: boolean // Bandera global: bloquea grabación y edición durante transcripción async
  unprocessedPhrase: string
  interimText: string
  documentText: string
  setRecording: (recording: boolean) => void
  setWhisperMode: (whisper: boolean) => void
  setProcessingAudio: (processing: boolean) => void // Activa/desactiva el bloqueo del lienzo
  lastDictatedChunk: string
  setLastDictatedChunk: (text: string) => void
  addUnprocessedPhrase: (text: string) => void
  clearUnprocessedPhrase: () => void
  setInterimText: (text: string) => void
  setDocumentText: (text: string) => void
  clearDictation: () => void
  clearCanvas: () => void
  resetStore: () => void
  contextBuffer: string[]
  addToContext: (text: string) => void
}

export const useDictationStore = create<DictationState>((set) => ({
  isRecording: false,
  isWhisperMode: false,
  isProcessingAudio: false,
  unprocessedPhrase: '',
  interimText: '',
  documentText: typeof window !== 'undefined' ? localStorage.getItem('gema_checkpoint') || '' : '',
  setRecording: (isRecording) => set({ isRecording }),
  setWhisperMode: (isWhisperMode) => set({ isWhisperMode }),
  setProcessingAudio: (isProcessingAudio) => set({ isProcessingAudio }),
  lastDictatedChunk: '',
  setLastDictatedChunk: (text) => set({ lastDictatedChunk: text }),
  addUnprocessedPhrase: (text) => set((state) => ({ unprocessedPhrase: state.unprocessedPhrase + text })),
  clearUnprocessedPhrase: () => set({ unprocessedPhrase: '' }),
  setInterimText: (interimText) => set({ interimText }),
  setDocumentText: (documentText) => {
    set({ documentText });
    if (typeof window !== 'undefined') localStorage.setItem('gema_checkpoint', documentText);
  },
  clearCanvas: () => {
    set({ documentText: '' });
    if (typeof window !== 'undefined') localStorage.removeItem('gema_checkpoint');
  },
  clearDictation: () => set({ unprocessedPhrase: '', interimText: '', documentText: '', contextBuffer: [] }),
  resetStore: () => set({ isRecording: false, isWhisperMode: false, isProcessingAudio: false, unprocessedPhrase: '', interimText: '', documentText: '', contextBuffer: [] }),
  contextBuffer: [],
  addToContext: (text) => set((state) => ({
    // Mantenemos solo los últimos 3 fragmentos para no saturar el prompt
    contextBuffer: [...state.contextBuffer, text].slice(-3)
  })),
}))
