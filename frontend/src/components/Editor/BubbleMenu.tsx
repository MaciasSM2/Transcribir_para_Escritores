import React, { useEffect, useRef } from 'react';
import type { Editor } from '@tiptap/react';
import { BubbleMenuPlugin, BubbleMenuPluginProps } from '@tiptap/extension-bubble-menu';
import { MessageSquareQuote, Bold, Italic } from 'lucide-react';
import { useDialogueTransform } from '../../infrastructure/editor/commands/useDialogueTransform';

export const BubbleMenu = ({ editor }: { editor: Editor }) => {
  const menuRef = useRef<HTMLDivElement>(null);
  const { transformSelectedText } = useDialogueTransform(editor);

  useEffect(() => {
    if (!menuRef.current || !editor) return;

    const plugin = BubbleMenuPlugin({
      pluginKey: 'gema-bubble-menu',
      editor,
      element: menuRef.current,
      tippyOptions: { duration: 100 },
    } as BubbleMenuPluginProps);

    editor.registerPlugin(plugin);
    return () => {
      editor.unregisterPlugin('gema-bubble-menu');
    };
  }, [editor]);

  return (
    <div
      ref={menuRef}
      className="flex items-center gap-1 p-1 bg-slate-900 text-white rounded-lg shadow-xl border border-slate-700"
      style={{ visibility: 'hidden' }}
    >
      {/* Botón de Transformación de Diálogo */}
      <button
        onClick={() => transformSelectedText('Narrativa Estándar')}
        className="flex items-center gap-2 px-3 py-1.5 hover:bg-blue-600 rounded-md transition-colors text-xs font-bold"
        title="Formatear como Diálogo RAE (Ctrl+Shift+D)"
      >
        <MessageSquareQuote size={14} />
        Limpiar Diálogo
      </button>

      <div className="w-[1px] h-4 bg-slate-700 mx-1" />

      {/* Herramientas Rápidas de Formato */}
      <button
        onClick={() => editor.chain().focus().toggleBold().run()}
        className={`p-1.5 rounded ${editor.isActive('bold') ? 'bg-blue-500' : 'hover:bg-slate-800'}`}
      >
        <Bold size={14} />
      </button>
      <button
        onClick={() => editor.chain().focus().toggleItalic().run()}
        className={`p-1.5 rounded ${editor.isActive('italic') ? 'bg-blue-500' : 'hover:bg-slate-800'}`}
      >
        <Italic size={14} />
      </button>
    </div>
  );
};
