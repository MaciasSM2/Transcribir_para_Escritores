from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import StreamingResponse
import io

from services.export.metadata_extractor import ManuscriptMetadataExtractor
from services.export.docx_rae_exporter import RaeDocxExporter
import schemas

router = APIRouter()

# Inyección de dependencias acoplada a las implementaciones concretas de la estrategia
extractor = ManuscriptMetadataExtractor()
exporter = RaeDocxExporter()

@router.post("/manuscript/analytics", status_code=200)
def get_manuscript_analytics(request: schemas.ProcessTextRequest):
    """Endpoint de telemetría literaria para poblar el Dashboard de Metadatos del Panel 3."""
    try:
        metadata = extractor.extract_metrics(request.raw_text)
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al analizar el manuscrito: {str(e)}")

@router.post("/manuscript/export/rae")
def export_manuscript_to_docx(request: schemas.ProcessTextRequest):
    """Genera y descarga el archivo .docx formateado de forma limpia según la norma RAE."""
    try:
        binary_data = exporter.generate_file(request.raw_text)
        
        # Retornamos el flujo binario nativo forzando la descarga en el cliente Windows 11
        return StreamingResponse(
            io.BytesIO(binary_data),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=manuscrito_rae.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo crítico en la compilación del documento: {str(e)}")
