import streamlit as st
import google.generativeai as genai
import requests
import io
from PyPDF2 import PdfReader

# --- 1. BASE DE DADOS ORGANIZADA POR REGIÃO ---
CADERNOS_SUL = {
    "Nenhum": None,
    "PESCA ARTESANAL": "1nnfAxqmZvnHKm4ZoVxexUoImDBBm3KuC",
    "PESCA INDUSTRIAL": "1wyb2gyxMZ-WWVK2kkWBG96fi0cRJXlTA",
    "AQUICULTURA": "1J4wtuiPfKtH00wYvzieckJKqXT-CtYfe",
    "PETRÓLEO E GÁS": "1pdR94_yc_mGPIO9vODRCHOzMkb6mbPcy",
    "ENERGIAS RENOVÁVEIS": "1lbRv2lQQNEBIsCJDz5Ha03w-ByaAwAJt",
    "GEOLOGIA E RECURSOS MINERAIS": "1AWbgrbaiqu5uzPTcpyABfD025J8rjWuO",
    "NAVEGAÇÃO, PORTOS E INDÚSTRIA NAVAL": "1ytOdHmuNLrMJk8laqU2XuBm9e0Zwgv8t",
    "SEGURANÇA E DEFESA": "1WQFgZYR4-CJZFVCXtz3ADNvoVqgDs8IG",
    "TURISMO": "1D9H11ZwDcmwanyWYBltPFXtVAX-Qzwrm",
    "MEIO AMBIENTE E MUDANÇA DO CLIMA": "1ONtkFycmqg72t4btG5LWLieqi8XQa20f",
    "MULTISSETORIAL INVESTIMENTOS": "1mKFtBk9lHezfl0vPzsO358AxZ_HNYmlk",
    "INTEGRAÇÃO GERCO PEM": "1bPIxGFANNbd4HbaUrB7Bhukd-HzsOoPZ"
}

CADERNOS_NE = {
    "Nenhum": None,
    "AQUICULTURA": "1kcOy8uKNonAWo5pA5Aj6ak_eRGhGkKFl",
    "SEGURANÇA E DEFESA": "1HCJygxjqxVPFz9Z6yEByi5fFSysi_aqC",
    "PETRÓLEO E GÁS NATURAL": "1lG1hWBnibfdX_5MJ_eGMpJS4mVHu4TMx",
    "MEIO AMBIENTE E MUDANÇA DO CLIMA": "18zN53AJAZaX445giWdN5FZyg6x3fwyG1",
    "ENERGIAS RENOVÁVEIS": "1LmPst6oY56lLpGK_TWXxFNG8-CdOS8zV",
    "GEOLOGIA E RECURSOS MINERAIS": "1_DD0NcFYmhB7YramfF7QTQTsV3ITMURo",
    "TURISMO": "1kdsI5bGdbIRIPLnXIsPfz9y3XwnY9B-4",
    "PESCA INDUSTRIAL": "1y_3pL2w6iOVZsQlmH0L-hmKUubX863mV",
    "PESCA ARTESANAL": "19arloC0UKOKjwOrQqeKDm7WJGFTkBT8x",
    "ENSINO E PESQUISA DO MAR": "1wYU6AV-4ATcn3kgKtodBXh8Ufs3i3xzA",
    "NAVEGAÇÃO, PORTOS E INDÚSTRIA NAVAL": "1VIqhy5ZmZhQOhNeYWoj2-HSZBkHmGiRR"
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
    <p>Inteligência Documental Rastreável por Região</p>
</div>
""", unsafe_allow_html=True)

# --- 3. CONEXÃO COM A IA ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    modelo_nome = None
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            modelo_nome = m.name
            break
    if modelo_nome:
        model = genai.GenerativeModel(modelo_nome)
except Exception as e:
    st.error(f"Erro de conexão: {e}")

# --- 4. FUNÇÃO DE LEITURA ---
def ler_pdf(file_id, nome_doc, regiao):
    try:
        url = f'https://drive.google.com/uc?id={file_id}'
        response = requests.get(url)
        f = io.BytesIO(response.content)
        reader = PdfReader(f)
        texto = ""
        for i, page in enumerate(reader.pages):
            texto += f"\n[DOC: {regiao} - {nome_doc} | PÁGINA: {i+1}]\n" + page.extract_text()
        return texto
    except:
        return ""

# --- 5. BARRA LATERAL (DOIS SELETORES) ---
st.sidebar.header("📚 Seleção de Cadernos")

# Seletor Região Sul
escolha_sul = st.sidebar.selectbox("📍 Região Sul:", list(CADERNOS_SUL.keys()))
# Seletor Região Nordeste
escolha_ne = st.sidebar.selectbox("📍 Região Nordeste:", list(CADERNOS_NE.keys()))

contexto_pdf = ""
selecionados_nomes = []

with st.sidebar.status("📖 Processando documentos...", expanded=False):
    if escolha_sul != "Nenhum":
        contexto_pdf += ler_pdf(CADERNOS_SUL[escolha_sul], escolha_sul, "SUL")
        selecionados_nomes.append(f"Sul ({escolha_sul})")
    
    if escolha_ne != "Nenhum":
        contexto_pdf += ler_pdf(CADERNOS_NE[escolha_ne], escolha_ne, "NE")
        selecionados_nomes.append(f"NE ({escolha_ne})")

if selecionados_nomes:
    st.sidebar.success(f"IA carregada: {', '.join(selecionados_nomes)}")
else:
    st.sidebar.warning("Nenhum caderno selecionado.")

# Instrução Mestra
instrucao_mestra = f"""Você é um Acadêmico Rigoroso.
BASE DE DADOS ATUAL:
{contexto_pdf if contexto_pdf else 'NENHUM DOCUMENTO SELECIONADO.'}

REGRAS CRÍTICAS:
1. Responda APENAS com base no texto acima.
2. Cite sempre o Caderno (Sul ou NE), o Tema e a Página.
3. Se não houver dados, informe que a informação não consta nos documentos carregados.
4. Finalize com: '⚠️ *Aviso: Sou uma IA. Confira as informações nos cadernos oficiais.*'
"""

# --- 6. INTERFACE DE ABAS COM TRATAMENTO DE COTA ---
aba1, aba2 = st.tabs(["🔮 Oráculo (Chat)", "⚖️ Comparador Regional"])

with aba1:
    chat_box = st.container(height=400)
    if "mensagens" not in st.session_state: st.session_state.mensagens = []
    with chat_box:
        for m in st.session_state.mensagens: st.chat_message(m["role"]).write(m["content"])
            
    pergunta = st.chat_input("Sua dúvida técnica...")
    if pergunta:
        if not selecionados_nomes:
            st.error("Selecione ao menos um caderno na barra lateral!")
        else:
            chat_box.chat_message("user").write(pergunta)
            st.session_state.mensagens.append({"role": "user", "content": pergunta})
            with chat_box:
                with st.spinner("Consultando base oficial..."):
                    try:
                        res = model.generate_content(instrucao_mestra + "\nPergunta: " + pergunta)
                        st.chat_message("assistant").write(res.text)
                        st.session_state.mensagens.append({"role": "assistant", "content": res.text})
                    except Exception as e:
                        if "429" in str(e) or "ResourceExhausted" in str(e):
                            st.error("⚠️ Limite de processamento atingido. Por favor, aguarde 60 segundos antes da próxima pergunta.")
                        else:
                            st.error(f"Erro inesperado: {e}")

with aba2:
    if len(selecionados_nomes) < 2:
        st.info("💡 Selecione um caderno do Sul E um do Nordeste para habilitar a comparação.")
    else:
        st.subheader(f"Comparação Técnica: {selecionados_nomes[0]} vs {selecionados_nomes[1]}")
        if st.button("Executar Comparação Real"):
            with st.spinner("Analisando documentos (isso pode demorar devido ao volume de dados)..."):
                try:
                    res_comp = model.generate_content(instrucao_mestra + "\nTAREFA: Realize uma comparação técnica entre as abordagens destes dois cadernos regionais.")
                    st.markdown(res_comp.text)
                except Exception as e:
                    if "429" in str(e) or "ResourceExhausted" in str(e):
                        st.error("⚠️ O volume de dados desses dois cadernos é muito grande para a cota gratuita. Tente comparar cadernos menores ou aguarde um minuto.")
                    else:
                        st.error(f"Erro na comparação: {e}")
