"""
Tests: Router de Historial
Cubre historial de jobs, guardado de documentos, listado y lectura.
"""
import pytest


TONE_GENERAL = "General / Por Defecto"


class TestJobHistory:
    """GET /api/v1/audio/jobs — historial de transcripciones."""

    def test_empty_history_returns_list(self, client):
        """BD vacía → lista vacía."""
        response = client.get("/api/v1/audio/jobs")
        assert response.status_code == 200
        assert response.json() == []

    def test_history_after_upload(self, client):
        """Tras un upload → historial tiene 1 item."""
        import io
        fake_wav = io.BytesIO(b"\x00" * 100)
        client.post(
            "/api/v1/audio/upload",
            files={"file": ("test.wav", fake_wav, "audio/wav")},
        )
        response = client.get("/api/v1/audio/jobs")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestDocumentHistory:
    """Operaciones sobre documentos guardados en el Vault."""

    SAMPLE_DOC = {
        "text": "Este es el contenido del documento de prueba. Suficientemente largo para ser procesado.",
        "tone_name": TONE_GENERAL,
        "title": "Test Document",
    }

    def test_save_document_returns_doc_id(self, client, tmp_path, monkeypatch):
        """POST /api/v1/docs/save → 201 + doc_id."""
        # Redirigir VAULT_DIR al directorio temporal del test
        import api.v1.endpoints.documents as history_router
        monkeypatch.setattr(history_router, "VAULT_DIR", str(tmp_path))

        response = client.post("/api/v1/docs/save", json=self.SAMPLE_DOC)
        assert response.status_code == 201
        body = response.json()
        assert "doc_id" in body
        assert body["status"] == "ok"

    def test_list_documents_returns_list(self, client, tmp_path, monkeypatch):
        """GET /api/v1/docs/list → lista de documentos."""
        import api.v1.endpoints.documents as history_router
        monkeypatch.setattr(history_router, "VAULT_DIR", str(tmp_path))

        client.post("/api/v1/docs/save", json=self.SAMPLE_DOC)
        response = client.get("/api/v1/docs/list")
        assert response.status_code == 200
        docs = response.json()
        assert len(docs) == 1
        assert docs[0]["title"] == "Test Document"

    def test_read_document_returns_text(self, client, tmp_path, monkeypatch):
        """GET /api/v1/docs/read/{id} → texto completo."""
        import api.v1.endpoints.documents as history_router
        monkeypatch.setattr(history_router, "VAULT_DIR", str(tmp_path))

        save_resp = client.post("/api/v1/docs/save", json=self.SAMPLE_DOC)
        doc_id = save_resp.json()["doc_id"]

        read_resp = client.get(f"/api/v1/docs/read/{doc_id}")
        assert read_resp.status_code == 200
        assert read_resp.json()["text"] == self.SAMPLE_DOC["text"]

    def test_read_nonexistent_document_returns_404(self, client):
        """Documento inexistente → 404."""
        response = client.get("/api/v1/docs/read/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
