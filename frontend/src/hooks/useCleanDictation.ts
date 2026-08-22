// frontend/src/hooks/useCleanDictation.ts
import { useCallback, useRef, useState, useEffect } from 'react';
import { BrowserSpeechAdapter } from '../infrastructure/audio/BrowserSpeechAdapter';
import { useDictationStore } from '../store/useDictationStore';
import { useInferenceStore } from '../store/useInferenceStore';

export function useCleanDictation() {
  const adapterRef = useRef<BrowserSpeechAdapter | null>(null);
  const { setDocumentText, setInterimText } = useDictationStore();
  const [isRecording, setIsRecording] = useState(false);

  // Sync state cleanly if store/adapter gets out of sync
  useEffect(() => {
    return () => {
      if (adapterRef.current) {
        adapterRef.current.stop();
      }
    };
  }, []);

  const startDictation = useCallback(() => {
    if (!adapterRef.current) {
      adapterRef.current = new BrowserSpeechAdapter();
      adapterRef.current.initialize({
        onDeltaResult: (finalChunk) => {
          // Fase C: Desacoplamiento. Enviamos el chunk a la tienda.
          // El lienzo (RichCanvas) lo escuchará e insertará nativamente en Tiptap.
          useDictationStore.getState().setLastDictatedChunk(finalChunk);
        },
        onInterimResult: (interimText) => {
          // Este texto va a un componente flotante, no altera el lienzo principal
          setInterimText(interimText);
          useInferenceStore.getState().setLiveBuffer(interimText);
        },
        onError: (err) => console.error(err),
        onDisconnect: () => {
          setInterimText('');
          useInferenceStore.getState().setLiveBuffer('');
          setIsRecording(false);
        }
      });
    }
    
    adapterRef.current.start();
    setIsRecording(true);
  }, [setDocumentText, setInterimText]);

  const stopDictation = useCallback(() => {
    adapterRef.current?.stop();
    setIsRecording(false);
    setInterimText('');
  }, [setInterimText]);

  const startRecording = startDictation;
  const stopRecording = stopDictation;
  const pauseForTyping = stopDictation;

  return { startDictation, stopDictation, isRecording, startRecording, stopRecording, pauseForTyping };
}
