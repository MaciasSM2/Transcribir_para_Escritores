import spacy
from collections import Counter

class StylometryEngine:
    def __init__(self):
        # Asegurarse de que el modelo esté instalado (ej. python -m spacy download es_core_news_sm)
        self.nlp = spacy.load("es_core_news_sm")

    def extract_dna(self, text: str) -> dict:
        doc = self.nlp(text)
        sentences = list(doc.sents)
        
        # 1. Riqueza léxica (Type-Token Ratio)
        words = [token.text.lower() for token in doc if token.is_alpha]
        ttr = len(set(words)) / len(words) if words else 0
        
        # 2. Longitud media de oración
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # 3. Densidad de categorías gramaticales (POS)
        pos_counts = Counter([token.pos_ for token in doc])
        total_pos = sum(pos_counts.values()) if pos_counts else 1
        
        pos_ratios = {pos: count / total_pos for pos, count in pos_counts.items()}

        return {
            "lexical_richness": round(ttr, 3),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "adjective_density": round(pos_ratios.get("ADJ", 0), 3),
            "verb_density": round(pos_ratios.get("VERB", 0), 3),
            "frequent_connectors": [word for word, count in Counter(words).most_common(10) if len(word) > 4]
        }
