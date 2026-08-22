import { create } from 'zustand';

type TabType = 'tone' | 'history' | 'import';

type ViewType = 'dictation' | 'review';

interface UIState {
  currentView: ViewType;
  isSettingsOpen: boolean;
  settingsActiveTab: TabType;
  isFullscreen: boolean;
  editorTheme: 'night' | 'sepia' | 'paper' | 'light';
  setCurrentView: (view: ViewType) => void;
  openSettings: (tab?: TabType) => void;
  closeSettings: () => void;
  setSettingsTab: (tab: TabType) => void;
  toggleFullscreen: () => void;
  setEditorTheme: (theme: 'night' | 'sepia' | 'paper' | 'light') => void;
}

export const useUIStore = create<UIState>((set) => ({
  currentView: 'dictation',
  isSettingsOpen: false,
  settingsActiveTab: 'tone',
  isFullscreen: false,
  editorTheme: 'light',
  setCurrentView: (view) => set({ currentView: view }),
  openSettings: (tab = 'tone') => set({ isSettingsOpen: true, settingsActiveTab: tab }),
  closeSettings: () => set({ isSettingsOpen: false }),
  setSettingsTab: (tab) => set({ settingsActiveTab: tab }),
  toggleFullscreen: () => {
    set((state) => {
      const nextState = !state.isFullscreen;
      if (typeof window !== 'undefined') {
        if (nextState) {
          document.documentElement.requestFullscreen().catch((e) => console.error(e));
        } else {
          if (document.fullscreenElement) {
            document.exitFullscreen().catch((e) => console.error(e));
          }
        }
      }
      return { isFullscreen: nextState };
    });
  },
  setEditorTheme: (theme) => set({ editorTheme: theme }),
}));
