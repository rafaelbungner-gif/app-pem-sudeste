import streamlit as st
import google.generativeai as genai
import requests
import io
import re
from PyPDF2 import PdfReader

# ============================================================================
# 📚 BANCO DE DADOS DOS CADERNOS (IDs DO GOOGLE DRIVE)
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
# 💅 ESTILOS CSS PERSONALIZADOS
# ============================================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #F0F9FF 0%, #E0F2FE 100%);
    }
    
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
    
    .sidebar-divider {
        border-top: 2px dashed rgba(255,255,255,0.25);
        margin: 20px 0;
    }
    
    .wave-divider {
        height: 60px;
        background: url('image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%230EA5E9" fill-opacity="0.15" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,112C672,96,768,96,864,112C960,128,1056,160,1152,160C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
        background-size: cover;
        margin: 30px 0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
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
    
    /* Tabelas Markdown */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    
    th {
        background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 100%);
        color: white;
        padding: 14px 18px;
        text-align: left;
        font-weight: 600;
        font-size: 0.95em;
    }
    
    td {
        padding: 14px 18px;
        border-bottom: 1px solid #E2E8F0;
        color: #374151;
        line-height: 1.6;
        font-size: 0.92em;
    }
    
    tr:hover {
        background: #F8FAFC;
    }
    
    tr:last-child td {
        border-bottom: none;
    }
    
    /* Citações */
    .citation {
        display: inline-block;
        background: #E0F2FE;
        color: #0369A1;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75em;
        font-weight: 600;
        margin-left: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 🌊 HEADER PRINCIPAL
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
    
    modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    if 'models/gemini-1.5-pro-latest' in modelos_disponiveis:
        modelo_nome = 'models/gemini-1.5-pro-latest'
    elif 'models/gemini-1.5-flash-latest' in modelos_disponiveis:
        modelo_nome = 'models/gemini-1.5-flash-latest'
    elif 'models/gemini-1.0-pro' in modelos_disponiveis:
        modelo_nome = 'models/gemini-1.0-pro'
    else:
        modelo_nome = modelos_disponiveis[0] if modelos_disponiveis else 'models/gemini-pro'
    
    st.sidebar.caption(f"🤖 Modelo: `{modelo_nome.replace('models/', '')}`")

    instrucao_sistema = """Você é um analista técnico de alto rigor especializado no Plano de Espaço Marinho (PEM) do Brasil.
    REGRAS OBRIGATÓRIAS:
    1. Baseie-se ESTRITAMENTE nos trechos fornecidos
    2. Cada afirmação DEVE ter citação: (Região | Caderno | Pág. X)
    3. Se não encontrar informação, diga: "Não encontrei essa informação nos cadernos"
    4. NÃO invente dados, leis, números ou citações
    5. Para tabelas: máximo 2 frases por célula, sempre com citação"""

    model = genai.GenerativeModel(
        model_name=modelo_nome,
        system_instruction=instrucao_sistema,
        generation_config=genai.GenerationConfig(
            temperature=0.15,
            top_p=0.85,
            top_k=40,
            max_output_tokens=8192
        )
    )
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
                cabecalho = f"[{regiao} | {nome_doc} | Pág. {i+1}]"
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
def buscar_paginas_relevantes(pergunta, todas_as_paginas, limite_paginas=20):
    paginas_estruturais = []
    for pag in todas_as_paginas:
        match = re.search(r'Pág.:\s*(\d+)', pag['cabecalho'])
        if match and int(match.group(1)) <= 6:
            paginas_estruturais.append(pag)

    palavras_pergunta = re.findall(r'\w+', pergunta.lower())
    palavras_ignoradas = {'o', 'a', 'os', 'as', 'de', 'do', 'da', 'em', 'no', 'na', 
                          'para', 'com', 'que', 'quais', 'qual', 'como', 'sobre'}
    palavras_chave = [p for p in palavras_pergunta if p not in palavras_ignoradas and len(p) > 3]
    
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
# 🎯 EXTRATOR DE TRECHOS RELEVANTES
# ============================================================================
def extrair_trechos_relevantes(paginas_filtradas, pergunta, max_caracteres=700):
    palavras_chave = set(re.findall(r'\w{4,}', pergunta.lower()))
    trechos = []
    
    for pag in paginas_filtradas:
        paragrafos = pag['texto_original'].split('\n\n')
        
        for i, paragrafo in enumerate(paragrafos):
            paragrafo_limpo = paragrafo.strip()
            if len(paragrafo_limpo) < 50:
                continue
            
            score = sum(1 for palavra in palavras_chave if palavra.lower() in paragrafo_limpo.lower())
            
            if score >= 2:
                contexto_completo = []
                if i > 0 and len(paragrafos[i-1].strip()) > 40:
                    contexto_completo.append(paragrafos[i-1].strip())
                contexto_completo.append(paragrafo_limpo)
                if i < len(paragrafos) - 1 and len(paragrafos[i+1].strip()) > 40:
                    contexto_completo.append(paragrafos[i+1].strip())
                
                texto_final = '\n\n'.join(contexto_completo)[:max_caracteres]
                
                trechos.append({
                    'cabecalho': pag['cabecalho'],
                    'texto': texto_final,
                    'score': score
                })
    
    trechos.sort(key=lambda x: x['score'], reverse=True)
    return trechos[:25]

# ============================================================================
# 📏 CONTROLE DE TOKENS
# ============================================================================
def contar_tokens(texto):
    return len(texto) // 4

def limitar_contexto(contexto, max_tokens=8000):
    tokens_atuais = contar_tokens(contexto)
    if tokens_atuais <= max_tokens:
        return contexto, tokens_atuais
    
    linhas = contexto.split('\n')
    contexto_reduzido = []
    tokens_usados = 0
    
    for linha in linhas:
        tokens_linha = contar_tokens(linha)
        if tokens_usados + tokens_linha <= max_tokens:
            contexto_reduzido.append(linha)
            tokens_usados += tokens_linha
    
    return '\n'.join(contexto_reduzido), tokens_usados

# ============================================================================
# 🎯 DETECTOR DE TIPO DE PERGUNTA
# ============================================================================
def detectar_tipo_pergunta(pergunta):
    p = pergunta.lower()
    if any(w in p for w in ['compare', 'diferença', 'diferenças', 'entre', 'vs', 'versus']):
        return "comparacao"
    elif any(w in p for w in ['liste', 'listar', 'quais', 'cite', 'mencione']):
        return "lista"
    elif any(w in p for w in ['legislação', 'lei', 'norma', 'regulamento', 'marco legal']):
        return "legislacao"
    elif any(w in p for w in ['impacto', 'consequência', 'efeito', 'resultado']):
        return "analise"
    return "padrao"

# ============================================================================
# 🎯 PROMPTS OTIMIZADOS
# ============================================================================
def criar_prompt_final(pergunta, contexto, tipo="padrao"):
    
    prompts = {
        "padrao": f"""
### CONTEXTO DOCUMENTAL
{contexto}

---

### PERGUNTA
{pergunta}

---

### INSTRUÇÕES
1. Responda APENAS com base no contexto acima
2. Citação obrigatória: (Região | Caderno | Pág. X) após cada afirmação
3. Use bullet points para organizar
4. Se não encontrar: "Não encontrei essa informação nos cadernos"
5. NÃO invente dados ou citações
6. Máximo 600 palavras

### RESPOSTA
""",

        "comparacao": f"""
### CONTEXTO DOCUMENTAL
{contexto}

---

### TAREFA
Compare Sul vs Nordeste sobre: {pergunta}

---

### FORMATO OBRIGATÓRIO

Use ESTA estrutura de tabela:

| Aspecto | Região Sul | Região Nordeste |
|---------|------------|-----------------|
| [Aspecto 1] | [Info Sul com citação] | [Info NE com citação] |
| [Aspecto 2] | [Info Sul com citação] | [Info NE com citação] |
| [Aspecto 3] | [Info Sul com citação] | [Info NE com citação] |
| [Aspecto 4] | [Info Sul com citação] | [Info NE com citação] |
| [Aspecto 5] | [Info Sul com citação] | [Info NE com citação] |

---

### REGRAS DA TABELA
- Máximo 2 frases por célula
- Citação em cada célula: (Região | Caderno | Pág. X)
- Se não tiver info: "Não documentado"
- Mínimo 5 aspectos

---

### APÓS A TABELA

**📌 Similaridades:**
- [Item com citação]

**⚠️ Diferenças:**
- [Item com citação]

**🔍 Lacunas:**
- [O que não está documentado]

---

### RESPOSTA
""",

        "lista": f"""
### CONTEXTO DOCUMENTAL
{contexto}

---

### PERGUNTA
{pergunta}

---

### INSTRUÇÕES
- Liste TODOS os itens encontrados
- Cada item: descrição + citação (Região | Caderno | Pág. X)
- Agrupe por categoria
- Informe total de itens

### RESPOSTA
""",

        "legislacao": f"""
### CONTEXTO DOCUMENTAL
{contexto}

---

### PERGUNTA
{pergunta}

---

### INSTRUÇÕES
1. Liste leis/normas específicas
2. Cite página para cada informação
3. Se não houver detalhes, informe
4. NÃO invente números de leis

### RESPOSTA
""",

        "analise": f"""
### CONTEXTO DOCUMENTAL
{contexto}

---

### PERGUNTA
{pergunta}

---

### ESTRUTURA
1. **Resumo**: Principais pontos (2-3 frases)
2. **Impactos por Categoria**:
   - 🌿 Ambiental
   - 👥 Social
   - 💰 Econômico
3. **Citações**: (Região | Caderno | Pág. X) em cada afirmação

### RESPOSTA
"""
    }
    
    return prompts.get(tipo, prompts["padrao"])

# ============================================================================
# 🎯 FORMATADOR DE TABELAS
# ============================================================================
def formatar_tabela_markdown(texto):
    linhas = texto.split('\n')
    resultado = []
    i = 0
    
    while i < len(linhas):
        linha = linhas[i].strip()
        
        if linha.startswith('|') and linha.count('|') >= 3:
            tabela = []
            while i < len(linhas) and (linhas[i].strip().startswith('|') or '---' in linhas[i]):
                tabela_linha = linhas[i].strip()
                partes = [p.strip() for p in tabela_linha.split('|') if p.strip()]
                if len(partes) >= 2:
                    tabela.append('| ' + ' | '.join(partes) + ' |')
                else:
                    tabela.append(tabela_linha)
                i += 1
            
            if len(tabela) >= 2 and '---' not in tabela[1]:
                cols = tabela[0].count('|') - 1
                separador = '| ' + ' | '.join(['---'] * cols) + ' |'
                tabela.insert(1, separador)
            
            resultado.extend(tabela)
        else:
            resultado.append(linha)
            i += 1
    
    return '\n'.join(resultado)

# ============================================================================
# 📚 BARRA LATERAL
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0; background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 100%); 
                border-radius: 15px; margin-bottom: 20px;">
        <div style="font-size: 4em;">📚</div>
        <h3 style="color: white; margin: 10px 0;">Biblioteca PEM</h3>
        <p style="color: rgba(255,255,255,0.85); font-size: 0.85em;">Cadernos Setoriais Oficiais</p>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<h4>📍 Região Sul</h4>", unsafe_allow_html=True)
    escolha_sul = st.selectbox("", list(CADERNOS_SUL.keys()), key="sul_select", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<h4>📍 Região Nordeste</h4>", unsafe_allow_html=True)
    escolha_ne = st.selectbox("", list(CADERNOS_NE.keys()), key="ne_select", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    
    if "cadernos_ativos" not in st.session_state:
        st.session_state.cadernos_ativos = []
    if "todas_as_paginas_lidas" not in st.session_state:
        st.session_state.todas_as_paginas_lidas = []
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []
    
    if st.session_state.cadernos_ativos:
        st.markdown('<div class="loaded-notebooks"><h4 style="color:#059669;margin:0 0 12px 0;">✅ Carregados</h4>', unsafe_allow_html=True)
        
        for regiao, nome, _ in st.session_state.cadernos_ativos:
            icon = "🗺️" if regiao == "SUL" else "🌴"
            region_class = "region-sul" if regiao == "SUL" else "region-ne"
            st.markdown(f"""
            <div class="loaded-notebook-item">
                <span class="notebook-icon">{icon}</span>
                <span class="notebook-region {region_class}">{regiao}</span>
                <span style="color:#374151;flex:1;">{nome}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.todas_as_paginas_lidas)}</div>
            <div class="metric-label">📄 Páginas Indexadas</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("👈 Selecione cadernos para começar")

# ============================================================================
# 💾 CONTROLE DE ESTADO
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
        st.sidebar.success("🎉 Pronto!")
        st.rerun()

# ============================================================================
# 📑 ABAS PRINCIPAIS
# ============================================================================
aba1, aba2 = st.tabs(["🔮 Chat", "⚖️ Comparador"])

with aba1:
    st.markdown("""
    <div style="background: white; border-radius: 15px; padding: 25px; 
                box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 20px;">
        <h3 style="color: #0C4A6E; margin-top: 0;">💬 Como posso ajudar?</h3>
        <p style="color: #64748B; margin-bottom: 0;">
            Faça perguntas sobre zoneamento, conservação, impactos, turismo, pesca e legislação.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []
    
    for m in st.session_state.mensagens:
        with st.chat_message(m["role"], avatar="👤" if m["role"]=="user" else "🤖"):
            st.markdown(m["content"])
    
    pergunta = st.chat_input("Sua pergunta sobre os cadernos PEM...")
    
    if pergunta:
        if not st.session_state.cadernos_ativos:
            st.error("⚠️ Selecione ao menos um caderno!")
        else:
            st.session_state.mensagens.append({"role": "user", "content": pergunta})
            
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("🔍 Analisando documentos..."):
                    pags = buscar_paginas_relevantes(pergunta, st.session_state.todas_as_paginas_lidas, 15)
                    trechos = extrair_trechos_relevantes(pags, pergunta)
                    
                    contexto = ""
                    for t in trechos:
                        contexto += f"\n{t['cabecalho']}\n{t['texto']}\n"
                    
                    contexto, tokens = limitar_contexto(contexto, 6000)
                    tipo = detectar_tipo_pergunta(pergunta)
                    prompt = criar_prompt_final(pergunta, contexto, tipo)
                    
                    with st.expander(f"📚 {len(trechos)} trechos ({tokens} tokens)"):
                        for t in trechos:
                            st.markdown(f"`{t['cabecalho']}` | Score: {t['score']}")
                    
                    try:
                        res = model.generate_content(prompt)
                        resposta = formatar_tabela_markdown(res.text)
                        st.markdown(resposta)
                        st.session_state.mensagens.append({"role": "assistant", "content": resposta})
                    except Exception as e:
                        st.error(f"⚠️ Erro: {e}")

with aba2:
    if len(st.session_state.cadernos_ativos) < 2:
        st.markdown("""
        <div style="background: #FFFBEB; border-radius: 15px; padding: 35px; 
                    border: 2px solid #FCD34D; text-align: center;">
            <div style="font-size: 3.5em; margin-bottom: 15px;">💡</div>
            <h3 style="color: #92400E; margin-top: 0;">Comparação Regional</h3>
            <p style="color: #78350F; margin-bottom: 25px;">
                Selecione <strong>um caderno do Sul e um do Nordeste</strong> na barra lateral.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 100%); 
                    border-radius: 15px; padding: 25px; color: white; margin-bottom: 20px;">
            <h3 style="margin-top: 0;">⚖️ Comparação Estratégica Regional</h3>
            <p style="margin-bottom: 0; opacity: 0.92;">Sul vs Nordeste</p>
        </div>
        """, unsafe_allow_html=True)
        
        tema_comparacao = st.text_input(
            "🎯 Tema da comparação:",
            placeholder="Ex: zoneamento, licenciamento, conservação...",
            value="diretrizes zoneamento conservação"
        )
        
        if st.button("🚀 Executar Comparação", type="primary", use_container_width=True):
            with st.spinner("📊 Analisando..."):
                pags = buscar_paginas_relevantes(tema_comparacao, st.session_state.todas_as_paginas_lidas, 25)
                trechos = extrair_trechos_relevantes(pags, tema_comparacao)
                
                contexto = ""
                for t in trechos:
                    contexto += f"\n{t['cabecalho']}\n{t['texto']}\n"
                
                contexto, tokens = limitar_contexto(contexto, 10000)
                prompt = criar_prompt_final(tema_comparacao, contexto, "comparacao")
                
                with st.expander(f"📚 {len(trechos)} fontes ({tokens} tokens)"):
                    for t in trechos:
                        st.markdown(f"`{t['cabecalho']}` | Score: {t['score']}")
                
                try:
                    res = model.generate_content(prompt)
                    resposta = formatar_tabela_markdown(res.text)
                    st.markdown(resposta)
                    
                    st.download_button(
                        label="📋 Baixar Comparação",
                        data=resposta,
                        file_name=f"comparacao_{tema_comparacao.replace(' ', '_')}.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"⚠️ Erro: {e}")

# ============================================================================
# 🌊 FOOTER
# ============================================================================
st.markdown("<div class='wave-divider'></div>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 30px; color: #64748B; font-size: 0.9em;">
    <p>🌊 <strong>Assistente PEM</strong> | Marinha do Brasil - SECIRM</p>
    <p style="opacity: 0.5; font-size: 0.8em;">⚠️ Valide informações nos documentos oficiais</p>
</div>
""", unsafe_allow_html=True)
