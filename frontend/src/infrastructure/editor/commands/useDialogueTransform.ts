import { useCallback } from 'react';
import { Editor } from '@tiptap/react';
import { API_BASE } from '../../../lib/api';

/**
 * Hook de infraestructura encargado de extraer el texto del lienzo Tiptap,
 * enviarlo al motor de diálogos local y actualizar los nodos ProseMirror.
 */
export const useDialogueTransform = (editor: Editor | null) => {
  
  const transformSelectedText = useCallback(async (toneName: string) => {
    if (!editor) return;

    // 1. Obtener la selección actual del escritor en el lienzo A4
    const { from, to, empty } = editor.state.selection;
    if (empty) return; // Protección si no hay texto seleccionado

    const selectedText = editor.state.doc.textBetween(from, to, ' ');

    try {
      // 2. Despachar payload al pipeline de segmentación del backend
      const response = await fetch(`${API_BASE}/dialogue/parse-scene`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_text: selectedText,
          tone_name: toneName
        })
      });

      if (!response.ok) throw new Error('Fallo en el parsing estructural de la escena');

      const data = await response.json(); // Mapea con DialogueSceneResponse

      // 3. Modificación atómica del árbol de nodos mediante comandos de Tiptap
      // insertContent maneja automáticamente el parsing de saltos de línea (\n\n) a etiquetas <p>
      editor
        .chain()
        .focus()
        .deleteSelection() // Remueve el bloque conversacional desorganizado viejo
        .insertContent(data.formatted_prose) // Inyecta la prosa limpia con rayas RAE
        .run();

    } catch (error) {
      console.error("Error ejecutando la transformación dramática:", error);
    }
  }, [editor]);

  return { transformSelectedText };
};
