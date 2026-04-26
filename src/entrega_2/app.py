import streamlit as st
import streamlit.components.v1 as components
import os
import re

# 1. Configuração da página Streamlit (Ocupar tela inteira)
st.set_page_config(page_title="Conta Certo", page_icon=os.path.join("Frontend", "images", "ContaCerto_logo_Icon.png"), layout="wide", initial_sidebar_state="collapsed")

# Remover o padding padrão do Streamlit e menus para o HTML ficar em Fullscreen
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
            max-width: 100%;
        }
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        /* Garantir que o contêiner principal do Streamlit tenha sempre fundo claro cobrindo a tela */
        .stApp {
            background-color: #f7f9fc !important;
        }
        
        /* Ajustar o iframe para ocupar a tela inteira */
        iframe {
            width: 100%;
            height: 100vh;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Função para carregar o conteúdo dos arquivos HTML originais
def carregar_html(nome_arquivo):
    caminho = os.path.join("Frontend", nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

# 3. Gerenciamento de Estado Inicial
if 'pagina_atual' not in st.session_state:
    st.session_state['pagina_atual'] = 'login'


# 4. Lógica de Roteamento e Renderização
if st.session_state['pagina_atual'] == 'login':
    html_content = carregar_html("login.html")
    
    # Remover apenas o script original do formulário, garantindo que não apague outros scripts (como o do olho mágico)
    html_content = re.sub(r"<script>(?:(?!</script>)[\s\S])*?login-form[\s\S]*?</script>", "", html_content)
    
    # Injetar um script que utiliza a API oficial de Custom Components do Streamlit
    # Isso permite que o Javascript do iFrame envie mensagens diretas ao backend Python!
    script_redirecionamento = """
    <script>
        function sendMessageToStreamlitClient(type, data) {
            var outData = Object.assign({
                isStreamlitMessage: true,
                type: type,
            }, data);
            window.parent.postMessage(outData, "*");
        }

        // Informar ao Streamlit que o componente está pronto
        function init() {
            sendMessageToStreamlitClient("streamlit:componentReady", {apiVersion: 1});
        }

        // Função para enviar o papel (admin ou aluno) para o Python
        function setComponentValue(value) {
            sendMessageToStreamlitClient("streamlit:setComponentValue", {value: value});
        }

        window.addEventListener("message", function(event) {
            if (event.data.type === "streamlit:render") {
                // Ajustar altura automaticamente
                sendMessageToStreamlitClient("streamlit:setFrameHeight", {height: 800});
            }
        });

        init();

        document.getElementById('login-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            
            if (email === 'admin@le.com') {
                setComponentValue('admin');
            } else if (email === 'aluno@le.com') {
                setComponentValue('aluno');
            } else {
                alert('Credenciais inválidas. Tente:\\nAdmin: admin@le.com\\nAluno: aluno@le.com');
            }
        });
    </script>
    """
    html_content = html_content.replace("</body>", script_redirecionamento + "\\n</body>")
    
    # Para capturar retornos em Python, precisamos usar 'declare_component' apontando para um diretório real.
    # Vamos criar uma pasta invisível temporária e jogar nosso HTML modificado lá.
    component_dir = os.path.join(os.getcwd(), ".streamlit_login_component")
    os.makedirs(component_dir, exist_ok=True)
    with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Declarar o componente
    login_component = components.declare_component("login_component", path=component_dir)
    
    # Chamar o componente e capturar o retorno do JS (role)
    role = login_component()
    
    # Se o Javascript enviou um valor, processamos o login
    if role in ['admin', 'aluno']:
        st.session_state['pagina_atual'] = role + "_home"
        st.rerun()

elif st.session_state['pagina_atual'] == 'admin_home':
    html_content = carregar_html("admin_home.html")
    components.html(html_content, height=1000, scrolling=True)

elif st.session_state['pagina_atual'] == 'aluno_home':
    html_content = carregar_html("aluno_home.html")
    components.html(html_content, height=1000, scrolling=True)
