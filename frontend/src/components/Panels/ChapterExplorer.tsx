import React from 'react';
import { FilePlus, FolderPlus, Search, FileText, ChevronRight, Edit2, Trash2 } from 'lucide-react';
import { useProjectStore } from '../../store/useProjectStore';
import { useInferenceStore } from '../../store/useInferenceStore';

export const ChapterExplorer = () => {
  const { chapters, addChapter, deleteChapter, renameChapter, activeChapterId, setActiveChapter, searchQuery, setSearchQuery, loadChapters } = useProjectStore();
  const { liveBuffer, isProcessing } = useInferenceStore();
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [editTitle, setEditTitle] = React.useState('');

  const isLocked = isProcessing || !!liveBuffer;

  React.useEffect(() => {
    loadChapters();
  }, [loadChapters]);

  const filteredChapters = chapters.filter(ch => 
    ch.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full">
      {/* BARRA DE ACCIONES RÁPIDAS (Justo como tu captura) */}
      <div className={`flex items-center gap-4 mb-4 px-2 text-slate-400 ${isLocked ? 'opacity-40 pointer-events-none' : ''}`}>
        <button 
          onClick={() => {
            if (isLocked) return;
            addChapter('Nueva Escena');
          }} 
          title="Nueva Escena"
          disabled={isLocked}
        >
          <FilePlus size={16} className="hover:text-blue-500 transition-colors" />
        </button>
        <button title="Nueva Carpeta">
          <FolderPlus size={16} className="hover:text-blue-500 transition-colors" />
        </button>
        <div className="h-4 w-[1px] bg-slate-200 dark:bg-slate-800" />
        <div className="flex items-center gap-2 flex-1 bg-slate-100 dark:bg-slate-800 rounded px-2 py-1">
          <Search size={14} className="text-slate-400" />
          <input 
            type="text" 
            placeholder="Buscar escena..." 
            className="bg-transparent text-xs outline-none w-full text-slate-600 dark:text-slate-300"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* LISTA DE ARCHIVOS */}
      <div className={`space-y-0.5 ${isLocked ? 'opacity-60' : ''}`}>
        {filteredChapters.map((ch) => (
          <div 
            key={ch.id}
            onClick={() => {
              if (isLocked) {
                alert('Guarda o descarta el estilo literario actual antes de cambiar de escena.');
                return;
              }
              setActiveChapter(ch.id);
            }}
            className={`group flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer transition-all ${
              isLocked ? 'pointer-events-none cursor-not-allowed' : ''
            } ${
              activeChapterId === ch.id 
              ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600' 
              : 'hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-600'
            }`}
          >
            <ChevronRight size={12} className={activeChapterId === ch.id ? 'text-blue-500' : 'text-slate-400'} />
            <FileText size={14} className="flex-shrink-0" />
            
            {editingId === ch.id ? (
              <input 
                type="text" 
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    if (editTitle.trim()) {
                      renameChapter(ch.id, editTitle.trim());
                    }
                    setEditingId(null);
                  } else if (e.key === 'Escape') {
                    setEditingId(null);
                  }
                }}
                onBlur={() => {
                  if (editTitle.trim()) {
                    renameChapter(ch.id, editTitle.trim());
                  }
                  setEditingId(null);
                }}
                className="bg-white dark:bg-slate-800 border border-blue-400 dark:border-blue-700 rounded px-1.5 py-0.5 text-xs outline-none text-slate-800 dark:text-slate-100 flex-1 min-w-0"
                autoFocus
                onClick={(e) => e.stopPropagation()}
              />
            ) : (
              <>
                <span className="text-sm truncate font-medium flex-1 min-w-0">{ch.title}</span>
                
                <div className="hidden group-hover:flex items-center gap-1 ml-auto flex-shrink-0">
                  <button 
                    onClick={(e) => { 
                      e.stopPropagation(); 
                      setEditingId(ch.id); 
                      setEditTitle(ch.title); 
                    }} 
                    title="Cambiar Nombre"
                    className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-slate-400 hover:text-slate-700 dark:hover:text-slate-300 transition-all"
                  >
                    <Edit2 size={12} />
                  </button>
                  <button 
                    onClick={(e) => { 
                      e.stopPropagation(); 
                      if (confirm(`¿Estás seguro de eliminar "${ch.title}"?`)) {
                        deleteChapter(ch.id); 
                      }
                    }} 
                    title="Eliminar Escena"
                    className="p-1 hover:bg-red-100 dark:hover:bg-red-950/30 rounded text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-all"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
