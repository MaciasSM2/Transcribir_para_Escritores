import { API_BASE } from './api';

/**
 * Cliente de API con esteroides de seguridad para entorno local.
 * Antes de disparar peticiones pesadas (AI/Audio), verifica la salud del host.
 */
export async function secureRequest(endpoint: string, options: RequestInit, isHeavyTask: boolean = false) {
  if (isHeavyTask) {
    // 1. Verificación rápida de salud antes de la tarea pesada
    const healthCheck = await fetch(`${API_BASE}/system/health/hardware`);
    const health = await healthCheck.json();

    if (!health.healthy) {
      throw new Error("SISTEMA_SATURADO: Libera memoria RAM antes de procesar más texto.");
    }
  }

  const response = await fetch(`${API_BASE}${endpoint}`, options);
  if (!response.ok) throw new Error(`API_ERROR: ${response.status}`);
  
  return response.json();
}
