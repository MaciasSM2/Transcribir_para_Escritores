import React from 'react';
import { Eye, Terminal, Sparkles } from 'lucide-react';
import { LiveTranscriptionBuffer } from './LiveTranscriptionBuffer';
import { AIChangeFeed } from './AIChangeFeed';
import { SystemMetricsContainer } from './SystemMetricsContainer';
import { Panel3Header } from './Panel3Header';
import { ExportController } from './ExportController';

/**
 * Panel 3: El Monitor de Inteligencia.
 * Actúa como la columna derecha del entorno inspirado en Obsidian.
 */
export const Panel3: React.FC = () => {
  return (
    <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 select-none relative">
      
      {/* Botón de Acción Principal (Mesa de Revisión) */}
      <Panel3Header />


      {/* SECCIÓN 3: LOG DE MODIFICACIONES DE LA IA (Scroll Flexible) */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
        <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 mb-1 sticky top-0 bg-slate-50 dark:bg-slate-900 py-1 z-10">
          <Sparkles size={14} className="text-purple-500" />
          <span className="text-xs font-bold uppercase tracking-wider">Auditoría de Prosa (Ollama)</span>
        </div>
        <AIChangeFeed />
      </div>

      {/* SECCIÓN 4: EXPORTACIÓN Y ANALÍTICA (Fijo Inferior) */}
      <ExportController />

    </div>
  );
};
