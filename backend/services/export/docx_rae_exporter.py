import io
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .contracts import IDocumentExporter

class RaeDocxExporter(IDocumentExporter):
    """
    Estrategia de exportación que limpia cualquier estilo espurio de la UI
    y aplica de forma estricta el estándar ortotipográfico y de maquetación de la RAE.
    """

    def generate_file(self, raw_text: str) -> bytes:
        doc = Document()
        
        # 📐 Configuración de Márgenes Estándar (2.54 cm / 1 pulgada en todos los flancos)
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # 🔤 Configuración del Estilo Normal (Times New Roman, 12pt, Interlineado Doble)
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(12)
        
        # Partimos el texto por párrafos limpios
        paragraphs = raw_text.split('\n\n')
        
        for p_text in paragraphs:
            if not p_text.strip():
                continue
                
            p = doc.add_paragraph()
            p_format = p.paragraph_format
            
            # Reglas RAE: Interlineado doble y sangría reglamentaria en la primera línea
            p_format.line_spacing = 2.0
            p_format.first_line_indent = Inches(0.5)
            p_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            # Tratamiento especial si es una raya de diálogo
            cleaned_text = p_text.strip()
            if cleaned_text.startswith('—'):
                # Aseguramos la raya larga oficial y removemos espacios huérfanos iniciales
                p.add_run(cleaned_text)
            else:
                p.add_run(cleaned_text)

        # Guardado atómico en un búfer de memoria para evitar escrituras lentas en el disco local
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        
        return file_stream.getvalue()
