import React from 'react';
import { useInferenceStore } from '../../store/useInferenceStore';
import { ArrowRight, CheckCircle, ShieldAlert } from 'lucide-react';

export const AIChangeFeed: React.FC = () => {
  // Suscripción selectiva al array de modificaciones para optimizar rendimiento
  const { modifications, setPendingReplacement, removeModification } = useInferenceStore();

  const handleApply = (mod: any) => {
    setPendingReplacement(mod);
    removeModification(mod.id);
  };

  if (modifications.length === 0) {
    return (
      <div className="h-32 flex flex-col items-center justify-center border border-dashed border-slate-200 dark:border-slate-800 rounded-xl p-4 text-center">
        <CheckCircle size={20} className="text-slate-300 dark:text-slate-700 mb-2" />
        <p className="text-xs text-slate-400 dark:text-slate-500">
          Mesa de Revisión Lista. No hay sugerencias pendientes.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2.5">
      {modifications.map((mod) => (
        <div 
          key={mod.id} 
          className="p-3 bg-white dark:bg-slate-950 rounded-xl border border-slate-100 dark:border-slate-850 shadow-sm space-y-1.5 transition-all hover:border-slate-300 dark:hover:border-slate-700 animate-in slide-in-from-right"
        >
          {/* Header de la Tarjeta de Modificación */}
          <div className="flex items-center justify-between text-[10px]">
            <span className={`px-2 py-0.5 rounded-full font-medium ${
              mod.type === 'rae_dialogo' ? 'bg-purple-50 text-purple-600 dark:bg-purple-950/40 dark:text-purple-400' :
              mod.type === 'muletilla' ? 'bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-400' :
              'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-400'
            }`}>
              {mod.type.toUpperCase().replace('_', ' ')}
            </span>
            <span className="text-slate-400 font-mono">{mod.timestamp}</span>
          </div>

          {/* Comparativa de Texto (Antes / Después) */}
          <div className="text-xs space-y-1 font-serif">
            <p className="text-slate-400 line-through bg-slate-50 dark:bg-slate-900/40 px-1.5 py-0.5 rounded">
              {mod.original}
            </p>
            <div className="flex items-start gap-1 text-slate-700 dark:text-slate-300 bg-emerald-50/30 dark:bg-emerald-950/10 px-1.5 py-0.5 rounded">
              <ArrowRight size={12} className="text-emerald-500 mt-0.5 flex-shrink-0" />
              <p className="font-medium">{mod.replaced}</p>
            </div>
          </div>

          {/* Explicación Técnica de la decisión de la IA */}
          <p className="text-[10px] text-slate-400 dark:text-slate-500 font-sans leading-normal mb-2">
            {mod.description}
          </p>

          <button 
            onClick={() => handleApply(mod)}
            className="w-full py-1.5 mt-2 bg-slate-100 hover:bg-emerald-100 hover:text-emerald-700 text-slate-600 text-[10px] font-bold rounded-lg transition-colors flex items-center justify-center gap-1 border border-transparent hover:border-emerald-200"
          >
            <CheckCircle size={12} /> Aceptar Cambio
          </button>
        </div>
      ))}
    </div>
  );
};
