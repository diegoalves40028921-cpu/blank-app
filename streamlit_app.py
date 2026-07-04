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
    df = carregar_dados()
    if df.empty:
        st.info("Nenhum perfil cadastrado.")
    else:
        df = df.dropna(subset=["Nome"])
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
