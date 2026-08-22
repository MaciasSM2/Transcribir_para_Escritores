import React from 'react';
import { Panel1 } from '../components/Panels/Panel1';
import { RichCanvas } from '../components/Editor/RichCanvas';
import { Panel3 } from '../components/Panels/Panel3';

export const TriplePanelLayout = () => {
  return (
    <div className="flex h-screen w-full bg-slate-50 dark:bg-slate-950 overflow-hidden font-sans">
      
      {/* PANEL 1: 260px fijo (Navegación) */}
      <aside className="w-[260px] flex-shrink-0 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 z-20">
        <Panel1 />
      </aside>

      {/* PANEL 2: Flexible (Lienzo A4) */}
      <main className="flex-1 flex flex-col min-w-0 bg-slate-100 dark:bg-slate-950">
        <RichCanvas />
      </main>

      {/* PANEL 3: 320px fijo (IA & Corrección) */}
      <aside className="w-[320px] flex-shrink-0 border-l border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 z-20 shadow-[-10px_0_15px_-3px_rgba(0,0,0,0.02)]">
        <Panel3 />
      </aside>

    </div>
  );
};
