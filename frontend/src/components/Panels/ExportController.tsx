import React from 'react';
import { useManuscriptAnalytics } from '../../hooks/useManuscriptAnalytics';
import { ManuscriptAnalyticsGrid } from './ManuscriptAnalyticsGrid';
import { Download, BarChart4 } from 'lucide-react';

/**
 * ExportController: Une la botonera de acciones del Dashboard RAE con el flujo del lienzo.
 * Se incrusta directamente en la sección inferior o superior del Panel 3.
 */
export const ExportController: React.FC = () => {
  const { analytics, isAnalyzing, isExporting, fetchAnalytics, exportToDocxRae } = useManuscriptAnalytics();

  const getEditorText = () => {
    // Extracción limpia del texto desde el DOM (ProseMirror)
    // para mantener el desacoplamiento estricto de la UI visual.
    const pmElement = document.querySelector('.ProseMirror') as HTMLElement;
    return pmElement ? pmElement.innerText || pmElement.textContent || '' : '';
  };

  const handleCalculate = () => {
    const plainText = getEditorText();
    fetchAnalytics(plainText);
  };

  const handleExport = () => {
    const plainText = getEditorText();
    // Exportación nativa respetando la norma editorial configurada
    exportToDocxRae(plainText, "Genesis_Manuscrito_RAE.docx");
  };

  return (
    <div className="space-y-4 w-full p-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 flex-shrink-0">
      {/* Botonera de Acciones de Control */}
      <div className="flex gap-2">
        <button
          onClick={handleCalculate}
          disabled={isAnalyzing}
          className="flex-1 py-1.5 px-3 bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-slate-800 dark:hover:bg-slate-750 dark:text-slate-200 rounded-xl font-medium text-xs flex items-center justify-center gap-1.5 transition-all disabled:opacity-50"
        >
          <BarChart4 size={14} />
          {isAnalyzing ? 'Calculando...' : 'Ficha Técnica'}
        </button>

        <button
          onClick={handleExport}
          disabled={isExporting}
          className="flex-1 py-1.5 px-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-md shadow-emerald-600/10 disabled:opacity-50"
        >
          <Download size={14} />
          {isExporting ? 'Compilando...' : 'Exportar RAE'}
        </button>
      </div>

      {/* Grid de Resultados Analíticos */}
      <ManuscriptAnalyticsGrid data={analytics} loading={isAnalyzing} />
    </div>
  );
};
