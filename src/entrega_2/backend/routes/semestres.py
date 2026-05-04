"""
Rotas de semestres (CRUD — somente admin).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.semestre import Semestre
from schemas.semestre import SemestreCreate, SemestreUpdate, SemestreResponse
from auth.dependencies import get_current_user, require_admin
from models.usuario import Usuario

router = APIRouter(prefix="/api/semestres", tags=["Semestres"])


# ── GET / ───────────────────────────────────────
@router.get("/", response_model=list[SemestreResponse])
def listar_semestres(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista todos os semestres (qualquer usuário autenticado)."""
    semestres = db.query(Semestre).order_by(Semestre.ano.desc(), Semestre.periodo.desc()).all()
    return semestres


# ── POST / ──────────────────────────────────────
@router.post("/", response_model=SemestreResponse, status_code=status.HTTP_201_CREATED)
def criar_semestre(
    dados: SemestreCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    """Cria um novo semestre (somente admin)."""
    semestre = Semestre(
        nome=dados.nome,
        ano=dados.ano,
        periodo=dados.periodo,
        data_inicio=dados.data_inicio,
        data_termino=dados.data_termino,
        status=dados.status,
    )
    db.add(semestre)
    db.commit()
    db.refresh(semestre)
    return semestre


# ── PUT /:id ────────────────────────────────────
@router.put("/{semestre_id}", response_model=SemestreResponse)
def editar_semestre(
    semestre_id: int,
    dados: SemestreUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    """Edita um semestre existente (somente admin)."""
    semestre = db.query(Semestre).filter(Semestre.id == semestre_id).first()
    if not semestre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semestre não encontrado.",
        )

    if dados.nome is not None:
        semestre.nome = dados.nome
    if dados.ano is not None:
        semestre.ano = dados.ano
    if dados.periodo is not None:
        semestre.periodo = dados.periodo
    if dados.data_inicio is not None:
        semestre.data_inicio = dados.data_inicio
    if dados.data_termino is not None:
        semestre.data_termino = dados.data_termino
    if dados.status is not None:
        semestre.status = dados.status

    db.commit()
    db.refresh(semestre)
    return semestre


# ── DELETE /:id ─────────────────────────────────
@router.delete("/{semestre_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_semestre(
    semestre_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    """Exclui um semestre e todas as equipes associadas (somente admin)."""
    semestre = db.query(Semestre).filter(Semestre.id == semestre_id).first()
    if not semestre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semestre não encontrado.",
        )

    db.delete(semestre)
    db.commit()
    return None
