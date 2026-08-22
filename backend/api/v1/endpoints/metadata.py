# backend/api/v1/endpoints/metadata.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import schemas
from services.nlp.metadata_engine import OllamaMetadataEngine

router = APIRouter()

# Inyección del motor concreto bajo la abstracción del protocolo
metadata_provider = OllamaMetadataEngine(model_name="llama3")

@router.post("/generate", response_model=schemas.BookMetadataResponse, status_code=200)
async def generate_book_datasheet(request: schemas.MetadataGenerationRequest):
    """
    Analiza de forma integral el manuscrito provisto para compilar la ficha técnica,
    identificando tropos literarios, público objetivo y construyendo la sinopsis.
    """
    if len(request.text.strip()) < 100:
        raise HTTPException(
            status_code=400, 
            detail="El volumen de texto es insuficiente para realizar una extracción semántica precisa."
        )
        
    features = await metadata_provider.extract_semantic_features(
        text=request.text, 
        tone_context=request.tone_name
    )
    
    return features
