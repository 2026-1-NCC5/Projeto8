"""
Seed de dados mockup para HistoricoAlimento.
92 registros novos usando os mesmos itens que já existem no banco,
distribuídos entre as 4 equipes no período de janeiro a junho de 2024.

Itens existentes no banco (mantidos para consistência):
  - Feijão
  - Arroz
  - Leite em Pó
  - Fubá
  - Macarrão
  - Açúcar
  - Óleo

Execute: python seed_mockup.py
(com o backend rodando ou .env configurado)
"""

from datetime import date
from database import SessionLocal, engine, Base
from models import HistoricoAlimento


REGISTROS = [
    # ── Janeiro ──────────────────────────────────────────────────────────────
    {"equipe_id": 1, "data": date(2024, 1, 3),  "item": "Feijão",       "quantidade": 120, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 1, 5),  "item": "Arroz",        "quantidade": 80,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 1, 8),  "item": "Leite em Pó",  "quantidade": 150, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 1, 10), "item": "Fubá",         "quantidade": 60,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 1, 12), "item": "Macarrão",     "quantidade": 500, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 1, 15), "item": "Açúcar",       "quantidade": 90,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 1, 17), "item": "Óleo",         "quantidade": 40,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 1, 19), "item": "Feijão",       "quantidade": 35,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 1, 22), "item": "Arroz",        "quantidade": 100, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 1, 24), "item": "Leite em Pó",  "quantidade": 75,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 1, 26), "item": "Fubá",         "quantidade": 130, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 1, 29), "item": "Macarrão",     "quantidade": 420, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 1, 31), "item": "Açúcar",       "quantidade": 60,  "unidade": "un", "status": "pendente"},

    # ── Fevereiro ────────────────────────────────────────────────────────────
    {"equipe_id": 2, "data": date(2024, 2, 2),  "item": "Óleo",         "quantidade": 75,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 2, 5),  "item": "Feijão",       "quantidade": 55,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 2, 7),  "item": "Arroz",        "quantidade": 50,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 2, 9),  "item": "Leite em Pó",  "quantidade": 95,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 2, 12), "item": "Fubá",         "quantidade": 110, "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 2, 14), "item": "Macarrão",     "quantidade": 160, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 2, 16), "item": "Açúcar",       "quantidade": 600, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 2, 19), "item": "Óleo",         "quantidade": 80,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 2, 21), "item": "Feijão",       "quantidade": 45,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 2, 23), "item": "Arroz",        "quantidade": 90,  "unidade": "un", "status": "pendente"},
    {"equipe_id": 4, "data": date(2024, 2, 26), "item": "Leite em Pó",  "quantidade": 40,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 2, 28), "item": "Fubá",         "quantidade": 120, "unidade": "un", "status": "concluido"},

    # ── Março ────────────────────────────────────────────────────────────────
    {"equipe_id": 2, "data": date(2024, 3, 1),  "item": "Macarrão",     "quantidade": 85,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 3, 4),  "item": "Açúcar",       "quantidade": 175, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 3, 6),  "item": "Óleo",         "quantidade": 550, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 3, 8),  "item": "Feijão",       "quantidade": 100, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 3, 11), "item": "Arroz",        "quantidade": 70,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 3, 13), "item": "Leite em Pó",  "quantidade": 65,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 3, 15), "item": "Fubá",         "quantidade": 130, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 3, 18), "item": "Macarrão",     "quantidade": 55,  "unidade": "un", "status": "pendente"},
    {"equipe_id": 2, "data": date(2024, 3, 20), "item": "Açúcar",       "quantidade": 110, "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 3, 22), "item": "Óleo",         "quantidade": 200, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 3, 25), "item": "Feijão",       "quantidade": 480, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 3, 27), "item": "Arroz",        "quantidade": 75,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 3, 29), "item": "Leite em Pó",  "quantidade": 85,  "unidade": "un", "status": "concluido"},

    # ── Abril ────────────────────────────────────────────────────────────────
    {"equipe_id": 3, "data": date(2024, 4, 1),  "item": "Fubá",         "quantidade": 140, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 4, 3),  "item": "Macarrão",     "quantidade": 70,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 4, 5),  "item": "Açúcar",       "quantidade": 130, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 4, 8),  "item": "Óleo",         "quantidade": 180, "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 4, 10), "item": "Feijão",       "quantidade": 700, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 4, 12), "item": "Arroz",        "quantidade": 45,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 4, 15), "item": "Leite em Pó",  "quantidade": 90,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 4, 17), "item": "Fubá",         "quantidade": 95,  "unidade": "un", "status": "pendente"},
    {"equipe_id": 3, "data": date(2024, 4, 19), "item": "Macarrão",     "quantidade": 150, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 4, 22), "item": "Açúcar",       "quantidade": 100, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 4, 24), "item": "Óleo",         "quantidade": 220, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 4, 26), "item": "Feijão",       "quantidade": 530, "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 4, 29), "item": "Arroz",        "quantidade": 80,  "unidade": "un", "status": "concluido"},

    # ── Maio ─────────────────────────────────────────────────────────────────
    {"equipe_id": 4, "data": date(2024, 5, 2),  "item": "Leite em Pó",  "quantidade": 160, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 5, 3),  "item": "Fubá",         "quantidade": 140, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 5, 6),  "item": "Macarrão",     "quantidade": 240, "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 5, 8),  "item": "Açúcar",       "quantidade": 800, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 5, 10), "item": "Óleo",         "quantidade": 110, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 5, 13), "item": "Feijão",       "quantidade": 120, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 5, 15), "item": "Arroz",        "quantidade": 55,  "unidade": "un", "status": "pendente"},
    {"equipe_id": 3, "data": date(2024, 5, 17), "item": "Leite em Pó",  "quantidade": 60,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 5, 20), "item": "Fubá",         "quantidade": 115, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 5, 22), "item": "Macarrão",     "quantidade": 170, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 5, 24), "item": "Açúcar",       "quantidade": 260, "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 5, 27), "item": "Óleo",         "quantidade": 650, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 5, 29), "item": "Feijão",       "quantidade": 125, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 5, 31), "item": "Arroz",        "quantidade": 110, "unidade": "un", "status": "concluido"},

    # ── Junho ─────────────────────────────────────────────────────────────────
    {"equipe_id": 2, "data": date(2024, 6, 3),  "item": "Leite em Pó",  "quantidade": 180, "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 6, 5),  "item": "Fubá",         "quantidade": 150, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 6, 7),  "item": "Macarrão",     "quantidade": 280, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 6, 10), "item": "Açúcar",       "quantidade": 900, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 6, 12), "item": "Óleo",         "quantidade": 130, "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 6, 14), "item": "Feijão",       "quantidade": 90,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 6, 17), "item": "Arroz",        "quantidade": 70,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 6, 19), "item": "Leite em Pó",  "quantidade": 140, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 6, 21), "item": "Fubá",         "quantidade": 125, "unidade": "un", "status": "pendente"},
    {"equipe_id": 3, "data": date(2024, 6, 24), "item": "Macarrão",     "quantidade": 190, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 6, 25), "item": "Açúcar",       "quantidade": 300, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 6, 26), "item": "Óleo",         "quantidade": 850, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 6, 27), "item": "Feijão",       "quantidade": 140, "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 6, 28), "item": "Arroz",        "quantidade": 100, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 6, 28), "item": "Leite em Pó",  "quantidade": 75,  "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 6, 28), "item": "Fubá",         "quantidade": 130, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 6, 29), "item": "Macarrão",     "quantidade": 160, "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 6, 29), "item": "Açúcar",       "quantidade": 200, "unidade": "un", "status": "concluido"},
    {"equipe_id": 4, "data": date(2024, 6, 30), "item": "Óleo",         "quantidade": 320, "unidade": "un", "status": "concluido"},
    {"equipe_id": 1, "data": date(2024, 6, 30), "item": "Feijão",       "quantidade": 950, "unidade": "un", "status": "concluido"},
    {"equipe_id": 2, "data": date(2024, 6, 30), "item": "Arroz",        "quantidade": 150, "unidade": "un", "status": "concluido"},
    {"equipe_id": 3, "data": date(2024, 6, 30), "item": "Leite em Pó",  "quantidade": 110, "unidade": "un", "status": "concluido"},
]


def seed_mockup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print(f"[*] Inserindo {len(REGISTROS)} registros de mockup...")

        for r in REGISTROS:
            registro = HistoricoAlimento(
                equipe_id=r["equipe_id"],
                data=r["data"],
                item=r["item"],
                quantidade=r["quantidade"],
                unidade=r["unidade"],
                peso=float(r["quantidade"]) * 1.25,
                status=r["status"],
            )
            db.add(registro)

        db.commit()
        print(f"   [OK] {len(REGISTROS)} registros inseridos com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"   [ERRO] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_mockup()