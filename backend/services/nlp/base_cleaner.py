import re
import logging

logger = logging.getLogger("gema-cleaner")

class TextCleaner:
    """Elimina muletillas y disfluencias comunes del español hablado."""

    FILLERS = [
        r'\behh+\b', r'\bmmm+\b', r'\bahh+\b', r'\buhh+\b',
        r'\bestee+\b', r'\beh\b', r'\bah\b', r'\buh\b',
        r'\bo sea\b', r'\bbueno\s*\.\.\.', r'\bpues\s*\.\.\.',
        r'\bdigamos\b', r'\bla verdad es que\b',
    ]

    _compiled = [re.compile(p, re.IGNORECASE) for p in FILLERS]

    def clean_disfluencies(self, text: str) -> str:
        if not text or not text.strip():
            return text

        cleaned = text
        for pattern in self._compiled:
            cleaned = pattern.sub('', cleaned)

        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        cleaned = re.sub(r'\s+([.,;:!?])', r'\1', cleaned)
        return cleaned.strip()
