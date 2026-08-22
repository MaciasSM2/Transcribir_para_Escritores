#!/usr/bin/env bash
# =============================================================================
# GEMA v2.0 — Script de Orquestación para Linux / macOS
# =============================================================================

set -e

echo -e "\033[1;36m=======================================================================\033[0m"
echo -e "\033[1;33m  💎 GEMA v2.0 — Estación de Dictado y Asistente Literario Local       \033[0m"
echo -e "\033[0;37m  100% Privado | Motor Zero-IA | Diálogos RAE | Exportación Editorial  \033[0m"
echo -e "\033[1;36m=======================================================================\033[0m"
echo ""

# 1. Comprobar dependencias
echo -e "\033[1;34m[1/4] Verificando dependencias del sistema...\033[0m"
command -v python3 >/dev/null 2>&1 || { echo -e "\033[1;31m[!] Python 3 no encontrado. Instálalo para continuar.\033[0m"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo -e "\033[1;31m[!] Node.js/NPM no encontrado. Instálalo para continuar.\033[0m"; exit 1; }

if command -v ffmpeg >/dev/null 2>&1; then
    echo -e "\033[1;32m  ✓ FFmpeg localizado correctamente.\033[0m"
else
    echo -e "\033[1;33m  [!] Advertencia: FFmpeg no detectado. Instala con 'sudo apt install ffmpeg' o 'brew install ffmpeg'.\033[0m"
fi

# 2. Comprobar Ollama
echo -e "\033[1;34m[2/4] Verificando servidor Ollama...\033[0m"
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "\033[1;32m  ✓ Ollama está activo y respondiendo.\033[0m"
else
    if command -v ollama >/dev/null 2>&1; then
        echo -e "\033[1;33m  [*] Iniciando 'ollama serve' en segundo plano...\033[0m"
        ollama serve >/dev/null 2>&1 &
    else
        echo -e "\033[0;37m  [i] Ollama no instalado. Gema funcionará en modo Motor Zero-IA.\033[0m"
    fi
fi

# 3. Iniciar Backend
echo -e "\033[1;34m[3/4] Iniciando Backend FastAPI en http://localhost:8000...\033[0m"
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# 4. Iniciar Frontend
echo -e "\033[1;34m[4/4] Iniciando Frontend Next.js en http://localhost:3000...\033[0m"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "\033[1;32m=======================================================================\033[0m"
echo -e "\033[1;32m  🎉 ¡Gema está lista para escribir!                                  \033[0m"
echo -e "\033[1;33m  Abre tu navegador en: http://localhost:3000                         \033[0m"
echo -e "\033[1;32m=======================================================================\033[0m"
echo "Presiona Ctrl+C para detener todos los servicios."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
