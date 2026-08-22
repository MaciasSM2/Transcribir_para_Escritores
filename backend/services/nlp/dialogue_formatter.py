# backend/services/nlp/dialogue_formatter.py
from typing import List
from .dialogue_contracts import DialogueLine

class RaeDialogueFormatter:
    """
    Estrategia encargada de aplicar las directrices ortotípicas complejas de la RAE 
    para la inserción de rayas de diálogo (—), espaciados e incisos.
    """

    @staticmethod
    def _is_verbo_dicendi(text: str) -> bool:
        """Determina heurísticamente si el inciso inicia con un verbo de habla."""
        # Diccionario optimizado O(1) de verbos dicendi comunes en español
        dicendi_verbs = {
            "dijo", "respondió", "replicó", "exclamó", "preguntó", 
            "añadió", "comentó", "susurró", "murmuró", "asintió"
        }
        if not text:
            return False
        first_word = text.strip().split()[0].lower().replace(",", "").replace(".", "")
        return first_word in dicendi_verbs

    def format_scene(self, lines: List[DialogueLine]) -> str:
        """
        Toma las líneas estructuradas y construye la prosa con la puntuación inmaculada de la RAE.
        """
        prose_blocks = []

        for line in lines:
            if line.character == "Narrador" or not line.speech:
                # Si es pura narración, se añade como párrafo ordinario
                prose_blocks.append(f"{line.speech or line.inciso}\n\n")
                continue

            # Construcción del núcleo del diálogo
            rendered_line = f"—{line.speech.strip()}"

            if line.inciso:
                inciso_text = line.inciso.strip()
                has_dicendi = self._is_verbo_dicendi(inciso_text) or not line.is_action_only

                if has_dicendi:
                    # RAE Rule: Si el inciso comienza con verbo dicendi, va en minúscula
                    # y el punto de la oración de habla se traslada al final del inciso.
                    inciso_clean = inciso_text[0].lower() + inciso_text[1:]
                    rendered_line += f" —{inciso_clean}."
                else:
                    # RAE Rule: Si es acción pura, el texto de habla cierra con punto,
                    # y el inciso inicia en mayúscula independiente.
                    rendered_line += f". —{inciso_text}."
            else:
                # Si no hay inciso, simplemente cerramos la intervención con su punto final
                rendered_line += "."

            prose_blocks.append(f"{rendered_line}\n\n")

        return "".join(prose_blocks).strip()
