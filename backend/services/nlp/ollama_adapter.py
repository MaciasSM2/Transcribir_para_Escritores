import httpx
import logging
import asyncio
from services.nlp.structural_processor import StructuralProcessor

logger = logging.getLogger("gema-ollama")

class OllamaCoherenceAdapter:
    """Adaptador asíncronico para inyectar coherencia sintáctica mediante LLMs locales."""
    _semaphore = asyncio.Semaphore(1)

    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.endpoint = f"{base_url}/api/generate"
        self.model_name = model_name
        self.spacy_processor = StructuralProcessor()

    async def refine_prose(self, raw_text: str, tone_context: str = "Tono neutral", format_type: str = "narrative", context: list = None) -> str:
        """
        Envía el texto transcrito (raw_text) a Ollama local para mejorar la coherencia
        y aplicar el tono indicado.
        Retorna el texto mejorado. Si Ollama no está disponible, retorna el texto original.
        """
        if not self.is_available():
            logger.warning("Ollama no está disponible. Retornando texto original.")
            return raw_text

        # 1. Pre-procesamiento Estructural (Párrafos y formato base)
        pre_processed_text = self.spacy_processor.format_document(raw_text)

        context_str = "\n".join(context) if context else "No hay contexto previo."

        # Prompt optimizado para Estructura, Narración y Memoria
        prompt = f"""
Actúa como un corrector de estilo de una editorial de prestigio con memoria fotográfica. 
Tu tarea es transformar el dictado en una obra literaria profesional con formato de {format_type}.

CONTEXTO ANTERIOR (Para mantener consistencia de trama y personajes):
{context_str}

INSTRUCCIONES DE DIÁLOGO (CRÍTICO):
1. Cada vez que detectes que alguien habla, empieza un nuevo párrafo con una raya de diálogo (—). No uses comillas (").
2. Si hay una interrupción del narrador (ej: dijo Juan), usa rayas de inciso: —Hola —dijo Juan—. ¿Cómo estás?
3. Si el inciso usa un verbo de habla (dijo, respondió), empieza en minúscula.
4. Asegúrate de que los puntos y comas queden fuera de los incisos según la RAE.

ESTRUCTURA NARRATIVA Y MEMORIA:
1. Divide el texto en párrafos con doble salto de línea.
2. Elimina muletillas y ruidos del audio.
3. El tono debe ser: {tone_context}.
4. Si el texto actual contradice el contexto (ej. cambia el nombre de un personaje), prioriza el contexto anterior.
5. Asegura que el estilo narrativo fluya desde el párrafo anterior.

TEXTO DICTADO A CORREGIR:
{pre_processed_text}
"""

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }

        try:
            # Uso de cliente HTTP asíncronico para no congelar el Event Loop de FastAPI
            async with self._semaphore:
                logger.info("Iniciando inferencia en Ollama (Bloqueo de Semáforo activo)")
                async with httpx.AsyncClient() as client:
                    response = await client.post(self.endpoint, json=payload, timeout=45.0)
                    
                    if response.status_code == 200:
                        refined_text = response.json().get("response", raw_text)
                        refined_text = refined_text.strip()
                        
                        # Refuerzo estructural (Párrafos y Rayas)
                        if format_type == "novel":
                            refined_text = self.spacy_processor.finalize_literary_format(refined_text)
                            
                        return refined_text
                    
                    logger.warning(f"Ollama retornó código inválido: {response.status_code}")
                    return raw_text
        except httpx.TimeoutException:
            logger.error("Timeout excedido al consultar el servidor local de Ollama.")
            return raw_text
        except Exception as e:
            logger.error(f"Fallo en la comunicación con Ollama: {str(e)}")
            return raw_text

    async def refine_prose_with_dna(self, raw_text: str, dna_metrics: dict) -> str:
        prompt = f"""
        Eres el 'Gemelo Literario' del autor. Tu objetivo es corregir el dictado manteniendo su ADN único.
        
        PARÁMETROS DE ESTILO DEL AUTOR:
        - Longitud de frase: {dna_metrics.get('avg_sentence_length', 0)} palabras.
        - Densidad de adjetivos: {dna_metrics.get('adjective_density', 0)}.
        - Palabras preferidas: {", ".join(dna_metrics.get('frequent_connectors', []))}.
        
        INSTRUCCIONES:
        1. Si el autor prefiere frases cortas, no las unas.
        2. Mantén su nivel de riqueza léxica ({dna_metrics.get('lexical_richness', 0)}).
        3. Corrige puntuación y sintaxis sin alterar su 'voz'.
        
        TEXTO:
        {raw_text}
        """
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }

        try:
            async with self._semaphore:
                logger.info("Iniciando inferencia DNA en Ollama (Bloqueo de Semáforo activo)")
                async with httpx.AsyncClient() as client:
                    response = await client.post(self.endpoint, json=payload, timeout=45.0)
                    if response.status_code == 200:
                        refined_text = response.json().get("response", raw_text)
                        return refined_text.strip()
                    logger.warning(f"Ollama retornó código inválido (DNA): {response.status_code}")
                    return raw_text
        except Exception as e:
            logger.error(f"Fallo en la comunicación con Ollama (DNA): {str(e)}")
            return raw_text

    def is_available(self) -> bool:
        """Comprueba de forma síncrona/asíncrona si Ollama está disponible. Útil para health check."""
        try:
            # Síncrono por simplicidad en endpoints de estado
            with httpx.Client(timeout=3.0) as client:
                r = client.get(self.endpoint.replace("/api/generate", "/api/tags"))
                return r.status_code == 200
        except Exception:
            return False
