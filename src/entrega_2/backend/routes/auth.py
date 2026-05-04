"""
Rotas de autenticação: cadastro e login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.usuario import Usuario
from schemas.auth import LoginRequest, TokenResponse, UsuarioTokenInfo
from schemas.usuario import UsuarioCreate, UsuarioResponse
from auth.security import hash_senha, verificar_senha, criar_token_acesso
from config import settings

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


@router.post("/cadastro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastro(dados: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova conta de aluno ou mentor.
    Admins são promovidos diretamente no banco.
    """
    # Verificar email único
    if db.query(Usuario).filter(Usuario.email == dados.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail.",
        )

    # Validações específicas para aluno
    if dados.tipo == "aluno":
        if not dados.ra:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="RA é obrigatório para alunos.",
            )
        if not dados.curso:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Curso é obrigatório para alunos.",
            )
        if dados.curso not in settings.CURSOS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Curso inválido. Cursos aceitos: {', '.join(settings.CURSOS_VALIDOS)}",
            )
        # Verificar RA único
        if db.query(Usuario).filter(Usuario.ra == dados.ra).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário com este RA.",
            )

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        telefone=dados.telefone,
        senha_hash=hash_senha(dados.senha),
        tipo=dados.tipo,
        ra=dados.ra if dados.tipo == "aluno" else None,
        curso=dados.curso if dados.tipo == "aluno" else None,
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica o usuário e retorna um token JWT.
    """
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = criar_token_acesso(data={"sub": str(usuario.id), "tipo": usuario.tipo})

    return TokenResponse(
        access_token=token,
        usuario=UsuarioTokenInfo(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            tipo=usuario.tipo,
        ),
    )
