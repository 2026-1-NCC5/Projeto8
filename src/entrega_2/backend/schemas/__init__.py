"""
Schemas Pydantic — exporta tudo de um lugar só.
"""

from schemas.auth import TokenResponse, LoginRequest
from schemas.usuario import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
    SenhaUpdate,
    UsuarioBuscaResponse,
)
from schemas.semestre import SemestreCreate, SemestreUpdate, SemestreResponse
from schemas.equipe import (
    EquipeCreate,
    EquipeUpdate,
    EquipeResponse,
    EquipeDetalheResponse,
    EquipeMinhaResponse,
)
from schemas.historico_alimento import (
    HistoricoAlimentoCreate,
    HistoricoAlimentoUpdate,
    HistoricoAlimentoResponse,
    HistoricoPaginado,
)
