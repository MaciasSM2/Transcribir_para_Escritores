<#
.SYNOPSIS
  Script de Orquestación para Gema v2.0 - Local Edition
  Levanta el entorno completo de trabajo literario con validaciones preventivas.
#>

$host.UI.RawUI.WindowTitle = "💎 Gema — Estación Literaria Local"
Clear-Host

Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host "  💎 GEMA v2.0 — Estación de Dictado y Asistente Literario Local       " -ForegroundColor Yellow
Write-Host "  100% Privado | Motor Zero-IA | Diálogos RAE | Exportación Editorial  " -ForegroundColor Gray
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Dependencias Críticas del Sistema
Write-Host "[1/4] Verificando herramientas del sistema..." -ForegroundColor Cyan

if (!(Get-Command "python" -ErrorAction SilentlyContinue)) { 
    Write-Host " [!] ERROR: Python 3 no está instalado o no se encuentra en el PATH." -ForegroundColor Red
    Write-Host "     Por favor instálalo desde https://python.org" -ForegroundColor Red
    pause
    exit 1
}

if (!(Get-Command "npm" -ErrorAction SilentlyContinue)) { 
    Write-Host " [!] ERROR: Node.js / NPM no está instalado o no se encuentra en el PATH." -ForegroundColor Red
    Write-Host "     Por favor instálalo desde https://nodejs.org" -ForegroundColor Red
    pause
    exit 1
}

if (!(Get-Command "ffmpeg" -ErrorAction SilentlyContinue)) { 
    Write-Host " [!] ADVERTENCIA: FFmpeg no detectado en el PATH." -ForegroundColor Yellow
    Write-Host "     El dictado en directo funcionará, pero la conversión de audios subidos se verá limitada." -ForegroundColor Yellow
    Write-Host "     Instalación recomendada: winget install Gyan.FFmpeg" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ FFmpeg localizado correctamente." -ForegroundColor Green
}

# 2. Localizar Entorno Virtual de Python
$venvPython = ""
if (Test-Path "backend\venv\Scripts\python.exe") {
    $venvPython = "backend\venv\Scripts\activate"
} elseif (Test-Path ".venv\Scripts\python.exe") {
    $venvPython = "..\.venv\Scripts\activate"
}

# 3. Comprobar Demonio de Ollama
Write-Host "[2/4] Verificando servidor de inferencia local (Ollama)..." -ForegroundColor Cyan
try {
    $ollamaCheck = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✓ Ollama está activo y respondiendo en el puerto 11434." -ForegroundColor Green
} catch {
    if (Get-Command "ollama" -ErrorAction SilentlyContinue) {
        Write-Host "  [*] Iniciando demonio 'ollama serve' en segundo plano..." -ForegroundColor Yellow
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Minimized
    } else {
        Write-Host "  [i] Ollama no instalado. Gema funcionará en modo Motor Zero-IA (100% determinista)." -ForegroundColor Gray
    }
}

# 4. Iniciar Backend (FastAPI)
Write-Host "[3/4] Iniciando Motor de Inteligencia Backend (FastAPI)..." -ForegroundColor Cyan
if ($venvPython -ne "") {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; & $venvPython; uvicorn main:app --reload --port 8000" -WindowStyle Minimized
} else {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn main:app --reload --port 8000" -WindowStyle Minimized
}
Write-Host "  ✓ Backend inicializado en http://localhost:8000" -ForegroundColor Green

# 5. Iniciar Frontend (Next.js)
Write-Host "[4/4] Iniciando Lienzo de Escritura Frontend (Next.js)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WindowStyle Minimized
Write-Host "  ✓ Frontend inicializado en http://localhost:3000" -ForegroundColor Green

Write-Host ""
Write-Host "=======================================================================" -ForegroundColor Green
Write-Host "  🎉 ¡Gema está lista para escribir!                                  " -ForegroundColor Green
Write-Host "  Abre tu navegador en: http://localhost:3000                         " -ForegroundColor Yellow
Write-Host "=======================================================================" -ForegroundColor Green
Write-Host ""
