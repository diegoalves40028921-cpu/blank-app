import streamlit as st
import json
import os

# Configuração inicial da página estilo Aplicativo de Celular
st.set_page_config(
    page_title="CrismaGram Pro",
    page_icon="📸",
    layout="centered"
)

# Estilização customizada para parecer o Instagram
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    div[data-testid="stBlock"] {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #DBDBDB;
        margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #0095F6;
        color: white;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar banco de dados temporário na memória compartilhada
if "dados_crismandos" not in st.session_state:
    st.session_state.dados_crismandos = [
        {
            "Nome": "Exemplo de Jovem",
            "Turma": "Turma 1",
            "Presenca": "Médio",
            "Notas": "Bem-vindo ao CrismaGram! Edite ou adicione novos perfis.",
            "Batismo": True,
            "Eucaristia": False,
            "ParaTirar": False
        }
    ]

# --- TOPO ESTILO INSTAGRAM ---
st.title("📸 CrismaGram")
st.caption("Gestão Unificada de Crismandos para Catequistas")

# Criação de Abas no Topo
aba_feed, aba_novo = st.tabs(["🏠 Feed de Perfis", "➕ Criar Novo Perfil"])

# --- ABA 1: FEED DE PERFIS ---
with aba_feed:
    # Filtro por turma
    filtro = st.selectbox("Filtrar por Turma:", ["Todas", "Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"])
    
    # Renderização dos Cards
    for idx, j in enumerate(st.session_state.dados_crismandos):
        if filtro != "Todas" and j["Turma"] != filtro:
            continue
            
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.write("# 👤") # Avatar temporário padrão web
                
            with col2:
                st.subheader(j["Nome"])
                st.write(f"**{j['Turma']}** • Frequência: {j['Presenca']}")
                st.write(f"_{j['Notas']}_")
                
                # Badges de Sacramentos
                status_b = "✅ Batizado" if j["Batismo"] else "❌ Sem Batismo"
                status_e = "✅ 1ª Comunhão" if j["Eucaristia"] else "❌ Sem Eucaristia"
                st.write(f"{status_b}  |  {status_e}")
                
                if j["ParaTirar"]:
                    st.warning("⚠️ Solicitado Afastamento")
                
                # Botão para remover perfil
                if st.button("🗑️ Excluir", key=f"del_{idx}"):
                    st.session_state.dados_crismandos.pop(idx)
                    st.rerun()

# --- ABA 2: CADASTRO DE NOVOS MEMBROS ---
with aba_novo:
    st.subheader("Nova Publicação de Perfil")
    
    with st.form("cadastro_jovem", clear_on_submit=True):
        nome = st.text_input("Nome Completo:")
        turma = st.selectbox("Escolha a Turma:", ["Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"])
        presenca = selectbox_presenca = st.selectbox("Frequência:", ["Muito Presente", "Médio", "Pouco Presente"])
        notas = st.text_input("Biografia / Notas do Jovem:")
        
        batismo = st.checkbox("Já possui Batismo")
        eucaristia = st.checkbox("Já possui 1ª Comunhão")
        tirar = st.checkbox("Marcar para Afastamento")
        
        enviado = st.form_submit_button("Publicar Perfil")
        
        if enviado:
            if not nome:
                st.error("O nome é obrigatório!")
            else:
                novo = {
                    "Nome": nome,
                    "Turma": turma,
                    "Presenca": presenca,
                    "Notas": text_notas if (text_notas := notas) else "Sem biografia.",
                    "Batismo": batismo,
                    "Eucaristia": eucaristia,
                    "ParaTirar": tirar
                }
                st.session_state.dados_crismandos.append(novo)
                st.success("Perfil publicado com sucesso! Vá para a aba 'Feed de Perfis'.")
                st.rerun()
