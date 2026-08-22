import Dexie, { Table } from 'dexie';

export interface ChapterEntry {
  id?: number;
  chapterId: string;
  title?: string;
  content: string; // JSON de Tiptap
  updatedAt: number;
}

class GemaDatabase extends Dexie {
  chapters!: Table<ChapterEntry>;

  constructor() {
    super('GemaLocalDB');
    this.version(1).stores({
      chapters: '++id, chapterId, updatedAt' // Indexamos por chapterId
    });
  }
}

const db = new GemaDatabase();

export const LocalPersistenceService = {
  async saveChapter(chapterId: string, content: any, title?: string) {
    const updatedAt = Date.now();
    const payload: ChapterEntry = {
      chapterId,
      content: typeof content === 'string' ? content : JSON.stringify(content),
      updatedAt
    };
    if (title) payload.title = title;
    
    // Si ya existe, actualizamos para no sobreescribir el título si no se envía
    const existing = await db.chapters.where('chapterId').equals(chapterId).first();
    if (existing) {
      if (!title) payload.title = existing.title;
      payload.id = existing.id;
    }
    
    return await db.chapters.put(payload);
  },

  async getLatestContent(chapterId: string) {
    const entry = await db.chapters.where('chapterId').equals(chapterId).first();
    try {
      return entry ? JSON.parse(entry.content) : null;
    } catch (e) {
      return entry ? entry.content : null; // Fallback for raw text
    }
  },

  async getAllChapters() {
    const all = await db.chapters.toArray();
    return all.map(entry => {
      let contentObj = entry.content;
      try { contentObj = JSON.parse(entry.content); } catch(e) {}
      return {
        id: entry.chapterId,
        title: entry.title || 'Nueva Escena',
        content: contentObj,
        updatedAt: entry.updatedAt
      };
    });
  },

  async deleteChapter(chapterId: string) {
    const existing = await db.chapters.where('chapterId').equals(chapterId).first();
    if (existing && existing.id) {
      await db.chapters.delete(existing.id);
    }
  },

  async renameChapter(chapterId: string, newTitle: string) {
    const existing = await db.chapters.where('chapterId').equals(chapterId).first();
    if (existing) {
      existing.title = newTitle;
      existing.updatedAt = Date.now();
      await db.chapters.put(existing);
    }
  }
};
