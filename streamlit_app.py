import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
import base64
import io

# Configuração da Página
st.set_page_config(page_title="CrismaGram Pro", page_icon="📸", layout="centered")

# --- ESTILO INSTAGRAM (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #EFEFEF; border-radius: 4px; padding: 10px 20px; font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #0095F6 !class; color: white !important; }
    
    /* Card do Post */
    .post-card {
        background-color: white; border: 1px solid #DBDBDB; border-radius: 8px;
        margin-bottom: 25px; padding: 0px; overflow: hidden;
    }
    .post-header { padding: 12px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #FAFAFA; }
    .post-img { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; background-color: #f0f0f0; }
    .post-content { padding: 12px; }
    .badge {
        padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-right: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM GOOGLE SHEETS ---
# No Streamlit Cloud, você colará o link da planilha nos "Secrets"
url = "COLE_AQUI_O_LINK_DA_SUA_PLANILHA_DO_GOOGLE" # Substitua pelo seu link

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    return conn.read(spreadsheet=url, usecols=[0,1,2,3,4,5,6,7])

# Função para converter imagem para texto (para salvar na planilha)
def img_to_base64(image_file):
    if image_file:
        img = Image.open(image_file)
        img = img.resize((400, 400)) # Otimiza o tamanho
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=70)
        return base64.b64encode(buffered.getvalue()).decode()
    return ""

# --- INTERFACE ---
st.title("📸 CrismaGram")

aba_feed, aba_novo = st.tabs(["🏠 Feed de Membros", "➕ Criar Novo Perfil"])

# --- ABA 1: FEED ---
with aba_feed:
    df = carregar_dados()
    
    filtro_turma = st.selectbox("🔍 Filtrar Turma:", ["Todas"] + sorted(df['Turma'].unique().tolist()))
    
    for index, row in df.iterrows():
        if filtro_turma != "Todas" and row['Turma'] != filtro_turma:
            continue
            
        # HTML do Card Estilo Instagram
        st.markdown(f"""
            <div class="post-card">
                <div class="post-header">
                    <div style="width: 32px; height: 32px; background: #E1306C; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                        {row['Nome'][0]}
                    </div>
                    <div style="font-weight: bold; color: #262626;">{row['Nome']}</div>
                </div>
        """, unsafe_allow_html=True)
        
        # Exibir Foto Real ou Placeholder
        if row['Foto'] and len(str(row['Foto'])) > 100:
            st.image(f"data:image/jpeg;base64,{row['Foto']}", use_column_width=True)
        else:
            st.markdown('<div style="width: 100%; height: 300px; background: #fafafa; display: flex; align-items: center; justify-content: center; color: #ccc;">Sem Foto</div>', unsafe_allow_html=True)
            
        # Conteúdo do Card
        status_batismo = "✅ Batizado" if row['Batismo'] else "❌ Sem Batismo"
        status_euca = "✅ 1ª Comunhão" if row['Eucaristia'] else "❌ Sem Eucaristia"
        cor_aviso = "#ED4956" if row['ParaTirar'] else "#ffffff"
        
        st.markdown(f"""
                <div class="post-content">
                    <div style="margin-bottom: 8px;">
                        <span class="badge" style="background: #EFEFEF; color: #262626;">{row['Turma']}</span>
                        <span class="badge" style="background: #0095F6; color: white;">{row['Presenca']}</span>
                    </div>
                    <div style="color: #262626; font-size: 14px; margin-bottom: 8px;">
                        <b>{row['Nome']}</b> {row['Notas']}
                    </div>
                    <div style="font-size: 12px; color: #8E8E8E;">
                        {status_batismo} • {status_euca}
                    </div>
                    {"<div style='color: #ED4956; font-weight: bold; font-size: 12px; margin-top: 5px;'>⚠️ SOLICITADO AFASTAR</div>" if row['ParaTirar'] else ""}
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- ABA 2: CADASTRO ---
with aba_novo:
    st.subheader("Publicar Novo Perfil")
    
    with st.form("form_registro", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        turma = st.selectbox("Turma", ["Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"])
        presenca = st.selectbox("Frequência", ["Muito Presente", "Médio", "Pouco Presente"])
        notas = st.text_area("Biografia / Notas")
        
        col_b, col_e, col_t = st.columns(3)
        batismo = col_b.checkbox("Batizado")
        eucaristia = col_e.checkbox("1ª Comunhão")
        tirar = col_t.checkbox("⚠️ Afastar")
        
        arquivo_foto = st.file_uploader("📷 Carregar Foto do Crismando", type=["jpg", "png", "jpeg"])
        
        if st.form_submit_button("Publicar Perfil"):
            if nome:
                foto_base64 = img_to_base64(arquivo_foto)
                
                # Criar nova linha
                nova_linha = pd.DataFrame([{
                    "Nome": nome,
                    "Turma": turma,
                    "Presenca": presenca,
                    "Notas": notas,
                    "Batismo": batismo,
                    "Eucaristia": eucaristia,
                    "ParaTirar": tirar,
                    "Foto": foto_base64
                }])
                
                # Atualizar Planilha
                df_atualizado = pd.concat([df, nova_linha], ignore_index=True)
                conn.update(spreadsheet=url, data=df_atualizado)
                
                st.success("Perfil publicado com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha o nome.")
