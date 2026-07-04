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

@st.cache_data(ttl=5)
def carregar_dados():
    colunas_necessarias = ["Nome", "Turma", "Presenca", "Batismo", "Eucaristia", "Qualidades", "Defeitos", "Foto"]
    try:
        df = conn.read(spreadsheet=url_planilha)
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

aba_feed, aba_gerenciar = st.tabs(["🏠 Feed de Membros", "⚙️ Cadastrar / Atualizar Perfil"])

# --- ABA 1: FEED DE MEMBROS ---
with aba_feed:
    df = carregar_dados()
    
    if not df.empty:
        df = df.dropna(subset=["Nome"])
        df = df[df["Nome"].astype(str).str.strip() != ""]
        df = df[df["Nome"].astype(str).str.contains(r'[a-zA-Z]', na=False)]
    
    if df.empty:
        st.info("Nenhum perfil válido encontrado. Use a aba ao lado para adicionar o primeiro!")
    else:
        turma_f = st.selectbox("Filtrar por Turma", ["Todas", "Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"])
        if turma_f != "Todas":
            df = df[df["Turma"] == turma_f]

        for _, row in df.iterrows():
            with st.container():
                alertas = ""
                if str(row['Batismo']).strip().upper() == "NÃO": alertas += '<span class="alert-badge">SEM BATISMO</span>'
                if str(row['Eucaristia']).strip().upper() == "NÃO": alertas += '<span class="alert-badge">SEM 1ª EUCARISTIA</span>'
                
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
                
                presenca_val = row['Presenca'] if pd.notna(row['Presenca']) and str(row['Presenca']).strip() != "" else "Média"
                qualidades_val = row['Qualidades'] if pd.notna(row['Qualidades']) and str(row['Qualidades']).strip() != "" else "Nenhuma registrada"
                defeitos_val = row['Defeitos'] if pd.notna(row['Defeitos']) and str(row['Defeitos']).strip() != "" else "Nenhum registrado"

                st.markdown(f"""
                <div class="post-card" style="margin-top:-20px; border-top:none;">
                    <div class="post-content">
                        <span class="badge">Presença: {presenca_val}</span><br><br>
                        <strong>✅ Qualidades:</strong> {qualidades_val}<br>
                        <strong>❌ Defeitos:</strong> {defeitos_val}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- ABA 2: CADASTRAR OU ATUALIZAR ---
with aba_gerenciar:
    st.markdown("### 📝 Salvar Informações")
    st.caption("Dica: Se você digitar um **Nome** que já existe, o sistema irá atualizar os dados dele automaticamente em vez de criar uma cópia.")
    
    df_lista = carregar_dados()
    nomes_existentes = []
    if not df_lista.empty:
        df_lista = df_lista.dropna(subset=["Nome"])
        nomes_existentes = [n for n in df_lista["Nome"].tolist() if str(n).strip() != ""]

    # Opção de selecionar um nome existente para carregar ou digitar um novo
    modo = st.radio("Como deseja prosseguir?", ["Digitar um novo nome", "Selecionar um crismando existente para atualizar"])
    
    with st.form("form_cadastro", clear_on_submit=True):
        if modo == "Selecionar um crismando existente para atualizar" and nomes_existentes:
            nome = st.selectbox("Escolha o Crismando", nomes_existentes)
        else:
            nome = st.text_input("Nome completo do Crismando *")
            
        turma = st.selectbox("Turma", ["Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"])
        presenca = st.select_slider("Nível de Presença", options=["Baixa", "Média", "Alta"], value="Média")
        
        col1, col2 = st.columns(2)
        batismo = col1.radio("Possui Batismo?", ["Sim", "Não"])
        eucaristia = col2.radio("Fez 1ª Eucaristia?", ["Sim", "Não"])
        
        qualidades = st.text_area("Qualidades (Pontos Positivos)")
        defeitos = st.text_area("Defeitos (Pontos a melhorar)")
        foto = st.file_uploader("Foto de Perfil (Opcional ao atualizar)", type=["jpg", "png"])
        
        if st.form_submit_button("🚀 Salvar / Atualizar Dados"):
            if not nome or not str(nome).strip():
                st.error("O campo Nome é obrigatório!")
            else:
                payload = {
                    "Nome": str(nome).strip(), 
                    "Turma": turma, 
                    "Presenca": presenca,
                    "Batismo": batismo, 
                    "Eucaristia": eucaristia,
                    "Qualidades": qualidades, 
                    "Defeitos": defeitos,
                    "Foto": img_to_base64(foto) if foto else ""
                }
                try:
                    res = requests.post(url_script_google, json=payload)
                    if res.status_code == 200:
                        st.success(f"Dados salvos com sucesso!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Erro ao enviar dados para o Google Sheets.")
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")
