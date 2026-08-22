# backend/api/v1/endpoints/dna.py
import json
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from services.nlp.stylometry_engine import StylometryEngine

router = APIRouter()
stylometry_engine = StylometryEngine()

@router.post("/train", status_code=200)
async def train_dna(
    sample_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Recibe un archivo de texto del usuario, extrae su ADN literario (estilometría),
    y lo guarda/actualiza en la base de datos para que Ollama pueda clonar su estilo.
    """
    if not sample_file.filename.endswith(('.txt', '.docx')):
        raise HTTPException(status_code=400, detail="El archivo debe ser .txt o .docx")
    
    # Por ahora sólo leemos TXT plano. En el futuro integrar mammoth para docx.
    try:
        content = await sample_file.read()
        text = content.decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error leyendo el archivo. Asegúrate de que sea texto plano utf-8.")
        
    if len(text.split()) < 100:
        raise HTTPException(status_code=400, detail="El texto es muy corto para extraer un ADN fiable. Mínimo 100 palabras.")
        
    # Extraer ADN
    metrics = stylometry_engine.extract_dna(text)
    
    # Buscar usuario actual (por ahora usaremos un default 'default_user')
    user_id = "default_user"
    user_dna = db.query(models.UserDNA).filter(models.UserDNA.user_id == user_id).first()
    
    if not user_dna:
        user_dna = models.UserDNA(user_id=user_id)
        db.add(user_dna)
        
    user_dna.metrics_json = json.dumps(metrics)
    db.commit()
    db.refresh(user_dna)
    
    return {"message": "ADN literario extraído y guardado con éxito.", "metrics": metrics}
