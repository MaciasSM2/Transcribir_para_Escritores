# GEMA — Directrices para Agentes y Desarrolladores

Este documento establece las convenciones de arquitectura y flujo de desarrollo para agentes de IA y desarrolladores humanos en el repositorio **GEMA (Transcribir para Escritores)**.

---

## 🏛️ Arquitectura y Principios de Diseño
1. **Clean Architecture & SOLID:**
   - La capa de presentación (UI / Next.js) está desacoplada de la infraestructura mediante interfaces y adaptadores.
   - En el frontend, `infrastructure/` contiene implementaciones de hardware (Web Speech API) y exportaciones (`IDocumentExporter`).
   - En el backend, los servicios (`services/`) implementan lógica de negocio pura y delegan persistencia al ORM (`models.py`) y transcodificación a subprocessos (`ffmpeg_processor.py`).
2. **Local-First & Privacidad Absoluta:**
   - Todo procesamiento debe operar en la máquina local del usuario sin llamadas a servicios de terceros ni telemetría no consentida.
3. **Concurrencia No Bloqueante:**
   - En el backend, las tareas pesadas de audio usan el patrón **Async Request-Reply (HTTP 202)** y `ProcessPoolExecutor` para evitar el GIL.
   - En el frontend, el cálculo de diferencias (*Myers Diff*) corre en un **Web Worker** (`diffWorker.ts`) para mantener la interfaz a 60 FPS.

---

## 🧪 Pruebas y Validación
- Todo nuevo endpoint o refactor en backend debe validarse con `pytest`.
- Todo cambio en frontend debe superar `npm run lint` y `npx tsc --noEmit`.
