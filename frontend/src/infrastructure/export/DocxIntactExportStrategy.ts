import { IDocumentExporter } from './IDocumentExporter';
import { BrowserDownloadHelper } from './BrowserDownloadHelper';

/**
 * Estrategia de exportación híbrida "Intacta":
 * Toma el HTML de Tiptap tal cual y llama al servidor Node.js
 * para convertirlo a DOCX manteniendo el formato original visual.
 */
export class DocxIntactExportStrategy implements IDocumentExporter {
  public async export(htmlContent: string, title: string = 'Gema_Documento_Intacto'): Promise<void> {
    if (!htmlContent) throw new Error('No hay contenido para exportar.');

    try {
      const response = await fetch('/api/export/docx-intact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ htmlContent }),
      });

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.statusText}`);
      }

      const blob = await response.blob();
      BrowserDownloadHelper.triggerDownload(blob, `${title.replace(/\s+/g, '_')}.docx`);
    } catch (err) {
      console.error('[DocxIntactExportStrategy] Error al empaquetar DOCX Intacto:', err);
      throw err;
    }
  }
}
