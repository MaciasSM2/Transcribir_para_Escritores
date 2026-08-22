import { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel } from 'docx';
import { IDocumentExporter } from './IDocumentExporter';
import { BrowserDownloadHelper } from './BrowserDownloadHelper';

export class DocxEditorialExportStrategy implements IDocumentExporter {
  private readonly DEFAULT_FONT = 'Times New Roman';
  private readonly DEFAULT_SIZE = 24;

  public async export(htmlContent: string, title: string = 'Gema_Documento_Editorial'): Promise<void> {
    if (!htmlContent) throw new Error('No hay contenido para exportar.');

    // 1. Convert HTML to plain text paragraphs
    const parser = new DOMParser();
    const docHtml = parser.parseFromString(htmlContent, 'text/html');
    const rawParagraphs: string[] = [];
    docHtml.body.childNodes.forEach((node) => {
      if (node.textContent && node.textContent.trim().length > 0) {
        rawParagraphs.push(node.textContent.trim());
      }
    });

    const docxParagraphs = rawParagraphs.map((pText) => {
      const isDialogue = pText.startsWith('—') || pText.startsWith('-');
      return new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: {
          before: 0,
          after: 0,
          line: 480, // Double spacing
        },
        indent: {
          firstLine: isDialogue ? 400 : 708,
        },
        children: [
          new TextRun({
            text: pText,
            font: this.DEFAULT_FONT,
            size: this.DEFAULT_SIZE,
          }),
        ],
      });
    });

    const doc = new Document({
      sections: [{
        properties: {
          page: {
            size: { width: "210mm", height: "297mm" },
            margin: { top: "25mm", bottom: "25mm", left: "25mm", right: "25mm" },
          },
        },
        children: [
          new Paragraph({
            heading: HeadingLevel.HEADING_1,
            alignment: AlignmentType.CENTER,
            spacing: { after: 240 },
            children: [
              new TextRun({ text: title.toUpperCase(), font: this.DEFAULT_FONT, size: 28, bold: true }),
            ],
          }),
          ...docxParagraphs,
        ],
      }],
    });

    try {
      const blob = await Packer.toBlob(doc);
      BrowserDownloadHelper.triggerDownload(blob, `${title.replace(/\s+/g, '_')}.docx`);
    } catch (err) {
      console.error('[DocxEditorialExportStrategy] Error:', err);
      throw err;
    }
  }
}
