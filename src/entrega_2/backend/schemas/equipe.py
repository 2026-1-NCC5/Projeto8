"""
Schemas de equipe.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas.usuario import UsuarioBuscaResponse


class EquipeCreate(BaseModel):
    nome: str
    semestre_id: int
    mentor_ids: list[int] = []
    membro_ids: list[int] = []


class EquipeUpdate(BaseModel):
    nome: Optional[str] = None
    mentor_ids: Optional[list[int]] = None
    membro_ids: Optional[list[int]] = None


class EquipeResponse(BaseModel):
    """Listagem resumida de equipes."""

    id: int
    nome: str
    semestre_id: int
    total_membros: int = 0
    criado_em: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MembroDetalhe(BaseModel):
    id: int
    nome: str
    curso: Optional[str] = None
    ra: Optional[str] = None

    model_config = {"from_attributes": True}


class MentorDetalhe(BaseModel):
    id: int
    nome: str

    model_config = {"from_attributes": True}


class EquipeDetalheResponse(BaseModel):
    """Detalhes completos da equipe (para tela de detalhes)."""

    id: int
    nome: str
    semestre_id: int
    total_arrecadado: int = 0
    membros: list[MembroDetalhe] = []
    mentores: list[MentorDetalhe] = []
    criado_em: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EquipeMinhaResponse(BaseModel):
    """Equipe do aluno logado no semestre ativo."""

    id: int
    nome: str
    semestre_nome: str
    semestre_id: int
    total_arrecadado: int = 0
    membros: list[MembroDetalhe] = []
    mentores: list[MentorDetalhe] = []

    model_config = {"from_attributes": True}
