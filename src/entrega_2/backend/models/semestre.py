"""
Model: Semestre
Períodos acadêmicos gerenciados pelo admin.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Date, DateTime, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base


class Semestre(Base):
    __tablename__ = "semestres"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)  # Ex: "2024.1 - Primavera"
    ano = Column(Integer, nullable=False)
    periodo = Column(String(20), nullable=False)  # "1º Semestre" | "2º Semestre"
    data_inicio = Column(Date, nullable=True)
    data_termino = Column(Date, nullable=True)
    status = Column(String(10), nullable=False, default="ativo")  # ativo | inativo
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relacionamentos
    equipes = relationship("Equipe", back_populates="semestre", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('ativo', 'inativo')", name="ck_status_semestre"),
    )

    def __repr__(self):
        return f"<Semestre(id={self.id}, nome='{self.nome}', status='{self.status}')>"
