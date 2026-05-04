"""
Model: Usuario
Suporta 3 tipos: aluno, mentor, admin.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefone = Column(String(20), nullable=False)
    senha_hash = Column(String(255), nullable=False)
    tipo = Column(String(10), nullable=False, default="aluno")  # aluno | mentor | admin
    ra = Column(String(20), unique=True, nullable=True)  # somente aluno
    curso = Column(String(100), nullable=True)  # somente aluno
    foto_url = Column(String(500), nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relacionamentos
    equipes_como_membro = relationship(
        "EquipeMembro", back_populates="usuario", cascade="all, delete-orphan"
    )
    equipes_como_mentor = relationship(
        "EquipeMentor", back_populates="usuario", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("tipo IN ('aluno', 'mentor', 'admin')", name="ck_tipo_usuario"),
    )

    def __repr__(self):
        return f"<Usuario(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"
