import streamlit as st
import pandas as pd
from PIL import Image
import base64
import io
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CrismaGram Pro", page_icon="📸", layout="centered")

# --- LINKS ---
# Usamos o link de exportação em CSV para garantir que o texto longo da imagem não seja corrompido
url_planilha_csv = "https://docs.google.com/spreadsheets/d/182OkAojppcXhIyxDiVlzY-bcFscW-pN3T8EJdQNc1Sc/export?format=csv"
url_script_google = "https://script.google.com/macros/s/AKfycbzMq22vbopzFdvVD6gfliJu9McSAJetnmbEd_YxerKkJtuM4Fl9jwiKDUiUqug4gvhI4Q/exec"

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

# --- FUNÇÃO DE CARREGAR DADOS BLINDADA (SEM CORROMPER BASE64) ---
@st.cache_data(ttl=1)  # Atualização praticamente em tempo real
def carregar_dados():
    colunas_necessarias = ["Nome", "Turma", "Presenca", "Batismo", "Eucaristia", "Qualidades", "Defeitos", "Foto"]
    try:
        # Fazendo o download direto do CSV para evitar o comportamento de cache agressivo do conector padrão
        response = requests.get(url_planilha_csv)
        if response.status_code == 200:
            # Forçamos o pandas a ler TUDO como string pura para não misturar colunas ou quebrar o Base64
            df = pd.read_csv(io.StringIO(response.text), dtype=str)
            
            # Garante que todas as colunas necessárias existam
            for col in colunas_necessarias:
                if col not in df.columns:
                    df[col] = ""
            return df
        else:
            return pd.DataFrame(columns=colunas_necessarias)
    except Exception as e:
        return pd.DataFrame(columns=colunas_necessarias)

# --- FUNÇÃO PARA CONVERTER E COMPACTAR IMAGEM ---
def img_to_base64(image_file):
    if image_file:
        img = Image.open(image_file)
        img = img.convert("RGB")
        # Reduzimos um pouco o tamanho para 350x350 e qualidade 60% para garantir que caiba no Google Sheets sem cortar
        img = img.resize((350, 350)) 
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=60)
        return base64.b64encode(buffered.getvalue()).decode()
    return ""

# --- CONTEÚDO PRINCIPAL ---
st.title("📸 CrismaGram")

aba_perfil, aba_gerenciar = st.tabs(["🔍 Ver Perfil", "⚙️ Cadastrar / Atualizar"])

# --- ABA 1: VISUALIZAR PERFIL DETALHADO ---
with aba_perfil:
    df = carregar_dados()
    
    if not df.empty:
        # Limpeza estrita de linhas inválidas ou vazias
        df = df.dropna(subset=["Nome"])
        df = df[df["Nome"].astype(str).str.strip() != ""]
        df = df[df["Nome"].astype(str).str.contains(r'[a-zA-Z]', na=False)]
        
    if df.empty:
        st.info("Nenhum perfil cadastrado ainda. Vá na aba de gerenciamento ao lado!")
    else:
        st.markdown("### Selecione quem deseja visualizar:")
        col_t, col_n = st.columns(2)
        
        turma_f = col_t.selectbox("Filtrar por Turma", ["Todas", "Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"])
        df_filtrado = df if turma_f == "Todas" else df[df["Turma"] == turma_f]
        
        if df_filtrado.empty:
            st.warning("Nenhum crismando encontrado nesta turma.")
        else:
            nome_selecionado = col_n.selectbox("Escolha o Crismando", df_filtrado["Nome"].tolist())
            row = df_filtrado[df_filtrado["Nome"] == nome_selecionado].iloc[0]
            
            # --- CARD DO PERFIL ---
            st.markdown('<div class="profile-card">', unsafe_allow_html=True)
            
            # Exibição Inteligente da Foto
            foto_string = str(row['Foto']).strip() if pd.notna(row['Foto']) else ""
            if len(foto_string) > 100:
                # Remove possíveis quebras de página ou prefixos duplicados se houver
                if "data:image" in foto_string:
                    foto_string = foto_string.split(",")[-1]
                st.image(f"data:image/jpeg;base64,{foto_string}", width=220)
            else:
                st.warning("👤 Sem foto de identificação disponível ou imagem corrompida. Envie uma nova foto na aba ao lado.")
                
            st.markdown(f'<div class="profile-name">{row["Nome"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="profile-detail">Membro da <strong>{row["Turma"]}</strong></div>', unsafe_allow_html=True)
            
            # Alertas de Sacramentos
            if str(row['Batismo']).strip().upper() == "NÃO":
                st.markdown('<div class="alert-box">⚠️ ATENÇÃO: SEM BATISMO</div>', unsafe_allow_html=True)
            if str(row['Eucaristia']).strip().upper() == "NÃO":
                st.markdown('<div class="alert-box">⚠️ ATENÇÃO: SEM 1ª EUCARISTIA</div>', unsafe_allow_html=True)
                
            # Nível de Presença
            presenca_val = row['Presenca'] if pd.notna(row['Presenca']) and str(row['Presenca']).strip() != "" else "Média"
            st.markdown(f'<div class="badge-presenca">Frequência/Presença: {presenca_val}</div>', unsafe_allow_html=True)
            
            # Qualidades e Defeitos Formatados
            qualidades_val = row['Qualidades'] if pd.notna(row['Qualidades']) and str(row['Qualidades']).strip()
