"""
Schemas do usuário (criação, resposta, atualização).
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UsuarioCreate(BaseModel):
    """Dados para cadastro de usuário (aluno ou mentor)."""

    nome: str
    email: EmailStr
    telefone: str
    senha: str
    tipo: str  # "aluno" ou "mentor"
    ra: Optional[str] = None
    curso: Optional[str] = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v):
        if v not in ("aluno", "mentor"):
            raise ValueError("Tipo deve ser 'aluno' ou 'mentor'. Admin é promovido no banco.")
        return v

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v):
        if len(v) < 6:
            raise ValueError("A senha deve ter no mínimo 6 caracteres.")
        return v


class UsuarioResponse(BaseModel):
    """Dados retornados do usuário (sem senha)."""

    id: int
    nome: str
    email: str
    telefone: str
    tipo: str
    ra: Optional[str] = None
    curso: Optional[str] = None
    foto_url: Optional[str] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UsuarioUpdate(BaseModel):
    """Dados editáveis do perfil."""

    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None


class SenhaUpdate(BaseModel):
    """Alteração de senha."""

    senha_atual: str
    nova_senha: str
    confirmar_senha: str

    @field_validator("nova_senha")
    @classmethod
    def validar_nova_senha(cls, v):
        if len(v) < 6:
            raise ValueError("A nova senha deve ter no mínimo 6 caracteres.")
        return v


class UsuarioBuscaResponse(BaseModel):
    """Resultado da busca de usuários (para modal de equipes)."""

    id: int
    nome: str
    ra: Optional[str] = None
    curso: Optional[str] = None

    model_config = {"from_attributes": True}
