import streamlit as st
import google.generativeai as genai
import requests
import io
from PyPDF2 import PdfReader

# --- 1. CONFIGURAÇÃO DOS SEUS CADERNOS (COLOQUE OS IDs REAIS AQUI) ---
MEUS_CADERNOS = {
    "Caderno Sul - Vol 1": "SEU_ID_AQUI",
    "Caderno Nordeste - Gestão": "SEU_ID_AQUI",
    # Adicione os outros aqui seguindo o mesmo padrão
}

st.set_page_config(page_title="Assistente PEM Sudeste", layout="wide")

# --- 2. DESIGN E ESTILO ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0284C7 100%);
        padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px;
    }
</style>
<div class="main-header">
    <h1>🌊 Assistente PEM Sudeste</h1>
    <p>Inteligência Documental Rastreável</p>
</div>
""", unsafe_allow_html=True)

# --- 3. CONEXÃO SEGURA COM O GOOGLE AI ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Busca automática de modelo para evitar o erro "NotFound"
    modelo_nome = None
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            modelo_nome = m.name
            break
    
    if modelo_nome:
        model = genai.GenerativeModel(modelo_nome)
    else:
        st.error("Nenhum modelo de IA compatível encontrado.")
except Exception as e:
    st.error(f"Erro de conexão: {e}")

# --- 4. FUNÇÃO DE LEITURA DE PDF ---
def ler_pdf(file_id, nome_doc):
    try:
        url = f'https://drive.google.com/uc?id={file_id}'
        response = requests.get(url)
        f = io.BytesIO(response.content)
        reader = PdfReader(f)
        texto = ""
        for i, page in enumerate(reader.pages):
            texto += f"\n[ARQUIVO: {nome_doc} | PÁGINA: {i+1}]\n" + page.extract_text()
        return texto
    except:
        return ""

# --- 5. BARRA LATERAL (SELETOR) ---
st.sidebar.header("📚 Painel de Documentos")
selecionados = st.sidebar.multiselect("Selecione os cadernos para análise:", list(MEUS_CADERNOS.keys()))

contexto_pdf = ""
if selecionados:
    with st.sidebar.status("📖 Lendo PDFs...", expanded=False):
        for nome in selecionados:
            contexto_pdf += ler_pdf(MEUS_CADERNOS[nome], nome)
    st.sidebar.success(f"IA carregada com {len(selecionados)} documento(s).")

# Instrução para evitar invenções
instrucao_mestra = f"""Você é um Acadêmico Rigoroso.
BASE DE DADOS ATUAL:
{contexto_pdf if selecionados else 'NENHUM DOCUMENTO SELECIONADO.'}

REGRAS CRÍTICAS:
1. Responda APENAS com base no texto acima.
2. Se não estiver no texto, diga explicitamente que não encontrou nos cadernos selecionados.
3. Cite o nome do Caderno e a Página de cada informação.
4. Finalize com: '⚠️ *Aviso: Sou uma IA. Confira as informações nos cadernos oficiais.*'
"""

# --- 6. INTERFACE DE ABAS ---
aba1, aba2 = st.tabs(["🔮 Oráculo (Chat)", "⚖️ Comparador"])

with aba1:
    chat_box = st.container(height=400)
    if "mensagens" not in st.session_state: st.session_state.mensagens = []
    
    with chat_box:
        for m in st.session_state.mensagens: st.chat_message(m["role"]).write(m["content"])
            
    pergunta = st.chat_input("Sua dúvida técnica...")
    if pergunta:
        if not selecionados:
            st.error("Selecione um caderno na barra lateral primeiro!")
        else:
            chat_box.chat_message("user").write(pergunta)
            st.session_state.mensagens.append({"role": "user", "content": pergunta})
            
            with chat_box:
                with st.spinner("Consultando base oficial..."):
                    res = model.generate_content(instrucao_mestra + "\nPergunta: " + pergunta)
                    st.chat_message("assistant").write(res.text)
                    st.session_state.mensagens.append({"role": "assistant", "content": res.text})

with aba2:
    if len(selecionados) < 2:
        st.info("💡 Selecione ao menos 2 cadernos na barra lateral para comparar.")
    else:
        if st.button("Executar Comparação Real"):
            with st.spinner("Analisando documentos selecionados..."):
                res_comp = model.generate_content(instrucao_mestra + "\nTAREFA: Compare tecnicamente os cadernos selecionados.")
                st.markdown(res_comp.text)
