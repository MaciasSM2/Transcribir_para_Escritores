import { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel } from 'docx';
import { IDocumentExporter } from './IDocumentExporter';
import { BrowserDownloadHelper } from './BrowserDownloadHelper';

/**
 * Estrategia concreta para exportar documentos en formato DOCX profesional.
 * Aplica de forma estricta las directrices editoriales convencionales (estilo RAE/APA).
 */
export class DocxExportStrategy implements IDocumentExporter {
  private readonly DEFAULT_FONT = 'Times New Roman';
  private readonly DEFAULT_SIZE = 24; // 24 halves-of-a-point = 12pt en Word

  public async export(text: string, title: string = 'Gema_Documento_APA'): Promise<void> {
    if (!text) throw new Error('No hay contenido de texto disponible para exportar.');

    // 1. Segmentación del texto por párrafos lógicos definidos por el procesador estructural
    const rawParagraphs = text.split(/\n\n+/);
    
    // 2. Mapeo de strings hacia objetos de dominio de la librería docx
    const docxParagraphs = rawParagraphs.map((pText) => {
      const trimmedText = pText.trim();
      
      // Detección heurística de diálogos literarios para aplicar sangrías especiales
      const isDialogue = trimmedText.startsWith('—');

      return new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: {
          before: 0,
          after: 0,
          line: 480, // 480 line-spacing-twips = 2.0 (Espaciado Doble Estricto)
        },
        indent: {
          // Sangría de primera línea obligatoria en narrativa (1.25 cm = 708 twips)
          // Si es diálogo, se reduce ligeramente para mantener alineamiento estético con la raya
          firstLine: isDialogue ? 400 : 708,
        },
        children: [
          new TextRun({
            text: trimmedText,
            font: this.DEFAULT_FONT,
            size: this.DEFAULT_SIZE,
          }),
        ],
      });
    });

    // 3. Construcción del documento con su configuración geométrica de página (A4)
    const doc = new Document({
      sections: [{
        properties: {
          page: {
            size: {
              width: "210mm",
              height: "297mm",
            },
            margin: {
              top: "25mm",
              bottom: "25mm",
              left: "25mm",
              right: "25mm",
            },
          },
        },
        children: [
          // Título del borrador como Encabezado Estilizado
          new Paragraph({
            heading: HeadingLevel.HEADING_1,
            alignment: AlignmentType.CENTER,
            spacing: { after: 240 },
            children: [
              new TextRun({
                text: title.toUpperCase(),
                font: this.DEFAULT_FONT,
                size: 28, // 14pt
                bold: true,
              }),
            ],
          }),
          ...docxParagraphs,
        ],
      }],
    });

    // 4. Compilación del buffer binario y disparo de la descarga en el navegador
    try {
      const blob = await Packer.toBlob(doc);
      BrowserDownloadHelper.triggerDownload(blob, `${title.replace(/\s+/g, '_')}.docx`);
    } catch (err) {
      console.error('[DocxExportStrategy] Error al empaquetar DOCX:', err);
      throw err;
    }
  }
}
