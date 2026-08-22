// Declaración de tipos para html-to-docx (no tiene @types en npm)
declare module 'html-to-docx' {
  interface DocxOptions {
    table?: { row?: { cantSplit?: boolean } };
    footer?: boolean;
    pageNumber?: boolean;
    title?: string;
    subject?: string;
    creator?: string;
    margins?: {
      top?: number;
      right?: number;
      bottom?: number;
      left?: number;
      header?: number;
      footer?: number;
      gutter?: number;
    };
  }

  function HTMLtoDOCX(
    htmlString: string,
    headerHTMLString: string | null,
    options?: DocxOptions,
    footerHTMLString?: string | null
  ): Promise<Buffer>;

  export default HTMLtoDOCX;
}
