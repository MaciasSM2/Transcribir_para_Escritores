import os
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas

router = APIRouter()

# Configuración de rutas (Ruta absoluta para evitar errores de CWD)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VAULT_DIR = os.path.join(BASE_DIR, "local_history_vault")
os.makedirs(VAULT_DIR, exist_ok=True)

@router.post("/save", status_code=201)
def save_document(request: schemas.SaveDocumentRequest, db: Session = Depends(get_db)):
    """Guarda un texto procesado en el vault físico y registra la entrada en DB."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_title = request.title if request.title else f"Documento_{timestamp}"
    
    # Sanitizar nombre de archivo
    safe_title = "".join(c for c in doc_title if c.isalnum() or c in (' ', '_')).rstrip()
    filename = f"{safe_title.replace(' ', '_')}_{timestamp}.txt"
    file_path = os.path.join(VAULT_DIR, filename)
    
    try:
        with open(file_path, mode="w", encoding="utf-8") as f:
            f.write(request.text)
            
        excerpt = request.text[:150] + "..." if len(request.text) > 150 else request.text
        
        db_doc = models.DocumentHistory(
            title=doc_title,
            file_path=file_path,
            excerpt=excerpt,
            tone_name=request.tone_name
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        return {"status": "ok", "doc_id": str(db_doc.id), "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al escribir en disco: {str(e)}")

@router.get("/list")
def list_documents(db: Session = Depends(get_db)):
    """Retorna el catálogo de documentos guardados en el historial."""
    docs = db.query(models.DocumentHistory).order_by(models.DocumentHistory.created_at.desc()).all()
    return [{
        "id": str(doc.id),
        "title": doc.title,
        "excerpt": doc.excerpt,
        "tone_name": doc.tone_name,
        "created_at": doc.created_at.isoformat()
    } for doc in docs]

@router.get("/read/{doc_id}")
def read_document(doc_id: str, db: Session = Depends(get_db)):
    """Recupera el contenido íntegro de un archivo desde el vault."""
    doc = db.query(models.DocumentHistory).filter(models.DocumentHistory.id == doc_id).first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Documento no encontrado en el sistema.")
        
    with open(doc.file_path, mode="r", encoding="utf-8") as f:
        content = f.read()
        
    return {"text": content, "title": doc.title}
