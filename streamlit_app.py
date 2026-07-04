import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
import base64
import io
import requests
import json

# Configuração da Página
st.set_page_config(page_title="CrismaGram Pro", page_icon="📸", layout="centered")

# --- CONFIGURAÇÕES DE LINKS ---
# 1. Cole aqui o link normal de visualização da sua planilha
url_planilha = "COLE_AQUI_O_LINK_DA_SUA_PLANILHA_DO_GOOGLE"

# 2. Sua URL do App da Web (Script do Google) já configurada!
url_script_google = "https://script.google.com/macros/s/AKfycbzMq22vbopzFdvVD6gfliJu9McSAJetnmbEd_YxerKkJtuM4Fl9jwiKDUiUqug4gvhI4Q/exec"

# --- ESTILO INSTAGRAM (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #EFEFEF; border-radius: 4px; padding: 10px 20px; font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #0095F6 !important; color: white !important; }
    
    /* Card do Post */
    .post-card {
        background-color: white; border: 1px solid #DBDBDB; border-radius: 8px;
        margin-bottom: 25px; padding: 0px; overflow: hidden;
    }
    .post-header { padding: 12px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #FAFAFA; }
    .post-content { padding: 12px; }
    .badge {
        padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-right: 5px;
    }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        st.cache_data.clear()
        return conn.read(spreadsheet=url_planilha)
    except Exception:
        return pd.DataFrame(columns=["Nome", "Turma", "Presenca", "Notas", "Batismo", "Eucaristia", "ParaTirar", "Foto"])

# --- FUNÇÃO DE TRATAMENTO DE FOTO (JPEG + PNG) ---
def img_to_base64(image_file):
    if image_file:
        img = Image.open(image_file)
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.convert("RGBA").split()[3])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")
            
        img = img.resize((400, 400)) 
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=75)
        return base64.b64encode(buffered.getvalue()).decode()
    return ""

# --- INTERFACE ---
st.title("📸 CrismaGram")

aba_feed, aba_novo = st.tabs(["🏠 Feed de Membros", "➕ Criar Novo Perfil"])

# --- ABA 1: FEED ---
with aba_feed:
    df = carregar_dados()
    
    if df.empty or "Nome" not in df.columns:
        st.info("Nenhum perfil publicado ainda. Vá na aba 'Criar Novo Perfil'!")
    else:
        df = df.dropna(subset=["Nome"])
        turmas_disponiveis = ["Todas"] + sorted(df['Turma'].dropna().unique().tolist())
        filtro_
