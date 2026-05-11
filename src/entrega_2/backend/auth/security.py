"""
Funções de segurança: hash de senha e geração/validação de JWT.
Usa bcrypt diretamente (passlib é incompatível com bcrypt >= 4.1).
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from config import settings


# ── Hashing ─────────────────────────────────────
def hash_senha(senha: str) -> str:
    """Gera o hash bcrypt de uma senha em texto plano."""
    senha_bytes = senha.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha_bytes, salt).decode("utf-8")


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash."""
    return bcrypt.checkpw(
        senha_plana.encode("utf-8"), senha_hash.encode("utf-8")
    )


# ── JWT ─────────────────────────────────────────
def criar_token_acesso(data: dict, expires_delta: timedelta | None = None) -> str:
    """Cria um token JWT com os dados fornecidos."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decodificar_token(token: str) -> dict | None:
    """Decodifica um token JWT. Retorna None se inválido/expirado."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
        return None
