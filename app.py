import streamlit as st
import google.generativeai as genai
import requests
import io
import re
from PyPDF2 import PdfReader

CADERNOS_SUL = {
    "Nenhum": None,
    "AQUICULTURA": "1J4wtuiPfKtH00wYvzieckJKqXT-CtYfe",
    "ENERGIAS RENOVÁVEIS": "1lbRv2lQQNEBIsCJDz5Ha03w-ByaAwAJt",
    "GEOLOGIA E RECURSOS MINERAIS": "1AWbgrbaiqu5uzPTcpyABfD025J8rjWuO",
    "INTEGRAÇÃO GERCO PEM": "1bPIxGFANNbd4HbaUrB7Bhukd-HzsOoPZ",
    "MEIO AMBIENTE E MUDANÇA DO CLIMA": "1ONtkFycmqg72t4btG5LWLieqi8XQa20f",
    "MULTISSETORIAL INVESTIMENTOS": "1mKFtBk9lHezfl0vPzsO358AxZ_HNYmlk",
    "NAVEGAÇÃO, PORTOS E INDÚSTRIA NAVAL": "1ytOdHmuNLrMJk8laqU2XuBm9e0Zwgv8t",
    "PESCA ARTESANAL": "1nnfAxqmZvnHKm4ZoVxexUoImDBBm3KuC",
    "PESCA INDUSTRIAL": "1wyb2gyxMZ-WWVK2kkWBG96fi0cRJXlTA",
    "PETRÓLEO E GÁS": "1pdR94_yc_mGPIO9vODRCHOzMkb6mbPcy",
    "SEGURANÇA E DEFESA": "1WQFgZYR4-CJZFVCXtz3ADNvoVqgDs8IG",
    "TURISMO": "1D9H11ZwDcmwanyWYBltPFXtVAX-Qzwrm"

    CADERNOS_NE = {
    "Nenhum": None,
    "AQUICULTURA": "1kcOy8uKNonAWo5pA5Aj6ak_eRGhGkKFl",
    "ENERGIAS RENOVÁVEIS": "1LmPst6oY56lLpGK_TWXxFNG8-CdOS8zV",
    "ENSINO E PESQUISA DO MAR": "1wYU6AV-4ATcn3kgKtodBXh8Ufs3i3xzA",
    "GEOLOGIA E RECURSOS MINERAIS": "1_DD0NcFYmhB7YramfF7QTQTsV3ITMURo",
    "MEIO AMBIENTE E MUDANÇA DO CLIMA": "18zN53AJAZaX445giWdN5FZyg6x3fwyG1",
    "NAVEGAÇÃO, PORTOS E INDÚSTRIA NAVAL": "1VIqhy5ZmZhQOhNeYWoj2-HSZBkHmGiRR",
    "PESCA ARTESANAL": "19arloC0UKOKjwOrQqeKDm7WJGFTkBT8x",
    "PESCA INDUSTRIAL": "1y_3pL2w6iOVZsQlmH0L-hmKUubX863mV",
    "PETRÓLEO E GÁS NATURAL": "1lG1hWBnibfdX_5MJ_eGMpJS4mVHu4TMx",
    "SEGURANÇA E DEFESA": "1HCJygxjqxVPFz9Z6yEByi5fFSysi_aqC",
    "TURISMO": "1kdsI5bGdbIRIPLnXIsPfz9y3XwnY9B-4"
}
}

import streamlit as st
import google.generativeai as genai
import requests
import io
import re
from PyPDF2 import PdfReader

# ============================================================================
# 🎨 CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Assistente PEM",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# 💅 ESTILOS CSS PERSONALIZADOS
# ============================================================================
st.markdown("""
<style>
    /* Fundo principal com gradiente suave */
    .stApp {
        background: linear-gradient(180deg, #F0F9FF 0%, #E0F2FE 100%);
    }
    
    /* Header principal com imagem de fundo do litoral brasileiro */
    .main-header {
        background-image: 
            linear-gradient(135deg, rgba(12, 74, 110, 0.85) 0%, rgba(3, 105, 161, 0.80) 50%, rgba(14, 165, 233, 0.85) 100%),
            url('https://images.unsplash.com/photo-1590523741831-ab7f85327541?w=1600&h=600&fit=crop&q=80');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        padding: 55px 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 15px 50px rgba(14, 165, 233, 0.35);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.12) 0%, transparent 60%);
        pointer-events: none;
        z-index: 0;
    }
    
    .main-header h1 {
        font-size: 3.5em;
        font-weight: 800;
        margin: 0;
        text-shadow: 3px 3px 8px rgba(0,0,0,0.5);
        position: relative;
        z-index: 1;
        letter-spacing: -1px;
    }
    
    .main-header p {
        font-size: 1.35em;
        margin-top: 12px;
        opacity: 0.98;
        position: relative;
        z-index: 1;
        font-weight: 400;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.4);
    }
    
    /* Badge de status */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 7px 18px;
        border-radius: 25px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 6px;
        background: rgba(255,255,255,0.18);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.25);
        transition: all 0.3s ease;
    }
    
    .status-badge:hover {
        background: rgba(255,255,255,0.28);
        transform: translateY(-2px);
    }
    
    /* Sidebar estilizada */
    .sidebar-section {
        background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 12px 0;
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 4px 15px rgba(12, 74, 110, 0.25);
    }
    
    .sidebar-section h4 {
        color: white;
        margin-bottom: 12px;
        font-size: 1em;
        font-weight: 600;
    }
    
    /* Lista de cadernos carregados */
    .loaded-notebooks {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border-radius: 12px;
        padding: 18px;
        margin: 15px 0;
        border: 1px solid #86EFAC;
        box-shadow: 0 3px 12px rgba(16, 185, 129, 0.15);
    }
    
    .loaded-notebook-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 0;
        border-bottom: 1px solid #BBF7D0;
        font-size: 0.9em;
    }
    
    .loaded-notebook-item:last-child {
        border-bottom: none;
    }
    
    .notebook-icon {
        font-size: 1.4em;
    }
    
    .notebook-region {
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 8px;
        font-size: 0.75em;
        text-transform: uppercase;
    }
    
    .region-sul {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
    }
    
    .region-ne {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
    }
    
    /* Links na sidebar */
    .source-link {
        display: flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border-radius: 12px;
        padding: 14px 16px;
        margin: 8px 0;
        text-decoration: none;
        color: #0C4A6E;
        font-weight: 600;
        font-size: 0.88em;
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .source-link:hover {
        background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%);
        color: white;
        border-color: #0284C7;
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.35);
    }
    
    .source-link-icon {
        font-size: 1.3em;
    }
    
    /* Métricas e stats */
    .metric-card {
        background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 100%);
        border-radius: 15px;
        padding: 22px;
        text-align: center;
        color: white;
        box-shadow: 0 6px 20px rgba(12, 74, 110, 0.35);
        margin: 15px 0;
    }
    
    .metric-value {
        font-size: 2.8em;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-label {
        font-size: 0.92em;
        opacity: 0.92;
        margin-top: 6px;
    }
    
    /* Divider na sidebar */
    .sidebar-divider {
        border-top: 2px dashed rgba(255,255,255,0.25);
        margin: 20px 0;
    }
    
    /* Divider decorativo */
    .wave-divider {
        height: 60px;
        background: url('image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%230EA5E9" fill-opacity="0.15" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,112C672,96,768,96,864,112C960,128,1056,160,1152,160C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
        background-size: cover;
        margin: 30px 0;
    }
    
    /* Esconder footer padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tabs personalizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    /* Selectbox estilizada */
    .stSelectbox label {
        color: #0C4A6E;
        font-weight: 600;
        font-size: 0.9em;
    }
    
    /* Botões personalizados */
    .stButton > button {
        background: linear-gradient(135deg, #0369A1 0%, #0EA5E9 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 🌊 HEADER PRINCIPAL COM IMAGEM DE FUNDO (LITORAL BRASILEIRO)
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🌊 Assistente PEM</h1>
    <p>Busca Inteligente e Rastreável</p>
    <div style="margin-top: 22px;">
        <span class="status-badge">✓ IA Ativa</span>
        <span class="status-badge">✓ PDF Indexado</span>
        <span class="status-badge">✓ Multi-Região</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# 🔧 CONFIGURAÇÃO DA IA
# ============================================================================
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
    st.error(f"⚠️ Erro de conexão com o Google AI: {e}")

# ============================================================================
# 📄 FUNÇÃO DE LEITURA DE PDF
# ============================================================================
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
    except Exception as ex:
        st.error(f"Erro ao ler PDF: {ex}")
        return []

# ============================================================================
# 🔍 BUSCADOR INTELIGENTE
# ============================================================================
def buscar_paginas_relevantes(pergunta, todas_as_paginas, limite_paginas=8):
    paginas_estruturais = []
    for pag in todas_as_paginas:
        match = re.search(r'PÁGINA:\s*(\d+)', pag['cabecalho'])
        if match and int(match.group(1)) <= 6:
            paginas_estruturais.append(pag)

    palavras_pergunta = re.findall(r'\w+', pergunta.lower())
    palavras_ignoradas = {'o', 'a', 'os', 'as', 'de', 'do', 'da', 'em', 'no', 'na', 
                          'para', 'com', 'que', 'quais', 'qual', 'como', 'sobre', 
                          'diferença', 'entre'}
    palavras_chave = [p for p in palavras_pergunta if p not in palavras_ignoradas and len(p) > 2]
    
    melhores_paginas = []
    if palavras_chave:
        resultados = []
        for pag in todas_as_paginas:
            pontuacao = sum(1 for palavra in palavras_chave if palavra in pag["texto"])
            if pontuacao > 0:
                resultados.append((pontuacao, pag))
        
        resultados.sort(key=lambda x: x[0], reverse=True)
        melhores_paginas = [item[1] for item in resultados[:limite_paginas]]
    
    paginas_finais = paginas_estruturais.copy()
    for pag in melhores_paginas:
        if pag not in paginas_finais:
            paginas_finais.append(pag)
            
    return paginas_finais

# ============================================================================
# 📚 BARRA LATERAL APRIMORADA
# ============================================================================
with st.sidebar:
    # Header da sidebar com ícone
    st.markdown("""
    <div style="text-align: center; padding: 20px 0; background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 100%); 
                border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(12, 74, 110, 0.3);">
        <div style="font-size: 4em; margin-bottom: 5px;">📚</div>
        <h3 style="color: white; margin: 10px 0; font-weight: 700;">Biblioteca PEM</h3>
        <p style="color: rgba(255,255,255,0.85); font-size: 0.85em; margin: 0;">Cadernos Setoriais Oficiais</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Links para os cadernos oficiais
    st.markdown("**🔗 Fontes Oficiais**")
    st.markdown("""
    <a href="https://www.marinha.mil.br/secirm/psrm/pem/cadernos-setoriais-pem-nordeste" 
       target="_blank" class="source-link">
        <span class="source-link-icon">🌴</span> Cadernos Nordeste
    </a>
    <a href="https://www.marinha.mil.br/secirm/pt-br/psrm/pem/cadernos-setoriais-pem-sul" 
       target="_blank" class="source-link">
        <span class="source-link-icon">🗺️</span> Cadernos Sul
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    
    # Seleção de cadernos - SEÇÕES COLORIDAS
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<h4>📍 Região Sul</h4>", unsafe_allow_html=True)
    escolha_sul = st.selectbox("", list(CADERNOS_SUL.keys()), key="sul_select", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<h4>📍 Região Nordeste</h4>", unsafe_allow_html=True)
    escolha_ne = st.selectbox("", list(CADERNOS_NE.keys()), key="ne_select", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    
    # Status dos cadernos ativos
    if "cadernos_ativos" not in st.session_state:
        st.session_state.cadernos_ativos = []
    if "todas_as_paginas_lidas" not in st.session_state:
        st.session_state.todas_as_paginas_lidas = []
    
    if st.session_state.cadernos_ativos:
        st.markdown("""
        <div class="loaded-notebooks">
            <h4 style="color: #059669; margin-top: 0; margin-bottom: 12px; font-weight: 700;">
                ✅ Cadernos Carregados
            </h4>
        """, unsafe_allow_html=True)
        
        for regiao, nome, _ in st.session_state.cadernos_ativos:
            if regiao == "SUL":
                icon = "🗺️"
                region_class = "region-sul"
            else:
                icon = "🌴"
                region_class = "region-ne"
            
            st.markdown(f"""
            <div class="loaded-notebook-item">
                <span class="notebook-icon">{icon}</span>
                <span class="notebook-region {region_class}">{regiao}</span>
                <span style="color: #374151; flex: 1; font-weight: 500;">{nome}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Contador de páginas
        total_paginas = len(st.session_state.todas_as_paginas_lidas)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_paginas}</div>
            <div class="metric-label">📄 Páginas Indexadas</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("👈 Selecione os cadernos acima para começar")

# ============================================================================
# 💾 CONTROLE DE ESTADO E CARREGAMENTO
# ============================================================================
cadernos_selecionados_agora = []
if escolha_sul and escolha_sul != "Nenhum": 
    cadernos_selecionados_agora.append(("SUL", escolha_sul, CADERNOS_SUL[escolha_sul]))
if escolha_ne and escolha_ne != "Nenhum": 
    cadernos_selecionados_agora.append(("NE", escolha_ne, CADERNOS_NE[escolha_ne]))

if cadernos_selecionados_agora != st.session_state.cadernos_ativos:
    st.session_state.todas_as_paginas_lidas = []
    st.session_state.cadernos_ativos = cadernos_selecionados_agora.copy()
    
    if cadernos_selecionados_agora:
        with st.sidebar.status("📖 Processando documentos...", expanded=True):
            for regiao, nome, file_id in cadernos_selecionados_agora:
                paginas = ler_e_fatiar_pdf(file_id, nome, regiao)
                st.session_state.todas_as_paginas_lidas.extend(paginas)
                st.write(f"✓ {regiao} - {nome}: **{len(paginas)}** páginas")
        st.sidebar.success(f"🎉 Pronto!")
        st.rerun()

# ============================================================================
# 📑 ABAS PRINCIPAIS
# ============================================================================
aba1, aba2 = st.tabs(["🔮 Oráculo (Chat)", "⚖️ Comparador Regional"])

with aba1:
    st.markdown("""
    <div style="background: white; border-radius: 15px; padding: 25px; 
                box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 20px;">
        <h3 style="color: #0C4A6E; margin-top: 0;">💬 Como posso ajudar?</h3>
        <p style="color: #64748B; margin-bottom: 0;">
            Faça perguntas sobre zoneamento, conservação, impactos ambientais, 
            turismo, pesca e demais temas dos cadernos PEM.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    chat_box = st.container()
    
    if "mensagens" not in st.session_state: 
        st.session_state.mensagens = []
    
    with chat_box:
        for m in st.session_state.mensagens:
            with st.chat_message(m["role"], avatar="👤" if m["role"] == "user" else "🤖"):
                st.markdown(m["content"])
    
    pergunta = st.chat_input("Ex: Quais os impactos no turismo costeiro?", key="chat_input")
    
    if pergunta:
        if not st.session_state.cadernos_ativos:
            st.error("⚠️ **Selecione ao menos um caderno na barra lateral!**")
        else:
            st.session_state.mensagens.append({"role": "user", "content": pergunta})
            
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("🔍 Buscando nas páginas mais relevantes..."):
                    paginas_filtradas = buscar_paginas_relevantes(
                        pergunta, 
                        st.session_state.todas_as_paginas_lidas, 
                        limite_paginas=8
                    )
                    
                    contexto_enxuto = ""
                    for pag in paginas_filtradas:
                        contexto_enxuto += f"\n{pag['cabecalho']}\n{pag['texto_original']}\n"
                    
                    # Mostrar fontes encontradas em expander
                    with st.expander(f"📚 {len(paginas_filtradas)} fontes consultadas", expanded=False):
                        for pag in paginas_filtradas:
                            st.markdown(f"**{pag['cabecalho']}**")
                    
                    instrucao_mestra = f"""Você é um Acadêmico Rigoroso especializado em Plano de Espaço Marinho.
                    LEIA APENAS ESTES TRECHOS ESPECÍFICOS RETIRADOS DOS DOCUMENTOS:
                    {contexto_enxuto if contexto_enxuto else 'Nenhum trecho relevante encontrado.'}
                    
                    REGRAS:
                    1. Responda APENAS com base nos trechos acima.
                    2. Cite OBRIGATORIAMENTE o Caderno (Região e Nome) e a Página exata.
                    3. Use formatação Markdown para melhor leitura.
                    4. Se a resposta não estiver nos trechos, diga: "Não encontrei essa informação nos documentos."
                    5. Termine com: '⚠️ *Aviso: Sou uma IA. Confira as informações nos cadernos oficiais.*'
                    """
                    
                    try:
                        res = model.generate_content(instrucao_mestra + "\n\nPergunta: " + pergunta)
                        st.markdown(res.text)
                        st.session_state.mensagens.append({"role": "assistant", "content": res.text})
                    except Exception as e:
                        st.error(f"⚠️ Erro: {e}")

with aba2:
    if len(st.session_state.cadernos_ativos) < 2:
        st.markdown("""
        <div style="background: #FFFBEB; border-radius: 15px; padding: 35px; 
                    border: 2px solid #FCD34D; text-align: center; box-shadow: 0 4px 15px rgba(245, 158, 11, 0.15);">
            <div style="font-size: 3.5em; margin-bottom: 15px;">💡</div>
            <h3 style="color: #92400E; margin-top: 0; font-size: 1.5em;">Comparação Regional</h3>
            <p style="color: #78350F; margin-bottom: 25px; font-size: 1.05em;">
                Selecione <strong>um caderno do Sul e um do Nordeste</strong> na barra lateral 
                para habilitar a comparação entre as regiões.
            </p>
            <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                <span style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                            color: white; padding: 10px 25px; border-radius: 25px; font-weight: 600;">
                    🗺️ Sul
                </span>
                <span style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); 
                            color: white; padding: 10px 25px; border-radius: 25px; font-weight: 600;">
                    🌴 Nordeste
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 100%); 
                    border-radius: 15px; padding: 25px; color: white; margin-bottom: 20px;
                    box-shadow: 0 6px 20px rgba(12, 74, 110, 0.35);">
            <h3 style="margin-top: 0; font-size: 1.4em;">⚖️ Comparação Estratégica Regional</h3>
            <p style="margin-bottom: 0; opacity: 0.92;">
                Analise diferenças e similaridades nas diretrizes entre as regiões Sul e Nordeste.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); 
                        border-radius: 15px; padding: 20px; border: 2px solid #10B981;
                        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15);">
                <h4 style="color: #10B981; margin-top: 0;">🗺️ Sul</h4>
                <p style="color: #374151; margin-bottom: 0; font-weight: 500;">
                    {st.session_state.cadernos_ativos[0][1]}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_comp2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%); 
                        border-radius: 15px; padding: 20px; border: 2px solid #F59E0B;
                        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.15);">
                <h4 style="color: #F59E0B; margin-top: 0;">🌴 Nordeste</h4>
                <p style="color: #374151; margin-bottom: 0; font-weight: 500;">
                    {st.session_state.cadernos_ativos[1][1]}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🚀 Executar Comparação", type="primary", use_container_width=True):
            with st.spinner("📊 Analisando diretrizes em ambos os cadernos..."):
                paginas_comp = buscar_paginas_relevantes(
                    "diretrizes conflitos zoneamento conservação impacto", 
                    st.session_state.todas_as_paginas_lidas, 
                    limite_paginas=12
                )
                
                contexto_comp = ""
                for pag in paginas_comp:
                    contexto_comp += f"\n{pag['cabecalho']}\n{pag['texto_original']}\n"
                
                prompt_comp = f"""Você é um analista técnico especializado em Planejamento de Espaço Marinho.
                Baseado APENAS nos trechos abaixo:
                {contexto_comp}
                
                TAREFA: 
                1. Compare tecnicamente as abordagens regionais
                2. Destaque similaridades e diferenças
                3. Cite os cadernos e páginas de origem
                4. Use formatação Markdown com tabelas quando apropriado
                """
                
                try:
                    res_comp = model.generate_content(prompt_comp)
                    st.markdown(res_comp.text)
                    
                    # Box de fontes
                    with st.expander("📚 Fontes da Comparação"):
                        for pag in paginas_comp:
                            st.markdown(f"- {pag['cabecalho']}")
                except Exception as e:
                    st.error("⚠️ Erro na comparação. Tente uma pergunta mais específica.")

# ============================================================================
# 🌊 FOOTER
# ============================================================================
st.markdown("<div class='wave-divider'></div>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 30px; color: #64748B; font-size: 0.9em;">
    <p>🌊 <strong>Assistente PEM</strong> | Busca Inteligente em Cadernos Setoriais</p>
    <p style="opacity: 0.7; margin-top: 12px;">
        <a href="https://www.marinha.mil.br/secirm/psrm/pem" target="_blank" 
           style="color: #0EA5E9; text-decoration: none; font-weight: 600;">
            📌 Fonte Oficial: Marinha do Brasil - SECIRM
        </a>
    </p>
    <p style="opacity: 0.5; font-size: 0.8em; margin-top: 18px;">
        ⚠️ As informações devem ser validadas nos documentos oficiais
    </p>
</div>
""", unsafe_allow_html=True)
