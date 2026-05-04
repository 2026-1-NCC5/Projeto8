import streamlit as st
import streamlit.components.v1 as components
import os
import re

# ─────────────────────────────────────────────
# 1. Configuração da página
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Conta Certo",
    page_icon=os.path.join("Frontend", "images", "ContaCerto_logo_Icon.png"),
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
    <style>
        .block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
        header, #MainMenu, footer { display: none !important; }
        .stApp { background-color: #f7f9fc !important; }
        iframe { width: 100vw !important; border: none !important; display: block; }
    </style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 2. Helpers
# ─────────────────────────────────────────────
def carregar_html(nome_arquivo):
    caminho = os.path.join("Frontend", nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()


def _script_navegacao(mapeamento: dict) -> str:
    """Gera script que mapeia seletores CSS → páginas Streamlit via postMessage."""
    bindings_js = ""
    for seletor, destino in mapeamento.items():
        bindings_js += f"""
        document.querySelectorAll('{seletor}').forEach(function(el) {{
            el.addEventListener('click', function(e) {{
                e.preventDefault();
                setComponentValue('{destino}');
            }});
        }});
"""
    return f"""
    <script>
        function sendMessageToStreamlitClient(type, data) {{
            var outData = Object.assign({{ isStreamlitMessage: true, type: type }}, data);
            window.parent.postMessage(outData, "*");
        }}
        function init() {{
            sendMessageToStreamlitClient("streamlit:componentReady", {{apiVersion: 1}});
        }}
        function setComponentValue(value) {{
            sendMessageToStreamlitClient("streamlit:setComponentValue", {{value: value}});
        }}
        window.addEventListener("message", function(event) {{
            if (event.data.type === "streamlit:render") {{
                sendMessageToStreamlitClient("streamlit:setFrameHeight", {{height: document.body.scrollHeight || 900}});
            }}
        }});
        init();
        {bindings_js}
    </script>
    """


def _renderizar_como_componente(html_content: str, mapeamento: dict, chave: str, altura: int = 900):
    """Injeta navegação e renderiza como componente interativo."""
    script = _script_navegacao(mapeamento)
    html_content = html_content.replace("</body>", script + "\n</body>")

    component_dir = os.path.join(os.getcwd(), ".streamlit_login_component")
    os.makedirs(component_dir, exist_ok=True)
    with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    comp = components.declare_component("login_component", path=component_dir)
    return comp(key=chave)


def _renderizar_simples(nome_arquivo: str, altura: int = 1000):
    """Renderiza páginas que não precisam devolver valor ao Python."""
    html_content = carregar_html(nome_arquivo)
    components.html(html_content, height=altura, scrolling=True)


def _handle_resultado(resultado):
    """Trata navegação comum (perfil/sair) e retorna True se processou."""
    if resultado in ("aluno_perfil", "admin_perfil", "login", "cadastro",
                     "admin_home", "admin_equipes", "admin_detalhes_equipe",
                     "aluno_home", "aluno_minha_equipe"):
        if resultado == "login":
            # Limpar sessão ao sair
            st.session_state["token"] = None
            st.session_state["usuario"] = None
        st.session_state["pagina_atual"] = resultado
        st.rerun()
        return True
    return False


# ── URL da API Backend ──────────────────────────
API_URL = "http://localhost:8000"

if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = "login"
if "token" not in st.session_state:
    st.session_state["token"] = None
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

pagina = st.session_state["pagina_atual"]


# ── LOGIN ──────────────────────────────────────
if pagina == "login":
    html_content = carregar_html("login.html")
    html_content = re.sub(
        r"<script>(?:(?!</script>)[\s\S])*?login-form[\s\S]*?</script>",
        "",
        html_content,
    )
    script_login = """
    <script>
        function sendMessageToStreamlitClient(type, data) {
            var outData = Object.assign({ isStreamlitMessage: true, type: type }, data);
            window.parent.postMessage(outData, "*");
        }
        function init() {
            sendMessageToStreamlitClient("streamlit:componentReady", {apiVersion: 1});
        }
        function setComponentValue(value) {
            sendMessageToStreamlitClient("streamlit:setComponentValue", {value: value});
        }
        window.addEventListener("message", function(event) {
            if (event.data.type === "streamlit:render") {
                sendMessageToStreamlitClient("streamlit:setFrameHeight", {height: 800});
            }
        });
        init();
        document.getElementById('login-form').addEventListener('submit', function(e) {
            e.preventDefault();
            var email = document.getElementById('email').value;
            var senha = document.getElementById('password').value;

            var submitBtn = e.target.querySelector('button[type="submit"]');
            var originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = 'Entrando...';
            submitBtn.disabled = true;

            fetch('""" + API_URL + """/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, senha: senha })
            })
            .then(function(resp) {
                if (!resp.ok) {
                    return resp.json().then(function(err) { throw new Error(err.detail || 'Erro no login'); });
                }
                return resp.json();
            })
            .then(function(data) {
                var destino = 'aluno_home';
                if (data.usuario.tipo === 'admin') {
                    destino = 'admin_home';
                }
                var payload = JSON.stringify({
                    destino: destino,
                    token: data.access_token,
                    usuario: data.usuario
                });
                setComponentValue(payload);
            })
            .catch(function(err) {
                alert(err.message || 'Erro ao conectar com o servidor.');
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        });
        document.querySelectorAll('.btn-criar-conta').forEach(function(el) {
            el.addEventListener('click', function(e) {
                e.preventDefault();
                setComponentValue(JSON.stringify({ destino: 'cadastro' }));
            });
        });
    </script>
    """
    html_content = html_content.replace("</body>", script_login + "\n</body>")

    component_dir = os.path.join(os.getcwd(), ".streamlit_login_component")
    os.makedirs(component_dir, exist_ok=True)
    with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    login_comp = components.declare_component("login_component", path=component_dir)
    resultado = login_comp(key="login")

    if resultado:
        try:
            import json
            dados = json.loads(resultado)
            destino = dados.get("destino", "login")
            if dados.get("token"):
                st.session_state["token"] = dados["token"]
                st.session_state["usuario"] = dados["usuario"]
            st.session_state["pagina_atual"] = destino
            st.rerun()
        except (json.JSONDecodeError, TypeError):
            # Fallback para navegação simples (ex: cadastro)
            if resultado in ["admin_home", "aluno_home", "cadastro"]:
                st.session_state["pagina_atual"] = resultado
                st.rerun()

# ── CADASTRO ──────────────────────────────────
elif pagina == "cadastro":
    html_content = carregar_html("cadastro.html")
    resultado = _renderizar_como_componente(
        html_content,
        mapeamento={".btn-voltar-login": "login"},
        chave="cadastro",
        altura=900,
    )
    _handle_resultado(resultado)

# ── ADMIN HOME ────────────────────────────────
elif pagina == "admin_home":
    html_content = carregar_html("admin_home.html")
    resultado = _renderizar_como_componente(
        html_content,
        mapeamento={
            "#btn-acessar-equipes": "admin_equipes",
            ".btn-equipes-mobile": "admin_equipes",
            ".btn-perfil": "admin_perfil",
            ".btn-sair": "login",
        },
        chave="admin_home",
        altura=1000,
    )
    _handle_resultado(resultado)

# ── ADMIN EQUIPES ─────────────────────────────
elif pagina == "admin_equipes":
    html_content = carregar_html("admin_equipes.html")
    resultado = _renderizar_como_componente(
        html_content,
        mapeamento={
            ".btn-iniciar-contagem": "admin_detalhes_equipe",
            ".btn-home": "admin_home",
            ".btn-perfil": "admin_perfil",
            ".btn-sair": "login",
        },
        chave="admin_equipes",
        altura=1000,
    )
    _handle_resultado(resultado)

# ── ADMIN DETALHES EQUIPE ─────────────────────
elif pagina == "admin_detalhes_equipe":
    html_content = carregar_html("admin_detalhes_equipe.html")
    resultado = _renderizar_como_componente(
        html_content,
        mapeamento={
            ".btn-equipes": "admin_equipes",
            ".btn-home": "admin_home",
            ".btn-perfil": "admin_perfil",
            ".btn-sair": "login",
        },
        chave="admin_detalhes_equipe",
        altura=1500,
    )
    _handle_resultado(resultado)

# ── ADMIN PERFIL ──────────────────────────────
elif pagina == "admin_perfil":
    html_content = carregar_html("admin_perfil.html")
    resultado = _renderizar_como_componente(
        html_content,
        mapeamento={
            ".btn-admin-home": "admin_home",
            ".btn-equipes-mobile": "admin_equipes",
            ".btn-sair": "login",
        },
        chave="admin_perfil",
        altura=1200,
    )
    _handle_resultado(resultado)

# ── ALUNO HOME ────────────────────────────────
elif pagina == "aluno_home":
    html_content = carregar_html("aluno_home.html")
    resultado = _renderizar_como_componente(
        html_content,
        mapeamento={
            ".btn-acessar-equipe": "aluno_minha_equipe",
            ".btn-perfil": "aluno_perfil",
            ".btn-sair": "login",
        },
        chave="aluno_home",
        altura=1000,
    )
    _handle_resultado(resultado)

# ── ALUNO MINHA EQUIPE ───────────────────────
elif pagina == "aluno_minha_equipe":
    html_content = carregar_html("aluno_minha_equipe.html")
    resultado = _renderizar_como_componente(
        html_content,
        mapeamento={
            ".btn-aluno-home": "aluno_home",
            ".btn-perfil": "aluno_perfil",
            ".btn-sair": "login",
        },
        chave="aluno_minha_equipe",
        altura=1500,
    )
    _handle_resultado(resultado)

# ── ALUNO PERFIL ──────────────────────────────
elif pagina == "aluno_perfil":
    html_content = carregar_html("aluno_perfil.html")
    resultado = _renderizar_como_componente(
        html_content,
        mapeamento={
            ".btn-aluno-home": "aluno_home",
            ".btn-sair": "login",
        },
        chave="aluno_perfil",
        altura=1200,
    )
    _handle_resultado(resultado)
