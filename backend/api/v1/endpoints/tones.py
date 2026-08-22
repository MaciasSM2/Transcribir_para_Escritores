from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter()

@router.post("/", status_code=200)
def update_tone_settings(request: schemas.ToneRequest, db: Session = Depends(get_db)):
    """Actualiza o crea la referencia de estilo para un tono literario específico."""
    tone = db.query(models.ToneSettings).filter(models.ToneSettings.tone_name == request.tone_name).first()
    
    if tone:
        tone.reference_text = request.reference_text
    else:
        tone = models.ToneSettings(
            tone_name=request.tone_name, 
            reference_text=request.reference_text
        )
        db.add(tone)
    
    db.commit()
    return {"status": "ok", "updated": request.tone_name, "tone_name": request.tone_name}

@router.get("/")
def get_all_tones(db: Session = Depends(get_db)):
    """Obtiene el diccionario completo de referencias de estilo configuradas."""
    tones = db.query(models.ToneSettings).all()
    # Retornamos un mapeo nombre -> texto para fácil consumo en el frontend
    return {tone.tone_name: tone.reference_text for tone in tones}
