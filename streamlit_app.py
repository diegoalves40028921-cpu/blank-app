import streamlit as st
import pandas as pd
from PIL import Image
import base64
import io
import requests
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerenciador de Jovens da Crisma", page_icon="🕊️", layout="centered")

# --- LINKS ---
url_planilha_csv = "https://docs.google.com/spreadsheets/d/182OkAojppcXhIyxDiVlzY-bcFscW-pN3T8EJdQNc1Sc/export?format=csv"
url_script_google = "https://script.google.com/macros/s/AKfycbyPtxsjXFLO46Y9F9HEoqrtr8WqRxvesZp2qk8hPc_oIj120u6u2S3ULOLzLWLlloVaJg/exec"

# --- ESTILO CSS PARA O PERFIL ---
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .profile-card { background-color: white; border: 1px solid #DBDBDB; border-radius: 12px; padding: 24px; margin-top: 10px; box-shadow: 0px 4px 6px rgba(0,0,0,0.02); }
    .profile-name { font-size: 24px; font-weight: bold; color: #262626; margin-bottom: 4px; margin-top: 15px; }
    .profile-detail { font-size: 14px; color: #8E8E8E; margin-bottom: 15px; }
    .badge-presenca { background-color: #E8F0FE; color: #1A73E8; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; display: inline-block; margin-bottom: 15px; }
    .alert-box { background-color: #FFEBEB; border-left: 4px solid #FF4B4B; color: #D93025; padding: 10px; border-radius: 4px; font-size: 13px; font-weight: bold; margin-bottom: 10px; }
    .section-title { font-size: 16px; font-weight: bold; color: #262626; margin-top: 15px; margin-bottom: 5px; display: flex; align-items: center; }
    .section-content { background-color: #F8F9FA; padding: 12px; border-radius: 8px; font-size: 14px; color: #4A4A4A; border: 1px solid #E0E0E0; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE CARREGAR DADOS ---
@st.cache_data(ttl=1)
def carregar_dados():
    colunas_necessarias = ["Nome", "Turma", "Presenca", "Batismo", "Eucaristia", "Qualidades", "Defeitos", "Foto"]
    try:
        response = requests.get(url_planilha_csv)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text), dtype=str)
            for col in colunas_necessarias:
                if col not in df.columns:
                    df[col] = ""
            return df
        elif response.status_code == 404:
            st.error("⚠️ **Erro 404: Planilha Privada!** No canto superior direito da Planilha, mude o acesso para 'Qualquer pessoa com o link'.")
            return pd.DataFrame(columns=colunas_necessarias)
        else:
            return pd.DataFrame(columns=colunas_necessarias)
    except Exception as e:
        return pd.DataFrame(columns=colunas_necessarias)

# --- FUNÇÃO PARA CONVERTER IMAGEM ---
def img_to_base64(image_file):
    if image_file:
        img = Image.open(image_file)
        img = img.convert("RGB")
        img = img.resize((350, 350))
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=60)
        return base64.b64encode(buffered.getvalue()).decode()
    return ""

# --- CONTEÚDO PRINCIPAL ---
st.title("🕊️ Gerenciador de Jovens da Crisma")

aba_perfil, aba_gerenciar = st.tabs(["🔍 Ver Perfil", "⚙️ Cadastrar / Gerenciar"])

# --- ABA 1: VISUALIZAR PERFIL DETALHADO ---
with aba_perfil:
    df = carregar_dados()
    
    if not df.empty:
        df = df.dropna(subset=["Nome"])
        df = df[df["Nome"].astype(str).str.strip() != ""]
        df = df[df["Nome"].astype(str).str.contains(r'[a-zA-Z]', na=False)]
        
    if df.empty:
        st.info("Nenhum perfil válido carregado. Registre o primeiro membro na aba ao lado.")
    else:
        st.markdown("### Selecione quem deseja visualizar:")
        col_t, col_n = st.columns(2)
        
        turma_f = col_t.selectbox("Filtrar por Turma", ["Todas", "Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"])
        df_filtrado = df if turma_f == "Todas" else df[df["Turma"] == turma_f]
        
        if df_filtrado.empty:
            st.warning("Nenhum crismando encontrado nesta turma.")
        else:
            nome_selecionado = col_n.selectbox("Escolha o Crismando", df_filtrado["Nome
