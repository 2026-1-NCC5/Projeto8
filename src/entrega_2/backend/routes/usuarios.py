"""
Rotas de usuário: perfil, atualização, senha, foto, exclusão e busca.
"""

import os
import uuid
import shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.usuario import Usuario
from schemas.usuario import UsuarioResponse, UsuarioUpdate, SenhaUpdate, UsuarioBuscaResponse
from auth.dependencies import get_current_user
from auth.security import verificar_senha, hash_senha
from config import settings

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])


# ── GET /me ─────────────────────────────────────
@router.get("/me", response_model=UsuarioResponse)
def obter_meu_perfil(current_user: Usuario = Depends(get_current_user)):
    """Retorna os dados do usuário logado."""
    return current_user


# ── PUT /me ─────────────────────────────────────
@router.put("/me", response_model=UsuarioResponse)
def atualizar_perfil(
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Atualiza nome, email e/ou telefone do perfil."""
    if dados.email and dados.email != current_user.email:
        existente = db.query(Usuario).filter(
            Usuario.email == dados.email, Usuario.id != current_user.id
        ).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este e-mail já está em uso por outro usuário.",
            )
        current_user.email = dados.email

    if dados.nome is not None:
        current_user.nome = dados.nome
    if dados.telefone is not None:
        current_user.telefone = dados.telefone

    db.commit()
    db.refresh(current_user)
    return current_user


# ── PUT /me/senha ───────────────────────────────
@router.put("/me/senha")
def alterar_senha(
    dados: SenhaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Altera a senha do usuário logado."""
    if not verificar_senha(dados.senha_atual, current_user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta.",
        )

    if dados.nova_senha != dados.confirmar_senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha e a confirmação não coincidem.",
        )

    current_user.senha_hash = hash_senha(dados.nova_senha)
    db.commit()
    return {"detail": "Senha atualizada com sucesso."}


# ── PUT /me/foto ────────────────────────────────
@router.put("/me/foto", response_model=UsuarioResponse)
def upload_foto(
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Faz upload da foto de perfil do usuário."""
    # Validar tipo de arquivo
    allowed = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if foto.content_type not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de arquivo inválido. Aceitos: JPG, PNG, GIF, WebP.",
        )

    # Validar tamanho (2MB)
    contents = foto.file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo muito grande. Máximo: 2MB.",
        )
    foto.file.seek(0)

    # Criar diretório de uploads
    upload_dir = os.path.join(settings.UPLOAD_DIR, "avatars")
    os.makedirs(upload_dir, exist_ok=True)

    # Remover foto anterior se existir
    if current_user.foto_url:
        old_path = current_user.foto_url.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)

    # Salvar nova foto
    ext = foto.filename.split(".")[-1] if "." in foto.filename else "jpg"
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(foto.file, f)

    current_user.foto_url = f"/{filepath}"
    db.commit()
    db.refresh(current_user)
    return current_user


# ── DELETE /me ──────────────────────────────────
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def excluir_conta(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Exclui permanentemente a conta do usuário logado."""
    # Remover foto se existir
    if current_user.foto_url:
        old_path = current_user.foto_url.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)

    db.delete(current_user)
    db.commit()
    return None


# ── GET /buscar ─────────────────────────────────
@router.get("/buscar", response_model=list[UsuarioBuscaResponse])
def buscar_usuarios(
    q: str = Query(..., min_length=2, description="Nome para buscar"),
    tipo: str = Query(..., description="Tipo: 'aluno' ou 'mentor'"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Busca usuários pelo nome (para modal de criação/edição de equipes).
    Requer autenticação. Filtrado por tipo (aluno/mentor).
    """
    if tipo not in ("aluno", "mentor"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo deve ser 'aluno' ou 'mentor'.",
        )

    usuarios = (
        db.query(Usuario)
        .filter(Usuario.tipo == tipo, Usuario.nome.ilike(f"%{q}%"))
        .limit(20)
        .all()
    )
    return usuarios
