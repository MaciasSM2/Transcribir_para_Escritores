"""
Prueba de integración end-to-end que replica exactamente el flujo del browser:
  1. POST /api/transcribe/file  → espera 202 Accepted
  2. GET  /api/transcribe/status/{job_id}  cada 3s → hasta completed/error/timeout

Uso:
    python backend/test_integration_async.py
"""
import urllib.request
import urllib.error
import json
import time
import os

BASE_URL = "http://localhost:8000"
AUDIO_FILE = os.path.join(os.path.dirname(__file__), "test_audio.wav")
MAX_POLL_RETRIES = 20  # 20 × 3s = 60s máximo para este test

# ── Colores ANSI para terminal ────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def log(color: str, tag: str, msg: str):
    print(f"{color}{BOLD}[{tag}]{RESET} {msg}")

# ── PASO 1: Subir audio ───────────────────────────────────────────────────────
log(CYAN, "UPLOAD", f"Enviando {AUDIO_FILE} -> POST {BASE_URL}/api/transcribe/file")

with open(AUDIO_FILE, "rb") as f:
    audio_bytes = f.read()

boundary = "----FormBoundary7MA4YWxkTrZu0gW"
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="test_audio.wav"\r\n'
    f"Content-Type: audio/wav\r\n\r\n"
).encode() + audio_bytes + f"\r\n--{boundary}--\r\n".encode()

req = urllib.request.Request(
    f"{BASE_URL}/api/transcribe/file",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST",
)

t0 = time.time()
try:
    with urllib.request.urlopen(req) as resp:
        elapsed_upload = time.time() - t0
        status_code = resp.status
        data = json.loads(resp.read())
except urllib.error.HTTPError as e:
    elapsed_upload = time.time() - t0
    status_code = e.code
    data = json.loads(e.read())

job_id = data.get("job_id", "")

print()
if status_code == 202:
    log(GREEN, f"HTTP {status_code}", f"Accepted en {elapsed_upload*1000:.0f}ms ✓")
else:
    log(RED, f"HTTP {status_code}", f"Esperaba 202, recibí {status_code}")

log(CYAN, "JOB ID", job_id)
log(CYAN, "STATUS", data.get("status", "?"))
print()

# ── PASO 2: Polling ───────────────────────────────────────────────────────────
log(CYAN, "POLLING", f"Consultando estado cada 3s (máx {MAX_POLL_RETRIES} intentos)…")
print()

checklist = {
    "202_inmediato":   status_code == 202,
    "job_id_recibido": bool(job_id),
    "polling_ok":      False,
    "completado":      False,
    "temp_limpio":     False,
}

for attempt in range(1, MAX_POLL_RETRIES + 1):
    with urllib.request.urlopen(f"{BASE_URL}/api/transcribe/status/{job_id}") as r:
        poll = json.loads(r.read())

    s = poll["status"]
    color = YELLOW if s == "pending" else (GREEN if s == "completed" else RED)
    transcription_preview = repr(poll.get("transcription") or "")[:60]
    log(color, f"Poll #{attempt}", f"status={s}  transcription={transcription_preview}")

    checklist["polling_ok"] = True

    if s == "completed":
        checklist["completado"] = True
        break
    elif s == "error":
        log(RED, "ERROR", poll.get("transcription", "Error desconocido"))
        break

    if attempt < MAX_POLL_RETRIES:
        time.sleep(3)
    else:
        log(RED, "TIMEOUT", "El job no completó en el tiempo máximo del test")

# ── PASO 3: Verificar limpieza de temp_audio ─────────────────────────────────
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_audio")
residual = [f for f in os.listdir(TEMP_DIR)] if os.path.isdir(TEMP_DIR) else []
checklist["temp_limpio"] = len(residual) == 0
residual_msg = "vacío ✓" if not residual else f"¡{len(residual)} archivo(s) residual(es)! {residual}"

# ── RESULTADO FINAL ───────────────────────────────────────────────────────────
print()
print(f"{BOLD}{'─'*55}{RESET}")
print(f"{BOLD}  AUDITORÍA DE INTEGRACIÓN — CHECKLIST{RESET}")
print(f"{BOLD}{'─'*55}{RESET}")

items = [
    ("202_inmediato",   "Respuesta 202 Accepted (liberación inmediata)"),
    ("job_id_recibido", "Job ID recibido en la respuesta inicial"),
    ("polling_ok",      "Polling al endpoint de status funcionó"),
    ("completado",      "Job cambió a status='completed'"),
    ("temp_limpio",     f"temp_audio limpio: {residual_msg}"),
]

all_pass = True
for key, label in items:
    ok = checklist[key]
    symbol = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
    all_pass = all_pass and ok
    print(f"  {symbol}  {label}")

print(f"{BOLD}{'─'*55}{RESET}")
verdict = f"{GREEN}PASADO{RESET}" if all_pass else f"{RED}FALLIDO{RESET}"
print(f"  Resultado: {BOLD}{verdict}{RESET}")
print(f"{'─'*55}")
