import streamlit as st
import pandas as pd
from PIL import Image
import base64
import io
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CrismaGram Pro", page_icon="📸", layout="centered")

# --- LINKS ---
url_planilha_csv = "https://docs.google.com/spreadsheets/d/182OkAojppcXhIyxDiVlzY-bcFscW-pN3T8EJdQNc1Sc/export?format=csv"

# ⚠️ COLE AQUI A NOVA URL GERADA NO PASSO 1
url_script_google = "COLE_A_NOVA_URL_AQUI"

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
        st.info("Nenhum perfil válido carregado. Registe o primeiro membro na aba ao lado.")
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
                if "data:image" in foto_string:
                    foto_string = foto_string.split(",")[-1]
                st.image(f"data:image/jpeg;base64,{foto_string}", width=220)
            else:
                st.warning("👤 Perfil sem foto de identificação disponível.")
                
            st.markdown(f'<div class="profile-name">{row["Nome"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="profile-detail">Membro da <strong>{row["Turma"]}</strong></div>', unsafe_allow_html=True)
            
            # Alertas de Sacramentos
            if str(row['Batismo']).strip().upper() == "NÃO":
                st.markdown('<div class="alert-box">⚠️ ATENÇÃO: SEM BATISMO</div>', unsafe_allow_html=True)
            if str(row['Eucaristia']).strip().upper() == "NÃO":
                st.markdown('<div class="alert-box">⚠️ ATENÇÃO: SEM 1ª EUCARISTIA</div>', unsafe_allow_html=True)
                
            # Nível de Presença
            presenca_val = row['Presenca'] if pd.notna(row['Presenca']) and str(row['Presenca']).strip() != "" else "Não informada"
            st.markdown(f'<div class="badge-presenca">Frequência/Presença: {presenca_val}</div>', unsafe_allow_html=True)
            
            # Qualidades e Defeitos Formatados
            qualidades_val = row['Qualidades'] if pd.notna(row['Qualidades']) and str(row['Qualidades']).strip() != "" else "Nenhuma qualidade registrada ainda."
            defeitos_val = row['Defeitos'] if pd.notna(row['Defeitos']) and str(row['Defeitos']).strip() != "" else "Nenhum defeito registrado."
            
            st.markdown('<div class="section-title">✅ Qualidades / Pontos Positivos:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="section-content">{qualidades_val}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="section-title">❌ Defeitos / Pontos a Melhorar:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="section-content">{defeitos_val}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# --- ABA 2: CADASTRAR OU ATUALIZAR ---
with aba_gerenciar:
    st.markdown("### 📝 Cadastrar ou Modificar Perfil")
    
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
        
        qualidades_input = st.text_area("Escreva as Qualidades:")
        defeitos_input = st.text_area("Escreva os Defeitos:")
        foto = st.file_uploader("Foto de Perfil", type=["jpg", "png"])
        
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
                    "Qualidades": qualidades_input, 
                    "Defeitos": defeitos_input,
                    "Foto": img_to_base64(foto) if foto else ""
                }
                
                try:
                    res = requests.post(url_script_google, json=payload)
                    if res.status_code == 200:
                        st.success("Dados salvos com sucesso!")
                        st.cache_data.clear()
                        st.rerun()
                    elif res.status_code == 401:
                        st.error("⚠️ **Erro 401: Não Autorizado!** Volte ao Apps Script e mude 'Quem tem acesso' para 'Qualquer pessoa'.")
                    else:
                        st.error(f"Erro ao enviar dados. Código HTTP: {res.status_code}")
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")
