"""
Model: HistoricoAlimento
Registros de contagem de alimentos por equipe.
Futuramente preenchido via API YOLO de detecção de alimentos.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base


class HistoricoAlimento(Base):
    __tablename__ = "historico_alimentos"

    id = Column(Integer, primary_key=True, index=True)
    equipe_id = Column(Integer, ForeignKey("equipes.id", ondelete="CASCADE"), nullable=False)
    data = Column(Date, nullable=False)
    item = Column(String(255), nullable=False)  # Ex: "Cestas Básicas Premium"
    quantidade = Column(Integer, nullable=False)
    unidade = Column(String(20), nullable=False, default="un")  # un, kg, etc.
    status = Column(String(20), nullable=False, default="concluido")  # concluido | pendente
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relacionamentos
    equipe = relationship("Equipe", back_populates="historico_alimentos")

    __table_args__ = (
        CheckConstraint(
            "status IN ('concluido', 'pendente')", name="ck_status_historico"
        ),
    )

    def __repr__(self):
        return f"<HistoricoAlimento(id={self.id}, item='{self.item}', qtd={self.quantidade})>"
