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

# --- ESTILO CSS PARA O PERFIL ---
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .profile-card { background-color: white; border: 1px solid #DBDBDB; border-radius: 12px; padding: 24px; margin-top: 10px; box-shadow: 0px 4px 6px rgba(0,0,0,0.02); }
    .profile-name { font-size: 24px; font-weight: bold; color: #262626; margin-bottom: 4px; }
    .profile-detail { font-size: 14px; color: #8E8E8E; margin-bottom: 15px; }
    .badge-presenca { background-color: #E8F0FE; color: #1A73E8; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; display: inline-block; margin-bottom: 15px; }
    .alert-box { background-color: #FFEBEB; border-left: 4px solid #FF4B4B; color: #D93025; padding: 10px; border-radius: 4px; font-size: 13px; font-weight: bold; margin-bottom: 10px; }
    .section-title { font-size: 16px; font-weight: bold; color: #262626; margin-top: 15px; margin-bottom: 5px; display: flex; align-items: center; }
    .section-content { background-color: #F8F9FA; padding: 12px; border-radius: 8px; font-size: 14px; color: #4A4A4A; border: 1px solid #E0E0E0; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=2)
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

aba_perfil, aba_gerenciar = st.tabs(["🔍 Ver Perfil", "⚙️ Cadastrar / Atualizar"])

# --- ABA 1: VISUALIZAR PERFIL DETALHADO ---
with aba_perfil:
    df = carregar_dados()
    
    if not df.empty:
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
            
            # Exibição da Foto
            if pd.notna(row['Foto']) and len(str(row['Foto'])) > 100:
                st.image(f"data:image/jpeg;base64,{row['Foto']}", width=250)
            else:
                st.info("👤 Este perfil está sem foto de identificação.")
                
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
            qualidades_val = row['Qualidades'] if pd.notna(row['Qualidades']) and str(row['Qualidades']).strip() != "" else "Nenhuma qualidade registrada ainda."
            defeitos_val = row['Defeitos'] if pd.notna(row['Defeitos']) and str(row['Defeitos']).strip() != "" else "Nenhum defeito ou ponto a melhorar registrado."
            
            st.markdown('<div class="section-title">✅ Qualidades / Pontos Positivos:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="section-content">{qualidades_val}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="section-title">❌ Defeitos / Pontos a Melhorar:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="section-content">{defeitos_val}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# --- ABA 2: CADASTRAR OU ATUALIZAR ---
with aba_gerenciar:
    st.markdown("### 📝 Cadastrar ou Modificar Perfil")
    st.caption("Se você digitar ou selecionar um nome que já existe, o sistema atualizará a linha dele na planilha.")
    
    df_lista = carregar_dados()
    nomes_existentes = []
    if not df_lista.empty:
        df_lista = df_lista.dropna(subset=["Nome"])
        nomes_existentes = [n for n in df_lista["Nome"].tolist() if str(n).strip() != ""]

    modo = st.radio("Como deseja prosseguir?", ["Criar novo perfil (Digitar)", "Editar um perfil existente (Selecionar)"])
    
    with st.form("form_cadastro", clear_on_submit=True):
        if modo == "Editar um perfil existente (Selecionar)" and nomes_existentes:
            nome = st.selectbox("Escolha o Crismando para Modificar", nomes_existentes)
        else:
            nome = st.text_input("Nome completo do Crismando *")
            
        turma = st.selectbox("Turma", ["Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"])
        presenca = st.select_slider("Nível de Presença", options=["Baixa", "Média", "Alta"], value="Média")
        
        col1, col2 = st.columns(2)
        batismo = col1.radio("Possui Batismo?", ["Sim", "Não"])
        eucaristia = col2.radio("Fez 1ª Eucaristia?", ["Sim", "Não"])
        
        qualidades = st.text_area("Escreva as Qualidades:")
        defeitos = st.text_area("Escreva os Defeitos:")
        foto = st.file_uploader("Foto de Perfil (Deixe em branco para manter a atual se estiver editando)", type=["jpg", "png"])
        
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
