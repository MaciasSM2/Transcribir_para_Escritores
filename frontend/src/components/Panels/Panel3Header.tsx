import React from 'react';
import { Sparkles, Upload } from 'lucide-react';
import { useInferenceStore } from '../../store/useInferenceStore';
import { useProjectStore } from '../../store/useProjectStore';
import { useDictationStore } from '../../store/useDictationStore';
import { useToneStore } from '../../store/useToneStore';
import { useAudioUpload } from '../../hooks/useAudioUpload';

export const Panel3Header = () => {
  const { applyLiteraryStyle, isProcessing } = useInferenceStore();
  const { handleAudioUpload, isUploading } = useAudioUpload();
  
  // Extraemos el texto en tiempo real del buffer
  const { documentText, isProcessingAudio } = useDictationStore();
  
  // Extraemos el tono configurado
  const { toneName } = useToneStore();
  const activeTone = toneName || 'Narrativa Estándar';

  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);

  if (!mounted) {
    return (
      <div className="p-4 border-b bg-white/80 dark:bg-slate-900/80 backdrop-blur-md sticky top-0 z-10 flex flex-col gap-3" />
    );
  }

  return (
    <div className="p-4 border-b bg-white/80 dark:bg-slate-900/80 backdrop-blur-md sticky top-0 z-10 flex flex-col gap-3">
      <div className="flex justify-between items-center">
        <h3 className="text-xs font-black uppercase tracking-widest text-slate-400">
          Mesa de Revisión
        </h3>
      </div>
      <p className="text-[10px] text-slate-400">
        Tono actual: <span className="text-purple-600 font-bold">{activeTone}</span>
      </p>
    </div>
  );
};
