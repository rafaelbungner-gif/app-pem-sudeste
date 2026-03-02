import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import requests
import io
import re
import pandas as pd
from PyPDF2 import PdfReader

# ============================================================================
# 📚 BANCO DE DADOS DOS CADERNOS
# ============================================================================
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
    "TURISMO": "1D9H11ZwDcmwanyWYBltPFXtVAX-Qzwrm",
}
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
    "TURISMO": "1kdsI5bGdbIRIPLnXIsPfz9y3XwnY9B-4",
}

# ============================================================================
# 🎨 CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Assistente PEM",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# 💅 CSS
# ============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(160deg, #EFF6FF 0%, #DBEAFE 50%, #E0F2FE 100%); }

/* ── HEADER ─────────────────────────────────────────────── */
.main-header {
    background-image:
        linear-gradient(135deg,rgba(7,55,99,.92) 0%,rgba(3,105,161,.88) 50%,rgba(6,148,162,.90) 100%),
        url('https://images.unsplash.com/photo-1590523741831-ab7f85327541?w=1600&h=600&fit=crop&q=80');
    background-size:cover; background-position:center;
    padding:55px 40px 45px; border-radius:24px; color:white; text-align:center;
    margin-bottom:24px;
    box-shadow:0 20px 60px rgba(3,105,161,.4),inset 0 1px 0 rgba(255,255,255,.15);
    position:relative; overflow:hidden;
}
.main-header::after {
    content:''; position:absolute; bottom:0; left:0; right:0; height:4px;
    background:linear-gradient(90deg,#38BDF8,#06B6D4,#0EA5E9,#38BDF8);
    background-size:200% 100%; animation:shimmer 3s linear infinite;
}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
.main-header h1 { font-size:3em; font-weight:800; margin:0; text-shadow:0 4px 12px rgba(0,0,0,.4); letter-spacing:-1.5px; }
.main-header p  { font-size:1.15em; margin-top:10px; opacity:.95; text-shadow:0 2px 6px rgba(0,0,0,.3); }
.status-badge {
    display:inline-flex; align-items:center; gap:6px; padding:6px 16px; border-radius:30px;
    font-size:.82em; font-weight:600; margin:5px; background:rgba(255,255,255,.15);
    backdrop-filter:blur(16px); border:1px solid rgba(255,255,255,.3); transition:all .25s;
}

/* ── SIDEBAR ─────────────────────────────────────────────── */
.sidebar-header {
    background:linear-gradient(135deg,#073763 0%,#0369A1 100%);
    border-radius:16px; padding:20px; margin-bottom:16px; text-align:center;
    box-shadow:0 6px 20px rgba(7,55,99,.3);
}
.sidebar-section {
    background:linear-gradient(135deg,#0C4A6E 0%,#0369A1 100%);
    border-radius:14px; padding:16px; margin:8px 0;
    border:1px solid rgba(255,255,255,.12); box-shadow:0 4px 15px rgba(12,74,110,.25);
}
.sidebar-section h4 { color:white; margin-bottom:8px; font-size:.92em; font-weight:600; }
.loaded-notebooks {
    background:linear-gradient(135deg,#F0FDF4,#DCFCE7); border-radius:14px; padding:16px;
    margin:12px 0; border:1px solid #86EFAC; box-shadow:0 3px 12px rgba(16,185,129,.12);
}
.loaded-notebook-item { display:flex; align-items:center; gap:8px; padding:8px 0; border-bottom:1px solid #BBF7D0; font-size:.86em; }
.loaded-notebook-item:last-child { border-bottom:none; }
.notebook-region { font-weight:700; padding:3px 9px; border-radius:8px; font-size:.7em; text-transform:uppercase; }
.region-sul { background:linear-gradient(135deg,#10B981,#059669); color:white; }
.region-ne  { background:linear-gradient(135deg,#F59E0B,#D97706); color:white; }
.metric-card {
    background:linear-gradient(135deg,#0C4A6E,#0369A1); border-radius:16px; padding:20px;
    text-align:center; color:white; box-shadow:0 6px 20px rgba(12,74,110,.35); margin:12px 0;
}
.metric-value { font-size:2.6em; font-weight:800; text-shadow:2px 2px 4px rgba(0,0,0,.3); }
.metric-label { font-size:.88em; opacity:.9; margin-top:5px; }

/* ── TABS E BOTOES ───────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap:10px; }
.stTabs [data-baseweb="tab"] { border-radius:12px; padding:10px 26px; font-weight:600; font-size:.95em; }

/* ── CHAT ────────────────────────────────────────────────── */
.chat-intro {
    background:white; border-radius:16px; padding:22px 28px;
    box-shadow:0 4px 20px rgba(0,0,0,.07); margin-bottom:20px; border-top:4px solid #0EA5E9;
}
[data-testid="stVerticalBlockBorderWrapper"] > div[style*="height"] {
    border-radius: 16px !important;
    background: transparent !important;
}
.chat-empty-state {
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    height:100%; min-height:300px; color:#94A3B8; text-align:center; padding:40px;
}
.chat-empty-state .icon { font-size:3.5em; margin-bottom:16px; opacity:.5; }

/* ── SCORE BADGES ────────────────────────────────────────── */
.score-badge { display:inline-flex; align-items:center; gap:4px; padding:3px 10px; border-radius:20px; font-size:.76em; font-weight:700; margin:2px; }
.score-high   { background:linear-gradient(135deg,#10B981,#059669); color:white; }
.score-medium { background:linear-gradient(135deg,#F59E0B,#D97706); color:white; }
.score-low    { background:linear-gradient(135deg,#6366F1,#4F46E5); color:white; }

/* ── FOOTER ──────────────────────────────────────────────── */
.footer { text-align:center; padding:26px; color:#64748B; font-size:.87em; margin-top:16px; border-top:2px dashed #CBD5E1; }
#MainMenu{visibility:hidden;} footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 🌊 HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🌊 Assistente PEM</h1>
    <p>Busca Inteligente · Visual Explainer · Documentos Setoriais</p>
    <div style="margin-top:18px;">
        <span class="status-badge">✦ IA Ativa</span>
        <span class="status-badge">✦ Relatórios Visuais</span>
        <span class="status-badge">✦ Multi-Região</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# 🔧 CONFIGURAÇÃO DA IA
# ============================================================================
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    modelos_disponiveis = [
        m.name for m in genai.list_models()
        if "generateContent" in m.supported_generation_methods
    ]
    
    # Priorizar modelos com maior janela de contexto e capacidades (pro/flash)
    for candidato in [
        "models/gemini-1.5-pro-latest",
        "models/gemini-1.5-flash-latest",
        "models/gemini-1.0-pro",
    ]:
        if candidato in modelos_disponiveis:
            modelo_nome = candidato
            break
    else:
        modelo_nome = modelos_disponiveis[0] if modelos_disponiveis else "models/gemini-pro"

    st.sidebar.caption(f"🤖 Modelo: `{modelo_nome.replace('models/', '')}`")

    instrucao_sistema_chat = """Você é um analista técnico do Plano de Espaço Marinho (PEM) do Brasil.
REGRAS:
1. Use EXCLUSIVAMENTE as informações dos trechos fornecidos. Nada mais.
2. Cite a fonte de CADA afirmação factual: (Região | Caderno | Pág. X)."""

    model_chat = genai.GenerativeModel(
        model_name=modelo_nome,
        system_instruction=instrucao_sistema_chat,
    )
    
    # Modelo dedicado para o Visual Explainer (sem system prompt rígido para permitir formatação HTML livre)
    model_visual = genai.GenerativeModel(model_name=modelo_nome)

except Exception as e:
    st.error(f"⚠️ Erro de conexão com o Google AI: {e}")

# ============================================================================
# 📄 LEITURA DE PDF (Mantido intacto)
# ============================================================================
def ler_e_fatiar_pdf(file_id, nome_doc, regiao):
    paginas = []
    try:
        url = f"https://drive.google.com/uc?id={file_id}"
        response = requests.get(url, timeout=30)
        reader = PdfReader(io.BytesIO(response.content))
        for i, page in enumerate(reader.pages):
            texto = page.extract_text()
            if texto and texto.strip():
                paginas.append(
                    {
                        "cabecalho": f"[{regiao} | {nome_doc} | Pág. {i+1}]",
                        "texto": texto.lower(),
                        "texto_original": texto,
                        "pagina": i + 1,
                        "regiao": regiao,
                        "caderno": nome_doc,
                    }
                )
    except Exception as ex:
        st.error(f"Erro ao ler PDF: {ex}")
    return paginas

# ============================================================================
# 🔍 BUSCA PARA O CHAT (Mantido intacto)
# ============================================================================
PALAVRAS_IGNORADAS = {"o","a","os","as","de","do","da","dos","das","em","no","na","nos","nas","para","com","que"}

def extrair_palavras_chave(texto):
    tokens = re.findall(r"\b[a-záéíóúãõâêîôûàèìòùç]{4,}\b", texto.lower())
    return [t for t in tokens if t not in PALAVRAS_IGNORADAS]

def pontuar_pagina(pagina, palavras_chave):
    texto = pagina["texto"]
    return sum(len(re.findall(rf"\b{re.escape(p)}\b", texto)) for p in palavras_chave)

def buscar_paginas_relevantes(pergunta, todas_as_paginas, limite=20):
    palavras = extrair_palavras_chave(pergunta)
    if not palavras:
        return []
    resultados = [(pontuar_pagina(p, palavras), p) for p in todas_as_paginas]
    resultados = [(s, p) for s, p in resultados if s > 0]
    resultados.sort(key=lambda x: x[0], reverse=True)
    return resultados[:limite]

def extrair_trechos_para_chat(resultados_buscados, pergunta, max_chars=800):
    palavras = set(extrair_palavras_chave(pergunta))
    trechos = []
    for score, pag in resultados_buscados:
        paragrafos = pag["texto_original"].split("\n\n")
        melhor_score, melhor_paragrafo = 0, ""
        for paragrafo in paragrafos:
            if len(paragrafo.strip()) < 60:
                continue
            p_score = sum(1 for w in palavras if w in paragrafo.lower())
            if p_score > melhor_score:
                melhor_score, melhor_paragrafo = p_score, paragrafo.strip()
        if melhor_paragrafo:
            trechos.append({"cabecalho": pag["cabecalho"], "texto": melhor_paragrafo[:max_chars], "score": score})
    return trechos[:25]

def limitar_contexto(contexto, max_chars=40000):
    if len(contexto) <= max_chars: return contexto, len(contexto) // 4
    corte = contexto.rfind("\n\n", 0, max_chars)
    if corte == -1: corte = max_chars
    return contexto[:corte], corte // 4

def exibir_score_html(score):
    if score >= 5:   return f'<span class="score-badge score-high">▲ Alta ({score})</span>'
    elif score >= 2: return f'<span class="score-badge score-medium">● Média ({score})</span>'
    else:            return f'<span class="score-badge score-low">▼ Baixa ({score})</span>'

# ============================================================================
# 🎨 GERADOR DE PROMPTS PARA VISUAL EXPLAINER
# ============================================================================
def gerar_prompt_visual_explainer(tipo_visual, instrucao_usuario, contexto_documentos):
    
    base_html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        {scripts_extras}
    </head>
    <body class="bg-gray-50 text-gray-800 font-sans p-6 md:p-12">
        <div class="max-w-6xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden">
            <!-- Seu conteúdo gerado entra aqui -->
        </div>
    </body>
    </html>
    """
    
    regras_gerais = f"""
    Você é um agente especializado em "Visual Explainer". Sua função é transformar os dados extraídos dos cadernos do Plano Espacial Marinho (PEM) em uma página HTML estilizada, moderna e interativa.
    
    DADOS DE CONTEXTO (Use APENAS estes dados para preencher as informações):
    {contexto_documentos}
    
    PEDIDO DO USUÁRIO: {instrucao_usuario}
    
    REGRAS TÉCNICAS:
    1. Retorne EXCLUSIVAMENTE o código HTML completo. NUNCA use marcadores markdown como ```html ou ```. Comece com <!DOCTYPE html>.
    2. Use classes do Tailwind CSS (já incluso via CDN) para criar um design moderno, limpo e profissional.
    3. Cite as fontes dos dados (Região, Caderno, Página) discretamente no rodapé dos elementos ou em tooltips.
    """

    if tipo_visual == "Diagrama de Fluxo / Arquitetura (Mermaid)":
        scripts = """<script type="module">import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs'; mermaid.initialize({ startOnLoad: true, theme: 'neutral' });</script>"""
        return regras_gerais + f"""
        OBJETIVO: Criar um diagrama interativo usando Mermaid.js.
        ESTRUTURA:
        {base_html.replace('{scripts_extras}', scripts)}
        - No body, crie um cabeçalho bonito explicando o diagrama.
        - Crie uma div com a classe 'mermaid' e coloque a sintaxe do diagrama Mermaid dentro dela.
        - Exemplos de uso: fluxos de licenciamento ambiental, cadeia produtiva da pesca, governança.
        """
        
    elif tipo_visual == "Dashboard de Dados (Chart.js)":
        scripts = """<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>"""
        return regras_gerais + f"""
        OBJETIVO: Criar um dashboard com gráficos usando Chart.js.
        ESTRUTURA:
        {base_html.replace('{scripts_extras}', scripts)}
        - Identifique métricas, metas ou quantidades nos textos (ex: áreas de conservação, produção de pescado, investimentos).
        - Crie um layout em Grid com Tailwind e insira tags <canvas id="meuGraficoX"></canvas>.
        - No final do body, adicione as tags <script> com a lógica do Chart.js para renderizar os gráficos com cores harmoniosas.
        """
        
    elif tipo_visual == "Relatório Visual / Resumo Executivo":
        return regras_gerais + f"""
        OBJETIVO: Criar um relatório visual moderno (tipo infográfico web) focado em tipografia e Grid/Cards.
        ESTRUTURA:
        {base_html.replace('{scripts_extras}', '')}
        - Não use tabelas em formato de texto. Use CSS Grid do Tailwind para comparar regiões, listar legislações ou detalhar próximos passos.
        - Use ícones emoji, fontes grandes para números chave, e caixas coloridas (ex: bg-blue-100) para destacar informações.
        """
        
    elif tipo_visual == "Apresentação de Slides (HTML)":
        scripts = """
        <style>
            .slides-container { scroll-snap-type: y mandatory; height: 80vh; overflow-y: scroll; scroll-behavior: smooth; }
            .slide { scroll-snap-align: start; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 4rem; text-align: center; border-bottom: 2px solid #e5e7eb; }
        </style>
        """
        return regras_gerais + f"""
        OBJETIVO: Criar uma apresentação de slides em uma única página HTML, rolável usando CSS Scroll Snap.
        ESTRUTURA:
        {base_html.replace('{scripts_extras}', scripts)}
        - Crie uma div principal com a classe 'slides-container'.
        - Para cada tópico principal, crie uma div com a classe 'slide bg-white' (ou alterne cores de fundo suavemente com Tailwind).
        - Faça um slide de Título, slides de conteúdo (com listas ou resumos), e um slide de conclusão.
        """

# ============================================================================
# 📚 BARRA LATERAL
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div style="font-size:3em;">📚</div>
        <h3 style="color:white;margin:8px 0 4px;">Biblioteca PEM</h3>
        <p style="color:rgba(255,255,255,.8);font-size:.8em;margin:0;">Cadernos Setoriais Oficiais</p>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section"><h4>📍 Região Sul</h4>', unsafe_allow_html=True)
    escolha_sul = st.selectbox("", list(CADERNOS_SUL.keys()), key="sul_select", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section"><h4>📍 Região Nordeste</h4>', unsafe_allow_html=True)
    escolha_ne = st.selectbox("", list(CADERNOS_NE.keys()), key="ne_select", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    for key, default in [
        ("cadernos_ativos", []),
        ("todas_as_paginas_lidas", []),
        ("mensagens", []),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    if st.session_state.cadernos_ativos:
        st.markdown('<div class="loaded-notebooks"><h4 style="color:#059669;margin:0 0 10px 0;">✅ Carregados</h4>', unsafe_allow_html=True)
        for regiao, nome, _ in st.session_state.cadernos_ativos:
            icon = "🗺️" if regiao == "SUL" else "🌴"
            rc = "region-sul" if regiao == "SUL" else "region-ne"
            st.markdown(f"""
            <div class="loaded-notebook-item">
                <span>{icon}</span>
                <span class="notebook-region {rc}">{regiao}</span>
                <span style="color:#374151;flex:1;font-size:.85em;">{nome}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.todas_as_paginas_lidas)}</div>
            <div class="metric-label">📄 Páginas Indexadas</div>
        </div>""", unsafe_allow_html=True)

# ============================================================================
# 💾 CARREGAMENTO
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
                st.write(f"✓ {regiao} — {nome}: **{len(paginas)}** páginas")
        st.sidebar.success("🎉 Pronto para consulta!")
        st.rerun()

# ============================================================================
# 📑 ABAS
# ============================================================================
aba1, aba2 = st.tabs(["🔮 Chat Analítico", "✨ Visual Explainer (Páginas Web)"])

# ─────────────────────────────────────────────────────────────
# ABA 1 — CHAT (Mantido intacto)
# ─────────────────────────────────────────────────────────────
with aba1:
    chat_box = st.container(height=600, border=False)
    with chat_box:
        if not st.session_state.mensagens:
            st.markdown("""
            <div class="chat-empty-state">
                <div class="icon">🌊</div>
                <h4>Assistente PEM pronto para ajudar</h4>
                <p>Faça perguntas sobre os documentos carregados.</p>
            </div>""", unsafe_allow_html=True)
        else:
            for m in st.session_state.mensagens:
                with st.chat_message(m["role"], avatar="👤" if m["role"] == "user" else "🤖"):
                    st.markdown(m["content"])

    pergunta = st.chat_input("Digite sua pergunta sobre os cadernos PEM…")
    if pergunta:
        if not st.session_state.cadernos_ativos:
            st.error("⚠️ Selecione ao menos um caderno na barra lateral.")
        else:
            st.session_state.mensagens.append({"role": "user", "content": pergunta})
            with chat_box:
                with st.chat_message("user", avatar="👤"): st.markdown(pergunta)
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("🔍 Buscando e analisando documentos…"):
                        resultados = buscar_paginas_relevantes(pergunta, st.session_state.todas_as_paginas_lidas)
                        trechos = extrair_trechos_para_chat(resultados, pergunta)
                        contexto = "\n\n".join(f"{t['cabecalho']}\n{t['texto']}" for t in trechos)
                        contexto, tokens = limitar_contexto(contexto, 40000)

                        if not trechos:
                            st.warning("⚠️ Nenhum trecho relevante encontrado.")
                        else:
                            prompt = f"TRECHOS:\n{contexto}\n\nPERGUNTA: {pergunta}"
                            res = model_chat.generate_content(prompt)
                            st.markdown(res.text)
                            st.session_state.mensagens.append({"role": "assistant", "content": res.text})

# ─────────────────────────────────────────────────────────────
# ABA 2 — VISUAL EXPLAINER (A Mágica do HTML Gerado via IA)
# ─────────────────────────────────────────────────────────────
with aba2:
    st.markdown("""
    <div class="chat-intro" style="border-top-color:#10B981;">
        <h3 style="color:#1E3A5F;margin-top:0;">✨ Visual Explainer</h3>
        <p style="color:#64748B;margin:0;">
            Transforme o texto denso dos Cadernos do PEM em <strong>páginas Web completas, painéis interativos ou apresentações de slides</strong>. 
            A Inteligência Artificial irá ler os documentos ativos e desenhar o código HTML pronto para uso ou download.
        </p>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.cadernos_ativos:
        st.warning("⚠️ Selecione ao menos um caderno na barra lateral para extrair dados.")
    else:
        # Criar a lista de opções baseada apenas nos cadernos que já foram carregados
        opcoes_cadernos = ["Todos os Cadernos Ativos"] + [f"[{c[0]}] {c[1]}" for c in st.session_state.cadernos_ativos]
        
        col1, col2, col3 = st.columns([1, 1.2, 2])
        
        with col1:
            caderno_alvo = st.selectbox(
                "Analisar qual documento?",
                opcoes_cadernos
            )
            
        with col2:
            tipo_visual = st.selectbox(
                "Tipo de Apresentação Visual:",
                [
                    "Relatório Visual / Resumo Executivo",
                    "Diagrama de Fluxo / Arquitetura (Mermaid)",
                    "Dashboard de Dados (Chart.js)",
                    "Apresentação de Slides (HTML)"
                ]
            )
            
        with col3:
            instrucao = st.text_input(
                "O que você deseja visualizar/resumir?",
                placeholder="Ex: Resuma os principais conflitos ambientais..."
            )
            
        gerar_btn = st.button("🚀 Gerar Página HTML", type="primary", use_container_width=True)
        
        if gerar_btn and instrucao:
            with st.spinner(f"Criando {tipo_visual}... isso pode levar até 1 minuto."):
                
                # Filtrar as páginas com base no caderno alvo selecionado
                paginas_alvo = st.session_state.todas_as_paginas_lidas
                
                if caderno_alvo != "Todos os Cadernos Ativos":
                    # Extrai apenas o nome do caderno ignorando a tag da região (ex: de "[SUL] AQUICULTURA" extrai "AQUICULTURA")
                    nome_selecionado = caderno_alvo.split("] ")[1]
                    paginas_alvo = [p for p in paginas_alvo if p["caderno"] == nome_selecionado]
                
                # 1. Pegar contexto do documento filtrado para mandar pra IA
                textos_pdf = [p["cabecalho"] + "\n" + p["texto_original"] for p in paginas_alvo]
                contexto_bruto = "\n\n".join(textos_pdf)
                contexto_limpo, _ = limitar_contexto(contexto_bruto, max_chars=80000) 
                
                # 2. Gerar Prompt
                prompt_visual = gerar_prompt_visual_explainer(tipo_visual, instrucao, contexto_limpo)
                
                # 3. Chamar a IA
                try:
                    resposta_ia = model_visual.generate_content(prompt_visual)
                    html_gerado = resposta_ia.text
                    
                    # Limpeza de markdown caso a IA coloque o HTML dentro de blocos ```html ... ```
                    html_gerado = re.sub(r"^```html\n", "", html_gerado, flags=re.IGNORECASE)
                    html_gerado = re.sub(r"^```\n", "", html_gerado)
                    html_gerado = re.sub(r"```$", "", html_gerado)
                    
                    # Salva no session state para não perder caso a página recarregue
                    st.session_state['html_gerado'] = html_gerado
                    
                except Exception as e:
                    st.error(f"Erro ao gerar a página visual: {e}")

        # Se existir HTML gerado, renderiza e mostra botão de download
        if 'html_gerado' in st.session_state:
            st.markdown("---")
            st.subheader("Pré-visualização do Documento")
            
            # Renderiza o HTML dentro de um iFrame no Streamlit
            components.html(st.session_state['html_gerado'], height=700, scrolling=True)
            
            # Botão de Download do código HTML gerado
            st.download_button(
                label="📥 Fazer Download do HTML (Visual Explainer)",
                data=st.session_state['html_gerado'],
                file_name="relatorio_visual_pem.html",
                mime="text/html",
                use_container_width=True
            )

# ============================================================================
# 🌊 FOOTER
# ============================================================================
st.markdown("""
<div class="footer">
    <p>🌊 <strong>Assistente PEM</strong> · Marinha do Brasil — SECIRM</p>
    <p style="opacity:.5;font-size:.82em;margin-top:4px;">⚠️ Sempre valide as informações geradas pela IA.</p>
</div>""", unsafe_allow_html=True)
