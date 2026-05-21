import { create } from 'zustand'

interface DictationState {
  isRecording: boolean
  isProcessingAudio: boolean // Bandera global: bloquea grabación y edición durante transcripción async
  unprocessedPhrase: string
  interimText: string
  documentText: string
  setRecording: (recording: boolean) => void
  setProcessingAudio: (processing: boolean) => void // Activa/desactiva el bloqueo del lienzo
  addUnprocessedPhrase: (text: string) => void
  clearUnprocessedPhrase: () => void
  setInterimText: (text: string) => void
  setDocumentText: (text: string) => void
  clearDictation: () => void
  resetStore: () => void
}

export const useDictationStore = create<DictationState>((set) => ({
  isRecording: false,
  isProcessingAudio: false,
  unprocessedPhrase: '',
  interimText: '',
  documentText: '',
  setRecording: (isRecording) => set({ isRecording }),
  setProcessingAudio: (isProcessingAudio) => set({ isProcessingAudio }),
  addUnprocessedPhrase: (text) => set((state) => ({ unprocessedPhrase: state.unprocessedPhrase + text })),
  clearUnprocessedPhrase: () => set({ unprocessedPhrase: '' }),
  setInterimText: (interimText) => set({ interimText }),
  setDocumentText: (documentText) => set({ documentText }),
  clearDictation: () => set({ unprocessedPhrase: '', interimText: '', documentText: '' }),
  resetStore: () => set({ isRecording: false, isProcessingAudio: false, unprocessedPhrase: '', interimText: '', documentText: '' }),
}))
