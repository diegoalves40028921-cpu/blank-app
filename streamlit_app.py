import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
import base64
import io
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CrismaGram Pro", page_icon="📸", layout="centered")

# --- LINKS ---
url_planilha = "https://docs.google.com/spreadsheets/d/182OkAojppcXhIyxDiVlzY-bcFscW-pN3T8EJdQNc1Sc/edit?usp=sharing"
url_script_google = "https://script.google.com/macros/s/AKfycbzMq22vbopzFdvVD6gfliJu9McSAJetnmbEd_YxerKkJtuM4Fl9jwiKDUiUqug4gvhI4Q/exec"

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .post-card { background-color: white; border: 1px solid #DBDBDB; border-radius: 8px; margin-bottom: 20px; overflow: hidden; }
    .post-header { padding: 12px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #FAFAFA; font-weight: bold;}
    .post-content { padding: 12px; }
    .badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-right: 5px; display: inline-block; background-color: #f0f2f6; }
    .alert-badge { background-color: #FF4B4B; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 5px; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÃO DE CARREGAR BLINDADA CONTRA ERROS ---
@st.cache_data(ttl=10)
def carregar_dados():
    colunas_necessarias = ["Nome", "Turma", "Presenca", "Batismo", "Eucaristia", "Qualidades", "Defeitos", "Foto"]
    try:
        df = conn.read(spreadsheet=url_planilha)
        # Se faltar alguma coluna na planilha, o Python cria na hora para não dar erro
        for col in colunas_necessarias:
            if col not in df.columns:
                df[col] = ""
        return df
    except:
        return pd.DataFrame(columns=colunas_necessarias)

def img_to_base64(image_file):
    if image_file:
        img = Image.open(image_file)
        img = img.convert("RGB")
        img = img.resize((400, 400)) 
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=75)
        return base64.b64encode(buffered.getvalue()).decode()
    return ""

st.title("📸 CrismaGram")

aba_feed, aba_novo, aba_editar = st.tabs(["🏠 Feed", "➕ Novo Perfil", "✏️ Editar"])

# --- ABA 1: FEED ---
with aba_feed:
    df = carregar_dados()
    if df.empty or df["Nome"].astype(str).str.strip().eq("").all():
        st.info("Nenhum perfil cadastrado. Crie um na aba ao lado!")
    else:
        df = df.dropna(subset=["Nome"])
        df = df[df["Nome"].astype(str).str.strip() != ""] # Remove linhas vazias
        
        turma_f = st.selectbox("Filtrar Turma", ["Todas", "Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"])
        if turma_f != "Todas":
            df = df[df["Turma"] == turma_f]

        for _, row in df.iterrows():
            with st.container():
                # Alertas de Sacramentos
                alertas = ""
                if str(row['Batismo']).upper() == "NÃO": alertas += '<span class="alert-badge">SEM BATISMO</span>'
                if str(row['Eucaristia']).upper() == "NÃO": alertas += '<span class="alert-badge">SEM 1ª EUCARISTIA</span>'
                
                st.markdown(f"""
                <div class="post-card">
                    <div class="post-header">
                        <span>👤 {row['Nome']} ({row['Turma']})</span>
                        <div>{alertas}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if pd.notna(row['Foto']) and len(str(row['Foto'])) > 100:
                    st.image(f"data:image/jpeg;base64,{row['Foto']}", use_container_width=True)
                
                st.markdown(f"""
                <div class="post-card" style="margin-top:-20px; border-top:none;">
                    <div class="post-content">
                        <span class="badge">Presença: {row['Presenca']}</span><br><br>
                        <strong>✅ Qualidades:</strong> {row['Qualidades']}<br>
                        <strong>❌ Defeitos:</strong> {row['Defeitos']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- ABA 2: NOVO PERFIL ---
with aba_novo:
    with st.form("novo_p"):
        nome = st.text_input("Nome completo")
        turma = st.selectbox("Turma", ["Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"])
        presenca = st.select_slider("Nível de Presença", options=["Baixa", "Média", "Alta"], value="Alta")
        
        col1, col2 = st.columns(2)
        batismo = col1.radio("Possui Batismo?", ["Sim", "Não"])
        eucaristia = col2.radio("Fez 1ª Eucaristia?", ["Sim", "Não"])
        
        qualidades = st.text_area("Qualidades (Pontos Positivos)")
        defeitos = st.text_area("Defeitos (Pontos a melhorar)")
        foto = st.file_uploader("Foto de Perfil", type=["jpg", "png"])
        
        if st.form_submit_button("Salvar Perfil"):
            if not nome:
                st.error("Por favor, preencha o Nome!")
            else:
                payload = {
                    "Nome": nome, "Turma": turma, "Presenca": presenca,
                    "Batismo": batismo, "Eucaristia": eucaristia,
                    "Qualidades": qualidades, "Defeitos": defeitos,
                    "Foto": img_to_base64(foto) if foto else "",
                    "action": "create"
                }
                try:
                    res = requests.post(url_script_google, json=payload)
                    if res.status_code == 200:
                        st.success("Salvo com sucesso!")
                        st.cache_data.clear()
                    else:
                        st.error("Erro no servidor do Google.")
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")

# --- ABA 3: EDITAR PERFIL ---
with aba_editar:
    df_edit = carregar_dados()
    df_edit = df_edit.dropna(subset=["Nome"])
    df_edit = df_edit[df_edit["Nome"].astype(str).str.strip() != ""]
    
    if not df_edit.empty:
        nome_edit = st.selectbox("Selecione quem deseja editar", df_edit["Nome"].tolist())
        user_data = df_edit[df_edit["Nome"] == nome_edit].iloc[0]
        
        with st.form("edit_p"):
            lista_turmas = ["Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"]
            idx_turma = lista_turmas.index(user_data["Turma"]) if user_data["Turma"] in lista_turmas else 0
            new_turma = st.selectbox("Nova Turma", lista_turmas, index=idx_turma)
            
            new_presenca = st.select_slider("Nova Presença", options=["Baixa", "Média", "Alta"], value=user_data["Presenca"] if user_data["Presenca"] in ["Baixa", "Média", "Alta"] else "Alta")
            new_batismo = st.radio("Novo Batismo", ["Sim", "Não"], index=0 if user_data["Batismo"] == "Sim" else 1)
            new_eucaristia = st.radio("Nova Eucaristia", ["Sim", "Não"], index=0 if user_data["Eucaristia"] == "Sim" else 1)
            new_qualidades = st.text_area("Novas Qualidades", value=str(user_data["Qualidades"]))
            new_defeitos = st.text_area("Novos Defeitos", value=str(user_data["Defeitos"]))
            
            st.info("Para trocar a foto, crie um novo perfil ou edite diretamente na planilha do Google.")
            
            if st.form_submit_button("Atualizar Dados"):
                payload_edit = {
                    "Nome": nome_edit, "Turma": new_turma, "Presenca": new_presenca,
                    "Batismo": new_batismo, "Eucaristia": new_eucaristia,
                    "Qualidades": new_qualidades, "Defeitos": new_defeitos,
                    "action": "edit"
                }
                res = requests.post(url_script_google, json=payload_edit)
                if res.status_code == 200:
                    st.success("Dados atualizados!")
                    st.cache_data.clear()
    else:
        st.info("Cadastre pelo menos um perfil para poder editar.")
