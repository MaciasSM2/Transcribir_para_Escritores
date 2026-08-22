import httpx
import json
import asyncio
import logging

logger = logging.getLogger("gema-backend")

class NarrativeAnalyzer:
    def __init__(self, model="llama3"):
        self.url = "http://localhost:11434/api/generate"
        self.model = model

    async def analyze_tension(self, text: str) -> list:
        # Dividimos el texto en fragmentos lógicos (párrafos)
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        
        async def analyze_chunk(i, p):
            prompt = f"""
            Analiza la tensión narrativa del siguiente fragmento. 
            Responde ÚNICAMENTE con un objeto JSON plano que tenga esta estructura:
            {{ "score": (1-10), "pacing": "lento/fluido/rapido", "suggestion": "breve consejo" }}
            
            FRAGMENTO: {p}
            """
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(self.url, json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json" # Forzamos salida JSON
                    }, timeout=30.0)
                    
                    data = json.loads(response.json().get("response", "{}"))
                    return {
                        "id": i,
                        "paragraph": p[:50] + "...",
                        "score": data.get("score", 5),
                        "pacing": data.get("pacing", "fluido"),
                        "suggestion": data.get("suggestion", "")
                    }
            except Exception as e:
                logger.error(f"[NarrativeAnalyzer] Error en chunk {i}: {e}")
                return {"id": i, "paragraph": p[:50] + "...", "score": 5, "pacing": "fluido", "suggestion": "Error de análisis"}

        tasks = [analyze_chunk(i, p) for i, p in enumerate(paragraphs)]
        report = await asyncio.gather(*tasks)
        
        # Sort by id to ensure order
        report.sort(key=lambda x: x["id"])
        return report
