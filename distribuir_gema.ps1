# raiz/distribuir_gema.ps1
Write-Host "🔨 Compilando Gema v2.0 para Windows 11..." -ForegroundColor Cyan

# 1. Compilar Frontend
Write-Host "🎨 Generando binarios del Lienzo (Next.js)..." -ForegroundColor Yellow
cd frontend
npm run build
cd ..

# 2. Preparar el entorno de Python (Backend)
Write-Host "📦 Congelando dependencias del Motor de IA..." -ForegroundColor Yellow
cd backend
if (!(Test-Path "venv")) { python -m venv venv }
.\venv\Scripts\activate
pip install -r requirements.txt
# Opcional: Usar PyInstaller para crear un .exe del backend
# pyinstaller --onefile --name gema_engine main.py
cd ..

# 3. Crear Acceso Directo de Lanzamiento
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$HOME\Desktop\Gema.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$PSScriptRoot\run_gema.ps1`""
$Shortcut.IconLocation = "$PSScriptRoot\assets\icon.ico"
$Shortcut.Save()

Write-Host "✅ Distribución completada. Tienes un acceso directo en tu Escritorio." -ForegroundColor Green
