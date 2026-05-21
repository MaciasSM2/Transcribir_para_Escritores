'use client';
import React, { useState, useEffect, useRef } from 'react';
import { useDictationStore } from '@/store/useDictationStore';
import { useUIStore } from '@/store/useUIStore';
import { useCleanDictation } from '@/hooks/useCleanDictation';
import { Mic, MicOff, Square } from 'lucide-react';

export default function DictationCanvas() {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const { setCurrentView } = useUIStore();
  const { 
    unprocessedPhrase, 
    clearUnprocessedPhrase, 
    interimText, 
    isRecording,
    isProcessingAudio, // Bloqueo global durante transcripción de audio en segundo plano
    documentText,
    setDocumentText
  } = useDictationStore();
  const { startRecording, stopRecording, pauseForTyping } = useCleanDictation();

  // Sincronización del Cursor con texto dictado
  useEffect(() => {
    if (unprocessedPhrase && textareaRef.current) {
      const el = textareaRef.current;
      const start = el.selectionStart;
      const end = el.selectionEnd;
      
      const newText = documentText.substring(0, start) + unprocessedPhrase + documentText.substring(end);
      setDocumentText(newText);
      clearUnprocessedPhrase();
      
      // Mover el cursor después de que React actualice el DOM
      setTimeout(() => {
        el.selectionStart = start + unprocessedPhrase.length;
        el.selectionEnd = start + unprocessedPhrase.length;
        el.focus();
      }, 10);
    }
  }, [unprocessedPhrase, documentText, setDocumentText, clearUnprocessedPhrase]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Excluir teclas de navegación para no pausar si el usuario solo se mueve
    if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
      pauseForTyping();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setDocumentText(e.target.value);
  };

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

      {/* Canvas */}
      <div className="relative flex-grow h-full min-h-[400px]">
        <textarea
          ref={textareaRef}
          value={documentText}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          disabled={isProcessingAudio}
          className={`w-full h-full p-4 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-800 dark:text-slate-200 text-lg leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none font-serif transition-opacity ${
            isProcessingAudio ? 'opacity-40 cursor-not-allowed' : ''
          }`}
          placeholder="Comienza a dictar o escribir aquí tu novela..."
        />
        
        {/* Interim Text Preview Overlay */}
        {interimText && (
          <div className="absolute bottom-4 left-4 right-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm p-3 rounded-md shadow border border-blue-200 dark:border-blue-800 pointer-events-none">
            <span className="text-blue-500 font-medium italic animate-pulse">
              {interimText}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
