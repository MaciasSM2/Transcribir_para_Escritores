// frontend/src/components/ExportPreviewModal.tsx
import React, { useState } from 'react';
import { exportService } from '../infrastructure/export/ExportService';

export function ExportPreviewModal({ text, isOpen, onClose }: { text: string, isOpen: boolean, onClose: () => void }) {
  const [format, setFormat] = useState('editorial'); // 'editorial', 'apa', 'classic'
  
  const handleDownload = () => {
    // We pass format as the ExportFormat type. Assuming 'editorial' maps to 'docx' and 'apa' could map to 'docx' or we handle differently inside exportService
    // Since exportService expects 'docx', 'txt', 'pdf', we'll map them
    let exportFormat: 'docx' | 'txt' | 'pdf' = 'docx';
    if (format === 'apa' || format === 'classic') exportFormat = 'docx'; 
    exportService.exportDocument(exportFormat, text);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden border border-slate-200 dark:border-slate-800">
        <div className="p-6 border-b border-slate-200 dark:border-slate-800">
          <h3 className="text-xl font-bold text-slate-800 dark:text-slate-200">Configuración de Exportación Editorial</h3>
          <p className="text-sm text-slate-500">Ajusta cómo se verá tu manuscrito final.</p>
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Panel de Opciones */}
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2 text-slate-700 dark:text-slate-300">Normativa de Estilo</label>
              <select 
                value={format} 
                onChange={(e) => setFormat(e.target.value)}
                className="w-full p-3 rounded-xl bg-slate-100 dark:bg-slate-800 border-none outline-none text-slate-800 dark:text-slate-200"
              >
                <option value="editorial">Editorial (Raya de diálogo RAE)</option>
                <option value="apa">Académico (Normas APA 7ma Ed.)</option>
                <option value="classic">Clásico (Times New Roman 12pt)</option>
              </select>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
              <span className="text-sm text-slate-700 dark:text-slate-300">Sangría de primera línea</span>
              <div className="text-blue-600 font-bold">1.27 cm</div>
            </div>
          </div>

          {/* Previsualización Visual */}
          <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 font-serif text-[10px] leading-tight text-slate-800 dark:text-slate-300">
            <div className="mb-2 text-center font-bold uppercase tracking-widest">Previsualización</div>
            <p className="indent-4 mb-2">Esto es un ejemplo de cómo se verá tu párrafo inicial con el interlineado doble.</p>
            <p className="indent-4">—Así se verán los diálogos —dijo el sistema—, con la raya pegada al texto.</p>
          </div>
        </div>

        <div className="p-6 bg-slate-50 dark:bg-slate-800/50 flex justify-end gap-3">
          <button onClick={onClose} className="px-6 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition-colors">Cancelar</button>
          <button 
            onClick={handleDownload}
            className="px-6 py-2 bg-blue-600 text-white rounded-xl font-bold hover:shadow-lg transition-all"
          >
            Descargar Documento
          </button>
        </div>
      </div>
    </div>
  );
}
