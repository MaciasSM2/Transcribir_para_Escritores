# backend/api/v1/endpoints/system.py
from fastapi import APIRouter, HTTPException
from services.infrastructure.system_guardian import SystemGuardian
from services.infrastructure.windows_provider import Windows11HardwareProvider

router = APIRouter()

# Inyección de dependencias acoplada a abstracciones limpias
provider = Windows11HardwareProvider()
guardian = SystemGuardian(provider=provider)

@router.get("/health/hardware", status_code=200)
def get_local_hardware_status():
    """
    Endpoint de telemetría local. Permite al Frontend Next.js deshabilitar componentes 
    pesados de la UI si la CPU/RAM del Host entra en estado crítico de contención.
    """
    try:
        diagnostic = guardian.inspect_environment_safety()
        return diagnostic
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Fallo crítico al leer los contadores de rendimiento de Windows: {str(e)}"
        )
