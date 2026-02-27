import streamlit as st
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
.status-badge:hover { background:rgba(255,255,255,.25); transform:translateY(-2px); }

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
.source-link {
    display:flex; align-items:center; gap:10px;
    background:linear-gradient(135deg,#FFFFFF,#F8FAFC); border-radius:12px;
    padding:12px 15px; margin:6px 0; text-decoration:none; color:#0C4A6E;
    font-weight:600; font-size:.86em; border:1px solid #E2E8F0; transition:all .3s;
    box-shadow:0 2px 8px rgba(0,0,0,.06);
}
.source-link:hover {
    background:linear-gradient(135deg,#0EA5E9,#0284C7); color:white; border-color:#0284C7;
    transform:translateX(5px); box-shadow:0 4px 15px rgba(14,165,233,.35);
}
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
.sidebar-divider { border-top:2px dashed rgba(255,255,255,.2); margin:16px 0; }

/* ── TABS ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap:10px; }
.stTabs [data-baseweb="tab"] { border-radius:12px; padding:10px 26px; font-weight:600; font-size:.95em; }

/* ── BUTTONS ─────────────────────────────────────────────── */
.stButton>button {
    background:linear-gradient(135deg,#0369A1,#0EA5E9); color:white; border:none;
    border-radius:12px; padding:11px 30px; font-weight:600; font-size:.95em;
    transition:all .3s; box-shadow:0 4px 15px rgba(14,165,233,.4);
}
.stButton>button:hover { transform:translateY(-2px); box-shadow:0 8px 25px rgba(14,165,233,.55); }

/* ── TABLES ──────────────────────────────────────────────── */
table { width:100%; border-collapse:collapse; margin:20px 0; background:white; border-radius:14px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,.08); }
th { background:linear-gradient(135deg,#073763,#0369A1); color:white; padding:14px 18px; text-align:left; font-weight:700; font-size:.88em; text-transform:uppercase; letter-spacing:.5px; }
td { padding:13px 18px; border-bottom:1px solid #E2E8F0; color:#374151; line-height:1.7; font-size:.91em; vertical-align:top; }
tr:hover { background:#F8FAFF; }
tr:last-child td { border-bottom:none; }

/* ── SCORE BADGES ────────────────────────────────────────── */
.score-badge { display:inline-flex; align-items:center; gap:4px; padding:3px 10px; border-radius:20px; font-size:.76em; font-weight:700; margin:2px; }
.score-high   { background:linear-gradient(135deg,#10B981,#059669); color:white; }
.score-medium { background:linear-gradient(135deg,#F59E0B,#D97706); color:white; }
.score-low    { background:linear-gradient(135deg,#6366F1,#4F46E5); color:white; }

/* ── CHAT ────────────────────────────────────────────────── */
.chat-intro {
    background:white; border-radius:16px; padding:22px 28px;
    box-shadow:0 4px 20px rgba(0,0,0,.07); margin-bottom:20px; border-top:4px solid #0EA5E9;
}

/* ── EXTRATOR CARDS ──────────────────────────────────────── */
.ext-card {
    background:white; border-radius:14px; padding:18px 22px; margin:10px 0;
    box-shadow:0 3px 12px rgba(0,0,0,.07); transition:all .25s; border-left:5px solid #6366F1;
}
.ext-card:hover { box-shadow:0 6px 20px rgba(99,102,241,.2); transform:translateX(3px); }
.ext-legislacao  { border-left-color:#0EA5E9; }
.ext-passos      { border-left-color:#10B981; }
.ext-institucional { border-left-color:#F59E0B; }

.ext-badge {
    display:inline-flex; align-items:center; gap:5px; padding:3px 12px; border-radius:20px;
    font-size:.75em; font-weight:700; margin-right:8px;
}
.badge-legislacao    { background:#EFF6FF; color:#1E40AF; }
.badge-passos        { background:#F0FDF4; color:#065F46; }
.badge-institucional { background:#FFFBEB; color:#92400E; }

.ext-text   { color:#1E293B; font-size:.93em; line-height:1.8; margin:10px 0 8px; }
.ext-source { font-family:monospace; font-size:.79em; color:#6B7280; }

.ext-summary {
    border-radius:16px; padding:22px 28px; margin-bottom:22px; color:white;
    background:linear-gradient(135deg,#1E3A5F 0%,#0369A1 100%);
}
.ext-summary .num { font-size:2.2em; font-weight:800; }
.ext-summary .lbl { opacity:.85; font-size:.88em; margin-top:2px; }

.no-results { background:#FFF7ED; border-radius:14px; padding:28px; border:2px solid #FED7AA; text-align:center; }

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
    <p>Busca Inteligente · Rastreável · Fundamentada</p>
    <div style="margin-top:18px;">
        <span class="status-badge">✦ IA Ativa</span>
        <span class="status-badge">✦ PDF Indexado</span>
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

    st.sidebar.caption(f"🤖 `{modelo_nome.replace('models/', '')}`")

    instrucao_sistema = """Você é um analista técnico do Plano de Espaço Marinho (PEM) do Brasil.

REGRAS ABSOLUTAS — NUNCA VIOLE:
1. Use EXCLUSIVAMENTE as informações dos trechos fornecidos. Nada mais.
2. Se a informação não estiver nos trechos, diga: "Não encontrado nos documentos consultados."
3. NUNCA invente dados, números, leis, nomes, datas ou conclusões.
4. Cite a fonte de CADA afirmação factual: (Região | Caderno | Pág. X).
5. Complete SEMPRE a resposta integralmente — nunca corte um tópico no meio.
6. Seja direto e técnico. Sem introduções genéricas ou repetição da pergunta."""

    model = genai.GenerativeModel(
        model_name=modelo_nome,
        system_instruction=instrucao_sistema,
        generation_config=genai.GenerationConfig(
            temperature=0.05,
            top_p=0.85,
            top_k=20,
            max_output_tokens=8192,
        ),
    )
except Exception as e:
    st.error(f"⚠️ Erro de conexão com o Google AI: {e}")


# ============================================================================
# 📄 LEITURA DE PDF
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
# 🔍 BUSCA E PONTUAÇÃO
# ============================================================================
PALAVRAS_IGNORADAS = {
    "o","a","os","as","de","do","da","dos","das","em","no","na","nos","nas",
    "para","com","que","quais","qual","como","sobre","mais","este","esta",
    "isso","aqui","pelo","pela","pelos","pelas","entre","também","quando",
    "onde","muito","suas","seus","seu","sua","são","está","have","from",
    "essa","esses","essas","um","uma","uns","umas","por","sendo","pode",
    "será","foram","seria","aquele","neste","esse","isto","eles","elas",
    "numa","duma","dum","num","deste","desta","desse","dessa",
}

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


# ============================================================================
# 🎯 EXTRATOR DE TRECHOS PARA CHAT
# ============================================================================
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
            trechos.append(
                {"cabecalho": pag["cabecalho"], "texto": melhor_paragrafo[:max_chars], "score": score}
            )
    return trechos[:25]


# ============================================================================
# 📏 CONTROLE DE CONTEXTO
# ============================================================================
def limitar_contexto(contexto, max_chars=40000):
    if len(contexto) <= max_chars:
        return contexto, len(contexto) // 4
    corte = contexto.rfind("\n\n", 0, max_chars)
    if corte == -1:
        corte = max_chars
    return contexto[:corte], corte // 4


# ============================================================================
# 🎯 TIPO DE PERGUNTA E PROMPTS
# ============================================================================
def detectar_tipo_pergunta(pergunta):
    p = pergunta.lower()
    if any(w in p for w in ["compare","diferença","entre","vs","versus","contraste"]): return "comparacao"
    if any(w in p for w in ["legislação","lei","norma","regulamento","marco legal","decreto"]): return "legislacao"
    if any(w in p for w in ["impacto","consequência","efeito","resultado","afeta"]): return "analise"
    if any(w in p for w in ["liste","listar","quais","cite","mencione","enumere"]): return "lista"
    return "padrao"

def criar_prompt_final(pergunta, contexto, tipo="padrao"):
    regras = """
REGRAS (invioláveis):
• Use APENAS os trechos acima. Sem conhecimento externo.
• Cite cada afirmação: (Região | Caderno | Pág. X).
• Se não houver dados: declare "Não encontrado nos documentos consultados."
• NUNCA invente. Complete SEMPRE a resposta integralmente, sem cortar tópicos."""

    prompts = {
        "padrao": f"""TRECHOS DOCUMENTAIS:\n{contexto}\n{regras}\n\nPERGUNTA: {pergunta}\n\nRESPOSTA (organize com tópicos quando útil; aborde todos os aspectos encontrados):""",
        "comparacao": f"""TRECHOS DOCUMENTAIS:\n{contexto}\n{regras}\n\nPERGUNTA: {pergunta}\n\nRESPOSTA:\n## 1. Pontos em comum\n## 2. Diferenças encontradas\n## 3. Tabela comparativa (só se houver dados para ambas as regiões)\n## 4. Lacunas documentais""",
        "lista": f"""TRECHOS DOCUMENTAIS:\n{contexto}\n{regras}\n\nPERGUNTA: {pergunta}\n\nRESPOSTA — para cada item:\n- **Nome** — descrição (1-2 frases). Fonte: (Região | Caderno | Pág. X)\n\n**Total encontrado:** X itens""",
        "analise": f"""TRECHOS DOCUMENTAIS:\n{contexto}\n{regras}\n\nPERGUNTA: {pergunta}\n\nRESPOSTA por dimensão (inclua só as com dados):\n## 🌿 Ambiental\n## 👥 Social\n## 💰 Econômico\n## ⚖️ Institucional\n## ⚠️ Lacunas documentais""",
        "legislacao": f"""TRECHOS DOCUMENTAIS:\n{contexto}\n{regras}\n\nPERGUNTA: {pergunta}\n\nRESPOSTA:\n## 1. Instrumentos legais mencionados\n## 2. Competências e responsabilidades\n## 3. Lacunas ou conflitos apontados""",
    }
    return prompts.get(tipo, prompts["padrao"])


# ============================================================================
# 🎯 FORMATADOR DE TABELAS
# ============================================================================
def formatar_tabela_markdown(texto):
    linhas = texto.split("\n")
    resultado, i = [], 0
    while i < len(linhas):
        linha = linhas[i].strip()
        if linha.startswith("|") and linha.count("|") >= 3:
            tabela = []
            while i < len(linhas) and (linhas[i].strip().startswith("|") or "---" in linhas[i]):
                partes = [p.strip() for p in linhas[i].strip().split("|") if p.strip()]
                tabela.append("| " + " | ".join(partes) + " |" if len(partes) >= 2 else linhas[i].strip())
                i += 1
            if len(tabela) >= 2 and "---" not in (tabela[1] if len(tabela) > 1 else ""):
                cols = tabela[0].count("|") - 1
                tabela.insert(1, "| " + " | ".join(["---"] * cols) + " |")
            resultado.extend(tabela)
        else:
            resultado.append(linha)
            i += 1
    return "\n".join(resultado)

def exibir_score_html(score):
    if score >= 5:   return f'<span class="score-badge score-high">▲ Alta ({score})</span>'
    elif score >= 2: return f'<span class="score-badge score-medium">● Média ({score})</span>'
    else:            return f'<span class="score-badge score-low">▼ Baixa ({score})</span>'


# ============================================================================
# 📋 EXTRATOR INTELIGENTE — Legislação · Próximos Passos · Institucional
# ============================================================================

# ── Padrões por categoria ─────────────────────────────────────────────────
PADROES_EXTRATOR = {

    "Legislação": {
        "cor": "#0EA5E9",
        "icone": "⚖️",
        "badge": "badge-legislacao",
        "card": "ext-legislacao",
        "padroes": [
            # Referências explícitas a instrumentos normativos
            r"\blei\s+n[oº°]?\s*[\d\.]+",
            r"\bdecreto\s+n[oº°]?\s*[\d\.]+",
            r"\bresolução\s+n[oº°]?\s*[\d\.]+",
            r"\bportaria\s+n[oº°]?\s*[\d\.]+",
            r"\binstrução\s+normativa",
            r"\bnormativa\s+n[oº°]?\s*[\d\.]+",
            r"\bconvenção\b",
            r"\btratado\b",
            r"\bcódigo\s+(?:civil|penal|ambiental|florestal|de\s+\w+)",
            r"\bestatuto\b",
            r"\bregulamento\b",
            r"\bmarco\s+legal",
            r"\blegislação\s+(?:vigente|aplicável|federal|estadual|brasileira)",
            r"\bnorma\s+(?:técnica|regulamentadora|vigente)",
            r"\blicença\s+(?:ambiental|de\s+operação|prévia|de\s+instalação)",
            r"\blicenciamento\s+ambiental",
            r"\bpermissão\b",
            r"\bautorização\s+(?:legal|regulatória|ambiental)",
            r"\bcumprimento\s+(?:da\s+lei|das\s+normas|da\s+legislação)",
            r"\bnos\s+termos\s+da\s+(?:lei|legislação|normativa)",
            r"\bconforme\s+(?:a\s+lei|a\s+legislação|a\s+normativa|o\s+decreto)",
            r"\bamparo\s+legal",
            r"\bbase\s+legal",
            r"\bindispensável\s+(?:o\s+licenciamento|a\s+autorização)",
        ],
    },

    "Próximos Passos": {
        "cor": "#10B981",
        "icone": "🚀",
        "badge": "badge-passos",
        "card": "ext-passos",
        "padroes": [
            # Ações planejadas, futuras, recomendadas como continuidade
            r"\bpróxim[ao]s?\s+(?:etapa|passo|fase|ação|medida|atividade)",
            r"\betapa\s+(?:seguinte|posterior|futura|subsequente)",
            r"\bação\s+(?:prevista|planejada|futura|recomendada)",
            r"\bações\s+(?:previstas|planejadas|futuras|recomendadas)",
            r"\bpropõe-se\b",
            r"\bproposto\b",
            r"\bproposta[s]?\b",
            r"\bprevê-se\b",
            r"\bprevisto\b",
            r"\bprevê\b",
            r"\bserá\s+(?:realizado|desenvolvido|implementado|elaborado|criado|estabelecido)",
            r"\bserão\s+(?:realizados|desenvolvidos|implementados|elaborados|criados|estabelecidos)",
            r"\bpretende-se\b",
            r"\bplaneja-se\b",
            r"\bé\s+necessário\s+(?:elaborar|desenvolver|criar|implementar|realizar|avançar)",
            r"\bimplantação\s+(?:de|do|da)\b",
            r"\bimplementação\s+(?:de|do|da)\b",
            r"\bdesenvolvimento\s+(?:de|do|da)\b",
            r"\bcriação\s+(?:de|do|da)\b",
            r"\binstituir\b",
            r"\bestabelecer\b",
            r"\bfomentar\b",
            r"\bfortalecer\b",
            r"\baprimorar\b",
            r"\bprioridade\b",
            r"\bmeta\s+(?:de|do|da|para)\b",
            r"\bcronograma\b",
            r"\bprazo\s+(?:de|para|previsto)\b",
            r"\bmonitoramento\s+(?:contínuo|periódico|futuro)",
            r"\bacompanhamento\s+(?:contínuo|periódico|futuro)",
            r"\bdemanda\s+(?:futura|estudos|investigação|ação)",
            r"\brecomenda-se\b",
            r"\bé\s+recomendado\b",
            r"\bé\s+desejável\b",
            r"\bdeveria\b",
        ],
    },

    "Institucional": {
        "cor": "#F59E0B",
        "icone": "🏛️",
        "badge": "badge-institucional",
        "card": "ext-institucional",
        "padroes": [
            # Órgãos, competências, governança, responsabilidades
            r"\bcabe\s+(?:à|ao|aos|às)\b",
            r"\bcompete\s+(?:à|ao|aos|às)\b",
            r"\bé\s+responsabilidade\b",
            r"\bresponsável\s+(?:pela|pelo|pelos|pelas)\b",
            r"\bcoordenação\s+(?:de|do|da|entre)\b",
            r"\bgestão\s+(?:compartilhada|integrada|participativa|de)\b",
            r"\bgovernança\b",
            r"\barticula(?:ção|r)\s+(?:inter|entre|com)\b",
            r"\bintegração\s+(?:entre|de|institucional)\b",
            r"\binterlocução\b",
            r"\bórgão\s+(?:responsável|gestor|federal|estadual|competente|regulador)",
            r"\bórgãos\s+(?:responsáveis|gestores|federais|estaduais|competentes)",
            r"\bministério\b",
            r"\bsecretaria\b",
            r"\bagência\s+(?:nacional|estadual|reguladora)\b",
            r"\bcomitê\b",
            r"\bcomissão\b",
            r"\bconselho\b",
            r"\bfórum\b",
            r"\bgrupo\s+de\s+trabalho\b",
            r"\bcâmara\s+técnica\b",
            r"\binstância\s+(?:competente|decisória|gestora|federal|estadual)\b",
            r"\bórgão\s+ambiental\b",
            r"\bfiscalização\b",
            r"\bmonitoramento\s+(?:institucional|governamental)\b",
            r"\binteração\s+(?:institucional|entre\s+órgãos)\b",
            r"\bprotocolo\s+(?:de\s+cooperação|de\s+intenção|entre)\b",
            r"\bconvênio\b",
            r"\bparceria\s+(?:institucional|interinstitucional)\b",
            r"\bpoder\s+público\b",
            r"\badministração\s+pública\b",
            r"\bunião\s+federal\b",
            r"\bestados\s+(?:e\s+municípios|costeiros|federativos)\b",
            r"\bmunícipios?\b",
            r"\bmarinha\s+do\s+brasil\b",
            r"\bsecirm\b",
            r"\bibama\b",
            r"\bicmbio\b",
            r"\bana\b",
            r"\baneel\b",
            r"\bant\b",
            r"\bantaq\b",
        ],
    },
}

MIN_CHARS = 55
MAX_CHARS = 650

def extrair_sentencas(texto):
    sentencas = re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÃÕÂÊÎÔÛ])", texto)
    resultado = []
    for s in sentencas:
        s = s.strip()
        if MIN_CHARS <= len(s) <= MAX_CHARS:
            resultado.append(s)
    return resultado

def classificar_sentenca_extrator(sentenca):
    """Retorna lista de categorias que se aplicam (pode ser mais de uma)."""
    s_lower = sentenca.lower()
    categorias = []
    for categoria, cfg in PADROES_EXTRATOR.items():
        for padrao in cfg["padroes"]:
            if re.search(padrao, s_lower):
                categorias.append(categoria)
                break
    return categorias

def executar_extracao(todas_as_paginas):
    """Extrai e retorna lista de dicts com todas as informações relevantes."""
    resultados = []
    vistos = set()  # evita duplicatas exatas

    for pag in todas_as_paginas:
        for sentenca in extrair_sentencas(pag["texto_original"]):
            chave = (pag["caderno"], sentenca[:80])
            if chave in vistos:
                continue
            vistos.add(chave)

            categorias = classificar_sentenca_extrator(sentenca)
            for cat in categorias:
                resultados.append({
                    "Categoria": cat,
                    "Conteúdo": sentenca.strip(),
                    "Região": pag["regiao"],
                    "Caderno": pag["caderno"],
                    "Página": pag["pagina"],
                    "Fonte": pag["cabecalho"],
                })

    return resultados


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

    st.markdown("**🔗 Fontes Oficiais**")
    st.markdown("""
    <a href="https://www.marinha.mil.br/secirm/psrm/pem/cadernos-setoriais-pem-nordeste" target="_blank" class="source-link">
        <span>🌴</span> Cadernos Nordeste
    </a>
    <a href="https://www.marinha.mil.br/secirm/pt-br/psrm/pem/cadernos-setoriais-pem-sul" target="_blank" class="source-link">
        <span>🗺️</span> Cadernos Sul
    </a>""", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section"><h4>📍 Região Sul</h4>', unsafe_allow_html=True)
    escolha_sul = st.selectbox("", list(CADERNOS_SUL.keys()), key="sul_select", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section"><h4>📍 Região Nordeste</h4>', unsafe_allow_html=True)
    escolha_ne = st.selectbox("", list(CADERNOS_NE.keys()), key="ne_select", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    for key, default in [
        ("cadernos_ativos", []),
        ("todas_as_paginas_lidas", []),
        ("mensagens", []),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    if st.session_state.cadernos_ativos:
        st.markdown(
            '<div class="loaded-notebooks"><h4 style="color:#059669;margin:0 0 10px 0;">✅ Carregados</h4>',
            unsafe_allow_html=True,
        )
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
    else:
        st.info("👈 Selecione um caderno para começar")


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
aba1, aba2 = st.tabs(["🔮 Chat Analítico", "📋 Extrator de Informações"])


# ─────────────────────────────────────────────────────────────
# ABA 1 — CHAT ROLÁVEL COM INPUT FIXO
# ─────────────────────────────────────────────────────────────
with aba1:
    st.markdown("""
    <div class="chat-intro">
        <h3 style="color:#0C4A6E;margin-top:0;">💬 Faça sua pergunta</h3>
        <p style="color:#64748B;margin:0;">
            Perguntas sobre zoneamento, conservação, impactos, legislação, pesca, energia e mais.
            Respostas fundamentadas e rastreáveis até a página de origem.
        </p>
    </div>""", unsafe_allow_html=True)

    # Exibe histórico de mensagens — rola naturalmente
    for m in st.session_state.mensagens:
        with st.chat_message(m["role"], avatar="👤" if m["role"] == "user" else "🤖"):
            st.markdown(m["content"])

    # Input fixo no fundo (comportamento nativo do st.chat_input)
    pergunta = st.chat_input("Digite sua pergunta sobre os cadernos PEM…")

    if pergunta:
        if not st.session_state.cadernos_ativos:
            st.error("⚠️ Selecione ao menos um caderno na barra lateral.")
        else:
            st.session_state.mensagens.append({"role": "user", "content": pergunta})

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("🔍 Buscando e analisando documentos…"):

                    resultados = buscar_paginas_relevantes(
                        pergunta, st.session_state.todas_as_paginas_lidas, limite=20
                    )
                    trechos = extrair_trechos_para_chat(resultados, pergunta)
                    contexto = "\n\n".join(
                        f"{t['cabecalho']}\n{t['texto']}" for t in trechos
                    )
                    contexto, tokens_est = limitar_contexto(contexto, max_chars=40000)

                    with st.expander(
                        f"📚 {len(trechos)} trechos consultados | ~{tokens_est} tokens estimados",
                        expanded=False,
                    ):
                        for t in trechos:
                            st.markdown(
                                f"`{t['cabecalho']}` {exibir_score_html(t['score'])}",
                                unsafe_allow_html=True,
                            )

                    if not trechos:
                        aviso = "⚠️ Nenhum trecho relevante encontrado. Tente reformular ou carregar outros cadernos."
                        st.warning(aviso)
                        st.session_state.mensagens.append({"role": "assistant", "content": aviso})
                    else:
                        tipo = detectar_tipo_pergunta(pergunta)
                        prompt = criar_prompt_final(pergunta, contexto, tipo)
                        try:
                            res = model.generate_content(prompt)
                            resposta = formatar_tabela_markdown(res.text)
                            st.markdown(resposta)
                            st.session_state.mensagens.append({"role": "assistant", "content": resposta})
                        except Exception as e:
                            st.error(f"⚠️ Erro na geração: {e}")


# ─────────────────────────────────────────────────────────────
# ABA 2 — EXTRATOR DE INFORMAÇÕES
# ─────────────────────────────────────────────────────────────
with aba2:
    st.markdown("""
    <div class="chat-intro" style="border-top-color:#6366F1;">
        <h3 style="color:#1E3A5F;margin-top:0;">📋 Extrator de Informações Relevantes</h3>
        <p style="color:#64748B;margin:0;">
            Varre <strong>automaticamente</strong> todos os documentos carregados e extrai três categorias
            de informações críticas — <strong>sem IA</strong>, direto do texto, 100% rastreável.<br><br>
            <span style="display:inline-flex;gap:10px;flex-wrap:wrap;margin-top:4px;">
                <span style="background:#EFF6FF;color:#1E40AF;padding:4px 12px;border-radius:20px;font-size:.83em;font-weight:600;">⚖️ Legislação &amp; Normas</span>
                <span style="background:#F0FDF4;color:#065F46;padding:4px 12px;border-radius:20px;font-size:.83em;font-weight:600;">🚀 Próximos Passos</span>
                <span style="background:#FFFBEB;color:#92400E;padding:4px 12px;border-radius:20px;font-size:.83em;font-weight:600;">🏛️ Informações Institucionais</span>
            </span>
        </p>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.cadernos_ativos:
        st.warning("⚠️ Selecione ao menos um caderno na barra lateral.")
    else:
        if st.button("🚀 Extrair Informações", type="primary", use_container_width=True):
            with st.spinner("🔬 Varrendo padrões linguísticos nos documentos…"):
                st.session_state["extracao_cache"] = executar_extracao(
                    st.session_state.todas_as_paginas_lidas
                )

        if st.session_state.get("extracao_cache"):
            dados = st.session_state["extracao_cache"]
            df = pd.DataFrame(dados)

            # ── Filtros ────────────────────────────────────────────────
            st.markdown("---")
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                cats_disp = sorted(df["Categoria"].unique())
                cats_sel = st.multiselect("Categoria", cats_disp, default=cats_disp)
            with fc2:
                cads_disp = sorted(df["Caderno"].unique())
                cads_sel = st.multiselect("Caderno", cads_disp, default=cads_disp)
            with fc3:
                regioes_disp = sorted(df["Região"].unique())
                regioes_sel = st.multiselect("Região", regioes_disp, default=regioes_disp)

            busca_texto = st.text_input(
                "🔎 Filtrar por palavra no conteúdo:",
                placeholder="Ex: licença, IBAMA, cronograma, marinha…",
            )

            df_f = df[
                df["Categoria"].isin(cats_sel)
                & df["Caderno"].isin(cads_sel)
                & df["Região"].isin(regioes_sel)
            ]
            if busca_texto.strip():
                df_f = df_f[df_f["Conteúdo"].str.contains(busca_texto, case=False, na=False)]

            # ── Sumário ────────────────────────────────────────────────
            por_cat = df_f["Categoria"].value_counts()
            ORDER = ["Legislação", "Próximos Passos", "Institucional"]
            nums_html = "".join(
                f"""<div style="text-align:center;">
                    <div class="num">{por_cat.get(c, 0)}</div>
                    <div class="lbl">{PADROES_EXTRATOR[c]['icone']} {c}</div>
                </div>"""
                for c in ORDER
            )
            st.markdown(f"""
            <div class="ext-summary">
                <div style="display:flex;gap:40px;flex-wrap:wrap;align-items:center;justify-content:space-around;">
                    <div style="text-align:center;">
                        <div style="font-size:2.6em;font-weight:800;">{len(df_f)}</div>
                        <div style="opacity:.85;font-size:.88em;">registros encontrados</div>
                    </div>
                    {nums_html}
                </div>
            </div>""", unsafe_allow_html=True)

            # ── Resultados agrupados por Categoria → Caderno ──────────
            for cat in ORDER:
                df_cat = df_f[df_f["Categoria"] == cat]
                if df_cat.empty:
                    continue

                cfg = PADROES_EXTRATOR[cat]
                st.markdown(
                    f"## {cfg['icone']} {cat} &nbsp;<span style='font-size:.7em;color:#6B7280;'>({len(df_cat)} registros)</span>",
                    unsafe_allow_html=True,
                )

                for caderno in sorted(df_cat["Caderno"].unique()):
                    df_cad = df_cat[df_cat["Caderno"] == caderno].sort_values("Página")
                    regiao_cad = df_cad["Região"].iloc[0]
                    icon = "🗺️" if regiao_cad == "SUL" else "🌴"

                    with st.expander(
                        f"{icon} {caderno} — {len(df_cad)} itens",
                        expanded=False,
                    ):
                        for _, row in df_cad.iterrows():
                            conteudo = row["Conteúdo"]
                            if busca_texto.strip():
                                conteudo = re.sub(
                                    rf"(?i)({re.escape(busca_texto)})",
                                    r"<mark>\1</mark>",
                                    conteudo,
                                )
                            st.markdown(f"""
                            <div class="ext-card {cfg['card']}">
                                <div>
                                    <span class="ext-badge {cfg['badge']}">{cfg['icone']} {cat}</span>
                                    <span style="font-size:.79em;color:#9CA3AF;">Pág. {row['Página']}</span>
                                </div>
                                <div class="ext-text">{conteudo}</div>
                                <div class="ext-source">📍 {row['Fonte']}</div>
                            </div>""", unsafe_allow_html=True)

                st.markdown("")  # espaço entre categorias

            # ── Exportação ─────────────────────────────────────────────
            st.markdown("---")
            exp1, exp2 = st.columns(2)
            with exp1:
                csv_data = df_f[["Categoria", "Conteúdo", "Região", "Caderno", "Página"]].to_csv(
                    index=False, encoding="utf-8-sig"
                )
                st.download_button(
                    "📊 Exportar CSV",
                    csv_data,
                    file_name="extracao_pem.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with exp2:
                md_lines = ["# Extração de Informações — PEM\n"]
                for cat in ORDER:
                    df_c = df_f[df_f["Categoria"] == cat]
                    if not df_c.empty:
                        md_lines.append(f"\n## {PADROES_EXTRATOR[cat]['icone']} {cat} ({len(df_c)})\n")
                        for _, r in df_c.iterrows():
                            md_lines.append(f"- **[{r['Fonte']}]** {r['Conteúdo']}\n")
                st.download_button(
                    "📄 Exportar Markdown",
                    "\n".join(md_lines),
                    file_name="extracao_pem.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

        elif "extracao_cache" in st.session_state and not st.session_state["extracao_cache"]:
            st.markdown("""
            <div class="no-results">
                <div style="font-size:2.5em;margin-bottom:10px;">🔍</div>
                <h4 style="color:#92400E;margin:0 0 8px;">Nenhum registro identificado</h4>
                <p style="color:#78350F;margin:0;">
                    Verifique se os documentos carregados possuem texto legível (não são imagens escaneadas).
                </p>
            </div>""", unsafe_allow_html=True)


# ============================================================================
# 🌊 FOOTER
# ============================================================================
st.markdown("""
<div class="footer">
    <p>🌊 <strong>Assistente PEM</strong> · Marinha do Brasil — SECIRM</p>
    <p style="opacity:.5;font-size:.82em;margin-top:4px;">⚠️ Sempre valide as informações nos documentos oficiais antes de utilizá-las.</p>
</div>""", unsafe_allow_html=True)
