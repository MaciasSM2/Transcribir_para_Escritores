# 🤝 Guía de Contribución a Gema

¡Gracias por tu interés en contribuir a **Gema (Grabadora para Escritores)**! Este proyecto busca empoderar a escritores de todo el mundo mediante herramientas de dictado y asistencia literaria libres, privadas y de alta precisión.

---

## 📜 Código de Conducta

Nos comprometemos a fomentar un entorno abierto, inclusivo y respetuoso para todos los contribuidores. Por favor, mantén un trato empático, constructivo y profesional en issues, pull requests y discusiones.

---

## 🛠️ ¿Cómo Contribuir?

### 1. Reportar Errores (Bug Reports)
- Antes de abrir un issue, revisa si ya existe un reporte similar.
- Proporciona un título claro y pasos exactos para reproducir el fallo.
- Incluye detalles de tu entorno (Sistema Operativo, versión de Python, Node.js, si usas Ollama o Web Speech).

### 2. Proponer Nuevas Funcionalidades (Feature Requests)
- Describe claramente la necesidad del escritor y cómo la funcionalidad mejora la experiencia literaria.
- Explica la solución propuesta y posibles alternativas consideradas.

### 3. Enviar un Pull Request (PR)
1. Haz un Fork del repositorio y crea una rama a partir de `main`:
   ```bash
   git checkout -b feat/nombre-de-tu-mejora
   ```
2. Asegúrate de que los tests existentes pasen y añade nuevos tests si agregas funcionalidad:
   ```bash
   # Backend
   cd backend
   pytest -v

   # Frontend
   cd frontend
   npm run build
   ```
3. Realiza commits siguiendo la especificación [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/):
   - `feat: agregar nuevo perfil de tono para realismo sucio`
   - `fix: corregir puntuación de raya de diálogo en incisos múltiples`
   - `docs: actualizar manual de usuario con atajos de teclado`
4. Haz push a tu fork y abre un Pull Request contra la rama `main`.

---

## 🧪 Estándares de Calidad y Código

- **Python**: PEP 8, anotaciones de tipo completas (*Type Hints*) en firmas de métodos y funciones públicas.
- **TypeScript**: Modo estricto habilitado; no usar `any` salvo en casos excepcionales justificados.
- **Pruebas**: Cada nuevo endpoint o servicio de procesamiento debe contar con tests unitarios en `backend/tests/`.
