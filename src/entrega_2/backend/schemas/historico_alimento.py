"""
Schemas do histórico de alimentos.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class HistoricoAlimentoCreate(BaseModel):
    data: date
    item: str
    quantidade: int
    unidade: str = "un"
    status: str = "concluido"


class HistoricoAlimentoUpdate(BaseModel):
    data: Optional[date] = None
    item: Optional[str] = None
    quantidade: Optional[int] = None
    unidade: Optional[str] = None
    status: Optional[str] = None


class HistoricoAlimentoResponse(BaseModel):
    id: int
    equipe_id: int
    data: date
    item: str
    quantidade: int
    unidade: str
    status: str
    criado_em: Optional[datetime] = None

    model_config = {"from_attributes": True}


class HistoricoPaginado(BaseModel):
    """Resposta paginada do histórico."""

    items: list[HistoricoAlimentoResponse]
    total: int
    pagina: int
    por_pagina: int
    total_paginas: int
