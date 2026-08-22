"""
Tests: Router de Tonos
Cubre guardado y lectura de tonos literarios.
"""


TONE_GENERAL = "General / Por Defecto"
TONE_SCIFI = "Narrativa de Ciencia Ficción y Fantasía Épica"


class TestTones:
    """POST y GET /api/tones"""

    def test_get_tones_empty_returns_dict(self, client):
        """BD vacía → dict vacío."""
        response = client.get("/api/v1/tones")
        assert response.status_code == 200
        assert response.json() == {}

    def test_save_tone_creates_entry(self, client):
        """POST → 200 + tone_name."""
        response = client.post(
            "/api/v1/tones",
            json={"tone_name": TONE_GENERAL, "reference_text": "Texto de referencia para el tono general."},
        )
        assert response.status_code == 200
        assert response.json()["tone_name"] == TONE_GENERAL

    def test_get_tones_after_save(self, client):
        """Tras guardar un tono → GET lo devuelve."""
        ref_text = "Prosa directa, sin adornos, al grano."
        client.post(
            "/api/v1/tones",
            json={"tone_name": TONE_GENERAL, "reference_text": ref_text},
        )
        response = client.get("/api/v1/tones")
        assert response.status_code == 200
        body = response.json()
        assert TONE_GENERAL in body
        assert body[TONE_GENERAL] == ref_text

    def test_save_tone_updates_existing(self, client):
        """Guardar el mismo tono dos veces → actualiza, no duplica."""
        client.post(
            "/api/v1/tones",
            json={"tone_name": TONE_GENERAL, "reference_text": "Primera versión."},
        )
        client.post(
            "/api/v1/tones",
            json={"tone_name": TONE_GENERAL, "reference_text": "Segunda versión actualizada."},
        )
        response = client.get("/api/v1/tones")
        body = response.json()
        # Solo debe haber una entrada para este tono
        assert body[TONE_GENERAL] == "Segunda versión actualizada."
        assert list(body.keys()).count(TONE_GENERAL) == 1

    def test_save_multiple_tones(self, client):
        """Múltiples tonos distintos coexisten."""
        client.post("/api/v1/tones", json={"tone_name": TONE_GENERAL, "reference_text": "General."})
        client.post("/api/v1/tones", json={"tone_name": TONE_SCIFI, "reference_text": "Ciencia ficción."})

        response = client.get("/api/v1/tones")
        body = response.json()
        assert TONE_GENERAL in body
        assert TONE_SCIFI in body
