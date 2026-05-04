"""
Schemas do semestre.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class SemestreCreate(BaseModel):
    nome: str
    ano: int
    periodo: str  # "1º Semestre" | "2º Semestre"
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    status: str = "ativo"

    @field_validator("status")
    @classmethod
    def validar_status(cls, v):
        if v not in ("ativo", "inativo"):
            raise ValueError("Status deve ser 'ativo' ou 'inativo'.")
        return v

    @field_validator("ano")
    @classmethod
    def validar_ano(cls, v):
        if v < 2000 or v > 2100:
            raise ValueError("Ano deve estar entre 2000 e 2100.")
        return v


class SemestreUpdate(BaseModel):
    nome: Optional[str] = None
    ano: Optional[int] = None
    periodo: Optional[str] = None
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    status: Optional[str] = None


class SemestreResponse(BaseModel):
    id: int
    nome: str
    ano: int
    periodo: str
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    status: str
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    model_config = {"from_attributes": True}
