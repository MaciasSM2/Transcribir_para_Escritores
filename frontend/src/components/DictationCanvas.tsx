'use client';
import React, { useState, useEffect, useRef } from 'react';
import { useDictationStore } from '@/store/useDictationStore';
import { useUIStore } from '@/store/useUIStore';
import { useCleanDictation } from '@/hooks/useCleanDictation';
import { useToneStore } from '@/store/useToneStore';
import { API_BASE } from '@/lib/api';
import { RefinementStepper } from './RefinementStepper';
import { Mic, MicOff, Square, Wind, Sparkles } from 'lucide-react';

export default function DictationCanvas() {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const { setCurrentView } = useUIStore();
  const { toneName } = useToneStore();
  const [refinementStage, setRefinementStage] = useState<'idle' | 'lexical' | 'semantic' | 'completed'>('idle');
  const { 
    unprocessedPhrase, 
    clearUnprocessedPhrase, 
    interimText, 
    isRecording,
    isProcessingAudio, // Bloqueo global durante transcripción de audio en segundo plano
    documentText,
    setDocumentText,
    isWhisperMode,
    setWhisperMode
  } = useDictationStore();
  const { startRecording, stopRecording, pauseForTyping } = useCleanDictation();

  // Sincronización del Cursor con texto dictado
  useEffect(() => {
    if (unprocessedPhrase && textareaRef.current) {
      const el = textareaRef.current;
      const start = el.selectionStart;
      const end = el.selectionEnd;

      // 💡 C4 FIX: Usamos el estado más fresco del store directamente
      // para evitar que el closure de React use un documentText viejo.
      const currentText = useDictationStore.getState().documentText;
      
      const newText = 
        currentText.substring(0, start) + 
        unprocessedPhrase + 
        currentText.substring(end);

      setDocumentText(newText);
      clearUnprocessedPhrase();

      setTimeout(() => {
        el.selectionStart = start + unprocessedPhrase.length;
        el.selectionEnd = start + unprocessedPhrase.length;
        el.focus();
      }, 10);
    }
    // Eliminamos documentText de las dependencias para que solo se dispare
    // cuando llega una frase nueva, no cuando el usuario teclea.
  }, [unprocessedPhrase, setDocumentText, clearUnprocessedPhrase]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Excluir teclas de navegación para no pausar si el usuario solo se mueve
    if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
      pauseForTyping();
    }
  };

  // 1. Estado local para respuesta inmediata
  const [localText, setLocalText] = useState(documentText);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  // 2. Sincronizar localText cuando el store cambie externamente (ej. por dictado finalizado)
  useEffect(() => {
    setLocalText(documentText);
  }, [documentText]);

  // 3. Función de cambio con Debounce para el Store Global
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setLocalText(val); // Actualización visual inmediata

    if (debounceRef.current) clearTimeout(debounceRef.current);
    
    // Sincronizamos con el Store Global solo tras 800ms de inactividad
    debounceRef.current = setTimeout(() => {
      setDocumentText(val);
    }, 800);
  };

  const handleRefine = async () => {
    if (!localText) return;
    setRefinementStage('lexical');
    
    try {
      const response = await fetch(`${API_BASE}/audio/process-large-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: localText, tone_name: toneName })
      });
      
      setRefinementStage('semantic');
      const data = await response.json();
      
      setRefinementStage('completed');
      setDocumentText(data.refined_text || data.text || localText);
      
      setTimeout(() => {
        setRefinementStage('idle');
      }, 3000);
    } catch (e) {
      console.error(e);
      setRefinementStage('idle');
    }
  };

  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  const isRefineDisabled = !mounted || isProcessingAudio || localText.length === 0 || refinementStage !== 'idle';

  return (
    <div className="relative flex flex-col h-full bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm p-4">

      {/* OVERLAY DE PROCESAMIENTO (se superpone al lienzo completo durante transcripción) */}
      {isProcessingAudio && (
        <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-slate-900/60 backdrop-blur-md rounded-xl transition-all">
          <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-2xl flex flex-col items-center gap-4 border border-blue-500/30">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <div className="text-center">
              <h3 className="text-lg font-bold text-slate-800 dark:text-white">Transcribiendo Audio</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Por favor, espera a que termine el proceso…</p>
            </div>
          </div>
        </div>
      )}

      {/* Controles Flotantes */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold flex items-center gap-2 text-slate-800 dark:text-slate-200">
          <div className={`w-3 h-3 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-slate-400'}`} />
          Mesa de Dictado
        </h2>
        <div className="flex gap-2">
          {isRecording ? (
            <button 
              onClick={stopRecording}
              disabled={isProcessingAudio}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors font-medium ${
                isProcessingAudio
                  ? 'bg-slate-200 dark:bg-slate-700 text-slate-400 cursor-not-allowed'
                  : 'bg-red-100 text-red-600 hover:bg-red-200'
              }`}
            >
              <MicOff size={18} /> Pausar
            </button>
          ) : (
            <button 
              onClick={startRecording}
              disabled={isProcessingAudio}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors font-medium ${
                isProcessingAudio
                  ? 'bg-slate-200 dark:bg-slate-700 text-slate-400 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              <Mic size={18} /> Iniciar Dictado
            </button>
          )}
          <button
            onClick={() => setWhisperMode(!isWhisperMode)}
            disabled={isProcessingAudio}
            className={`p-2 ml-2 rounded-full border transition-all ${
              isWhisperMode 
                ? 'bg-purple-100 border-purple-500 text-purple-600 shadow-[0_0_10px_rgba(168,85,247,0.4)]' 
                : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-400'
            }`}
            title="Modo Susurro: Mejora voces bajas y filtra ruido de calle"
          >
            <Wind size={20} className={isWhisperMode ? 'animate-pulse' : ''} />
          </button>
          <button 
            onClick={handleRefine}
            disabled={isRefineDisabled}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors font-medium ml-2 ${
              isRefineDisabled
                ? 'bg-slate-400 text-slate-200 cursor-not-allowed'
                : 'bg-blue-100 text-blue-700 hover:bg-blue-200 border border-blue-300'
            }`}
          >
            <Sparkles size={18} /> Refinar
          </button>
          <button 
            onClick={() => setCurrentView('review')}
            disabled={isProcessingAudio}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors font-medium ml-2 ${
              isProcessingAudio
                ? 'bg-slate-400 text-slate-200 cursor-not-allowed'
                : 'bg-slate-800 text-white hover:bg-slate-900'
            }`}
          >
            <Square size={18} /> Finalizar y Revisar
          </button>
        </div>
      </div>

      {refinementStage !== 'idle' && (
        <div className="mb-4">
          <RefinementStepper stage={refinementStage} />
        </div>
      )}

      {/* Canvas */}
      <div className="relative flex-grow h-full min-h-[400px]">
        <textarea
          ref={textareaRef}
          value={localText}
          onChange={handleTextChange}
          onKeyDown={handleKeyDown}
          disabled={isProcessingAudio}
          className={`w-full h-full p-4 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-800 dark:text-slate-200 text-lg leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none font-serif transition-opacity ${
            isProcessingAudio ? 'opacity-40 cursor-not-allowed' : ''
          }`}
          placeholder="Comienza a dictar o escribir aquí tu novela..."
        />
        
        {/* 💡 OVERLAY DE PREVISUALIZACIÓN (INTERIM UI) */}
        {isRecording && interimText && (
          <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-20 transition-all animate-in fade-in slide-in-from-bottom-4 pointer-events-none">
            <div className="px-6 py-3 bg-blue-600/90 backdrop-blur-md text-white rounded-full shadow-2xl border border-blue-400/30 flex items-center gap-3">
              <div className="flex gap-1">
                <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce"></span>
              </div>
              <p className="text-sm font-medium italic opacity-90 truncate max-w-md">
                "{interimText}..."
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
