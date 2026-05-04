"""
Rotas de equipes: CRUD + equipe do aluno logado.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from database import get_db
from models.usuario import Usuario
from models.equipe import Equipe, EquipeMembro, EquipeMentor
from models.semestre import Semestre
from models.historico_alimento import HistoricoAlimento
from schemas.equipe import (
    EquipeCreate, EquipeUpdate, EquipeResponse,
    EquipeDetalheResponse, EquipeMinhaResponse,
    MembroDetalhe, MentorDetalhe,
)
from auth.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/equipes", tags=["Equipes"])


def _total(db, eid):
    return int(db.query(func.coalesce(func.sum(HistoricoAlimento.quantidade), 0)).filter(HistoricoAlimento.equipe_id == eid).scalar())


def _det(db, eq):
    m = [MembroDetalhe(id=e.usuario.id, nome=e.usuario.nome, curso=e.usuario.curso, ra=e.usuario.ra) for e in eq.membros]
    mt = [MentorDetalhe(id=e.usuario.id, nome=e.usuario.nome) for e in eq.mentores]
    return {"id": eq.id, "nome": eq.nome, "semestre_id": eq.semestre_id, "total_arrecadado": _total(db, eq.id), "membros": m, "mentores": mt, "criado_em": eq.criado_em}


def _load(db, eid):
    return db.query(Equipe).options(joinedload(Equipe.membros).joinedload(EquipeMembro.usuario), joinedload(Equipe.mentores).joinedload(EquipeMentor.usuario)).filter(Equipe.id == eid).first()


@router.get("/", response_model=list[EquipeResponse])
def listar_equipes(semestre_id: int = Query(...), db: Session = Depends(get_db), u: Usuario = Depends(get_current_user)):
    eqs = db.query(Equipe).filter(Equipe.semestre_id == semestre_id).options(joinedload(Equipe.membros)).all()
    return [EquipeResponse(id=e.id, nome=e.nome, semestre_id=e.semestre_id, total_membros=len(e.membros), criado_em=e.criado_em) for e in eqs]


@router.get("/minha", response_model=EquipeMinhaResponse)
def minha_equipe(db: Session = Depends(get_db), u: Usuario = Depends(get_current_user)):
    if u.tipo != "aluno":
        raise HTTPException(status_code=403, detail="Apenas alunos possuem 'minha equipe'.")
    sem = db.query(Semestre).filter(Semestre.status == "ativo").first()
    if not sem:
        raise HTTPException(status_code=404, detail="Nenhum semestre ativo.")
    em = db.query(EquipeMembro).join(Equipe).filter(EquipeMembro.usuario_id == u.id, Equipe.semestre_id == sem.id).first()
    if not em:
        raise HTTPException(status_code=404, detail="Você não está em nenhuma equipe neste semestre.")
    eq = _load(db, em.equipe_id)
    d = _det(db, eq)
    d["semestre_nome"] = sem.nome
    return EquipeMinhaResponse(**d)


@router.get("/{equipe_id}", response_model=EquipeDetalheResponse)
def detalhe_equipe(equipe_id: int, db: Session = Depends(get_db), u: Usuario = Depends(get_current_user)):
    eq = _load(db, equipe_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipe não encontrada.")
    return EquipeDetalheResponse(**_det(db, eq))


@router.post("/", response_model=EquipeDetalheResponse, status_code=201)
def criar_equipe(dados: EquipeCreate, db: Session = Depends(get_db), admin: Usuario = Depends(require_admin)):
    if not db.query(Semestre).filter(Semestre.id == dados.semestre_id).first():
        raise HTTPException(status_code=404, detail="Semestre não encontrado.")
    for mid in dados.membro_ids:
        if db.query(EquipeMembro).join(Equipe).filter(EquipeMembro.usuario_id == mid, Equipe.semestre_id == dados.semestre_id).first():
            a = db.query(Usuario).filter(Usuario.id == mid).first()
            raise HTTPException(status_code=409, detail=f"'{a.nome if a else mid}' já pertence a outra equipe neste semestre.")
    eq = Equipe(nome=dados.nome, semestre_id=dados.semestre_id)
    db.add(eq)
    db.flush()
    for mid in dados.membro_ids:
        db.add(EquipeMembro(equipe_id=eq.id, usuario_id=mid))
    for mid in dados.mentor_ids:
        db.add(EquipeMentor(equipe_id=eq.id, usuario_id=mid))
    db.commit()
    eq = _load(db, eq.id)
    return EquipeDetalheResponse(**_det(db, eq))


@router.put("/{equipe_id}", response_model=EquipeDetalheResponse)
def editar_equipe(equipe_id: int, dados: EquipeUpdate, db: Session = Depends(get_db), admin: Usuario = Depends(require_admin)):
    eq = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipe não encontrada.")
    if dados.nome is not None:
        eq.nome = dados.nome
    if dados.membro_ids is not None:
        for mid in dados.membro_ids:
            ex = db.query(EquipeMembro).join(Equipe).filter(EquipeMembro.usuario_id == mid, Equipe.semestre_id == eq.semestre_id, Equipe.id != equipe_id).first()
            if ex:
                a = db.query(Usuario).filter(Usuario.id == mid).first()
                raise HTTPException(status_code=409, detail=f"'{a.nome if a else mid}' já pertence a outra equipe neste semestre.")
        db.query(EquipeMembro).filter(EquipeMembro.equipe_id == equipe_id).delete()
        for mid in dados.membro_ids:
            db.add(EquipeMembro(equipe_id=equipe_id, usuario_id=mid))
    if dados.mentor_ids is not None:
        db.query(EquipeMentor).filter(EquipeMentor.equipe_id == equipe_id).delete()
        for mid in dados.mentor_ids:
            db.add(EquipeMentor(equipe_id=equipe_id, usuario_id=mid))
    db.commit()
    eq = _load(db, equipe_id)
    return EquipeDetalheResponse(**_det(db, eq))


@router.delete("/{equipe_id}", status_code=204)
def excluir_equipe(equipe_id: int, db: Session = Depends(get_db), admin: Usuario = Depends(require_admin)):
    eq = db.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipe não encontrada.")
    db.delete(eq)
    db.commit()
