"""
Models: Equipe, EquipeMembro, EquipeMentor
Equipes vinculadas a semestres, com membros (alunos) e mentores.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class Equipe(Base):
    __tablename__ = "equipes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    semestre_id = Column(Integer, ForeignKey("semestres.id", ondelete="CASCADE"), nullable=False)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relacionamentos
    semestre = relationship("Semestre", back_populates="equipes")
    membros = relationship("EquipeMembro", back_populates="equipe", cascade="all, delete-orphan")
    mentores = relationship("EquipeMentor", back_populates="equipe", cascade="all, delete-orphan")
    historico_alimentos = relationship(
        "HistoricoAlimento", back_populates="equipe", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Equipe(id={self.id}, nome='{self.nome}')>"


class EquipeMembro(Base):
    """Associação N:N entre Equipe e Usuario (tipo=aluno)."""

    __tablename__ = "equipe_membros"

    id = Column(Integer, primary_key=True, index=True)
    equipe_id = Column(Integer, ForeignKey("equipes.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    adicionado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    equipe = relationship("Equipe", back_populates="membros")
    usuario = relationship("Usuario", back_populates="equipes_como_membro")

    __table_args__ = (
        UniqueConstraint("equipe_id", "usuario_id", name="uq_equipe_membro"),
    )

    def __repr__(self):
        return f"<EquipeMembro(equipe_id={self.equipe_id}, usuario_id={self.usuario_id})>"


class EquipeMentor(Base):
    """Associação N:N entre Equipe e Usuario (tipo=mentor)."""

    __tablename__ = "equipe_mentores"

    id = Column(Integer, primary_key=True, index=True)
    equipe_id = Column(Integer, ForeignKey("equipes.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    adicionado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    equipe = relationship("Equipe", back_populates="mentores")
    usuario = relationship("Usuario", back_populates="equipes_como_mentor")

    __table_args__ = (
        UniqueConstraint("equipe_id", "usuario_id", name="uq_equipe_mentor"),
    )

    def __repr__(self):
        return f"<EquipeMentor(equipe_id={self.equipe_id}, usuario_id={self.usuario_id})>"
