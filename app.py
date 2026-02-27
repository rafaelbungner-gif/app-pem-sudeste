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
    "TURISMO": "1D9H11ZwDcmwanyWYBltPFXtVAX-Qzwrm"
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
    "TURISMO": "1kdsI5bGdbIRIPLnXIsPfz9y3XwnY9B-4"
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
# 💅 ESTILOS CSS
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(160deg, #EFF6FF 0%, #DBEAFE 50%, #E0F2FE 100%); }

    .main-header {
        background-image:
            linear-gradient(135deg, rgba(7,55,99,0.92) 0%, rgba(3,105,161,0.88) 50%, rgba(6,148,162,0.90) 100%),
            url('https://images.unsplash.com/photo-1590523741831-ab7f85327541?w=1600&h=600&fit=crop&q=80');
        background-size:cover; background-position:center;
        padding:60px 40px 50px; border-radius:24px; color:white; text-align:center; margin-bottom:28px;
        box-shadow:0 20px 60px rgba(3,105,161,0.4),inset 0 1px 0 rgba(255,255,255,0.15);
        position:relative; overflow:hidden;
    }
    .main-header::after {
        content:''; position:absolute; bottom:0; left:0; right:0; height:4px;
        background:linear-gradient(90deg,#38BDF8,#06B6D4,#0EA5E9,#38BDF8);
        background-size:200% 100%; animation:shimmer 3s linear infinite;
    }
    @keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
    .main-header h1{font-size:3.2em;font-weight:800;margin:0;text-shadow:0 4px 12px rgba(0,0,0,0.4);letter-spacing:-1.5px;}
    .main-header p{font-size:1.2em;margin-top:10px;opacity:0.95;font-weight:400;text-shadow:0 2px 6px rgba(0,0,0,0.3);}
    .status-badge{display:inline-flex;align-items:center;gap:6px;padding:7px 18px;border-radius:30px;font-size:0.82em;font-weight:600;margin:6px;background:rgba(255,255,255,0.15);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.3);transition:all 0.25s ease;}
    .status-badge:hover{background:rgba(255,255,255,0.25);transform:translateY(-2px);}

    .sidebar-header{background:linear-gradient(135deg,#073763 0%,#0369A1 100%);border-radius:16px;padding:22px;margin-bottom:18px;text-align:center;box-shadow:0 6px 20px rgba(7,55,99,0.3);}
    .sidebar-section{background:linear-gradient(135deg,#0C4A6E 0%,#0369A1 100%);border-radius:14px;padding:18px;margin:10px 0;border:1px solid rgba(255,255,255,0.12);box-shadow:0 4px 15px rgba(12,74,110,0.25);}
    .sidebar-section h4{color:white;margin-bottom:10px;font-size:0.95em;font-weight:600;}
    .source-link{display:flex;align-items:center;gap:10px;background:linear-gradient(135deg,#FFFFFF 0%,#F8FAFC 100%);border-radius:12px;padding:13px 16px;margin:7px 0;text-decoration:none;color:#0C4A6E;font-weight:600;font-size:0.87em;border:1px solid #E2E8F0;transition:all 0.3s ease;box-shadow:0 2px 8px rgba(0,0,0,0.06);}
    .source-link:hover{background:linear-gradient(135deg,#0EA5E9 0%,#0284C7 100%);color:white;border-color:#0284C7;transform:translateX(5px);box-shadow:0 4px 15px rgba(14,165,233,0.35);}
    .loaded-notebooks{background:linear-gradient(135deg,#F0FDF4 0%,#DCFCE7 100%);border-radius:14px;padding:18px;margin:14px 0;border:1px solid #86EFAC;box-shadow:0 3px 12px rgba(16,185,129,0.12);}
    .loaded-notebook-item{display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #BBF7D0;font-size:0.88em;}
    .loaded-notebook-item:last-child{border-bottom:none;}
    .notebook-region{font-weight:700;padding:3px 10px;border-radius:8px;font-size:0.72em;text-transform:uppercase;}
    .region-sul{background:linear-gradient(135deg,#10B981,#059669);color:white;}
    .region-ne{background:linear-gradient(135deg,#F59E0B,#D97706);color:white;}
    .metric-card{background:linear-gradient(135deg,#0C4A6E 0%,#0369A1 100%);border-radius:16px;padding:22px;text-align:center;color:white;box-shadow:0 6px 20px rgba(12,74,110,0.35);margin:14px 0;}
    .metric-value{font-size:2.8em;font-weight:800;text-shadow:2px 2px 4px rgba(0,0,0,0.3);}
    .metric-label{font-size:0.9em;opacity:0.9;margin-top:6px;}
    .sidebar-divider{border-top:2px dashed rgba(255,255,255,0.2);margin:18px 0;}

    .stTabs [data-baseweb="tab-list"]{gap:10px;}
    .stTabs [data-baseweb="tab"]{border-radius:12px;padding:10px 24px;font-weight:600;font-size:0.95em;}
    .stButton>button{background:linear-gradient(135deg,#0369A1 0%,#0EA5E9 100%);color:white;border:none;border-radius:12px;padding:12px 32px;font-weight:600;font-size:1em;transition:all 0.3s ease;box-shadow:0 4px 15px rgba(14,165,233,0.4);}
    .stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(14,165,233,0.55);}

    table{width:100%;border-collapse:collapse;margin:22px 0;background:white;border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);}
    th{background:linear-gradient(135deg,#073763 0%,#0369A1 100%);color:white;padding:15px 20px;text-align:left;font-weight:700;font-size:0.9em;text-transform:uppercase;letter-spacing:0.5px;}
    td{padding:14px 20px;border-bottom:1px solid #E2E8F0;color:#374151;line-height:1.7;font-size:0.92em;vertical-align:top;}
    tr:hover{background:#F8FAFF;}
    tr:last-child td{border-bottom:none;}

    .score-badge{display:inline-flex;align-items:center;gap:4px;padding:3px 11px;border-radius:20px;font-size:0.78em;font-weight:700;margin:2px;}
    .score-high{background:linear-gradient(135deg,#10B981,#059669);color:white;}
    .score-medium{background:linear-gradient(135deg,#F59E0B,#D97706);color:white;}
    .score-low{background:linear-gradient(135deg,#6366F1,#4F46E5);color:white;}

    .index-result{background:white;border-radius:14px;padding:18px 22px;margin:10px 0;border-left:5px solid #0EA5E9;box-shadow:0 3px 12px rgba(0,0,0,0.07);transition:all 0.25s ease;}
    .index-result:hover{box-shadow:0 6px 20px rgba(14,165,233,0.2);transform:translateX(3px);}
    .index-header{display:flex;align-items:center;gap:10px;margin-bottom:10px;}
    .index-location{font-family:monospace;font-size:0.82em;font-weight:700;background:linear-gradient(135deg,#EFF6FF,#DBEAFE);color:#1E40AF;padding:4px 12px;border-radius:8px;border:1px solid #BFDBFE;}
    .index-snippet{color:#4B5563;font-size:0.9em;line-height:1.7;border-top:1px solid #F1F5F9;padding-top:10px;margin-top:4px;}
    .index-snippet mark{background:linear-gradient(135deg,#FEF9C3,#FDE68A);color:#92400E;border-radius:4px;padding:1px 4px;font-weight:600;}
    .index-summary{background:linear-gradient(135deg,#073763 0%,#0369A1 100%);border-radius:16px;padding:22px 28px;margin-bottom:22px;color:white;}
    .no-results{background:#FFF7ED;border-radius:14px;padding:30px;border:2px solid #FED7AA;text-align:center;}

    .dir-card{background:white;border-radius:14px;padding:18px 22px;margin:10px 0;box-shadow:0 3px 12px rgba(0,0,0,0.07);transition:all 0.25s ease;border-left:5px solid #8B5CF6;}
    .dir-card:hover{box-shadow:0 6px 20px rgba(139,92,246,0.2);transform:translateX(3px);}
    .dir-obrigacao{border-left-color:#EF4444;}
    .dir-recomendacao{border-left-color:#F59E0B;}
    .dir-proposta{border-left-color:#10B981;}
    .dir-restricao{border-left-color:#6366F1;}
    .dir-badge{display:inline-flex;align-items:center;gap:5px;padding:3px 12px;border-radius:20px;font-size:0.76em;font-weight:700;margin-right:8px;}
    .badge-obrigacao{background:#FEE2E2;color:#991B1B;}
    .badge-recomendacao{background:#FEF3C7;color:#92400E;}
    .badge-proposta{background:#D1FAE5;color:#065F46;}
    .badge-restricao{background:#EDE9FE;color:#4C1D95;}
    .dir-text{color:#1E293B;font-size:0.93em;line-height:1.75;margin:10px 0 8px;}
    .dir-source{font-family:monospace;font-size:0.8em;color:#6B7280;}
    .dir-summary{background:linear-gradient(135deg,#4C1D95 0%,#6D28D9 100%);border-radius:16px;padding:22px 28px;margin-bottom:22px;color:white;}

    .chat-welcome{background:white;border-radius:16px;padding:25px 30px;box-shadow:0 4px 20px rgba(0,0,0,0.07);margin-bottom:22px;border-top:4px solid #0EA5E9;}
    .footer{text-align:center;padding:28px;color:#64748B;font-size:0.88em;margin-top:20px;border-top:2px dashed #CBD5E1;}
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
    <div style="margin-top:20px;">
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
    modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    for candidato in ['models/gemini-1.5-pro-latest','models/gemini-1.5-flash-latest','models/gemini-1.0-pro']:
        if candidato in modelos_disponiveis:
            modelo_nome = candidato
            break
    else:
        modelo_nome = modelos_disponiveis[0] if modelos_disponiveis else 'models/gemini-pro'

    st.sidebar.caption(f"🤖 `{modelo_nome.replace('models/', '')}`")

    instrucao_sistema = """Você é um analista técnico do Plano de Espaço Marinho (PEM) do Brasil.

REGRAS ABSOLUTAS — NUNCA VIOLE:
1. Use EXCLUSIVAMENTE as informações dos trechos fornecidos. Nada mais.
2. Se a informação não estiver nos trechos, diga: "Não encontrado nos documentos consultados."
3. NUNCA invente dados, números, leis, nomes, datas ou conclusões.
4. Cite a fonte de CADA afirmação factual: (Região | Caderno | Pág. X).
5. Complete SEMPRE a resposta — nunca corte no meio de um tópico ou seção.
6. Seja direto e técnico. Sem introduções genéricas ou repetição de perguntas."""

    model = genai.GenerativeModel(
        model_name=modelo_nome,
        system_instruction=instrucao_sistema,
        generation_config=genai.GenerationConfig(
            temperature=0.05,
            top_p=0.85,
            top_k=20,
            max_output_tokens=8192  # Respostas completas, sem corte
        )
    )
except Exception as e:
    st.error(f"⚠️ Erro de conexão com o Google AI: {e}")


# ============================================================================
# 📄 LEITURA DE PDF
# ============================================================================
def ler_e_fatiar_pdf(file_id, nome_doc, regiao):
    paginas = []
    try:
        url = f'https://drive.google.com/uc?id={file_id}'
        response = requests.get(url, timeout=30)
        reader = PdfReader(io.BytesIO(response.content))
        for i, page in enumerate(reader.pages):
            texto = page.extract_text()
            if texto and texto.strip():
                paginas.append({
                    "cabecalho": f"[{regiao} | {nome_doc} | Pág. {i+1}]",
                    "texto": texto.lower(),
                    "texto_original": texto,
                    "pagina": i + 1,
                    "regiao": regiao,
                    "caderno": nome_doc
                })
    except Exception as ex:
        st.error(f"Erro ao ler PDF: {ex}")
    return paginas


# ============================================================================
# 🔍 BUSCA E PONTUAÇÃO
# ============================================================================
PALAVRAS_IGNORADAS = {
    'o','a','os','as','de','do','da','dos','das','em','no','na','nos','nas',
    'para','com','que','quais','qual','como','sobre','mais','este','esta',
    'isso','aqui','pelo','pela','pelos','pelas','entre','também','quando',
    'onde','muito','suas','seus','seu','sua','são','está','have','from',
    'essa','esses','essas','um','uma','uns','umas','por','sendo','pode',
    'será','foram','seria','aquele','neste','esse','isto','eles','elas'
}

def extrair_palavras_chave(texto):
    tokens = re.findall(r'\b[a-záéíóúãõâêîôûàèìòùç]{4,}\b', texto.lower())
    return [t for t in tokens if t not in PALAVRAS_IGNORADAS]

def pontuar_pagina(pagina, palavras_chave):
    texto = pagina["texto"]
    return sum(len(re.findall(rf'\b{re.escape(p)}\b', texto)) for p in palavras_chave)

def buscar_paginas_relevantes(pergunta, todas_as_paginas, limite=20):
    palavras = extrair_palavras_chave(pergunta)
    if not palavras:
        return []
    resultados = [(pontuar_pagina(p, palavras), p) for p in todas_as_paginas]
    resultados = [(s, p) for s, p in resultados if s > 0]
    resultados.sort(key=lambda x: x[0], reverse=True)
    return resultados[:limite]


# ============================================================================
# 🗂️ ÍNDICE — busca direta sem IA
# ============================================================================
def buscar_indice(tema, todas_as_paginas, min_score=1, max_resultados=50):
    palavras = extrair_palavras_chave(tema)
    if not palavras:
        return []
    resultados = []
    for pag in todas_as_paginas:
        score = pontuar_pagina(pag, palavras)
        if score >= min_score:
            trecho = extrair_trecho_contexto(pag["texto_original"], palavras)
            resultados.append({
                "score": score, "cabecalho": pag["cabecalho"],
                "pagina": pag["pagina"], "regiao": pag["regiao"],
                "caderno": pag["caderno"], "trecho": trecho
            })
    resultados.sort(key=lambda x: x["score"], reverse=True)
    return resultados[:max_resultados]

def extrair_trecho_contexto(texto_original, palavras, janela=220):
    texto_lower = texto_original.lower()
    melhor_pos = -1
    for palavra in palavras:
        match = re.search(rf'\b{re.escape(palavra)}\b', texto_lower)
        if match:
            melhor_pos = match.start()
            break
    if melhor_pos == -1:
        return texto_original[:300].strip()
    inicio = max(0, melhor_pos - janela // 2)
    fim = min(len(texto_original), melhor_pos + janela)
    if inicio > 0:
        inicio = texto_original.rfind(' ', 0, inicio) + 1
    trecho = texto_original[inicio:fim].strip()
    if inicio > 0: trecho = '...' + trecho
    if fim < len(texto_original): trecho += '...'
    return trecho

def destacar_palavras(trecho, palavras):
    for palavra in palavras:
        trecho = re.sub(rf'(?i)\b({re.escape(palavra)})\b', r'<mark>\1</mark>', trecho)
    return trecho


# ============================================================================
# 📋 EXTRATOR DE DIRETRIZES E RECOMENDAÇÕES
# ============================================================================
PADROES_DIRETIVOS = {
    "Obrigação": [
        r'\bdeve\b', r'\bdevem\b', r'\bdeverá\b', r'\bdeverão\b',
        r'\bé obrigatório\b', r'\bé necessário\b', r'\bé preciso\b',
        r'\bfaz-se necessário\b', r'\bcabe\b', r'\bcompete\b',
        r'\bé vedado\b', r'\bé proibido\b', r'\bnão pode\b', r'\bnão podem\b',
        r'\bexige-se\b', r'\bé exigido\b'
    ],
    "Recomendação": [
        r'\bé recomendado\b', r'\bé recomendável\b', r'\brecomenda-se\b',
        r'\bé indicado\b', r'\bé aconselhável\b', r'\bé conveniente\b',
        r'\bsugere-se\b', r'\bé sugerido\b', r'\bpreferivelmente\b',
        r'\bidealmente\b', r'\bé desejável\b'
    ],
    "Proposta": [
        r'\bpropõe-se\b', r'\bproposto\b', r'\bproposta\b',
        r'\bprevê-se\b', r'\bprevisto\b', r'\bprevê\b', r'\bpropõem\b',
        r'\bpretende-se\b', r'\btem como objetivo\b', r'\bvisa\b', r'\bvisam\b',
        r'\bobjetiva\b', r'\bserá implementado\b', r'\bserá desenvolvido\b'
    ],
    "Restrição": [
        r'\bé restrito\b', r'\brestrito\b', r'\brestringido\b', r'\brestringir\b',
        r'\bnão é permitido\b', r'\bnão é permitida\b', r'\bnão deve\b',
        r'\bproibição\b', r'\bproibido\b', r'\bveda-se\b',
        r'\bimpede\b', r'\blimita\b', r'\bé limitado\b'
    ]
}

MIN_CHARS_DIRETIVA = 60
MAX_CHARS_DIRETIVA = 600

ICONE_CATEGORIA = {
    "Obrigação":    ("🔴", "badge-obrigacao",    "dir-obrigacao"),
    "Recomendação": ("🟡", "badge-recomendacao", "dir-recomendacao"),
    "Proposta":     ("🟢", "badge-proposta",     "dir-proposta"),
    "Restrição":    ("🟣", "badge-restricao",    "dir-restricao"),
}

def extrair_sentencas(texto):
    sentencas = re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÃÕ])', texto)
    return [s.strip() for s in sentencas if MIN_CHARS_DIRETIVA <= len(s.strip()) <= MAX_CHARS_DIRETIVA]

def classificar_sentenca(sentenca):
    s_lower = sentenca.lower()
    for categoria, padroes in PADROES_DIRETIVOS.items():
        for padrao in padroes:
            if re.search(padrao, s_lower):
                return categoria
    return None

def extrair_diretrizes(todas_as_paginas):
    diretrizes = []
    for pag in todas_as_paginas:
        for sentenca in extrair_sentencas(pag["texto_original"]):
            categoria = classificar_sentenca(sentenca)
            if categoria:
                diretrizes.append({
                    "Categoria": categoria,
                    "Diretriz": sentenca.strip(),
                    "Região": pag["regiao"],
                    "Caderno": pag["caderno"],
                    "Página": pag["pagina"],
                    "Fonte": pag["cabecalho"]
                })
    return diretrizes


# ============================================================================
# 🎯 EXTRATOR DE TRECHOS PARA O CHAT
# ============================================================================
def extrair_trechos_para_chat(resultados_buscados, pergunta, max_chars=800):
    palavras = set(extrair_palavras_chave(pergunta))
    trechos = []
    for score, pag in resultados_buscados:
        paragrafos = pag['texto_original'].split('\n\n')
        melhor_score, melhor_paragrafo = 0, ""
        for paragrafo in paragrafos:
            if len(paragrafo.strip()) < 60: continue
            p_score = sum(1 for w in palavras if w in paragrafo.lower())
            if p_score > melhor_score:
                melhor_score, melhor_paragrafo = p_score, paragrafo.strip()
        if melhor_paragrafo:
            trechos.append({'cabecalho': pag['cabecalho'], 'texto': melhor_paragrafo[:max_chars], 'score': score})
    return trechos[:25]


# ============================================================================
# 📏 CONTROLE DE CONTEXTO
# ============================================================================
def limitar_contexto(contexto, max_chars=40000):
    """Limita contexto preservando parágrafos completos — respostas nunca cortadas."""
    if len(contexto) <= max_chars:
        return contexto, len(contexto) // 4
    corte = contexto.rfind('\n\n', 0, max_chars)
    if corte == -1:
        corte = max_chars
    return contexto[:corte], corte // 4


# ============================================================================
# 🎯 DETECTOR DE TIPO DE PERGUNTA
# ============================================================================
def detectar_tipo_pergunta(pergunta):
    p = pergunta.lower()
    if any(w in p for w in ['compare','diferença','entre','vs','versus','contraste']): return "comparacao"
    if any(w in p for w in ['legislação','lei','norma','regulamento','marco legal','decreto']): return "legislacao"
    if any(w in p for w in ['impacto','consequência','efeito','resultado','afeta']): return "analise"
    if any(w in p for w in ['liste','listar','quais','cite','mencione','enumere']): return "lista"
    return "padrao"


# ============================================================================
# 🎯 PROMPTS — anti-alucinação, respostas sempre completas
# ============================================================================
def criar_prompt_final(pergunta, contexto, tipo="padrao"):
    regras = """
REGRAS (invioláveis):
• Use APENAS os trechos acima. Sem conhecimento externo.
• Cite cada afirmação: (Região | Caderno | Pág. X).
• Se não houver dados suficientes: diga "Não encontrado nos documentos consultados."
• NUNCA invente. Complete SEMPRE a resposta integralmente, sem cortar tópicos."""

    prompts = {
        "padrao": f"""TRECHOS DOCUMENTAIS:
{contexto}
{regras}

PERGUNTA: {pergunta}

RESPOSTA (organize com tópicos quando útil; aborde todos os aspectos encontrados):""",

        "comparacao": f"""TRECHOS DOCUMENTAIS:
{contexto}
{regras}

PERGUNTA: {pergunta}

RESPOSTA:
## 1. Pontos em comum
[com citações]

## 2. Diferenças encontradas
[com citações]

## 3. Tabela comparativa
[apenas se houver dados para ambas as regiões]

## 4. Lacunas documentais
[o que não foi encontrado]""",

        "lista": f"""TRECHOS DOCUMENTAIS:
{contexto}
{regras}

PERGUNTA: {pergunta}

RESPOSTA — para cada item encontrado:
- **Nome/título** — descrição (1-2 frases). Fonte: (Região | Caderno | Pág. X)

**Total encontrado:** X itens""",

        "analise": f"""TRECHOS DOCUMENTAIS:
{contexto}
{regras}

PERGUNTA: {pergunta}

RESPOSTA por dimensão (inclua apenas as com dados):
## 🌿 Ambiental
## 👥 Social
## 💰 Econômico
## ⚖️ Institucional
## ⚠️ Lacunas documentais""",

        "legislacao": f"""TRECHOS DOCUMENTAIS:
{contexto}
{regras}

PERGUNTA: {pergunta}

RESPOSTA:
## 1. Instrumentos legais mencionados
[lei/decreto/norma + número quando disponível + citação]

## 2. Competências e responsabilidades

## 3. Lacunas ou conflitos apontados"""
    }
    return prompts.get(tipo, prompts["padrao"])


# ============================================================================
# 🎯 FORMATADOR DE TABELAS
# ============================================================================
def formatar_tabela_markdown(texto):
    linhas = texto.split('\n')
    resultado, i = [], 0
    while i < len(linhas):
        linha = linhas[i].strip()
        if linha.startswith('|') and linha.count('|') >= 3:
            tabela = []
            while i < len(linhas) and (linhas[i].strip().startswith('|') or '---' in linhas[i]):
                partes = [p.strip() for p in linhas[i].strip().split('|') if p.strip()]
                tabela.append('| ' + ' | '.join(partes) + ' |' if len(partes) >= 2 else linhas[i].strip())
                i += 1
            if len(tabela) >= 2 and '---' not in (tabela[1] if len(tabela) > 1 else ''):
                cols = tabela[0].count('|') - 1
                tabela.insert(1, '| ' + ' | '.join(['---'] * cols) + ' |')
            resultado.extend(tabela)
        else:
            resultado.append(linha)
            i += 1
    return '\n'.join(resultado)

def exibir_score_html(score):
    if score >= 5:   return f'<span class="score-badge score-high">▲ Alta ({score})</span>'
    elif score >= 2: return f'<span class="score-badge score-medium">● Média ({score})</span>'
    else:            return f'<span class="score-badge score-low">▼ Baixa ({score})</span>'


# ============================================================================
# 📚 BARRA LATERAL
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div style="font-size:3.5em;">📚</div>
        <h3 style="color:white;margin:10px 0 4px;">Biblioteca PEM</h3>
        <p style="color:rgba(255,255,255,0.8);font-size:0.82em;margin:0;">Cadernos Setoriais Oficiais</p>
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

    for key, default in [("cadernos_ativos",[]),("todas_as_paginas_lidas",[]),("mensagens",[])]:
        if key not in st.session_state:
            st.session_state[key] = default

    if st.session_state.cadernos_ativos:
        st.markdown('<div class="loaded-notebooks"><h4 style="color:#059669;margin:0 0 12px 0;">✅ Carregados</h4>', unsafe_allow_html=True)
        for regiao, nome, _ in st.session_state.cadernos_ativos:
            icon = "🗺️" if regiao == "SUL" else "🌴"
            rc = "region-sul" if regiao == "SUL" else "region-ne"
            st.markdown(f"""
            <div class="loaded-notebook-item">
                <span>{icon}</span>
                <span class="notebook-region {rc}">{regiao}</span>
                <span style="color:#374151;flex:1;font-size:0.87em;">{nome}</span>
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
aba1, aba2, aba3 = st.tabs(["🔮 Chat Analítico", "🗂️ Índice de Temas", "📋 Extrator de Diretrizes"])


# ─────────────────────────────────────────────────────────────
# ABA 1 — CHAT
# ─────────────────────────────────────────────────────────────
with aba1:
    st.markdown("""
    <div class="chat-welcome">
        <h3 style="color:#0C4A6E;margin-top:0;">💬 Faça sua pergunta</h3>
        <p style="color:#64748B;margin:0;">
            Perguntas sobre zoneamento, conservação, impactos, legislação, pesca, energia e mais.
            Respostas fundamentadas e rastreáveis até a página de origem.
        </p>
    </div>""", unsafe_allow_html=True)

    for m in st.session_state.mensagens:
        with st.chat_message(m["role"], avatar="👤" if m["role"]=="user" else "🤖"):
            st.markdown(m["content"])

    pergunta = st.chat_input("Digite sua pergunta sobre os cadernos PEM...")

    if pergunta:
        if not st.session_state.cadernos_ativos:
            st.error("⚠️ Selecione ao menos um caderno na barra lateral.")
        else:
            st.session_state.mensagens.append({"role":"user","content":pergunta})
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("🔍 Buscando e analisando documentos..."):
                    resultados = buscar_paginas_relevantes(pergunta, st.session_state.todas_as_paginas_lidas, limite=20)
                    trechos = extrair_trechos_para_chat(resultados, pergunta)
                    contexto = "\n\n".join(f"{t['cabecalho']}\n{t['texto']}" for t in trechos)
                    contexto, tokens_est = limitar_contexto(contexto, max_chars=40000)

                    with st.expander(f"📚 {len(trechos)} trechos consultados | ~{tokens_est} tokens estimados", expanded=False):
                        for t in trechos:
                            st.markdown(f"`{t['cabecalho']}` {exibir_score_html(t['score'])}", unsafe_allow_html=True)

                    if not trechos:
                        aviso = "⚠️ Nenhum trecho relevante encontrado. Tente reformular ou carregar outros cadernos."
                        st.warning(aviso)
                        st.session_state.mensagens.append({"role":"assistant","content":aviso})
                    else:
                        tipo = detectar_tipo_pergunta(pergunta)
                        prompt = criar_prompt_final(pergunta, contexto, tipo)
                        try:
                            res = model.generate_content(prompt)
                            resposta = formatar_tabela_markdown(res.text)
                            st.markdown(resposta)
                            st.session_state.mensagens.append({"role":"assistant","content":resposta})
                        except Exception as e:
                            st.error(f"⚠️ Erro na geração: {e}")


# ─────────────────────────────────────────────────────────────
# ABA 2 — ÍNDICE DE TEMAS
# ─────────────────────────────────────────────────────────────
with aba2:
    st.markdown("""
    <div class="chat-welcome">
        <h3 style="color:#0C4A6E;margin-top:0;">🗂️ Índice de Temas</h3>
        <p style="color:#64748B;margin:0;">
            Veja em quais páginas um tema aparece — busca direta no texto,
            <strong>sem IA</strong>, 100% rastreável, com trechos destacados.
        </p>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.cadernos_ativos:
        st.warning("⚠️ Selecione ao menos um caderno na barra lateral.")
    else:
        col1, col2 = st.columns([4,1])
        with col1:
            tema_indice = st.text_input("🔎", placeholder="Ex: zoneamento, licença ambiental, correntes marítimas...", label_visibility="collapsed")
        with col2:
            btn_buscar = st.button("Buscar", type="primary", use_container_width=True)

        col_a, col_b, col_c = st.columns(3)
        with col_a: min_ocorrencias = st.slider("Ocorrências mínimas", 1, 10, 1)
        with col_b: max_resultados  = st.slider("Máx. páginas", 10, 100, 40)
        with col_c: mostrar_trecho  = st.toggle("Mostrar trechos", value=True)

        if btn_buscar and tema_indice.strip():
            with st.spinner("🔎 Varrendo documentos..."):
                resultados_indice = buscar_indice(tema_indice, st.session_state.todas_as_paginas_lidas, min_score=min_ocorrencias, max_resultados=max_resultados)

            if not resultados_indice:
                st.markdown(f"""
                <div class="no-results">
                    <div style="font-size:2.5em;margin-bottom:12px;">🔍</div>
                    <h4 style="color:#92400E;margin:0 0 8px;">Nenhuma menção encontrada</h4>
                    <p style="color:#78350F;margin:0;">
                        <strong>"{tema_indice}"</strong> não aparece com mínimo de {min_ocorrencias} ocorrência(s).
                        Tente variações ou reduza o filtro.
                    </p>
                </div>""", unsafe_allow_html=True)
            else:
                por_caderno = {}
                for r in resultados_indice:
                    por_caderno.setdefault(f"{r['regiao']} | {r['caderno']}", []).append(r)

                pag_total   = sum(len(v) for v in por_caderno.values())
                ocorr_total = sum(r['score'] for r in resultados_indice)

                st.markdown(f"""
                <div class="index-summary">
                    <div style="display:flex;gap:40px;flex-wrap:wrap;align-items:center;">
                        <div><div style="font-size:2.2em;font-weight:800;">{pag_total}</div><div style="opacity:0.85;font-size:0.9em;">páginas com menções</div></div>
                        <div><div style="font-size:2.2em;font-weight:800;">{ocorr_total}</div><div style="opacity:0.85;font-size:0.9em;">ocorrências totais</div></div>
                        <div><div style="font-size:2.2em;font-weight:800;">{len(por_caderno)}</div><div style="opacity:0.85;font-size:0.9em;">cadernos envolvidos</div></div>
                        <div style="flex:1;min-width:200px;">
                            <div style="opacity:0.85;font-size:0.88em;margin-bottom:4px;">Tema pesquisado</div>
                            <div style="font-size:1.1em;font-weight:700;background:rgba(255,255,255,0.15);padding:6px 14px;border-radius:8px;display:inline-block;">🔍 {tema_indice}</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

                palavras_busca = extrair_palavras_chave(tema_indice)
                for chave, paginas in por_caderno.items():
                    regiao, caderno = chave.split(" | ", 1)
                    icon = "🗺️" if regiao == "SUL" else "🌴"
                    total_ocorr = sum(p['score'] for p in paginas)
                    with st.expander(f"{icon} {caderno}  —  {len(paginas)} pág. · {total_ocorr} ocorrências", expanded=True):
                        for r in paginas:
                            trecho_html = ""
                            if mostrar_trecho and r['trecho']:
                                td = destacar_palavras(re.sub(r'<[^>]+>', '', r['trecho']), palavras_busca)
                                trecho_html = f'<div class="index-snippet">{td}</div>'
                            st.markdown(f"""
                            <div class="index-result">
                                <div class="index-header">
                                    <span class="index-location">{r['cabecalho']}</span>
                                    {exibir_score_html(r['score'])}
                                </div>
                                {trecho_html}
                            </div>""", unsafe_allow_html=True)

                st.markdown("---")
                linhas_exp = [f"# Índice — {tema_indice}\n", f"Total: {pag_total} páginas | {ocorr_total} ocorrências\n"]
                for r in resultados_indice:
                    linhas_exp.append(f"- {r['cabecalho']} ({r['score']} ocorrência(s))")
                st.download_button("📋 Exportar índice (.txt)", "\n".join(linhas_exp),
                                   file_name=f"indice_{tema_indice.replace(' ','_')}.txt", mime="text/plain")


# ─────────────────────────────────────────────────────────────
# ABA 3 — EXTRATOR DE DIRETRIZES
# ─────────────────────────────────────────────────────────────
with aba3:
    st.markdown("""
    <div class="chat-welcome" style="border-top-color:#8B5CF6;">
        <h3 style="color:#4C1D95;margin-top:0;">📋 Extrator de Diretrizes & Recomendações</h3>
        <p style="color:#64748B;margin:0;">
            Varre <strong>automaticamente</strong> todos os documentos e extrai <em>todas</em> as sentenças 
            normativas — obrigações, recomendações, propostas e restrições — organizadas, filtráveis e exportáveis.<br>
            <span style="font-size:0.88em;color:#8B5CF6;">✦ Sem IA · Zero alucinação · 100% baseado no texto dos documentos</span>
        </p>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.cadernos_ativos:
        st.warning("⚠️ Selecione ao menos um caderno na barra lateral.")
    else:
        if st.button("🚀 Extrair Todas as Diretrizes", type="primary", use_container_width=True):
            with st.spinner("🔬 Analisando padrões linguísticos em todos os documentos..."):
                st.session_state["diretrizes_cache"] = extrair_diretrizes(st.session_state.todas_as_paginas_lidas)

        if st.session_state.get("diretrizes_cache"):
            diretrizes = st.session_state["diretrizes_cache"]
            df = pd.DataFrame(diretrizes)

            # ── Filtros ──────────────────────────────────────────────────────
            st.markdown("---")
            fc1, fc2, fc3 = st.columns(3)
            with fc1: cats_sel    = st.multiselect("Categoria", sorted(df["Categoria"].unique()), default=sorted(df["Categoria"].unique()))
            with fc2: cads_sel    = st.multiselect("Caderno",   sorted(df["Caderno"].unique()),   default=sorted(df["Caderno"].unique()))
            with fc3: regioes_sel = st.multiselect("Região",    sorted(df["Região"].unique()),    default=sorted(df["Região"].unique()))
            busca_texto = st.text_input("🔎 Filtrar por palavra no texto:", placeholder="Ex: licença, pesca, ruído...")

            df_f = df[df["Categoria"].isin(cats_sel) & df["Caderno"].isin(cads_sel) & df["Região"].isin(regioes_sel)]
            if busca_texto.strip():
                df_f = df_f[df_f["Diretriz"].str.contains(busca_texto, case=False, na=False)]

            # ── Sumário ──────────────────────────────────────────────────────
            por_cat = df_f["Categoria"].value_counts()
            cat_html = "".join(
                f'<div><div style="font-size:1.8em;font-weight:800;">{por_cat.get(c,0)}</div>'
                f'<div style="opacity:0.85;font-size:0.88em;">{ICONE_CATEGORIA[c][0]} {c}s</div></div>'
                for c in ["Obrigação","Recomendação","Proposta","Restrição"] if c in por_cat
            )
            st.markdown(f"""
            <div class="dir-summary">
                <div style="display:flex;gap:36px;flex-wrap:wrap;align-items:center;">
                    <div><div style="font-size:2.4em;font-weight:800;">{len(df_f)}</div><div style="opacity:0.85;font-size:0.9em;">diretrizes encontradas</div></div>
                    {cat_html}
                </div>
            </div>""", unsafe_allow_html=True)

            # ── Resultados por caderno ────────────────────────────────────────
            for caderno in sorted(df_f["Caderno"].unique()):
                df_cad = df_f[df_f["Caderno"] == caderno]
                regiao_cad = df_cad["Região"].iloc[0]
                icon = "🗺️" if regiao_cad == "SUL" else "🌴"

                with st.expander(f"{icon} {caderno} — {len(df_cad)} diretrizes", expanded=False):
                    cats_cad = sorted(df_cad["Categoria"].unique())
                    sub_tabs = st.tabs([f"{ICONE_CATEGORIA[c][0]} {c}s ({len(df_cad[df_cad['Categoria']==c])})" for c in cats_cad]) if len(cats_cad) > 1 else [st.container()]

                    for idx, cat in enumerate(cats_cad):
                        with sub_tabs[idx]:
                            df_cat = df_cad[df_cad["Categoria"] == cat].sort_values("Página")
                            icone, badge_class, card_class = ICONE_CATEGORIA[cat]
                            for _, row in df_cat.iterrows():
                                texto_dest = row["Diretriz"]
                                if busca_texto.strip():
                                    texto_dest = re.sub(rf'(?i)({re.escape(busca_texto)})', r'<mark>\1</mark>', texto_dest)
                                st.markdown(f"""
                                <div class="dir-card {card_class}">
                                    <div>
                                        <span class="dir-badge {badge_class}">{icone} {cat}</span>
                                        <span style="font-size:0.8em;color:#9CA3AF;">Pág. {row['Página']}</span>
                                    </div>
                                    <div class="dir-text">{texto_dest}</div>
                                    <div class="dir-source">📍 {row['Fonte']}</div>
                                </div>""", unsafe_allow_html=True)

            # ── Exportação ────────────────────────────────────────────────────
            st.markdown("---")
            exp1, exp2 = st.columns(2)
            with exp1:
                csv_data = df_f[["Categoria","Diretriz","Região","Caderno","Página"]].to_csv(index=False, encoding="utf-8-sig")
                st.download_button("📊 Exportar como CSV", csv_data, file_name="diretrizes_pem.csv", mime="text/csv", use_container_width=True)
            with exp2:
                md_lines = ["# Diretrizes & Recomendações — PEM\n"]
                for cat in ["Obrigação","Recomendação","Proposta","Restrição"]:
                    df_c = df_f[df_f["Categoria"] == cat]
                    if not df_c.empty:
                        md_lines.append(f"\n## {ICONE_CATEGORIA[cat][0]} {cat}s ({len(df_c)})\n")
                        for _, r in df_c.iterrows():
                            md_lines.append(f"- **[{r['Fonte']}]** {r['Diretriz']}\n")
                st.download_button("📄 Exportar como Markdown", "\n".join(md_lines), file_name="diretrizes_pem.md", mime="text/markdown", use_container_width=True)

        elif "diretrizes_cache" in st.session_state and not st.session_state["diretrizes_cache"]:
            st.info("ℹ️ Nenhuma sentença diretiva identificada nos documentos carregados.")


# ============================================================================
# 🌊 FOOTER
# ============================================================================
st.markdown("""
<div class="footer">
    <p>🌊 <strong>Assistente PEM</strong> · Marinha do Brasil — SECIRM</p>
    <p style="opacity:0.5;font-size:0.82em;margin-top:4px;">⚠️ Sempre valide as informações nos documentos oficiais antes de utilizá-las.</p>
</div>""", unsafe_allow_html=True)
