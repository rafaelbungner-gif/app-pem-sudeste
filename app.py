import streamlit as st
import google.generativeai as genai
import requests
import io
from PyPDF2 import PdfReader

# --- 1. CONFIGURAÇÃO DOS SEUS CADERNOS (PREENCHA AQUI) ---
# Adicione todos os seus 22 cadernos seguindo o padrão: "Nome": "ID_DO_DRIVE"
MEUS_CADERNOS = {
    "Caderno Sul - Vol 1": "ID_SUL_1",
    "Caderno Sul - Vol 2": "ID_SUL_2",
    "Caderno Nordeste - Gestão": "ID_NORDESTE",
    "Caderno Nordeste - Pesca": "ID_PESCA_NE",
    # Adicione os outros 18 aqui...
}

st.set_page_config(page_title="PEM Sudeste - Inteligência Documental", layout="wide")

# --- 2. ESTILO VISUAL MODERNO ---
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
    <p>Leitura Técnica e Rastreável de Cadernos de Conservação</p>
</div>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES TÉCNICAS (Leitura do Drive) ---
def extrair_texto_pdf(file_id):
    try:
        url = f'https://drive.google.com/uc?id={file_id}'
        response = requests.get(url)
        f = io.BytesIO(response.content)
        reader = PdfReader(f)
        texto = ""
        for i, page in enumerate(reader.pages):
            texto += f"\n[FONTE: PÁGINA {i+1}]\n" + page.extract_text()
        return texto
    except:
        return ""

# --- 4. BARRA LATERAL (SELETOR DE FONTES) ---
st.sidebar.header("📚 Fontes de Conhecimento")
st.sidebar.write("Selecione até 2 cadernos para a IA analisar:")
selecionados = st.sidebar.multiselect("Cadernos ativos:", list(MEUS_CADERNOS.keys()), max_selections=2)

# Carregamento do texto na memória
contexto_documentos = ""
if selecionados:
    with st.sidebar.status("📖 Lendo documentos...", expanded=False):
        for nome in selecionados:
            id_drive = MEUS_CADERNOS[nome]
            contexto_documentos += f"\n--- INÍCIO DO ARQUIVO: {nome} ---\n"
            contexto_documentos += extrair_texto_pdf(id_drive)
    st.sidebar.success(f"{len(selecionados)} caderno(s) carregado(s)!")

# --- 5. CONFIGURAÇÃO DA IA ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

instrucao_base = """Você é um Acadêmico Rigoroso. 
REGRAS:
1. Responda APENAS com base no texto fornecido abaixo. 
2. Se a informação não estiver no texto, diga: 'Esta informação não consta nos cadernos selecionados'.
3. Sempre cite o Caderno e a Página (ex: Caderno Sul, pág. 12).
4. No final, adicione o aviso de que você é uma IA e as informações devem ser conferidas."""

# --- 6. INTERFACE DE ABAS ---
aba1, aba2 = st.tabs(["🔮 Oráculo (Consulta)", "⚖️ Comparador Técnico"])

with aba1:
    if not selecionados:
        st.warning("👈 Selecione ao menos um caderno na barra lateral para começar.")
    else:
        chat_container = st.container(height=400)
        if "mensagens" not in st.session_state: st.session_state.mensagens = []
        
        with chat_container:
            for m in st.session_state.mensagens: st.chat_message(m["role"]).write(m["content"])
            
        pergunta = st.chat_input("Sua dúvida técnica...")
        if pergunta:
            chat_container.chat_message("user").write(pergunta)
            st.session_state.mensagens.append({"role": "user", "content": pergunta})
            
            prompt = f"{instrucao_base}\n\nCONTEÚDO DOS CADERNOS:\n{contexto_documentos}\n\nPERGUNTA: {pergunta}"
            resposta = model.generate_content(prompt)
            
            chat_container.chat_message("assistant").write(resposta.text)
            st.session_state.mensagens.append({"role": "assistant", "content": resposta.text})

with aba2:
    if len(selecionados) < 2:
        st.info("💡 Selecione exatamente 2 cadernos na barra lateral para gerar uma comparação automática entre eles.")
    else:
        st.subheader(f"Análise Comparativa: {selecionados[0]} vs {selecionados[1]}")
        if st.button("Executar Comparação Técnica"):
            with st.spinner("Cruzando dados dos cadernos..."):
                prompt_comp = f"{instrucao_base}\n\nCONTEÚDO DOS CADERNOS:\n{contexto_documentos}\n\nTAREFA: Compare as abordagens desses dois cadernos sobre zoneamento e conflitos de uso. Aponte semelhanças e diferenças com rigor acadêmico."
                res_comp = model.generate_content(prompt_comp)
                st.markdown(res_comp.text)
