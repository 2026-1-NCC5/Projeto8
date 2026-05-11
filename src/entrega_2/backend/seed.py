"""
Script para popular o banco de dados com dados iniciais de teste.
Cria um admin, mentores, alunos, semestres, equipes e histórico.

Execute: python seed.py
"""

from datetime import date
from database import SessionLocal, engine, Base
from models import Usuario, Semestre, Equipe, EquipeMembro, EquipeMentor, HistoricoAlimento
from auth.security import hash_senha


def seed():
    # Criar tabelas
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Verificar se já existe dados
        if db.query(Usuario).first():
            print("[!] Banco ja possui dados. Seed cancelado.")
            print("   Para resetar, exclua as tabelas e execute novamente.")
            return

        print("[*] Populando banco de dados...")

        # ── Usuários ────────────────────────────
        admin = Usuario(
            nome="Admin Responsável", email="admin@le.com",
            telefone="(11) 91234-5678", senha_hash=hash_senha("123456"),
            tipo="admin",
        )

        mentores = [
            Usuario(nome="João Silva", email="joao.silva@le.com", telefone="(11) 99999-0001", senha_hash=hash_senha("123456"), tipo="mentor"),
            Usuario(nome="Ana Pereira", email="ana.pereira@le.com", telefone="(11) 99999-0002", senha_hash=hash_senha("123456"), tipo="mentor"),
            Usuario(nome="Roberto Gomes", email="roberto.gomes@le.com", telefone="(11) 99999-0003", senha_hash=hash_senha("123456"), tipo="mentor"),
            Usuario(nome="Fernanda Costa", email="fernanda.costa@le.com", telefone="(11) 99999-0004", senha_hash=hash_senha("123456"), tipo="mentor"),
            Usuario(nome="Marcos Oliveira", email="marcos.oliveira@le.com", telefone="(11) 99999-0005", senha_hash=hash_senha("123456"), tipo="mentor"),
        ]

        alunos = [
            Usuario(nome="Maria Oliveira", email="aluno@le.com", telefone="(11) 98765-4321", senha_hash=hash_senha("123456"), tipo="aluno", ra="12345678", curso="Ciência da Computação"),
            Usuario(nome="Carlos Souza", email="carlos.souza@email.com", telefone="(11) 98765-0002", senha_hash=hash_senha("123456"), tipo="aluno", ra="87654321", curso="Ciência da Computação"),
            Usuario(nome="Beatriz Lima", email="beatriz.lima@email.com", telefone="(11) 98765-0003", senha_hash=hash_senha("123456"), tipo="aluno", ra="11223344", curso="Administração"),
            Usuario(nome="Pedro Santos", email="pedro.santos@email.com", telefone="(11) 98765-0004", senha_hash=hash_senha("123456"), tipo="aluno", ra="44332211", curso="Administração"),
            Usuario(nome="Julia Ferreira", email="julia.ferreira@email.com", telefone="(11) 98765-0005", senha_hash=hash_senha("123456"), tipo="aluno", ra="55667788", curso="Publicidade e Propaganda"),
            Usuario(nome="Lucas Almeida", email="lucas.almeida@email.com", telefone="(11) 98765-0006", senha_hash=hash_senha("123456"), tipo="aluno", ra="99887766", curso="Relações Públicas"),
            Usuario(nome="Camila Rocha", email="camila.rocha@email.com", telefone="(11) 98765-0007", senha_hash=hash_senha("123456"), tipo="aluno", ra="33445566", curso="Relações Internacionais"),
        ]

        db.add(admin)
        db.add_all(mentores)
        db.add_all(alunos)
        db.flush()
        print(f"   [OK] {1 + len(mentores) + len(alunos)} usuarios criados")

        # ── Semestres ───────────────────────────
        sem_ativo = Semestre(
            nome="2024.1", ano=2024, periodo="1º Semestre",
            data_inicio=date(2024, 2, 5), data_termino=date(2024, 6, 30),
            status="ativo",
        )
        sem_inativo = Semestre(
            nome="2023.2", ano=2023, periodo="2º Semestre",
            data_inicio=date(2023, 8, 1), data_termino=date(2023, 12, 15),
            status="inativo",
        )
        db.add_all([sem_ativo, sem_inativo])
        db.flush()
        print("   [OK] 2 semestres criados")

        # ── Equipes ─────────────────────────────
        equipe_alpha = Equipe(nome="Alpha", semestre_id=sem_ativo.id)
        equipe_beta = Equipe(nome="Beta", semestre_id=sem_ativo.id)
        equipe_gamma = Equipe(nome="Gamma", semestre_id=sem_ativo.id)
        equipe_helios = Equipe(nome="Helios", semestre_id=sem_ativo.id)
        db.add_all([equipe_alpha, equipe_beta, equipe_gamma, equipe_helios])
        db.flush()

        # Membros (alunos nas equipes)
        db.add_all([
            EquipeMembro(equipe_id=equipe_alpha.id, usuario_id=alunos[0].id),
            EquipeMembro(equipe_id=equipe_alpha.id, usuario_id=alunos[1].id),
            EquipeMembro(equipe_id=equipe_beta.id, usuario_id=alunos[2].id),
            EquipeMembro(equipe_id=equipe_beta.id, usuario_id=alunos[3].id),
            EquipeMembro(equipe_id=equipe_gamma.id, usuario_id=alunos[4].id),
            EquipeMembro(equipe_id=equipe_gamma.id, usuario_id=alunos[5].id),
            EquipeMembro(equipe_id=equipe_helios.id, usuario_id=alunos[6].id),
        ])

        # Mentores nas equipes
        db.add_all([
            EquipeMentor(equipe_id=equipe_alpha.id, usuario_id=mentores[0].id),
            EquipeMentor(equipe_id=equipe_alpha.id, usuario_id=mentores[1].id),
            EquipeMentor(equipe_id=equipe_beta.id, usuario_id=mentores[2].id),
            EquipeMentor(equipe_id=equipe_gamma.id, usuario_id=mentores[3].id),
            EquipeMentor(equipe_id=equipe_helios.id, usuario_id=mentores[4].id),
        ])
        print("   [OK] 4 equipes criadas com membros e mentores")

        # ── Histórico de Alimentos ──────────────
        historicos = [
            HistoricoAlimento(equipe_id=equipe_alpha.id, data=date(2024, 5, 24), item="Cestas Básicas Premium", quantidade=450, unidade="un", status="concluido"),
            HistoricoAlimento(equipe_id=equipe_alpha.id, data=date(2024, 5, 21), item="Kits Higiene (Master)", quantidade=1200, unidade="un", status="concluido"),
            HistoricoAlimento(equipe_id=equipe_alpha.id, data=date(2024, 5, 18), item="Agasalhos Térmicos", quantidade=85, unidade="un", status="concluido"),
            HistoricoAlimento(equipe_id=equipe_alpha.id, data=date(2024, 5, 15), item="Leite em Pó Integral", quantidade=2085, unidade="un", status="concluido"),
            HistoricoAlimento(equipe_id=equipe_alpha.id, data=date(2024, 5, 12), item="Mantas de Lã", quantidade=1000, unidade="un", status="concluido"),
            HistoricoAlimento(equipe_id=equipe_beta.id, data=date(2024, 5, 20), item="Arroz 5kg", quantidade=300, unidade="un", status="concluido"),
            HistoricoAlimento(equipe_id=equipe_beta.id, data=date(2024, 5, 15), item="Feijão 1kg", quantidade=500, unidade="un", status="concluido"),
            HistoricoAlimento(equipe_id=equipe_gamma.id, data=date(2024, 5, 22), item="Óleo de Soja", quantidade=200, unidade="un", status="concluido"),
        ]
        db.add_all(historicos)
        print(f"   [OK] {len(historicos)} registros de historico criados")

        db.commit()
        print("\n[DONE] Seed concluido com sucesso!")
        print("\nCredenciais de teste:")
        print("   Admin:  admin@le.com / 123456")
        print("   Aluno:  aluno@le.com / 123456")
        print("   Mentor: joao.silva@le.com / 123456")

    except Exception as e:
        db.rollback()
        print(f"\n[ERRO] Erro no seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
