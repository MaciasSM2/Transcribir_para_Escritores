"""
Tests: Router de Transcripción
Cubre validaciones, respuesta 202, y polling de estado.
Los tests reales de Vosk/FFmpeg se marcan como @pytest.mark.slow.
"""
import io
import pytest


class TestTranscribeValidation:
    """Validaciones de entrada: MIME y extensión."""

    def test_invalid_mime_returns_400(self, client):
        """Archivo con MIME no-audio → 400."""
        fake_file = io.BytesIO(b"not audio data")
        response = client.post(
            "/api/v1/audio/upload",
            files={"file": ("test.wav", fake_file, "text/plain")},
        )
        assert response.status_code == 400
        assert "MIME" in response.json()["detail"]

    def test_invalid_extension_returns_400(self, client):
        """Archivo con extensión no permitida → 400."""
        fake_file = io.BytesIO(b"fake audio")
        response = client.post(
            "/api/v1/audio/upload",
            files={"file": ("malicious.exe", fake_file, "audio/wav")},
        )
        assert response.status_code == 400
        assert "Extensión" in response.json()["detail"]

    def test_valid_audio_returns_202(self, client):
        """Archivo .wav con MIME correcto → 202 + job_id."""
        fake_wav = io.BytesIO(b"\x00" * 100)
        response = client.post(
            "/api/v1/audio/upload",
            files={"file": ("test.wav", fake_wav, "audio/wav")},
        )
        assert response.status_code == 202
        body = response.json()
        assert "job_id" in body
        assert body["status"] == "pending"

    def test_valid_mp3_returns_202(self, client):
        """Archivo .mp3 → 202."""
        fake_mp3 = io.BytesIO(b"\xFF\xFB" * 50)
        response = client.post(
            "/api/v1/audio/upload",
            files={"file": ("audio.mp3", fake_mp3, "audio/mpeg")},
        )
        assert response.status_code == 202


class TestTranscribePolling:
    """Polling del estado de un job."""

    def test_polling_pending_job(self, client):
        """Job recién creado → status pending."""
        fake_wav = io.BytesIO(b"\x00" * 100)
        create_resp = client.post(
            "/api/v1/audio/upload",
            files={"file": ("test.wav", fake_wav, "audio/wav")},
        )
        job_id = create_resp.json()["job_id"]

        poll_resp = client.get(f"/api/v1/audio/status/{job_id}")
        assert poll_resp.status_code == 200
        body = poll_resp.json()
        assert body["job_id"] == job_id
        assert body["status"] in ("pending", "completed", "error")

    def test_polling_unknown_job_returns_404(self, client):
        """Job inexistente → 404."""
        response = client.get("/api/v1/audio/status/non-existent-uuid")
        assert response.status_code == 404
