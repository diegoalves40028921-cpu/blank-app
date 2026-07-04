import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
import base64
import io
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
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
    .post-header { padding: 12px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #FAFAFA; font-weight: bold;}
    .post-content { padding: 12px; }
    .badge {
        padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-right: 5px;
        display: inline-block; background-color: #f0f2f6; color: #31333F;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO G-SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Define tempo de vida do cache para 60 segundos
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        df = conn.read(spreadsheet=url_planilha)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return pd.DataFrame(columns=["Nome", "Turma", "Presenca", "Notas", "Batismo", "Eucaristia", "ParaTirar", "Foto"])

# --- FUNÇÃO DE TRATAMENTO DE FOTO (JPEG + PNG) ---
def img_to_base64(image_file):
    if image_file:
        img = Image.open(image_file)
        # Lida com transparência (PNG) convertendo fundo para branco
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
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Atualizar Feed"):
            st.cache_data.clear()
            st.rerun()
            
    df = carregar_dados()
    
    if df.empty or "Nome" not in df.columns:
        st.info("Nenhum perfil publicado ainda. Vá na aba 'Criar Novo Perfil'!")
    else:
        # Limpa dados vazios e prepara os filtros
        df = df.dropna(subset=["Nome"])
        turmas_disponiveis = ["Todas"] + sorted(df['Turma'].dropna().astype(str).unique().tolist())
        
        filtro_turma = st.selectbox("Filtre por Turma:", turmas_disponiveis)
        
        if filtro_turma != "Todas":
            df = df[df["Turma"].astype(str) == filtro_turma]
            
        if df.empty:
            st.warning("Nenhum perfil encontrado para esta turma.")
            
        # Renderiza o Feed
        for index, row in df.iterrows():
            nome = row.get("Nome", "Sem Nome")
            turma = row.get("Turma", "-")
            foto_b64 = row.get("Foto", "")
            
            st.markdown(f"""
            <div class="post-card">
                <div class="post-header">
                    👤 {nome} • <span style="color: gray; font-weight: normal;">Turma {turma}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Exibe a imagem se existir
            if pd.notna(foto_b64) and foto_b64.strip() != "":
                try:
                    st.image(f"data:image/jpeg;base64,{foto_b64}", use_container_width=True)
                except Exception:
                    st.error("Erro ao carregar a imagem deste perfil.")
            else:
                st.info("Sem foto de perfil.")
            
            # Exibe o conteúdo abaixo da imagem
            st.markdown(f"""
            <div class="post-card" style="margin-top: -25px; border-top: none; border-top-left-radius: 0; border-top-right-radius: 0;">
                <div class="post-content">
                    <span class="badge">Presença: {row.get('Presenca', 0)}%</span>
                    <span class="badge">Nota: {row.get('Notas', 0)}</span>
                    <span class="badge">Batismo: {row.get('Batismo', 'Não')}</span>
                    <span class="badge">Eucaristia: {row.get('Eucaristia', 'Não')}</span>
                    <br><br>
                    <strong>Para melhorar/observações:</strong> {row.get('ParaTirar', 'Nenhuma observação.')}
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- ABA 2: CRIAR NOVO PERFIL ---
with aba_novo:
    st.subheader("Novo Perfil")
    
    with st.form("form_novo", clear_on_submit=True):
        nome_input = st.text_input("Nome do Crismando *")
        turma_input = st.text_input("Turma *")
        
        col_a, col_b = st.columns(2)
        with col_a:
            presenca_input = st.number_input("Presença (%)", min_value=0, max_value=100, step=1)
            batismo_input = st.selectbox("Possui Batismo?", ["Sim", "Não"])
        with col_b:
            notas_input = st.number_input("Nota Geral", min_value=0.0, max_value=10.0, step=0.1)
            eucaristia_input = st.selectbox("Fez Eucaristia?", ["Sim", "Não"])
            
        observacoes = st.text_area("O que precisa tirar/melhorar (Observações)")
        foto_upload = st.file_uploader("Subir Foto", type=["jpg", "jpeg", "png"])
        
        enviado = st.form_submit_button("Publicar Perfil", type="primary")
        
        if enviado:
            if not nome_input or not turma_input:
                st.error("Os campos Nome e Turma são obrigatórios!")
            else:
                with st.spinner("Processando e enviando dados..."):
                    # Converte a foto em string base64 se existir
                    foto_string = img_to_base64(foto_upload) if foto_upload else ""
                    
                    # Monta o pacote de dados (JSON) que vai para o Google Script
                    payload = {
                        "Nome": nome_input,
                        "Turma": turma_input,
                        "Presenca": presenca_input,
                        "Notas": notas_input,
                        "Batismo": batismo_input,
                        "Eucaristia": eucaristia_input,
                        "ParaTirar": observacoes,
                        "Foto": foto_string
                    }
                    
                    try:
                        # Envia os dados via POST para a URL do Google Script
                        resposta = requests.post(url_script_google, json=payload)
                        if resposta.status_code == 200:
                            st.success("Perfil publicado com sucesso!")
                            st.cache_data.clear() # Limpa o cache para mostrar o novo perfil
                        else:
                            st.error(f"Erro ao salvar. Código HTTP: {resposta.status_code}")
                    except Exception as e:
                        st.error(f"Erro de conexão com o servidor: {e}")
