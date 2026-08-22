import { useState, useCallback } from 'react';
import { API_BASE } from '../lib/api';

interface AnalyticsData {
  word_count: number;
  character_count: number;
  estimated_pages: number;
  detected_entities: string[];
}

/**
 * Hook personalizado que encapsula la lógica de negocio para la analítica
 * del manuscrito y la descarga estricta de documentos binarios.
 */
export const useManuscriptAnalytics = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  /**
   * Despacha el contenido del lienzo para extraer entidades y métricas cuantitativas.
   */
  const fetchAnalytics = useCallback(async (rawText: string) => {
    if (!rawText.trim()) return;
    setIsAnalyzing(true);
    try {
      const response = await fetch(`${API_BASE}/export/manuscript/analytics`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: rawText })
      });
      if (!response.ok) throw new Error('Error en el cálculo de telemetría literaria');
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error("Fallo del servicio analítico local:", error);
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  /**
   * Descarga el manuscrito compilado bajo las normas tipográficas de la RAE.
   */
  const exportToDocxRae = useCallback(async (rawText: string, filename: string = "manuscrito_rae.docx") => {
    setIsExporting(true);
    try {
      const response = await fetch(`${API_BASE}/export/manuscript/export/rae`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: rawText })
      });

      if (!response.ok) throw new Error('Fallo al compilar el binario .docx');

      // 1. Convertir la respuesta de la API local en un objeto Blob
      const blob = await response.blob();
      
      // 2. Crear un enlace virtual en el DOM de Windows 11
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', filename);
      
      // 3. Disparar el evento de descarga nativo del sistema operativo
      document.body.appendChild(link);
      link.click();
      
      // 4. Limpieza absoluta de memoria (Garbage Collection Trigger)
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error("Error en la descarga del manuscrito:", error);
    } finally {
      setIsExporting(false);
    }
  }, []);

  return { analytics, isAnalyzing, isExporting, fetchAnalytics, exportToDocxRae };
};
