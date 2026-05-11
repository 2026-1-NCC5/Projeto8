"""
Schemas de autenticação (login / token).
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: "UsuarioTokenInfo"


class UsuarioTokenInfo(BaseModel):
    id: int
    nome: str
    email: str
    tipo: str

    model_config = {"from_attributes": True}


# Necessário para resolver a referência forward
TokenResponse.model_rebuild()
