import { create } from 'zustand';
import { LocalPersistenceService } from '../infrastructure/storage/LocalPersistenceService';

interface ProjectState {
  chapters: any[];
  activeChapterId: string | null;
  searchQuery: string;
  
  // Acciones
  loadChapters: () => Promise<void>;
  addChapter: (title: string) => Promise<string>;
  deleteChapter: (id: string) => Promise<void>;
  renameChapter: (id: string, newTitle: string) => Promise<void>;
  setActiveChapter: (id: string) => void;
  setSearchQuery: (query: string) => void;
  restoreVersion?: (id: string) => void;
  createManualSnapshot?: (chapterId: string, contentJson: string, label: string) => void;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  chapters: [],
  activeChapterId: null,
  searchQuery: '',

  loadChapters: async () => {
    const data = await LocalPersistenceService.getAllChapters();
    set({ chapters: data });
  },

  addChapter: async (title: string) => {
    const newId = crypto.randomUUID();
    const newChapter = { id: newId, title, content: '', updatedAt: Date.now() };
    await LocalPersistenceService.saveChapter(newId, '', title);
    set((state) => ({ 
      chapters: [...state.chapters, newChapter],
      activeChapterId: newId
    }));
    return newId;
  },

  deleteChapter: async (id: string) => {
    await LocalPersistenceService.deleteChapter(id);
    const updatedChapters = get().chapters.filter((ch) => ch.id !== id);
    set({ chapters: updatedChapters });
    
    if (get().activeChapterId === id) {
      set({ activeChapterId: updatedChapters.length > 0 ? updatedChapters[0].id : null });
    }
  },

  renameChapter: async (id: string, newTitle: string) => {
    await LocalPersistenceService.renameChapter(id, newTitle);
    const updatedChapters = get().chapters.map((ch) => 
      ch.id === id ? { ...ch, title: newTitle, updatedAt: Date.now() } : ch
    );
    set({ chapters: updatedChapters });
  },

  setActiveChapter: (id) => set({ activeChapterId: id }),
  setSearchQuery: (query) => set({ searchQuery: query }),
}));
