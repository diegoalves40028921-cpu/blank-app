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
url_script_google = "https://script.google.com/macros/s/AKfycbwex6IBKOW418weukD9wdLlHVEA5fNXJkTGn2LwCF3TG1U9Dh0oMpTwVPA7Fnyk_XKvnA/exec"

# --- ESTILO CSS PARA O PERFIL ---
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .profile-card { background-color: white; border: 1px solid #DBDBDB; border-radius: 12px; padding: 24px; margin-top: 10px; box-shadow: 0px 4px 6px rgba(0,0,0,0.02); }
    .profile-name { font-size: 24px; font-weight: bold; color: #262626; margin-bottom: 4px; margin-top: 15px; }
    .profile-detail { font-size: 14px; color: #8E8E8E; margin-bottom: 15px; }
    .badge-presenca { background-color: #E8F0FE; color: #1A73E8; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; display: inline-block; margin-bottom: 15px; margin-top: 10px; }
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
            
            df = df.fillna("")
            
            if not df.empty:
                df["Nome_Limpo"] = df["Nome"].astype(str).str.strip()
                df = df[df["Nome_Limpo"] != ""]
                df = df[df["Nome_Limpo"].str.lower() != "nan"]
                df = df.drop(columns=["Nome_Limpo"])
                
            return df
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
    
    if df.empty:
        st.info("Nenhum perfil cadastrado ou disponível no momento.")
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
            
            # 1. Tratar a Foto
            foto_string = str(row['Foto']).strip() if pd.notna(row['Foto']) else ""
            if len(foto_string) > 100:
                if "data:image" in foto_string:
                    foto_string = foto_string.split(",")[-1]
                img_html = f'<img src="data:image/jpeg;base64,{foto_string}" style="width: 220px; border-radius: 8px; object-fit: cover; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);">'
            else:
                img_html = '<div style="background-color: #FFF3CD; padding: 10px; border-radius: 8px; color: #856404; font-size: 14px; text-align: center; width: 220px;">👤 Perfil sem foto</div>'
            
            # 2. Tratar Textos
            turma_val = row["Turma"] if str(row["Turma"]).strip() != "" else "Não informada"
            presenca_val = row['Presenca'] if pd.notna(row['Presenca']) and str(row['Presenca']).strip() != "" else "Não informada"
            qualidades_val = row['Qualidades'] if pd.notna(row['Qualidades']) and str(row['Qualidades']).strip() != "" else "Nenhuma qualidade registada ainda."
            defeitos_val = row['Defeitos'] if pd.notna(row['Defeitos']) and str(row['Defeitos']).strip() != "" else "Nenhum defeito registado."
            
            # 3. Tratar Alertas
            alertas_html = ""
            if str(row['Batismo']).strip().upper() == "NÃO":
                alertas_html += '<div class="alert-box">⚠️ ATENÇÃO: SEM BATISMO</div>'
            if str(row['Eucaristia']).strip().upper() == "NÃO":
                alertas_html += '<div class="alert-box">⚠️ ATENÇÃO: SEM 1ª EUCARISTIA</div>'
                
            # 4. Unir tudo numa única string sem quebras de linha para evitar bugs do Markdown
            html_card_completo = (
                f'<div class="profile-card">'
                f'{img_html}'
                f'<div class="profile-name">{row["Nome"]}</div>'
                f'<div class="profile-detail">Membro da <strong>{turma_val}</strong></div>'
                f'{alertas_html}'
                f'<div class="badge-presenca">Frequência/Presença: {presenca_val}</div>'
                f'<div class="section-title">✅ Qualidades / Pontos Positivos:</div>'
                f'<div class="section-content">{qualidades_val}</div>'
                f'<div class="section-title">❌ Defeitos / Pontos a Melhorar:</div>'
                f'<div class="section-content">{defeitos_val}</div>'
                f'</div>'
            )
            
            # Renderiza o cartão final
            st.markdown(html_card_completo, unsafe_allow_html=True)

# --- ABA 2: CADASTRAR, EDITAR OU DELETAR ---
with aba_gerenciar:
    st.markdown("### 📝 Painel de Administração de Perfis")
    
    df_lista = carregar_dados()
    nomes_existentes = []
    if not df_lista.empty:
        nomes_existentes = [n for n in df_lista["Nome"].tolist() if str(n).strip() != ""]

    modo = st.radio("O que deseja fazer?", ["Criar novo perfil", "Editar perfil existente", "❌ Eliminar um perfil"], horizontal=True)
    
    # --- FLUXO 1: DELETAR PERFIL ---
    if modo == "❌ Eliminar um perfil":
        if not nomes_existentes:
            st.warning("Não há nenhum perfil registado para eliminar.")
        else:
            st.markdown("#### 🗑️ Eliminar Crismando definitivamente")
            nome_para_deletar = st.selectbox("Selecione o perfil que deseja APAGAR:", nomes_existentes, key="del_box")
            
            st.warning(f"⚠️ **Atenção:** Está prestes a apagar permanentemente o perfil de **{nome_para_deletar}** da folha de cálculo. Esta ação não pode ser revertida.")
            
            confirmou = st.checkbox(f"Estou ciente e quero eliminar permanentemente o perfil de {nome_para_deletar}.", value=False)
            
            if st.button("🔥 Confirmar Eliminação Definitiva", disabled=not confirmou, type="primary"):
                payload_delete = {"Nome": nome_para_deletar, "Acao": "EXCLUIR"}
                with st.spinner("A eliminar registo no Google Sheets..."):
                    try:
                        res = requests.post(url_script_google, json=payload_delete, allow_redirects=True)
                        if res.status_code == 200:
                            st.success(f"🎉 {res.text}")
                            st.cache_data.clear()
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error(f"Erro do servidor Google: {res.status_code}")
                    except Exception as e:
                        st.error(f"Erro de rede ao tentar eliminar: {e}")

    # --- FLUXO 2: FORMULÁRIO DE CRIAR / EDITAR ---
    else:
        val_nome = ""
        val_turma = "Turma 1"
        val_presenca = "Média"
        val_batismo = "Sim"
        val_eucaristia = "Sim"
        val_qualidades = ""
        val_defeitos = ""
        val_foto_atual = ""
        
        if modo == "Editar perfil existente" and nomes_existentes:
            nome_editado = st.selectbox("Escolha o Crismando para Modificar", nomes_existentes)
            val_nome = nome_editado
            
            dados_usuario = df_lista[df_lista["Nome"] == nome_editado].iloc[0]
            
            lista_turmas = ["Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"]
            val_turma = dados_usuario["Turma"] if dados_usuario["Turma"] in lista_turmas else "Turma 1"
            
            lista_presenca = ["Baixa", "Média", "Alta"]
            val_presenca = dados_usuario["Presenca"] if dados_usuario["Presenca"] in lista_presenca else "Média"
            
            val_batismo = "Não" if str(dados_usuario["Batismo"]).strip().upper() == "NÃO" else "Sim"
            val_eucaristia = "Não" if str(dados_usuario["Eucaristia"]).strip().upper() == "NÃO" else "Sim"
            
            val_qualidades = str(dados_usuario["Qualidades"]) if pd.notna(dados_usuario["Qualidades"]) and str(dados_usuario["Qualidades"]).strip() != "nan" else ""
            val_defeitos = str(dados_usuario["Defeitos"]) if pd.notna(dados_usuario["Defeitos"]) and str(dados_usuario["Defeitos"]).strip() != "nan" else ""
            val_foto_atual = str(dados_usuario["Foto"]).strip() if pd.notna(dados_usuario["Foto"]) else ""

        with st.form("form_cadastro", clear_on_submit=True):
            if modo != "Editar perfil existente" or not nomes_existentes:
                nome = st.text_input("Nome completo do Crismando *", value=val_nome)
            else:
                st.markdown(f"**Modificando o perfil de:** `{val_nome}`")
                nome = val_nome
                
            turmas_disponiveis = ["Turma 1", "Turma 2", "Turma 3", "Turma 4", "Turma 5"]
            idx_turma = turmas_disponiveis.index(val_turma)
            turma = st.selectbox("Turma", turmas_disponiveis, index=idx_turma)
            
            presencas_disponiveis = ["Baixa", "Média", "Alta"]
            idx_presenca = presencas_disponiveis.index(val_presenca)
            presenca = st.select_slider("Nível de Presença", options=presencas_disponiveis, value=val_presenca)
            
            col1, col2 = st.columns(2)
            idx_batismo = 1 if val_batismo == "Não" else 0
            batismo = col1.radio("Possui Batismo?", ["Sim", "Não"], index=idx_batismo)
            
            idx_eucaristia = 1 if val_eucaristia == "Não" else 0
            eucaristia = col2.radio("Fez 1ª Eucaristia?", ["Sim", "Não"], index=idx_eucaristia)
            
            qualidades_input = st.text_area("Escreva as Qualidades:", value=val_qualidades)
            defeitos_input = st.text_area("Escreva os Defeitos:", value=val_defeitos)
            
            if val_foto_atual and len(val_foto_atual) > 100:
                st.markdown("📷 **Foto atual guardada:**")
                if "data:image" in val_foto_atual:
                    val_foto_atual = val_foto_atual.split(",")[-1]
                st.image(f"data:image/jpeg;base64,{val_foto_atual}", width=100)
                foto = st.file_uploader("Deseja alterar a Foto de Perfil? (Deixe em branco para manter a atual)", type=["jpg", "png"])
            else:
                foto = st.file_uploader("Foto de Perfil", type=["jpg", "png"])
            
            if st.form_submit_button("🚀 Guardar / Atualizar Dados"):
                if not nome or not str(nome).strip():
                    st.error("O campo Nome é obrigatório!")
                else:
                    string_foto = img_to_base64(foto) if foto else (val_foto_atual if val_foto_atual else "")
                    
                    payload = {
                        "Nome": str(nome).strip(), 
                        "Turma": turma, 
                        "Presenca": presenca,
                        "Batismo": batismo, 
                        "Eucaristia": eucaristia,
                        "Qualidades": qualidades_input, 
                        "Defeitos": defeitos_input,
                        "Foto": string_foto,
                        "Acao": "SALVAR"
                    }
                    
                    with st.spinner("A conectar à base de dados do Google..."):
                        try:
                            res = requests.post(url_script_google, json=payload, allow_redirects=True)
                            if res.status_code == 200:
                                st.success(f"🎉 {res.text}")
                                st.cache_data.clear()
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error(f"Erro ao enviar os dados. Código HTTP: {res.status_code}")
                        except Exception as e:
                            st.error(f"Erro crítico de rede: {e}")
