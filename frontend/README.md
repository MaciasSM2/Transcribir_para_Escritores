# 🖥️ Gema Frontend — Interfaz de Escritura Literaria y Lienzo TipTap

Cliente web moderno para **Gema (Grabadora para Escritores)** construido sobre **Next.js 16 (App Router)**, **React 19**, **TypeScript** y **TipTap**.

---

## 🚀 Características del Frontend

- **Triple Panel Layout**:
  - *Panel Izquierdo*: Explorador de escenas y capítulos con ordenación y búsqueda reactiva.
  - *Panel Central*: Lienzo de escritura enriquecido TipTap configurado en formato folio A4 con menú flotante contextual.
  - *Panel Derecho*: Inspector analítico con métricas estilométricas en tiempo real, gráfico de tensión narrativa y monitor de hardware.
- **Búfer de Dictado en Directo**: Integración con **Web Speech API** para visualización instantánea con latencia cero de lo que el autor pronuncia.
- **Gestión de Estado Centralizada (Zustand)**:
  - `useDictationStore`: Control de búfer, transcripción y alertas de estilo.
  - `useProjectStore`: Estructura jerárquica de la obra literaria y navegación.
  - `useToneStore`: Calibración y sincronización de perfiles de tono.
  - `useHistoryStore`: Snapshots, versiones y comparación de diffs.
  - `useInferenceStore`: Estado de los workers asíncronos y bloqueo de concurrencia.
- **Persistencia Local-First con Dexie.js (IndexedDB)**: El usuario puede continuar escribiendo, creando capítulos y editando sin depender de la red ni del backend.
- **Exportación Tipográfica**: Exportador directo a Word (`.docx`) aplicando los estándares editoriales de la RAE.

---

## 🛠️ Comandos de Desarrollo

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo en http://localhost:3000
npm run dev

# Validar tipado TypeScript y compilar bundle de producción
npm run build

# Iniciar servidor de producción
npm start
```

---

## 📁 Estructura del Frontend

```
frontend/src/
├── app/                  # Rutas de la aplicación (App Router)
│   ├── api/              # Endpoints locales de exportación docx
│   ├── globals.css       # Estilos globales y temas
│   ├── layout.tsx        # Layout raíz
│   └── page.tsx          # Entrada a la estación Triple Panel
├── components/           # Componentes visuales
│   ├── Editor/           # Lienzo TipTap, RichCanvas, BubbleMenu, Toolbar
│   ├── Panels/           # ChapterExplorer, ManuscriptAnalyticsGrid, QuickControlCenter...
│   ├── StyleReportPanel.tsx
│   ├── TensionGraph.tsx
│   └── TopNavbar.tsx
├── hooks/                # Hooks personalizados (useAutoSave, useAudioUpload...)
├── infrastructure/       # Adaptadores de API, audio, exportador DOCX y Dexie.js
├── layouts/              # TriplePanelLayout
├── store/                # Zustand stores
└── types/                # Definiciones de tipos TypeScript
```
