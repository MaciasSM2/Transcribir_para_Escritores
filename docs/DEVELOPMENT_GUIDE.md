# 🛠️ Guía de Desarrollo y Entorno Técnico — Gema

Esta guía está dirigida a desarrolladores y contribuidores que deseen extender, mantener o depurar la plataforma **Gema**.

---

## 📑 Tabla de Contenidos

1. [Configuración del Entorno de Desarrollo](#1-configuración-del-entorno-de-desarrollo)
2. [Estructura y Convenciones de Código](#2-estructura-y-convenciones-de-código)
3. [Ejecución de Tests Automatizados](#3-ejecución-de-tests-automatizados)
4. [Migraciones de Base de Datos con Alembic](#4-migraciones-de-base-de-datos-con-alembic)
5. [Inferencia Local con Ollama y Modelos de Lenguaje](#5-inferencia-local-con-ollama-y-modelos-de-lenguaje)
6. [Flujo de Trabajo Git y Commits](#6-flujo-de-trabajo-git-y-commits)

---

## 1. Configuración del Entorno de Desarrollo

### Requisitos del Sistema
- **Python**: 3.12+ (con virtualenv).
- **Node.js**: 18+ (con npm).
- **FFmpeg**: Configurado en variables de entorno del sistema (`ffmpeg -version`).
- **Ollama**: Instalado localmente (`ollama --version`).

### Paso a Paso para Desarrolladores

```bash
# 1. Clonar el repositorio
git clone https://github.com/MaciasSM2/Transcribir_para_Escritores.git
cd Transcribir_para_Escritores

# 2. Configurar Backend (Python)
cd backend
python -m venv venv

# Activar venv:
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download es_core_news_sm

# 3. Configurar Frontend (Next.js)
cd ../frontend
npm install
```

---

## 2. Estructura y Convenciones de Código

### Backend (Python / FastAPI)
- **Tipado Estricto**: Todo método público debe incluir *type hints* para argumentos y retornos.
- **Modelos Pydantic v2**: Ubicados en `schemas.py` o en los contratos de cada subsistema (`services/nlp/dialogue_contracts.py`).
- **Inmutabilidad y Concurrencia**: Ningún endpoint debe bloquear el Event Loop de FastAPI con operaciones I/O síncronas pesadas. Utilizar `asyncio.to_thread` o semáforos asíncronos cuando corresponda.

### Frontend (Next.js 16 / TypeScript / React 19)
- **Componentes Modulares**: Máxima cohesión y bajo acoplamiento.
- **Zustand para Estado Global**: Evitar prop-drilling excesivo; centralizar la persistencia y mutaciones en `src/store/`.
- **CSS Vanilla + Tailwind Utilities**: Diseños limpios, soporte completo para tema oscuro/claro y adaptabilidad responsiva.

---

## 3. Ejecución de Tests Automatizados

La suite de pruebas del backend cubre integración, contratos RAE, robustez estilométrica y endpoints REST.

```bash
# En el directorio /backend:
pytest -v

# Ejecutar un módulo de tests específico:
pytest tests/test_dialogue_engine.py -v
pytest tests/test_routers_style.py -v

# En el directorio /frontend:
npm run build
```

---

## 4. Migraciones de Base de Datos con Alembic

El esquema relacional de SQLite se gestiona mediante Alembic en `backend/alembic/`.

```bash
cd backend

# Generar una nueva migración tras modificar models.py:
alembic revision --autogenerate -m "nombre_del_cambio"

# Aplicar migraciones pendientes:
alembic upgrade head

# Revertir la última migración:
alembic downgrade -1
```

---

## 5. Inferencia Local con Ollama y Modelos de Lenguaje

Para desarrollo con soporte completo de IA local:

```bash
# Iniciar el servidor local de Ollama:
ollama serve

# Descargar el modelo por defecto:
ollama pull llama3

# Modelos recomendados alternativos según recursos de hardware:
# Para máquinas con 8GB RAM:
ollama pull mistral
# Para máquinas con 16GB+ RAM:
ollama pull llama3:8b-instruct-q8_0
```

---

## 6. Flujo de Trabajo Git y Commits

Seguimos la convención de [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: ...` — Nueva funcionalidad.
- `fix: ...` — Corrección de error o bug.
- `docs: ...` — Cambios en documentación o comentarios.
- `refactor: ...` — Refactorización de código sin alterar comportamiento.
- `test: ...` — Adición o corrección de pruebas automatizadas.
- `chore: ...` — Mantenimiento de dependencias o configuración de build.
