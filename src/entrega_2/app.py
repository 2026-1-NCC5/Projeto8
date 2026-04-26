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
        .block-container { padding: 0; max-width: 100%; }
        header, #MainMenu, footer { visibility: hidden; }
        .stApp { background-color: #f7f9fc !important; }
        iframe { width: 100%; height: 100vh; border: none; }
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

if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = "login"

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
            if (email === 'admin@le.com') {
                setComponentValue('admin_home');
            } else if (email === 'aluno@le.com') {
                setComponentValue('aluno_home');
            } else {
                alert('Credenciais inválidas. Tente:\\nAdmin: admin@le.com\\nAluno: aluno@le.com');
            }
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

    if resultado in ["admin_home", "aluno_home"]:
        st.session_state["pagina_atual"] = resultado
        st.rerun()

# ── ADMIN HOME ────────────────────────────────
elif pagina == "admin_home":
    html_content = carregar_html("admin_home.html")
    resultado = _renderizar_como_componente(
        html_content,
        mapeamento={"#btn-acessar-equipes": "admin_equipes"},
        chave="admin_home",
        altura=1000,
    )
    if resultado == "admin_equipes":
        st.session_state["pagina_atual"] = "admin_equipes"
        st.rerun()

# ── ADMIN EQUIPES ─────────────────────────────
elif pagina == "admin_equipes":
    html_content = carregar_html("admin_equipes.html")
    resultado = _renderizar_como_componente(
        html_content,
        mapeamento={
            ".btn-iniciar-contagem": "admin_detalhes_equipe",
            ".btn-home": "admin_home"
        },
        chave="admin_equipes",
        altura=1000,
    )
    if resultado == "admin_detalhes_equipe":
        st.session_state["pagina_atual"] = "admin_detalhes_equipe"
        st.rerun()
    elif resultado == "admin_home":
        st.session_state["pagina_atual"] = "admin_home"
        st.rerun()

# ── ADMIN DETALHES EQUIPE ─────────────────────
elif pagina == "admin_detalhes_equipe":
    _renderizar_simples("admin_detalhes_equipe.html", altura=1200)

# ── ALUNO HOME ────────────────────────────────
elif pagina == "aluno_home":
    _renderizar_simples("aluno_home.html", altura=1000)

# ── ALUNO MINHA EQUIPE ───────────────────────
elif pagina == "aluno_minha_equipe":
    _renderizar_simples("aluno_minha_equipe.html", altura=1000)
