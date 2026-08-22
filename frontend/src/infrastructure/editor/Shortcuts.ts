import { Extension } from '@tiptap/core';

// Extensión de Tiptap para atajos globales
export const SnapshotShortcuts = Extension.create({
  name: 'snapshotShortcuts',

  addKeyboardShortcuts() {
    return {
      'Mod-Shift-s': () => {
        // Dispara el evento global para el snapshot manual
        window.dispatchEvent(new CustomEvent('trigger-manual-snapshot'));
        return true;
      },
    };
  },
});
