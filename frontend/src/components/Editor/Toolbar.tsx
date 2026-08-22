import React from 'react';
import { Camera } from 'lucide-react';
import { Editor } from '@tiptap/react';
import { useProjectStore } from '../../store/useProjectStore';

export const Toolbar = ({ editor }: { editor: Editor | null }) => {
  if (!editor) return null;

  return (
    <div className="sticky top-0 z-20 flex items-center gap-2 p-2 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
      {/* Aquí podemos añadir más controles del editor en el futuro */}
    </div>
  );
};
