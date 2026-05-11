"""
Reset completo do banco: dropa todas as tabelas e re-executa o seed.
Execute: python reset_db.py
"""

from database import engine, Base
from models import (  # noqa: F401
    Usuario, Semestre, Equipe, EquipeMembro, EquipeMentor, HistoricoAlimento
)
from seed import seed

print("[1/2] Dropando todas as tabelas...")
Base.metadata.drop_all(bind=engine)
print("      Tabelas removidas.")

print("[2/2] Recriando tabelas e executando seed...")
seed()

print("\n✅ Banco resetado com sucesso! Pronto para rodar os testes.")
