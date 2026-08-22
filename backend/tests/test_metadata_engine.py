# backend/tests/test_metadata_engine.py
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from services.nlp.metadata_engine import OllamaMetadataEngine

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_extract_semantic_features_happy_path(mock_post):
    """Certifica el procesamiento correcto del JSON nativo devuelto por Ollama y el cálculo de métricas."""
    
    # 1. Preparación del Payload simulado que emite el socket de Ollama
    mock_ollama_json = {
        "response": json.dumps({
            "synopsis": "En una estación espacial remota, un androide hereda la memoria de un escritor.",
            "target_audience": "Lectores de ciencia ficción dura y aficionados a la filosofía transhumanista.",
            "core_tropes": ["Inteligencia Artificial Despierta", "Aislamiento Espacial"],
            "keywords": ["Androide", "Estación Espacial", "Memoria"],
            "suggested_age_rating": "Adultos (18+)"
        })
    }
    
    # Configuración del mock de httpx para emular una respuesta HTTP 200 OK
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_ollama_json
    mock_post.return_value = mock_response

    # 2. Inicialización del motor bajo testeo
    engine = OllamaMetadataEngine(model_name="llama3")
    
    # Generamos un texto de longitud conocida para validar el algoritmo determinista de lectura (200 palabras)
    dummy_manuscript = " ".join(["palabra"] * 200)
    
    # 3. Ejecución del método bajo verificación
    result = await engine.extract_semantic_features(dummy_manuscript, "Ciencia Ficción")

    # 4. Aserciones de Integridad Estructural y Lógica
    assert "synopsis" in result
    assert result["suggested_age_rating"] == "Adultos (18+)"
    assert len(result["core_tropes"]) == 2
    # Verificación del cálculo determinista local: 200 palabras / 200 palabras por minuto = 1 minuto
    assert result["estimated_reading_time_minutes"] == 1
    mock_post.assert_called_once()

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_extract_semantic_features_resilience_on_malformed_json(mock_post):
    """Valida la resiliencia y el comportamiento del Graceful Degradation si la IA devuelve un JSON roto."""
    
    # Simulación de un JSON corrupto roto a mitad de la inferencia por falta de VRAM
    mock_corrupted_response = {
        "response": "{ \"synopsis\": \"Texto incompleto...",
    }
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_corrupted_response
    mock_post.return_value = mock_response

    engine = OllamaMetadataEngine(model_name="llama3")
    
    # Ejecución de la llamada (el bloque interno de try/except de json.loads debe activarse)
    result = await engine.extract_semantic_features("Texto de prueba genérico.", "General")
    
    # Aserción: El sistema debe degradar de forma segura activando los valores por defecto sin lanzar excepción HTTP 500
    assert "No se pudo generar la sinopsis automáticamente." in result["synopsis"]
    assert result["core_tropes"] == []
    assert result["estimated_reading_time_minutes"] == 1  # Sigue operando el cálculo base
