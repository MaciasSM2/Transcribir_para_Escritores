// frontend/src/infrastructure/audio/ISpeechTranscriber.ts

export interface TranscriptionCallbacks {
  onDeltaResult: (finalChunk: string) => void;
  onInterimResult: (interimText: string) => void;
  onError: (errorMessage: string) => void;
  onDisconnect: () => void;
}

export interface ISpeechTranscriber {
  initialize(callbacks: TranscriptionCallbacks): void;
  start(): void;
  stop(): void;
  isActive(): boolean;
}
