# 📋 Registro de Cambios (Changelog)

Todas las modificaciones notables de este proyecto se documentan en este archivo. El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [2.0.0] - 2026-05-29

### 🚀 Añadido
- **Lienzo Enriquecido TipTap**: Editor visual con soporte para atajos de teclado, menú contextual de reescritura y formato folio A4.
- **Formateador Ortotípico RAE**: Normalización estricta de rayas de diálogo (`—`), incisos y verbos *dicendi*.
- **Motor Experto Zero-IA**: Detección de legibilidad Fernández-Huerta, riqueza léxica (TTR), conteo silábico con Pyphen y segmentación con Pysbd.
- **Gráfico de Tensión Narrativa**: Mapeo visual interactivo del pulso emocional del capítulo.
- **Control de Versiones y Diff Semántico**: Comparador visual de versiones históricas basado en `diff-match-patch`.
- **Exportador DOCX Editorial RAE**: Generación de documentos Word con estándares editoriales (Times New Roman 12pt, 1.5 interlineado, sangría 1.25 cm).
- **Persistencia Local-First**: Almacenamiento instantáneo offline con Dexie.js (IndexedDB) en frontend y SQLite/Vault en backend.
- **Suite de Pruebas Automatizadas**: 35 tests exhaustivos en pytest con cobertura de contratos RAE, estilometría, endpoints y aislamiento en memoria.
- **Documentación Integral**: README principal, Manual de Usuario para Escritores, Documento de Arquitectura, Referencia de APIs y Guía de Desarrollo.

### 🛠️ Corregido
- Resuelto error de tipado TypeScript en `useProjectStore.ts` (`addChapter`).
- Corregido arranque de `FastAPI lifespan` para operar de forma no bloqueante y resiliente si Ollama está temporalmente apagado.
- Normalizado el contrato de retorno en `POST /api/v1/tones/`.
- Unificados los overrides de dependencias en `backend/tests/conftest.py`.

---

## [1.0.0] - 2026-05-12

### 🚀 Añadido
- Versión inicial del transcriptor de voz para escritores.
- Integración básica con Vosk ASR y Web Speech API.
- Endpoints REST para ingesta de audio y guardado de borradores.
