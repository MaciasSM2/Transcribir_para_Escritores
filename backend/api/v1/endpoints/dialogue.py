# backend/api/v1/endpoints/dialogue.py
from fastapi import APIRouter, HTTPException
from services.nlp.dialogue_contracts import DialogueSceneResponse
from services.nlp.ollama_dialogue import OllamaDialogueDetector
from services.nlp.dialogue_formatter import RaeDialogueFormatter
import schemas

router = APIRouter()

# Inyección de dependencias estructurada
detector = OllamaDialogueDetector(model_name="llama3")
formatter = RaeDialogueFormatter()

@router.post("/parse-scene", response_model=DialogueSceneResponse, status_code=200)
async def parse_conversational_scene(request: schemas.ProcessTextRequest):
    """
    Endpoint encargado de tomar un bloque de dictado continuo conversacional,
    extraer su semántica dramática y formatearlo bajo las estrictas reglas de la RAE.
    """
    if not request.raw_text.strip():
        raise HTTPException(status_code=400, detail="El texto provisto está vacío.")

    # 1. Inferencia semántica para segmentar interlocutores
    structured_lines = await detector.extract_dialogue_structure(request.raw_text)
    
    if not structured_lines:
        raise HTTPException(status_code=500, detail="Fallo interno al procesar la estructura dramática.")

    # 2. Aplicación de la estrategia tipográfica RAE
    formatted_prose = formatter.format_scene(structured_lines)

    return DialogueSceneResponse(
        formatted_prose=formatted_prose,
        lines=structured_lines
    )
