import React from 'react';
import { Folder, Search, Settings, Mic2, Sparkles, Book } from 'lucide-react';
import { ChapterExplorer } from './ChapterExplorer';
import { QuickControlCenter } from './QuickControlCenter';
import { useUIStore } from '../../store/useUIStore';

export const Panel1 = () => {
  const { openSettings } = useUIStore();

  return (
    <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-900 select-none">
      
      {/* SECCIÓN SUPERIOR: EXPLORADOR (Estilo Obsidian) */}
      <div className="p-4 flex items-center justify-between text-slate-500">
        <div className="flex items-center gap-2">
          <Folder size={16} />
          <span className="text-xs font-bold uppercase tracking-widest">Manuscrito</span>
        </div>
        <div className="flex gap-2">
          <Search size={14} className="hover:text-blue-500 cursor-pointer" />
          <Settings size={14} className="hover:text-blue-500 cursor-pointer" onClick={() => openSettings('tone')} />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-2 space-y-1">
        <ChapterExplorer />
      </div>

      {/* SECCIÓN INFERIOR: CONTROLES DE IA Y AUDIO */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-black/20">
        <QuickControlCenter />
      </div>

    </div>
  );
};
