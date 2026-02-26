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
    
    /* Header principal com efeito glassmorphism */
    .main-header {
        background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 50%, #0EA5E9 100%);
        padding: 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(14, 165, 233, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .main-header h1 {
        font-size: 3em;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.2em;
        margin-top: 10px;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* Cards personalizados */
    .info-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 5px solid #0EA5E9;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .card-sul {
        border-left-color: #10B981;
    }
    
    .card-ne {
        border-left-color: #F59E0B;
    }
    
    /* Sidebar estilizada */
    .sidebar-section {
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
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
    
    /* Container de chat */
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* Métricas e stats */
    .metric-card {
        background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(12, 74, 110, 0.3);
    }
    
    .metric-value {
        font-size: 2.5em;
        font-weight: 700;
    }
    
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
        margin-top: 5px;
    }
    
    /* Badge de status */
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 5px;
    }
    
    .status-active {
        background: #D1FAE5;
        color: #059669;
    }
    
    .status-loading {
        background: #FEF3C7;
        color: #D97706;
    }
    
    /* Divider decorativo */
    .wave-divider {
        height: 50px;
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%230EA5E9" fill-opacity="0.2" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,112C672,96,768,96,864,112C960,128,1056,160,1152,160C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
        background-size: cover;
        margin: 20px 0;
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
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 🌊 HEADER PRINCIPAL COM IMAGEM
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🌊 Assistente PEM</h1>
    <p>Plano de Espaço Marinho | Busca Inteligente e Rastreável</p>
    <div style="margin-top: 15px;">
        <span class="status-badge status-active">✓ IA Ativa</span>
        <span class="status-badge status-active">✓ PDF Indexado</span>
        <span class="status-badge status-active">✓ Multi-Região</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Imagem de banner (use URLs de imagens reais ou locais)
st.markdown("""
<div style="text-align: center; margin: -20px 0 30px 0;">
    <img src="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&h=300&fit=crop" 
         style="width: 100%; max-height: 250px; object-fit: cover; border-radius: 15px; 
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);" alt="Ocean Banner">
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
    except:
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
# 📚 BARRA LATERAL
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 3em;">📚</div>
        <h3 style="color: #0C4A6E; margin: 10px 0;">Biblioteca PEM</h3>
        <p style="color: #64748B; font-size: 0.9em;">Selecione os cadernos regionais</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("**📍 Região Sul**")
    escolha_sul = st.selectbox("", list(CADERNOS_SUL.keys()), key="sul_select")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("**📍 Região Nordeste**")
    escolha_ne = st.selectbox("", list(CADERNOS_NE.keys()), key="ne_select")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Status dos cadernos ativos
    if "cadernos_ativos" not in st.session_state:
        st.session_state.cadernos_ativos = []
    
    if st.session_state.cadernos_ativos:
        st.markdown("**✅ Cadernos Carregados:**")
        for regiao, nome, _ in st.session_state.cadernos_ativos:
            icon = "🟢" if regiao == "SUL" else "🟠"
            st.markdown(f"{icon} **{regiao}**: {nome}")
    
    st.divider()
    
    # Stats
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value" id="pages-count">0</div>
        <div class="metric-label">📄 Páginas Indexadas</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# 💾 CONTROLE DE ESTADO E CARREGAMENTO
# ============================================================================
if "todas_as_paginas_lidas" not in st.session_state:
    st.session_state.todas_as_paginas_lidas = []

cadernos_selecionados_agora = []
if escolha_sul != "Nenhum": 
    cadernos_selecionados_agora.append(("SUL", escolha_sul, CADERNOS_SUL[escolha_sul]))
if escolha_ne != "Nenhum": 
    cadernos_selecionados_agora.append(("NE", escolha_ne, CADERNOS_NE[escolha_ne]))

if cadernos_selecionados_agora != st.session_state.cadernos_ativos:
    st.session_state.todas_as_paginas_lidas = []
    st.session_state.cadernos_ativos = cadernos_selecionados_agora
    
    if cadernos_selecionados_agora:
        with st.sidebar.status("📖 Processando documentos...", expanded=True):
            total_paginas = 0
            for regiao, nome, file_id in cadernos_selecionados_agora:
                paginas = ler_e_fatiar_pdf(file_id, nome, regiao)
                st.session_state.todas_as_paginas_lidas.extend(paginas)
                total_paginas += len(paginas)
                st.write(f"✓ {regiao} - {nome}: {len(paginas)} páginas")
            
            # Atualizar contador
            st.session_state.total_paginas = total_paginas
        st.sidebar.success(f"🎉 {total_paginas} páginas prontas!")

# ============================================================================
# 📊 CARDS INFORMATIVOS
# ============================================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-card card-sul">
        <h4 style="color: #10B981; margin-top: 0;">🗺️ Região Sul</h4>
        <p style="color: #64748B; font-size: 0.9em; margin-bottom: 0;">
            Cadernos técnicos com diretrizes para o espaço marinho do sul do Brasil.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card card-ne">
        <h4 style="color: #F59E0B; margin-top: 0;">🌴 Região Nordeste</h4>
        <p style="color: #64748B; font-size: 0.9em; margin-bottom: 0;">
            Documentação completa sobre planejamento marinho do nordeste brasileiro.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-card">
        <h4 style="color: #0EA5E9; margin-top: 0;">🤖 IA Especializada</h4>
        <p style="color: #64748B; font-size: 0.9em; margin-bottom: 0;">
            Respostas baseadas exclusivamente nos documentos oficiais do PEM.
        </p>
    </div>
    """, unsafe_allow_html=True)

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
        st.info("""
        ### 💡 Dica
        Selecione **um caderno do Sul e um do Nordeste** na barra lateral para habilitar a comparação regional.
        """)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 100%); 
                    border-radius: 15px; padding: 25px; color: white; margin-bottom: 20px;">
            <h3 style="margin-top: 0;">⚖️ Comparação Estratégica Regional</h3>
            <p style="margin-bottom: 0; opacity: 0.9;">
                Analise diferenças e similaridades nas diretrizes entre as regiões Sul e Nordeste.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            st.markdown("""
            <div class="info-card card-sul">
                <h4 style="color: #10B981;">🗺️ Sul</h4>
                <p style="font-size: 0.9em; color: #64748B;">
                    """ + st.session_state.cadernos_ativos[0][1] + """
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_comp2:
            st.markdown("""
            <div class="info-card card-ne">
                <h4 style="color: #F59E0B;">🌴 Nordeste</h4>
                <p style="font-size: 0.9em; color: #64748B;">
                    """ + st.session_state.cadernos_ativos[1][1] + """
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
#  FOOTER
# ============================================================================
st.markdown("<div class='wave-divider'></div>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 30px; color: #64748B; font-size: 0.9em;">
    <p>🌊 <strong>Assistente PEM</strong> | Plano de Espaço Marinho do Brasil</p>
    <p style="opacity: 0.7;">Desenvolvido com Streamlit + Google Gemini AI</p>
    <p style="opacity: 0.5; font-size: 0.8em;">⚠️ As informações devem ser validadas nos documentos oficiais</p>
</div>
""", unsafe_allow_html=True)
