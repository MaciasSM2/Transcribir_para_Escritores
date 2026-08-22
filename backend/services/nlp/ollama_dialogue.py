# backend/services/nlp/ollama_dialogue.py
import httpx
import json
import logging
from typing import List
from .dialogue_contracts import IDialogueDetector, DialogueLine

logger = logging.getLogger("gema-dialogue-detector")

class OllamaDialogueDetector(IDialogueDetector):
    """Implementación concreta del detector de diálogos utilizando LLM Local en modo estructurado."""

    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.endpoint = f"{base_url}/api/generate"
        self.model_name = model_name

    async def extract_dialogue_structure(self, raw_text: str) -> List[DialogueLine]:
        system_prompt = (
            "Actúas como un transcriptor literario experto en análisis de guiones y narrativa.\n"
            "Tu tarea es analizar un texto plano proveniente de un dictado continuo que contiene una conversación "
            "e identificar los cambios de interlocutor y las acotaciones del narrador.\n"
            "Debes estructurar el resultado estrictamente en un arreglo JSON de objetos con el siguiente formato:\n"
            "[\n"
            "  {\n"
            "    \"character\": \"Nombre del personaje o 'Narrador'\",\n"
            "    \"speech\": \"Lo que dice el personaje exactamente, vacío si es solo narración\",\n"
            "    \"inciso\": \"La acotación o pensamiento del narrador si existe\",\n"
            "    \"is_action_only\": true/false (true si el inciso NO usa verbos de habla como dijo, exclamó, preguntó)\n"
            "  }\n"
            "]\n"
            "REGLAS CRÍTICAS:\n"
            "1. No inventes diálogos ni personajes. Cíñete al texto provisto.\n"
            "2. Separa las ideas de forma secuencial tal como ocurren en el flujo de habla."
        )

        payload = {
            "model": self.model_name,
            "prompt": raw_text,
            "system": system_prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1} # Alta fidelidad y baja variabilidad
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.endpoint, json=payload, timeout=45.0)
                if response.status_code == 200:
                    raw_response = response.json().get("response", "[]")
                    parsed_data = json.loads(raw_response)
                    return [DialogueLine(**line) for line in parsed_data]
                return []
        except Exception as e:
            logger.error(f"Fallo en la inferencia estructural de diálogos: {str(e)}")
            return []
