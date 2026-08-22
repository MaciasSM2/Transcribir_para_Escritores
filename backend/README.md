# ⚙️ Gema Backend — Motor ASR, Estilometría y Asistente Literario

Servicio central de procesamiento para **Gema (Grabadora para Escritores)** construido sobre **FastAPI**, **Python 3.12+**, **spaCy**, **Vosk** y **Ollama**.

---

## 🚀 Capacidades del Backend

- **Ingesta y Transcripción de Audio**:
  - Procesador espectral con **FFmpeg** (16kHz mono, aislamiento vocal y Modo Susurro).
  - Reconocimiento de voz offline sin conexión mediante **Vosk ASR**.
  - Worker de fondo asíncrono con patrón *Async Request-Reply* (`202 Accepted` + Polling).
- **Motor Experto Zero-IA**:
  - Limpieza léxica determinista de muletillas y titubeos fonéticos.
  - Análisis de legibilidad **Fernández-Huerta** y riqueza léxica **TTR**.
  - Conteo silábico con **Pyphen** y segmentación con **Pysbd**.
  - Análisis morfosintáctico con **spaCy** (`es_core_news_sm`).
- **Inferencia Local LLM con Ollama**:
  - Adaptador asíncrono con control de concurrencia (`asyncio.Semaphore(1)`).
  - Enriquecimiento de prosa y preservación del ADN literario del autor.
- **Formateador Ortotípico RAE**:
  - Puntuación rigurosa de rayas de diálogo (`—`), incisos y verbos *dicendi*.
- **Control de Versiones y Bóveda**:
  - Bóveda de archivos planos (`local_history_vault/`).
  - Base de datos SQLite (`gema.db`) con **SQLAlchemy** y **Alembic**.
  - Comparador de diferencias de texto con **diff-match-patch**.

---

## 🛠️ Comandos de Desarrollo

```bash
# Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\activate      # En Windows
source venv/bin/activate    # En Linux/macOS

# Instalar dependencias
pip install -r requirements.txt
python -m spacy download es_core_news_sm

# Iniciar servidor FastAPI con hot-reload en http://localhost:8000
uvicorn main:app --reload --port 8000

# Ejecutar suite de pruebas (35 tests)
pytest -v
```

---

## 📁 Estructura del Backend

```
backend/
├── api/v1/
│   ├── endpoints/       # Controladores REST (audio, style, docs, tones, dna...)
│   ├── websocket/       # Streaming en tiempo real (stream.py, manager.py)
│   └── router.py        # Registro unificado de endpoints
├── services/
│   ├── analytics/       # Procesadores de métricas de estilo y gráficos
│   ├── audio/           # FFmpeg procesador y filtros
│   ├── export/          # Exportadores DOCX RAE
│   ├── history/         # Repositorios y snapshots de versiones
│   ├── infrastructure/  # Orquestador local, monitor de hardware
│   ├── nlp/             # spaCy, Ollama adapter, limpiador léxico, RAE formatter
│   └── transcription/   # Vosk worker y orquestador ASR
├── alembic/             # Migraciones de base de datos
├── database.py          # Configuración SQLAlchemy SQLite
├── models.py            # Modelos de datos
├── schemas.py           # Esquemas Pydantic
└── tests/               # Suite de tests unitarios e integrados
```
