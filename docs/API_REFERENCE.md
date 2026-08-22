# 🔌 Referencia de API (REST & WebSocket) — Gema v2.0

Esta documentación describe todos los endpoints HTTP REST y la interfaz de streaming WebSocket expuestos por el backend de **Gema (FastAPI)**.

- **URL Base REST**: `http://localhost:8000/api/v1`
- **URL Base WebSocket**: `ws://localhost:8000/api/v1/stream/{client_id}`
- **Documentación Interactiva OpenAPI (Swagger)**: `http://localhost:8000/docs`
- **Documentación ReDoc**: `http://localhost:8000/redoc`

---

## 📑 Índice de Endpoints

- [1. Audio & Transcripción (`/audio`)](#1-audio--transcripción-audio)
- [2. Motor de Estilo & Estilometría (`/style`)](#2-motor-de-estilo--estilometría-style)
- [3. Gestión de Documentos & Bóveda (`/docs`)](#3-gestión-de-documentos--bóveda-docs)
- [4. Configuración de Tonos Literarios (`/tones`)](#4-configuración-de-tonos-literarios-tones)
- [5. ADN Literario Autoral (`/dna`)](#5-adn-literario-autoral-dna)
- [6. Formateo de Diálogos RAE (`/dialogue`)](#6-formateo-de-diálogos-rae-dialogue)
- [7. Historial & Diff Semántico (`/history`)](#7-historial--diff-semántico-history)
- [8. Salud del Hardware & Sistema (`/system`)](#8-salud-del-hardware--sistema-system)
- [9. Streaming en Tiempo Real (WebSocket)](#9-streaming-en-tiempo-real-websocket)

---

## 1. Audio & Transcripción (`/audio`)

### `POST /audio/upload`
Recibe un archivo de audio para procesamiento asíncrono en segundo plano (Patrón Async Request-Reply).

- **Content-Type**: `multipart/form-data`
- **Parámetros Form**:
  - `file`: Archivo binario de audio (`.wav`, `.mp3`, `.ogg`, `.m4a`, `.webm`, `.flac`, `.aac`).
  - `whisper_mode` *(opcional, bool)*: Activa el filtro espectral de realce para grabaciones a bajo volumen (default: `false`).
  - `tone_name` *(opcional, str)*: Perfil de estilo a aplicar (default: `"General / Por Defecto"`).
  - `format_type` *(opcional, str)*: Formato de salida (`"narrative"` o `"novel"`).
- **Código de Respuesta**: `202 Accepted`

```json
{
  "message": "Audio recibido y procesando en segundo plano.",
  "job_id": "8f31b8a5-d86b-4e8a-bf94-b2587da42e91",
  "status": "pending"
}
```

---

### `GET /audio/status/{job_id}`
Consulta el estado de procesamiento de un trabajo de transcripción.

- **Código de Respuesta**: `200 OK` (o `404 Not Found` si el `job_id` no existe).

```json
{
  "job_id": "8f31b8a5-d86b-4e8a-bf94-b2587da42e91",
  "status": "completed",
  "transcription": "—No hay nada más peligroso que un hombre sin nada que perder —dijo Philip Marlowe mientras encendía un cigarrillo."
}
```

---

### `GET /audio/jobs`
Retorna el historial completo de trabajos de audio procesados, ordenados del más reciente al más antiguo.

- **Código de Respuesta**: `200 OK`

```json
[
  {
    "id": "8f31b8a5-d86b-4e8a-bf94-b2587da42e91",
    "filename": "capitulo_1_escena_2.mp3",
    "transcription": "—Hola —dijo él.",
    "createdAt": "2026-05-29T14:32:00.000Z"
  }
]
```

---

## 2. Motor de Estilo & Estilometría (`/style`)

### `POST /style/process-text`
Ejecuta el pipeline de 3 capas (Limpieza Léxica $\to$ Coherencia Ollama $\to$ Análisis de Tensión) sobre un texto dictado.

- **Content-Type**: `application/json`
- **Body**:
```json
{
  "raw_text": "ehh bueno entonces juan dijo hola como estas y maria lo miro",
  "tone_name": "General / Por Defecto",
  "context": ["Capítulo anterior: Juan y María se encuentran en el parque."],
  "format_type": "novel"
}
```
- **Código de Respuesta**: `200 OK`
```json
{
  "corrected_text": "—Hola, ¿cómo estás? —dijo Juan.\n\nMaría lo miró fijamente sin responder.",
  "style_alerts": [],
  "tension_score": 0.65,
  "style_alignment_score": 0.88,
  "tone_name": "General / Por Defecto"
}
```

---

### `POST /style/analyze-text`
Calcula las métricas estilométricas computacionales puras sin modificar el contenido.

- **Body**:
```json
{
  "raw_text": "Texto completo del capítulo a evaluar...",
  "tone_name": "General / Por Defecto"
}
```
- **Código de Respuesta**: `200 OK`
```json
{
  "word_count": 1450,
  "sentence_count": 82,
  "avg_sentence_len": 17.68,
  "flesch_score": 68.4,
  "ttr_score": 0.62,
  "adjective_density": 0.14,
  "dialogue_ratio": 0.35,
  "style_alignment_score": 0.91
}
```

---

### `GET /style/engine/status`
Reporta la versión y estado operativo del motor estilométrico y los perfiles cargados.

- **Código de Respuesta**: `200 OK`
```json
{
  "engine_version": "2.0.0-ZeroIA",
  "engine_mode": "expert_system",
  "profiles_loaded": ["General / Por Defecto", "Noir", "Fantasía Épica", "Hemingway"],
  "profiles_count": 4
}
```

---

## 3. Gestión de Documentos & Bóveda (`/docs`)

### `POST /docs/save`
Persiste un documento procesado en el vault de disco físico y registra la entrada en SQLite.

- **Body**:
```json
{
  "title": "Capítulo 1: El Despertar",
  "text": "Contenido íntegro del capítulo...",
  "tone_name": "General / Por Defecto"
}
```
- **Código de Respuesta**: `201 Created`
```json
{
  "status": "ok",
  "doc_id": "3c91a7e2-18bc-418f-9df2-a984dfa60012",
  "file_path": ".../local_history_vault/Capitulo_1_20260529_143000.txt"
}
```

---

### `GET /docs/list`
Retorna el catálogo de documentos guardados en el historial.

- **Código de Respuesta**: `200 OK`
```json
[
  {
    "id": "3c91a7e2-18bc-418f-9df2-a984dfa60012",
    "title": "Capítulo 1: El Despertar",
    "excerpt": "Contenido inicial del capítulo...",
    "tone_name": "General / Por Defecto",
    "created_at": "2026-05-29T14:30:00"
  }
]
```

---

### `GET /docs/read/{doc_id}`
Recupera el texto completo de un documento almacenado en la bóveda.

- **Código de Respuesta**: `200 OK`
```json
{
  "title": "Capítulo 1: El Despertar",
  "text": "Contenido íntegro del capítulo..."
}
```

---

## 4. Configuración de Tonos Literarios (`/tones`)

### `GET /tones/`
Obtiene el catálogo de tonos literarios configurados con sus textos de referencia.

- **Código de Respuesta**: `200 OK`
```json
{
  "General / Por Defecto": "Texto de referencia base...",
  "Narrativa de Ciencia Ficción y Fantasía Épica": "Prosa rica y evocadora..."
}
```

---

### `POST /tones/`
Crea o actualiza la prosa de referencia para un tono literario.

- **Body**:
```json
{
  "tone_name": "Mi Estilo Personal",
  "reference_text": "Fragmento de prosa representativa del autor..."
}
```
- **Código de Respuesta**: `200 OK`
```json
{
  "status": "ok",
  "updated": "Mi Estilo Personal",
  "tone_name": "Mi Estilo Personal"
}
```

---

## 5. ADN Literario Autoral (`/dna`)

### `POST /dna/analyze-corpus`
Analiza un corpus de texto del autor y extrae sus métricas estilométricas canónicas.

- **Body**:
```json
{
  "corpus_text": "Texto extenso con varias páginas de la obra previa del autor...",
  "author_name": "Sebastian Macias"
}
```
- **Código de Respuesta**: `200 OK`
```json
{
  "status": "ok",
  "author_name": "Sebastian Macias",
  "metrics": {
    "avg_sentence_length": 16.4,
    "adjective_ratio": 0.12,
    "lexical_richness": 0.68,
    "dialogue_ratio": 0.42,
    "frequent_connectors": ["sin embargo", "no obstante", "mientras tanto"]
  }
}
```

---

## 6. Formateo de Diálogos RAE (`/dialogue`)

### `POST /dialogue/format-scene`
Transforma líneas de diálogo desestructuradas en prosa con formato ortotípico formal RAE.

- **Body**:
```json
{
  "lines": [
    {
      "character": "Juan",
      "speech": "Hola, ¿cómo estás?",
      "inciso": "Dijo Juan con una sonrisa",
      "is_action_only": false
    },
    {
      "character": "María",
      "speech": "No quiero volver a verte",
      "inciso": "Se dio la vuelta abruptamente",
      "is_action_only": true
    }
  ]
}
```
- **Código de Respuesta**: `200 OK`
```json
{
  "formatted_prose": "—Hola, ¿cómo estás? —dijo Juan con una sonrisa.\n\n—No quiero volver a verte. —Se dio la vuelta abruptamente.",
  "lines": [...]
}
```

---

## 7. Historial & Diff Semántico (`/history`)

### `GET /history/compare/{chapter_id}/{v_old}/{v_new}`
Compara dos versiones históricas de un capítulo mediante el algoritmo `diff-match-patch` y retorna el marcado HTML para visualización inmediata.

- **Código de Respuesta**: `200 OK`
```json
{
  "diff_html": "<span>Texto sin cambios </span><del style=\"background:#ffe6e6;\">palabra eliminada</del><ins style=\"background:#e6ffe6;\">palabra añadida</ins><span> resto del párrafo.</span>"
}
```

---

## 8. Salud del Hardware & Sistema (`/system`)

### `GET /system/health/hardware`
Reporta métricas de carga del host (CPU, memoria física y disponibilidad de GPU).

- **Código de Respuesta**: `200 OK`
```json
{
  "cpu_usage_percent": 18.5,
  "ram_usage_percent": 52.1,
  "ram_available_gb": 7.68,
  "healthy": true
}
```

---

### `GET /system/status`
Informa el estado de disponibilidad de los subsistemas locales (FFmpeg, Vosk y Ollama).

- **Código de Respuesta**: `200 OK`
```json
{
  "ffmpeg": true,
  "vosk_model": true,
  "ollama": true,
  "system_ready": true
}
```

---

## 9. Streaming en Tiempo Real (WebSocket)

### `WS /api/v1/stream/{client_id}`
Permite la transmisión bidireccional continua de fragmentos de audio PCM o texto para transcripción en vivo con latencia mínima.

- **Mensaje Enviado por Cliente**: Chunk binario de audio (PCM 16-bit) o JSON con evento `{"event": "start"}` / `{"event": "stop"}`.
- **Mensaje Recibido**:
```json
{
  "type": "partial_transcript",
  "text": "la noche estaba fría en la ciudad"
}
```
y al cierre de la intervención:
```json
{
  "type": "final_transcript",
  "text": "La noche estaba fría en la ciudad."
}
```
