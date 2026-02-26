import streamlit as st
import google.generativeai as genai
import requests
import io
import re
from PyPDF2 import PdfReader

# --- 1. BASE DE DADOS COMPLETA (SUL E NE) ---
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

st.set_page_config(page_title="Assistente PEM", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0284C7 100%);
        padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px;
    }
</style>
<div class="main-header">
    <h1>🌊 Assistente PEM (Sul e Nordeste)</h1>
    <p>Busca Inteligente e Rastreável (Otimizada contra travamentos)</p>
</div>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA IA ---
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
    st.error(f"Erro de conexão com o Google AI: {e}")

# --- O FATIADOR DE PDFs ---
def ler_e_fatiar_pdf(file_id, nome_doc, regiao):
    paginas_fatiadas = []
    try:
        url = f'https://drive.google.com/uc?id={file_id}'
        response = requests.get(url)
        f = io.BytesIO(response.content)
        reader = PdfReader(f)
        
        for i, page in enumerate(reader.pages):
            texto_pagina = page.extract_text()
            if texto_pagina:
                cabecalho = f"[CADERNO: {regiao} - {nome_doc} | PÁGINA: {i+1}]"
                paginas_fatiadas.append({
                    "cabecalho": cabecalho,
                    "texto": texto_pagina.lower(),
                    "texto_original": texto_pagina
                })
        return paginas_fatiadas
    except:
        return []

# --- O BUSCADOR INTELIGENTE ---
def buscar_paginas_relevantes(pergunta, todas_as_paginas, limite_paginas=8):
    palavras_pergunta = re.findall(r'\w+', pergunta.lower())
    palavras_ignoradas = {'o', 'a', 'os', 'as', 'de', 'do', 'da', 'em', 'no', 'na', 'para', 'com', 'que', 'quais', 'qual', 'como', 'sobre'}
    palavras_chave = [p for p in palavras_pergunta if p not in palavras_ignoradas and len(p) > 2]
    
    if not palavras_chave:
        return todas_as_paginas[:limite_paginas]

    resultados = []
    for pag in todas_as_paginas:
        pontuacao = sum(1 for palavra in palavras_chave if palavra in pag["texto"])
        if pontuacao > 0:
            resultados.append((pontuacao, pag))
    
    resultados.sort(key=lambda x: x[0], reverse=True)
    melhores_paginas = [item[1] for item in resultados[:limite_paginas]]
    
    return melhores_paginas

# --- BARRA LATERAL ---
st.sidebar.header("📚 Seleção de Cadernos")
escolha_sul = st.sidebar.selectbox("📍 Região Sul:", list(CADERNOS_SUL.keys()))
escolha_ne = st.sidebar.selectbox("📍 Região Nordeste:", list(CADERNOS_NE.keys()))

if "todas_as_paginas_lidas" not in st.session_state:
    st.session_state.todas_as_paginas_lidas = []
if "cadernos_ativos" not in st.session_state:
    st.session_state.cadernos_ativos = []

cadernos_selecionados_agora = []
if escolha_sul != "Nenhum": cadernos_selecionados_agora.append(("SUL", escolha_sul, CADERNOS_SUL[escolha_sul]))
if escolha_ne != "Nenhum": cadernos_selecionados_agora.append(("NE", escolha_ne, CADERNOS_NE[escolha_ne]))

# Controle de Memória (Só baixa se você trocar de caderno)
if cadernos_selecionados_agora != st.session_state.cadernos_ativos:
    st.session_state.todas_as_paginas_lidas = []
    st.session_state.cadernos_ativos = cadernos_selecionados_agora
    
    if cadernos_selecionados_agora:
        with st.sidebar.status("📖 Baixando e fatiando documentos (Isso ocorre apenas 1 vez)...", expanded=False):
            for regiao, nome, file_id in cadernos_selecionados_agora:
                paginas = ler_e_fatiar_pdf(file_id, nome, regiao)
                st.session_state.todas_as_paginas_lidas.extend(paginas)
        st.sidebar.success("Livros prontos na mesa!")

# --- ABAS ---
aba1, aba2 = st.tabs(["🔮 Oráculo (Chat)", "⚖️ Comparador Regional"])

with aba1:
    chat_box = st.container(height=400)
    if "mensagens" not in st.session_state: st.session_state.mensagens = []
    with chat_box:
        for m in st.session_state.mensagens: st.chat_message(m["role"]).write(m["content"])
            
    pergunta = st.chat_input("Ex: Quais os impactos no turismo?")
    if pergunta:
        if not st.session_state.cadernos_ativos:
            st.error("Selecione ao menos um caderno na barra lateral!")
        else:
            chat_box.chat_message("user").write(pergunta)
            st.session_state.mensagens.append({"role": "user", "content": pergunta})
            
            with chat_box:
                with st.spinner("Buscando as páginas mais relevantes e lendo..."):
                    paginas_filtradas = buscar_paginas_relevantes(pergunta, st.session_state.todas_as_paginas_lidas, limite_paginas=8)
                    
                    contexto_enxuto = ""
                    for pag in paginas_filtradas:
                        contexto_enxuto += f"\n{pag['cabecalho']}\n{pag['texto_original']}\n"
                    
                    instrucao_mestra = f"""Você é um Acadêmico Rigoroso.
                    LEIA APENAS ESTES TRECHOS ESPECÍFICOS RETIRADOS DOS DOCUMENTOS:
                    {contexto_enxuto if contexto_enxuto else 'Nenhum trecho relevante encontrado.'}
                    
                    REGRAS:
                    1. Responda APENAS com base nos trechos acima.
                    2. Cite OBRIGATORIAMENTE o Caderno (Região e Nome) e a Página exata listada no cabeçalho de cada trecho.
                    3. Se a resposta não estiver nos trechos, diga: "Não encontrei essa informação."
                    4. Termine com o aviso: '⚠️ Aviso: Sou uma IA. Confira as informações nos cadernos oficiais.'
                    """
                    
                    try:
                        res = model.generate_content(instrucao_mestra + "\nPergunta: " + pergunta)
                        st.chat_message("assistant").write(res.text)
                        st.session_state.mensagens.append({"role": "assistant", "content": res.text})
                    except Exception as e:
                        st.error(f"Erro: Aguarde um momento e tente novamente. Detalhe: {e}")

with aba2:
    if len(st.session_state.cadernos_ativos) < 2:
        st.info("💡 Selecione um caderno do Sul e um do Nordeste para comparar.")
    else:
        st.subheader("Comparação Estratégica")
        if st.button("Executar Comparação Real"):
            with st.spinner("Buscando diretrizes principais em ambos os cadernos..."):
                paginas_comp = buscar_paginas_relevantes("diretrizes conflitos zoneamento conservação impacto", st.session_state.todas_as_paginas_lidas, limite_paginas=12)
                
                contexto_comp = ""
                for pag in paginas_comp:
                    contexto_comp += f"\n{pag['cabecalho']}\n{pag['texto_original']}\n"
                    
                prompt_comp = f"""Você é um analista rigoroso. Baseado APENAS nos trechos abaixo:
                {contexto_comp}
                TAREFA: Compare tecnicamente as abordagens regionais apresentadas nos trechos e cite os cadernos e as páginas de onde tirou cada informação."""
                
                try:
                    res_comp = model.generate_content(prompt_comp)
                    st.markdown(res_comp.text)
                except Exception as e:
                    st.error("Erro na comparação. Tente fazer uma pergunta mais específica no chat ou aguarde um momento.")
