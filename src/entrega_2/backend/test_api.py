"""Script de teste da API - valida todos os endpoints."""
import requests

BASE = "http://localhost:8000/api"
results = []

def test(name, ok):
    status = "✅" if ok else "❌"
    results.append((name, ok))
    print(f"  {status} {name}")

print("=" * 50)
print("TESTE DE INTEGRAÇÃO — API ContaCerto")
print("=" * 50)

# 1. Cadastro de aluno
print("\n── AUTENTICAÇÃO ──")
r = requests.post(f"{BASE}/auth/cadastro", json={
    "tipo": "aluno", "nome": "Novo Aluno", "email": "novo@teste.com",
    "telefone": "(11)12345-6789", "senha": "teste123",
    "ra": "99999999", "curso": "Administração"
})
test("POST /auth/cadastro (aluno)", r.status_code == 201)

# 2. Login aluno
r = requests.post(f"{BASE}/auth/login", json={"email": "novo@teste.com", "senha": "teste123"})
test("POST /auth/login (aluno)", r.status_code == 200)
token_aluno = r.json().get("access_token", "") if r.status_code == 200 else ""
h_aluno = {"Authorization": f"Bearer {token_aluno}"}

# 3. Login admin (usando admin do seed)
r = requests.post(f"{BASE}/auth/login", json={"email": "admin@le.com", "senha": "123456"})
test("POST /auth/login (admin)", r.status_code == 200)
token_admin = r.json().get("access_token", "") if r.status_code == 200 else ""
h_admin = {"Authorization": f"Bearer {token_admin}"}

# 4. Perfil
print("\n── PERFIL ──")
r = requests.get(f"{BASE}/usuarios/me", headers=h_aluno)
test("GET /usuarios/me (aluno)", r.status_code == 200 and r.json().get("nome") == "Novo Aluno")

r = requests.get(f"{BASE}/usuarios/me", headers=h_admin)
test("GET /usuarios/me (admin)", r.status_code == 200)

# 5. Atualizar perfil
r = requests.put(f"{BASE}/usuarios/me", headers=h_aluno, json={
    "nome": "Aluno Atualizado", "email": "novo@teste.com", "telefone": "(11)00000-0000"
})
test("PUT /usuarios/me", r.status_code == 200)

# 6. Alterar senha
r = requests.put(f"{BASE}/usuarios/me/senha", headers=h_aluno, json={
    "senha_atual": "teste123", "nova_senha": "nova456", "confirmar_senha": "nova456"
})
test("PUT /usuarios/me/senha", r.status_code == 200)

# 7. Semestres
print("\n── SEMESTRES ──")
r = requests.get(f"{BASE}/semestres", headers=h_admin)
test("GET /semestres", r.status_code == 200)
sems = r.json() if r.status_code == 200 else []
if sems:
    print(f"     Encontrados: {len(sems)} semestres")

# 8. Equipes (admin) — requer semestre_id
print("\n── EQUIPES ──")
sem_id = sems[0]["id"] if sems else 1
r = requests.get(f"{BASE}/equipes", headers=h_admin, params={"semestre_id": sem_id})
test("GET /equipes (admin)", r.status_code == 200)
equipes = []
if r.status_code == 200:
    eq = r.json()
    equipes = eq if isinstance(eq, list) else eq.get("items", [])
    print(f"     Encontradas: {len(equipes)} equipes")

# 9. Detalhe da equipe
if equipes:
    eid = equipes[0]["id"]
    r = requests.get(f"{BASE}/equipes/{eid}", headers=h_admin)
    test(f"GET /equipes/{eid} (detalhe)", r.status_code == 200)
    if r.status_code == 200:
        d = r.json()
        print(f"     Nome: {d.get('nome')}, Membros: {len(d.get('membros', []))}")

    # 10. Historico paginado
    r = requests.get(f"{BASE}/equipes/{eid}/historico?por_pagina=5&pagina=1", headers=h_admin)
    test(f"GET /equipes/{eid}/historico (paginado)", r.status_code == 200)
    if r.status_code == 200:
        h_data = r.json()
        print(f"     Pag {h_data.get('pagina')}/{h_data.get('total_paginas')}, Total: {h_data.get('total')}")

# 11. Equipe minha (aluno sem equipe)
r = requests.get(f"{BASE}/equipes/minha", headers=h_aluno)
test("GET /equipes/minha (aluno sem equipe)", r.status_code == 404)

# Resumo
print("\n" + "=" * 50)
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"RESULTADO: {passed}/{total} testes passaram")
if passed == total:
    print("🎉 Todos os testes passaram!")
else:
    failed = [name for name, ok in results if not ok]
    print(f"❌ Falharam: {', '.join(failed)}")
