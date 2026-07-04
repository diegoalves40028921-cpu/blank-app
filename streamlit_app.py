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

@st.cache_data(ttl=10)
def carregar_dados():
    try:
        return conn.read(spreadsheet=url_planilha)
    except:
        return pd.DataFrame(columns=["Nome", "Turma", "Presenca", "Batismo", "Eucaristia", "Qualidades", "Defeitos", "Foto"])

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
