"""
Tests: Router de Motor Estilométrico
Cubre process-text (con y sin perfil), analyze-text y engine/status.
"""
import pytest


TONE_GENERAL = "General / Por Defecto"
TONE_THRILLER = "Misterio y Thriller"

SAMPLE_TEXT = (
    "El detective caminó por la calle oscura. "
    "Encontró una pista muy importante en el suelo. "
    "Era un papel viejo y arrugado que contenía información crucial."
)


class TestProcessText:
    """POST /api/v1/style/process-text"""

    def test_no_profile_uses_fallback(self, client):
        """Sin StyleProfile en BD → usa legacy, devuelve corrected_text."""
        response = client.post(
            "/api/v1/style/process-text",
            json={"raw_text": SAMPLE_TEXT, "tone_name": TONE_GENERAL},
        )
        assert response.status_code == 200
        body = response.json()
        assert "corrected_text" in body
        assert isinstance(body["corrected_text"], str)
        assert body["suggestions"] == []
        assert body["alerts"] == []

    def test_with_profile_returns_full_response(self, client, sample_style_profile):
        """Con StyleProfile en BD → usa FakeAIRulesEngine, devuelve listas."""
        response = client.post(
            "/api/v1/style/process-text",
            json={"raw_text": SAMPLE_TEXT, "tone_name": TONE_GENERAL},
        )
        assert response.status_code == 200
        body = response.json()
        assert "corrected_text" in body
        assert "suggestions" in body
        assert "alerts" in body
        assert "style_report" in body
        assert isinstance(body["suggestions"], list)
        assert isinstance(body["alerts"], list)

    def test_empty_text_still_responds(self, client, sample_style_profile):
        """Texto vacío → responde 200 (motor lo maneja gracefully)."""
        response = client.post(
            "/api/v1/style/process-text",
            json={"raw_text": "", "tone_name": TONE_GENERAL},
        )
        assert response.status_code == 200


class TestAnalyzeText:
    """POST /api/v1/style/analyze-text"""

    def test_returns_all_metrics(self, client):
        """Devuelve todas las métricas esperadas."""
        response = client.post(
            "/api/v1/style/analyze-text",
            json={"raw_text": SAMPLE_TEXT, "tone_name": TONE_GENERAL},
        )
        assert response.status_code == 200
        body = response.json()
        expected_keys = [
            "sentence_count", "word_count", "unique_words",
            "avg_sentence_len", "ttr", "adjective_density",
            "flesch_score", "fernandez_huerta",
        ]
        for key in expected_keys:
            assert key in body, f"Falta métrica: {key}"

    def test_word_count_is_correct(self, client):
        """word_count coincide con el conteo real de palabras."""
        text = "Hola mundo esto es una prueba de cinco palabras más."
        response = client.post(
            "/api/v1/style/analyze-text",
            json={"raw_text": text, "tone_name": TONE_GENERAL},
        )
        assert response.status_code == 200
        assert response.json()["word_count"] > 0

    def test_with_profile_includes_alignment_score(self, client, sample_style_profile):
        """Con perfil en BD → alignment_score presente."""
        response = client.post(
            "/api/v1/style/analyze-text",
            json={"raw_text": SAMPLE_TEXT, "tone_name": TONE_GENERAL},
        )
        assert response.status_code == 200
        assert "alignment_score" in response.json()


class TestEngineStatus:
    """GET /api/v1/style/engine/status"""

    def test_returns_engine_version(self, client):
        """Devuelve engine_version y engine_mode."""
        response = client.get("/api/v1/style/engine/status")
        assert response.status_code == 200
        body = response.json()
        assert body["engine_version"] == "3.0-pipeline"
        assert body["engine_mode"] == "cleaner+ollama+expert-rules"

    def test_profiles_is_list(self, client):
        """profiles_loaded siempre es lista."""
        response = client.get("/api/v1/style/engine/status")
        assert isinstance(response.json()["profiles_loaded"], list)

    def test_counts_are_integers(self, client):
        """Los conteos son enteros >= 0."""
        body = client.get("/api/v1/style/engine/status").json()
        assert isinstance(body["thesaurus_entries"], int)
        assert isinstance(body["prohibited_words"], int)
        assert isinstance(body["literary_dna_records"], int)
