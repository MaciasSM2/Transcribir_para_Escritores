'use client';

import DictationCanvas from '@/components/DictationCanvas';
import TopNavbar from '@/components/TopNavbar';
import CorrectionReviewer from '@/components/CorrectionReviewer';
import { useUIStore } from '@/store/useUIStore';
import { useDictationStore } from '@/store/useDictationStore';
import { useToneStore } from '@/store/useToneStore';
import { useHistoryStore } from '@/store/useHistoryStore';
import { useEffect } from 'react';
import { TriplePanelLayout } from '@/layouts/TriplePanelLayout';

export default function Home() {
  const { currentView } = useUIStore();
  const { documentText } = useDictationStore();
  const { toneName, fetchTones } = useToneStore();
  const { fetchHistory } = useHistoryStore();

  useEffect(() => {
    fetchHistory();
    fetchTones();
  }, [fetchHistory, fetchTones]);

  return <TriplePanelLayout />;
}
