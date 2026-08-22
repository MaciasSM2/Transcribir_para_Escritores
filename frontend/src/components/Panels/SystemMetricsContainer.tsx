import React, { useEffect, useState } from 'react';
import { useInferenceStore } from '../../store/useInferenceStore';
import { API_BASE } from '../../lib/api';
import { Cpu, HardDrive, ShieldAlert } from 'lucide-react';

interface HardwarePayload {
  healthy: boolean;
  ram_usage_percent: number;
  cpu_usage_percent: number;
  action_required: string;
}

/**
 * SystemMetricsContainer: Administra el sondeo pasivo de telemetría de Windows 11.
 * Muestra alertas visuales críticas si Ollama o Vosk saturan el Host local.
 */
export const SystemMetricsContainer: React.FC = () => {
  const [metrics, setMetrics] = useState<HardwarePayload | null>(null);
  const setStage = useInferenceStore((state) => state.setStage);

  useEffect(() => {
    const pollHardwareHealth = async () => {
      try {
        const response = await fetch(`${API_BASE}/system/health/hardware`);
        if (!response.ok) return;
        
        const data: HardwarePayload = await response.json();
        setMetrics(data);

        // Si el SystemGuardian del backend ordena estrangulamiento, mutamos el estado de la UI
        if (data.action_required === 'THROTTLE_INFERENCE') {
          setStage('idle'); // Pausa preventiva del pipeline pesado
        }
      } catch (error) {
        // Silenciar temporalmente el fallo de fetch cuando el backend está apagado
        // para evitar el overlay de error intrusivo de Next.js en desarrollo.
      }
    };

    // Inicialización inmediata del primer escaneo pre-vuelo
    pollHardwareHealth();

    // Establecimiento del bucle de sondeo controlado (Cada 4 segundos)
    const intervalId = setInterval(pollHardwareHealth, 4000);

    // Destrucción explícita del timer al desmontar el componente (SOLID - S)
    return () => clearInterval(intervalId);
  }, [setStage]);

  if (!metrics) return <div className="h-12 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse" />;

  return (
    <div className="space-y-3">
      {/* Barra de Progreso: Uso de CPU */}
      <div className="space-y-1">
        <div className="flex justify-between text-[10px] font-mono text-slate-500">
          <div className="flex items-center gap-1">
            <Cpu size={12} className="text-blue-500" />
            <span>Procesador Host (CPU)</span>
          </div>
          <span className="font-bold">{metrics.cpu_usage_percent}%</span>
        </div>
        <div className="w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div 
            className="bg-blue-500 h-full transition-all duration-500 ease-out" 
            style={{ width: `${metrics.cpu_usage_percent}%` }}
          />
        </div>
      </div>

      {/* Barra de Progreso: Uso de RAM */}
      <div className="space-y-1">
        <div className="flex justify-between text-[10px] font-mono text-slate-500">
          <div className="flex items-center gap-1">
            <HardDrive size={12} className="text-purple-500" />
            <span>Memoria Asignada (RAM)</span>
          </div>
          <span className="font-bold">{metrics.ram_usage_percent}%</span>
        </div>
        <div className="w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div 
            className={`h-full transition-all duration-500 ease-out ${
              metrics.ram_usage_percent > 85 ? 'bg-red-500' : 'bg-purple-500'
            }`} 
            style={{ width: `${metrics.ram_usage_percent}%` }}
          />
        </div>
      </div>

      {/* Alerta de Saturación Térmica / Concurrencia de VRAM */}
      {!metrics.healthy && (
        <div className="flex items-start gap-2 p-2.5 bg-red-50 dark:bg-red-950/30 border border-red-200/40 dark:border-red-900/40 rounded-xl animate-fade-in">
          <ShieldAlert size={14} className="text-red-500 mt-0.5 flex-shrink-0" />
          <p className="text-[10px] text-red-600 dark:text-red-400 leading-normal font-sans">
            <span className="font-bold">Capacidad Límite:</span> Inferencia retrasada preventivamente para proteger el archivo temporal. Cierra aplicaciones pesadas en Windows.
          </p>
        </div>
      )}
    </div>
  );
};
