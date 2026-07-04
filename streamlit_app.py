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

# --- CONEXÃO COM GOOGLE SHEETS ---
# Cole abaixo o link completo da sua planilha Google
url_planilha = "COLE_AQUI_O_LINK_DA_SUA_PLANILHA_DO_GOOGLE" 

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        return conn.read(spreadsheet=url_planilha)
    except Exception:
        return pd.DataFrame(columns=["Nome", "Turma", "Presenca", "Notas", "Batismo", "Eucaristia", "ParaTirar", "Foto"])

# --- FUNÇÃO DE TRATAMENTO DE FOTO (JPEG + PNG) ---
def img_to_base64(image_file):
    if image_file:
        # Abre a imagem enviada (pode ser PNG, JPEG, etc.)
        img = Image.open(image_file)
        
        # Se a imagem tiver transparência (comum em PNG), removemos para não dar erro no JPEG
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            # Cria um fundo branco do mesmo tamanho da imagem
            background = Image.new("RGB", img.size, (255, 255, 255))
            # Cola a imagem por cima do fundo branco usando a própria transparência como máscara
            background.paste(img, mask=img.convert("RGBA").split()[3])
            img = background
        elif img.mode != "RGB":
            # Converte outros formatos de cores comuns para RGB padrão
            img = img.convert("RGB")
            
        # Redimensiona a foto para um quadrado perfeito (estilo Instagram) e otimiza o peso
        img = img.resize((400, 400)) 
        
        # Transforma a imagem processada em texto seguro para guardar na planilha
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
        filtro_turma = st.selectbox("🔍 Filtrar Turma:", turmas_disponiveis)
        
        for index, row in df.iterrows():
            if filtro_turma != "Todas" and row['Turma'] != filtro_turma:
                continue
                
            nome_jovem = str(row['Nome'])
            letra_inicial = nome_jovem[0].upper() if nome_jovem else "👤"
            
            st.markdown(f"""
            <div class="post-card">
                <div class="post-header">
                    <div style="width: 32px; height: 32px; background: #E1306C; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                        {letra_inicial}
                    </div>
                    <div style="font-weight: bold; color: #262626;">{nome_jovem}</div>
                </div>
            """, unsafe_allow_html=True)
            
            foto_salva = row.get('Foto', "")
            if pd.notna(foto_salva) and len(str(foto_salva)) > 100:
                st.image("data:image/jpeg;base64," + str(foto_salva), use_container_width=True)
            else:
                st.markdown('<div style="width: 100%; height: 300px; background: #fafafa; display: flex; align-items: center; justify-content: center; color: #ccc;">Sem Foto</div>', unsafe_allow_html=True)
                
            status_batismo = "✅ Batizado" if row.get('Batismo') else "❌ Sem Batismo"
            status_euca = "✅ 1ª Comunhão" if row.get('Eucaristia') else "❌ Sem Eucaristia"
            
            st.markdown(f"""
                <div class="post-content">
                    <div style="margin-bottom: 8px;">
                        <span class="badge" style="background: #EFEFEF; color: #262626;">{row.get('Turma', 'Sem Turma')}</span>
                        <span class="badge" style="background: #0095F6; color: white;">{row.get('Presenca', 'Normal')}</span>
                    </div>
                    <div style="color: #262626; font-size: 14px; margin-bottom: 8px;">
                        <b>{nome_jovem}</b> {row.get('Notas', '')}
                    </div>
                    <div style="font-size: 12px; color: #8E8E8E;">
                        {status_batismo} • {status_euca}
                    </div>
            """, unsafe_allow_html=True)
            
            if row.get('ParaTirar'):
                st.markdown("<div style='color: #ED4956; font-weight: bold; font-size: 12px; margin-top: 5px;'>⚠️ SOLICITADO AFASTAR</div>", unsafe_allow_html=True)
                
            st.markdown("</div></div>", unsafe_allow_html=True)

# --- ABA 2: CADASTRO ---
with aba_novo:
    st.subheader("Publicar Novo Perfil")
    
    df_atual = carregar_dados()
    
    with st.form("form_registro", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        turma = st.selectbox("Turma", ["Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"])
        presenca = st.selectbox("Frequência", ["Muito Presente", "Médio", "Pouco Presente"])
        notas = st.text_area("Biografia / Notas")
        
        col_b, col_e, col_t = st.columns(3)
        batismo = col_b.checkbox("Batizado")
        eucaristia = col_e.checkbox("1ª Comunhão")
        tirar
