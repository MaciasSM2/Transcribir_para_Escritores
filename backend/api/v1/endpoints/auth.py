"""
Router: Autenticación JWT
Endpoints:
  POST /api/auth/login   — recibe username/password, devuelve access_token
  GET  /api/auth/me      — devuelve usuario actual (útil para verificar token)
"""
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from fastapi import Depends

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # segundos


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    """
    Autentica al usuario y devuelve un JWT.
    Para uso local: credenciales configuradas en variables de entorno
    GEMA_USER / GEMA_PASS (defaults: admin / gema2025).
    """
    if not authenticate_user(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": request.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=access_token)


@router.get("/me")
async def get_me(current_user: str = Depends(get_current_user)) -> dict:
    """Devuelve el usuario actual. Útil para verificar que el token es válido."""
    return {"username": current_user}
