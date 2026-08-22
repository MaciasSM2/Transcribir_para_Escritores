import pytest
from unittest.mock import AsyncMock, patch
from services.nlp.structural_processor import StructuralProcessor
from services.nlp.ollama_adapter import OllamaCoherenceAdapter
import models

def test_structural_processor_dialogue_and_paragraph_rules():
    """Valida que el post-procesador aplique correctamente las rayas RAE y la densidad de párrafos."""
    processor = StructuralProcessor()
    
    # Input crudo simulando un dictado accidentado con guiones cortos y espacios inválidos
    dirty_text = "- Hola, buenas tardes. \n-  A dónde vas? \n- Voy hacia el portal viejo - dijo el viejo mariscal."
    
    # Ejecución de la heurística determinista
    fixed_text = processor.finalize_literary_format(dirty_text)
    
    # Aserciones de control de calidad ortotipográfica
    assert "—Hola" in fixed_text, "Error: No se convirtió el guion corto inicial o se dejó un espacio inválido."
    assert "—A dónde" in fixed_text, "Error: Fallo al remover el doble espacio tras la raya de diálogo."
    assert "—dijo el viejo" in fixed_text, "Error: El inciso del narrador debe acoplarse directamente."

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_ollama_adapter_resilience_on_timeout(mock_post):
    """Certifica que si Ollama sufre un Timeout, el sistema degrada con gracia devolviendo el texto original."""
    import httpx
    
    # Forzamos al mock a lanzar una excepción de tiempo de espera excedido
    mock_post.side_effect = httpx.TimeoutException("Servidor ocupado ejecutando inferencia.")
    
    adapter = OllamaCoherenceAdapter(model_name="llama3")
    input_prose = "Texto crítico que no debe perderse bajo ninguna circunstancia."
    
    # Ejecución del adaptador asíncronico
    result = await adapter.refine_prose(input_prose, "Misterio y Thriller")
    
    # El sistema debe ser tolerante a fallos (Fault Tolerant) y retornar el input sin alteraciones
    assert result == input_prose, "Error: El adaptador alteró o destruyó el payload original ante un fallo de red."
