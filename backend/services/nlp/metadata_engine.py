# backend/services/nlp/metadata_engine.py
import httpx
import json
import logging
from typing import List
from .interfaces import IMetadataProvider

logger = logging.getLogger("gema-metadata-engine")

class OllamaMetadataEngine(IMetadataProvider):
    """Motor especializado en extracción de metadatos mediante Ollama utilizando JSON estructurado."""

    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.endpoint = f"{base_url}/api/generate"
        self.model_name = model_name
        self.words_per_minute = 200  # Velocidad media de lectura estándar en español

    def _calculate_reading_time(self, text: str) -> int:
        """Cálculo determinista de velocidad de lectura."""
        word_count = len(text.split())
        minutes = max(1, round(word_count / self.words_per_minute))
        return minutes

    async def extract_semantic_features(self, text: str, tone_context: str) -> dict:
        # Prompt fuertemente estructurado para obligar al modelo a ceñirse al esquema
        system_prompt = (
            "Actúas como un Analista de Mercado Editorial y Editor Literario.\n"
            "Analiza el texto provisto y genera metadatos precisos en ESPAÑOL.\n"
            "Es obligatorio que respondas EXCLUSIVAMENTE con un objeto JSON válido que contenga las siguientes llaves:\n"
            "{\n"
            "  \"synopsis\": \"string largo de contraportada sin spoilers destripantes\",\n"
            "  \"target_audience\": \"definición clara del público lector objetivo\",\n"
            "  \"core_tropes\": [\"tropo1\", \"tropo2\", \"tropo3\"],\n"
            "  \"keywords\": [\"tag1\", \"tag2\", \"tag3\", \"tag4\", \"tag5\"],\n"
            "  \"suggested_age_rating\": \"clasificación de edad estimada\"\n"
            "}\n"
            "No incluyas texto fuera del objeto JSON."
        )

        payload = {
            "model": self.model_name,
            "prompt": f"CONTEXTO DE GÉNERO: {tone_context}\n\nTEXTO DEL MANUSCRITO:\n{text}",
            "system": system_prompt,
            "stream": False,
            "format": "json"  # Forzamos el modo JSON nativo de Ollama
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.endpoint, json=payload, timeout=60.0)
                
                if response.status_code == 200:
                    raw_response = response.json().get("response", "{}")
                    parsed_json = json.loads(raw_response)
                    
                    # Inyectamos la métrica determinista calculada localmente
                    parsed_json["estimated_reading_time_minutes"] = self._calculate_reading_time(text)
                    return parsed_json
                
                raise RuntimeError(f"Ollama respondió con código erróneo: {response.status_code}")
        except Exception as e:
            logger.error(f"Fallo crítico en el motor de metadatos: {str(e)}")
            # Fallback seguro en caso de error de hardware o de timeout
            return {
                "synopsis": "No se pudo generar la sinopsis automáticamente.",
                "target_audience": "No determinado.",
                "core_tropes": [],
                "keywords": [],
                "estimated_reading_time_minutes": self._calculate_reading_time(text),
                "suggested_age_rating": "No determinado"
            }
