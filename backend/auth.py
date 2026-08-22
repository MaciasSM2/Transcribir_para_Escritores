"""
auth.py — Capa de autenticación JWT para Gema.

Diseño single-user para uso local.
Si se despliega en servidor, cambiar CREDENTIALS por usuarios en BD
y usar passlib para hashear contraseñas.

Variables de entorno:
  GEMA_SECRET  — clave de firma JWT (usa el default solo en desarrollo local)
  GEMA_USER    — usuario (default: admin)
  GEMA_PASS    — contraseña (default: gema2025)
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# ── Configuración ─────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("GEMA_SECRET", "gema-dev-secret-change-in-production-2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas para uso local

# Credenciales (single-user). En producción: tabla users en BD + bcrypt hash.
_ADMIN_USER = os.getenv("GEMA_USER", "admin")
_ADMIN_PASS = os.getenv("GEMA_PASS", "gema2025")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── Helpers ───────────────────────────────────────────────────────────────────
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(plain: str) -> str:
    return pwd_context.hash(plain)


def authenticate_user(username: str, password: str) -> bool:
    """Valida credenciales. Devuelve True si correctas."""
    return username == _ADMIN_USER and password == _ADMIN_PASS


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ── Dependency FastAPI ────────────────────────────────────────────────────────
async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependency que extrae y valida el Bearer token.
    Inyectar en cualquier endpoint con: Depends(get_current_user)
    Lanza 401 si el token es inválido o expirado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username
