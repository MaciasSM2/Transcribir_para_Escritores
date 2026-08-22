import React, { useState, useEffect } from 'react';
import { Mic2, Mic, MicOff, Sparkles, Upload, Check } from 'lucide-react';
import { useDictationStore } from '../../store/useDictationStore';
import { useCleanDictation } from '../../hooks/useCleanDictation';
import { useToneStore } from '../../store/useToneStore';
import { useAudioUpload } from '../../hooks/useAudioUpload';
import { useInferenceStore } from '../../store/useInferenceStore';

export const QuickControlCenter = () => {
  const { isRecording, isProcessingAudio, isWhisperMode, setWhisperMode, documentText } = useDictationStore();
  const { startRecording, stopRecording } = useCleanDictation();
  const { toneName, setTone } = useToneStore();
  const { handleAudioUpload, isUploading } = useAudioUpload();
  const { applyLiteraryStyle, isProcessing, liveBuffer } = useInferenceStore();

  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return <div className="space-y-4 animate-pulse h-64 bg-slate-100/50 dark:bg-slate-800/50 rounded-lg"></div>;
  }

  return (
    <div className="space-y-4">
      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Configuración Activa</h4>
      
      {/* BOTONES DE TRANSCRIPCIÓN Y ESTILO */}
      <div className="flex flex-col gap-2">
        <label className={`cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-200 dark:shadow-blue-900/20 ${(isProcessingAudio || isUploading) ? 'opacity-50 pointer-events-none' : ''}`}>
          {isUploading || isProcessingAudio ? (
            <div className="animate-spin h-3 w-3 border-2 border-white border-t-transparent rounded-full" />
          ) : (
            <Upload size={14} />
          )}
          Subir Audio
          <input 
            type="file" 
            accept="audio/*" 
            className="hidden" 
            onChange={(e) => {
              if (e.target.files?.[0]) {
                handleAudioUpload(e.target.files[0]);
                e.target.value = ''; // reset
              }
            }} 
          />
        </label>

        {liveBuffer ? (
          <button 
            onClick={() => useInferenceStore.getState().clearLog()}
            disabled={isProcessing}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-green-200 dark:shadow-green-900/20"
          >
            <Check size={14} />
            Guardar Estilo Literario
          </button>
        ) : (
          <button 
            onClick={() => applyLiteraryStyle(documentText, toneName || 'Narrativa Estándar')}
            disabled={isProcessing || !documentText || isProcessingAudio}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-purple-200 dark:shadow-purple-900/20 disabled:opacity-50"
          >
            {isProcessing ? (
              <div className="animate-spin h-3 w-3 border-2 border-white border-t-transparent rounded-full" />
            ) : (
              <Sparkles size={14} />
            )}
            Aplicar Estilo Literario
          </button>
        )}
      </div>

      {/* TOGGLE MODO SUSURRO */}
      <div className="flex items-center justify-between group">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-blue-100 dark:bg-blue-900/30 rounded-lg text-blue-600">
            <Mic2 size={14} />
          </div>
          <span className="text-xs font-medium">Modo Susurro</span>
        </div>
        <input 
          type="checkbox" 
          checked={isWhisperMode}
          onChange={(e) => setWhisperMode(e.target.checked)}
          className="w-8 h-4 bg-slate-300 rounded-full appearance-none checked:bg-blue-600 transition-all cursor-pointer relative after:content-[''] after:absolute after:w-3 after:h-3 after:bg-white after:rounded-full after:top-0.5 after:left-0.5 checked:after:translate-x-4 after:transition-all" 
        />
      </div>

      {/* SELECTOR DE TONO LITERARIO */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
          <Sparkles size={14} />
          <span className="text-xs font-medium">Tono Ollama</span>
        </div>
        <select 
          value={toneName}
          onChange={(e) => setTone(e.target.value, '')}
          className="w-full bg-slate-100 dark:bg-slate-800 border-none text-[11px] rounded-lg p-2 focus:ring-1 focus:ring-blue-500"
        >
          <option value="Narrativa de Ciencia Ficción y Fantasía Épica">Narrativa Fantástica</option>
          <option value="No Ficción Académica">Informe Formal</option>
          <option value="Diálogo Teatral">Diálogo Teatral</option>
        </select>
      </div>
    </div>
  );
};
