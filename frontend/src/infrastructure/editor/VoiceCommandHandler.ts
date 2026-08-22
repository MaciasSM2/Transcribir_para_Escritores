import { Editor } from '@tiptap/react';

const COMMAND_KEYWORDS = {
  bold: ['negrita', 'resaltar'],
  paragraph: ['nuevo párrafo', 'punto aparte'],
  dialogue: ['dijo', 'respondió', 'preguntó'], // Auto-formateo de rayas
};

export const handleVoiceCommand = (editor: Editor, text: string) => {
  const cleanText = text.toLowerCase().trim();

  // 1. Comando de Negrita
  if (COMMAND_KEYWORDS.bold.some(k => cleanText.includes(k))) {
    editor.chain().focus().toggleBold().run();
    return true; // Comando ejecutado
  }

  // 2. Comando de Párrafo
  if (COMMAND_KEYWORDS.paragraph.some(k => cleanText.includes(k))) {
    editor.chain().focus().setParagraph().run();
    return true;
  }

  // 3. Comando de Diálogo (inserta la raya y un espacio)
  if (COMMAND_KEYWORDS.dialogue.some(k => cleanText.includes(k))) {
    editor.chain().focus().insertContent(`— `).run();
    return true;
  }

  return false; // Es texto normal, no un comando
};
