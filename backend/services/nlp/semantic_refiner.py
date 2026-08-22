import httpx
import json
import logging

logger = logging.getLogger("gema-semantic-refiner")

class SemanticRefiner:
    """
    Filtro profundo que utiliza el modelo del lenguaje local para disolver
    marcadores discursivos complejos y reestructurar el habla desorganizada en prosa fluida.
    """

    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.endpoint = f"{base_url}/api/generate"
        self.model_name = model_name

    async def clean_deep(self, text: str, tone_name: str) -> str:
        """
        Realiza la inferencia local para reestructurar la sintaxis conversacional.
        """
        system_prompt = (
            "Actúas como un transcriptor y editor literario de alta gama.\n"
            "Tu misión es tomar un texto que proviene de un dictado por voz y limpiarlo de marcadores "
            "discursivos vacíos (como 'bueno', 'pues', 'o sea', 'entonces', 'digamos') que no aportan "
            "información al desarrollo narrativo.\n"
            "REGLAS DE OPERACIÓN:\n"
            "1. No alteres las palabras clave, los nombres propios ni el argumento del texto.\n"
            "2. Elimina el habla desorganizada y las ideas redundantes causadas por pensar en voz alta.\n"
            "3. Corrige la sintaxis y añade la puntuación correcta (puntos y comas lógicos).\n"
            "4. Devuelve ÚNICAMENTE el texto limpio, sin notas de autor, sin introducciones ni comentarios.\n"
            f"5. Ajusta sutilmente la estructura para que se adapte al estilo: {tone_name}."
        )

        payload = {
            "model": self.model_name,
            "prompt": text,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3  # Determinismo bajo para evitar alterar la voz original del autor
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.endpoint, json=payload, timeout=45.0)
                if response.status_code == 200:
                    return response.json().get("response", text).strip()
                return text
        except Exception as e:
            logger.error(f"Fallo en la inferencia semántica de limpieza: {str(e)}")
            return text
