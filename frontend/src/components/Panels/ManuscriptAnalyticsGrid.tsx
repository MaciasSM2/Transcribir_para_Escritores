import React from 'react';
import { BookOpen, FileText, Type, Users } from 'lucide-react';

interface AnalyticsGridProps {
  data: {
    word_count: number;
    character_count: number;
    estimated_pages: number;
    detected_entities: string[];
  } | null;
  loading: boolean;
}

/**
 * Componente que renderiza el grid de analíticas dentro del Panel 3.
 * Muestra el conteo de palabras, páginas estimadas y personajes detectados.
 */
export const ManuscriptAnalyticsGrid: React.FC<AnalyticsGridProps> = ({ data, loading }) => {
  if (loading) {
    return <div className="h-40 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse w-full" />;
  }

  if (!data) {
    return (
      <div className="p-4 bg-slate-100/50 dark:bg-slate-900/40 rounded-xl text-center border border-slate-200/40">
        <p className="text-[11px] text-slate-400">Presiona "Calcular Ficha Técnica" para auditar el manuscrito.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Grid de Métricas Cuantitativas */}
      <div className="grid grid-cols-3 gap-2">
        <div className="bg-white dark:bg-slate-950 p-2.5 rounded-xl border border-slate-100 dark:border-slate-850 shadow-sm text-center">
          <Type size={14} className="text-blue-500 mx-auto mb-1" />
          <p className="text-[10px] text-slate-400">Palabras</p>
          <p className="text-xs font-bold font-mono text-slate-700 dark:text-slate-300">{data.word_count}</p>
        </div>
        <div className="bg-white dark:bg-slate-950 p-2.5 rounded-xl border border-slate-100 dark:border-slate-850 shadow-sm text-center">
          <FileText size={14} className="text-purple-500 mx-auto mb-1" />
          <p className="text-[10px] text-slate-400">Caracteres</p>
          <p className="text-xs font-bold font-mono text-slate-700 dark:text-slate-300">{data.character_count}</p>
        </div>
        <div className="bg-white dark:bg-slate-950 p-2.5 rounded-xl border border-slate-100 dark:border-slate-850 shadow-sm text-center">
          <BookOpen size={14} className="text-emerald-500 mx-auto mb-1" />
          <p className="text-[10px] text-slate-400">Páginas A4</p>
          <p className="text-xs font-bold font-mono text-slate-700 dark:text-slate-300">~{data.estimated_pages}</p>
        </div>
      </div>

      {/* Listado de Entidades e Hilos Narrativos Detectados */}
      <div className="bg-white dark:bg-slate-950 p-3 rounded-xl border border-slate-100 dark:border-slate-850 shadow-sm space-y-2">
        <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-500">
          <Users size={12} className="text-purple-500" />
          <span>Foco de Personajes Detectados</span>
        </div>
        
        {data.detected_entities.length === 0 ? (
          <p className="text-[10px] text-slate-400 italic">No se han identificado nombres propios en este segmento.</p>
        ) : (
          <div className="flex flex-wrap gap-1">
            {data.detected_entities.map((entity, index) => (
              <span 
                key={index} 
                className="text-[10px] px-2 py-0.5 bg-slate-100 dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded font-medium text-slate-600 dark:text-slate-300"
              >
                {entity}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
