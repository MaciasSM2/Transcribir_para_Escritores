import React, { useEffect, useRef } from 'react';
import { useInferenceStore } from '../../store/useInferenceStore';
import { Disc } from 'lucide-react';

/**
 * LiveTranscriptionBuffer: Renderiza el flujo de texto crudo proveniente del ASR local (Vosk).
 * Utiliza referencias directas al DOM para el auto-scroll eficiente.
 */
export const LiveTranscriptionBuffer: React.FC = () => {
  // Suscripción atómica al búfer de voz viva para evitar re-renders en el lienzo central
  const liveBuffer = useInferenceStore((state) => state.liveBuffer);
  const currentStage = useInferenceStore((state) => state.currentStage);
  
  const containerRef = useRef<HTMLDivElement>(null);

  // Efecto encargado del Auto-Scroll optimizado
  useEffect(() => {
    if (containerRef.current) {
      // Desplazamiento nativo al fondo del contenedor al recibir nuevos tokens de habla
      containerRef.current.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [liveBuffer]); // Se dispara únicamente cuando muta la cadena de texto crudo

  return (
    <div className="relative">
      {/* Contenedor de Texto de Alta Contención */}
      <div 
        ref={containerRef}
        className="h-28 w-full bg-slate-900 text-slate-300 font-mono text-[11px] p-3 rounded-xl overflow-y-auto border border-slate-800 leading-relaxed shadow-inner custom-scrollbar"
      >
        {liveBuffer ? (
          <span className="animate-fade-in">{liveBuffer}</span>
        ) : (
          <span className="text-slate-600 italic">Esperando inicialización del micrófono...</span>
        )}
        
        {/* Cursor intermitente simulado de transcripción activa */}
        {currentStage === 'lexical_cleaning' && (
          <span className="inline-block w-1.5 h-3.5 bg-amber-500 ml-1 animate-pulse" />
        )}
      </div>

      {/* Indicador de Estado del Hardware Acústico */}
      {liveBuffer && (
        <div className="absolute top-2 right-2 flex items-center gap-1 bg-slate-950/80 px-2 py-0.5 rounded-md border border-slate-800">
          <Disc size={10} className="text-red-500 animate-spin" />
          <span className="text-[9px] text-red-400 font-bold uppercase tracking-tighter">REC LOCAL</span>
        </div>
      )}
    </div>
  );
};
