import { useState, useRef, useEffect } from 'react';
import { API_BASE } from '@/lib/api';
import { secureRequest } from '@/lib/api-client';
import { useDictationStore } from '@/store/useDictationStore';
import { useToneStore } from '@/store/useToneStore';
import { useHistoryStore } from '@/store/useHistoryStore';
import { useProjectStore } from '@/store/useProjectStore';

export const useAudioUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const { toneName, outputFormat } = useToneStore();
  const { isWhisperMode: whisperMode, setDocumentText, setProcessingAudio } = useDictationStore();
  const { addJob, fetchHistory } = useHistoryStore();

  const pollingCancelledRef = useRef(false);

  useEffect(() => {
    pollingCancelledRef.current = false;
    return () => {
      pollingCancelledRef.current = true;
    };
  }, []);

  const pollTranscriptionStatus = (jobId: string, filename: string) => {
    const MAX_RETRIES = 60; // 60 × 3s = 3 minutos máximo
    let retries = 0;

    const checkStatus = async () => {
      if (pollingCancelledRef.current) return;

      try {
        const res = await fetch(`${API_BASE}/audio/status/${jobId}`);
        if (!res.ok) throw new Error(`Error consultando estado: HTTP ${res.status}`);

        const data = await res.json();

        if (data.status === 'completed') {
          // Inyectar en Tiptap a través de setLastDictatedChunk para reflejarlo en el lienzo
          useDictationStore.getState().setLastDictatedChunk(data.transcription);
          
          addJob({
            id: jobId,
            filename,
            transcription: data.transcription,
            createdAt: new Date().toISOString(),
          });
          fetchHistory();
          setProcessingAudio(false);
          return;
        }

        if (data.status === 'error') {
          throw new Error(data.transcription || 'Error en el motor de transcripción.');
        }

        if (retries < MAX_RETRIES) {
          retries++;
          setTimeout(checkStatus, 3000);
        } else {
          throw new Error('Tiempo de espera agotado. El servidor tardó demasiado.');
        }
      } catch (err: unknown) {
        if (pollingCancelledRef.current) return;
        const message = err instanceof Error ? err.message : 'Error desconocido';
        console.error('Polling error:', message);
        alert(`Error en transcripción:\n${message}`);
        setProcessingAudio(false);
      }
    };

    checkStatus();
  };

  const handleAudioUpload = async (file: File) => {
    setIsUploading(true);
    setProcessingAudio(true);

    try {
      try {
        await secureRequest('/audio/upload', { method: 'HEAD' }, true);
      } catch (healthErr) {
        const msg = healthErr instanceof Error ? healthErr.message : '';
        if (msg.startsWith('SISTEMA_SATURADO')) {
          throw new Error(msg.replace('SISTEMA_SATURADO: ', ''));
        }
      }

      // 1. Crear una nueva escena con el nombre del archivo de audio para proteger las existentes
      const cleanName = file.name.replace(/\.[^/.]+$/, "");
      const title = `Grabación: ${cleanName}`;
      await useProjectStore.getState().addChapter(title);
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('whisper_mode', whisperMode ? 'true' : 'false');
      formData.append('tone_name', toneName);
      formData.append('format_type', outputFormat);

      const response = await fetch(`${API_BASE}/audio/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log(`Audio recibido. Job ID: ${data.job_id}. Iniciando sondeo...`);

      pollTranscriptionStatus(data.job_id, file.name);

    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Error desconocido';
      console.error('Error al subir audio:', message);
      alert(`Error al iniciar transcripción:\n${message}`);
      setProcessingAudio(false);
    } finally {
      setIsUploading(false);
    }
  };

  return { handleAudioUpload, isUploading };
};
