import spacy
import re

class StructuralProcessor:
    def __init__(self):
        # Fallback a un modelo más ligero si es_core_news_sm no estuviera, pero ya lo descargamos.
        self.nlp = spacy.load("es_core_news_sm")

    def format_document(self, text: str) -> str:
        doc = self.nlp(text)
        formatted_text = ""
        sentence_count = 0
        
        for sent in doc.sents:
            formatted_text += sent.text.strip() + " "
            sentence_count += 1
            
            # Cada 3 o 4 oraciones, si el sentido es completo, forzamos un párrafo
            # Esto evita el efecto de "muro de texto"
            if sentence_count >= 4:
                formatted_text = formatted_text.strip() + "\n\n"
                sentence_count = 0
                
        return formatted_text.strip()

    def finalize_literary_format(self, text: str) -> str:
        # 1. Convertir guiones cortos accidentales al inicio de línea en rayas largas
        text = re.sub(r'^-\s*', '—', text, flags=re.MULTILINE)
        
        # 2. Asegurar espacio después de la raya inicial
        # Pero pegado a la palabra: —Hola (Correcto) vs — Hola (Incorrecto)
        text = re.sub(r'^—\s*', '—', text, flags=re.MULTILINE)
        
        # 3. Corregir puntuación común en incisos
        # Ejemplo: "—dijo él." -> " —dijo él." y guiones cortos espaciados
        text = text.replace(" —", "—")
        text = text.replace(" - ", "—")
        
        return text.strip()
