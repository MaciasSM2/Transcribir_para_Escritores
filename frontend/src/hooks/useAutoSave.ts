import { useEffect, useRef } from 'react';
import { Editor } from '@tiptap/react';
import { LocalPersistenceService } from '../infrastructure/storage/LocalPersistenceService';

export const useAutoSave = (editor: Editor | null, chapterId: string) => {
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!editor || !chapterId) return;

    const handleUpdate = () => {
      if (timerRef.current) clearTimeout(timerRef.current);

      timerRef.current = setTimeout(async () => {
        const json = editor.getJSON();
        await LocalPersistenceService.saveChapter(chapterId, json);
        console.log(`[Gema] Escena ${chapterId} guardada en disco local.`);
      }, 2000);
    };

    editor.on('update', handleUpdate);
    return () => {
      editor.off('update', handleUpdate);
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
        
        // Guardado inmediato de emergencia antes de cambiar
        const json = editor.getJSON();
        LocalPersistenceService.saveChapter(chapterId, json);
        console.log(`[Gema] Guardado inmediato al cambiar escena: ${chapterId}`);
      }
    };
  }, [editor, chapterId]);
};
