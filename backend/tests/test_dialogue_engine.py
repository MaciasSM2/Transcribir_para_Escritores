import pytest
from services.nlp.dialogue_contracts import DialogueLine
from services.nlp.dialogue_formatter import RaeDialogueFormatter

@pytest.fixture
def formatter():
    """Factory fixture para instanciar el formateador ortotípico RAE."""
    return RaeDialogueFormatter()

def test_format_scene_with_verbo_dicendi(formatter):
    """
    Certifica que si el inciso inicia con un verbo dicendi, se fuerce la minúscula
    y el punto de la oración se mueva al final del bloque del narrador.
    """
    lines = [
        DialogueLine(
            character="Juan",
            speech="Hola, ¿cómo estás?",
            inciso="Dijo Juan con una sonrisa",
            is_action_only=False
        )
    ]
    
    result = formatter.format_scene(lines)
    
    # RAE: El verbo 'dijo' debe bajar a minúscula y cerrar con punto final tras el inciso
    assert result == "—Hola, ¿cómo estás? —dijo Juan con una sonrisa."

def test_format_scene_with_action_only(formatter):
    """
    Certifica que si el inciso describe una acción física (no dicendi), la frase de habla
    cierre con punto, el inciso inicie con mayúscula y termine en su propio punto.
    """
    lines = [
        DialogueLine(
            character="María",
            speech="No quiero volver a verte",
            inciso="Se dio la vuelta abruptamente",
            is_action_only=True
        )
    ]
    
    result = formatter.format_scene(lines)
    
    # RAE: El habla cierra con punto antes de la raya, y la acción mantiene su mayúscula inicial
    assert result == "—No quiero volver a verte. —Se dio la vuelta abruptamente."

def test_format_narrator_only_block(formatter):
    """Valida que los bloques rotulados como narración pura no sufran mutaciones de rayas."""
    lines = [
        DialogueLine(
            character="Narrador",
            speech=None,
            inciso="El viento soplaba con fuerza sobre los páramos desolados.",
            is_action_only=False
        )
    ]
    
    result = formatter.format_scene(lines)
    assert result == "El viento soplaba con fuerza sobre los páramos desolados."
