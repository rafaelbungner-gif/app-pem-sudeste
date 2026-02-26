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
# 💅 ESTILOS CSS
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
    
    /* Response quality indicator */
    .quality-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: 600;
        margin-left: 10px;
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
# 🔧 CONFIGURAÇÃO DA IA (COM BUSCA AUTOMÁTICA DO MELHOR MODELO)
# ============================================================================
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 1. Busca todos os modelos disponíveis na sua chave
    modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # 2. Escolhe o melhor modelo disponível automaticamente
    if 'models/gemini-1.5-pro-latest' in modelos_disponiveis:
        modelo_nome = 'models/gemini-1.5-pro-latest'
    elif 'models/gemini-1.5-flash-latest' in modelos_disponiveis:
        modelo_nome = 'models/gemini-1.5-flash-latest'
    elif 'models/gemini-1.0-pro' in modelos_disponiveis:
        modelo_nome = 'models/gemini-1.0-pro'
    elif 'models/gemini-pro' in modelos_disponiveis:
        modelo_nome = 'models/gemini-pro'
    else:
        modelo_nome = modelos_disponiveis[0] # Pega o primeiro que funcionar como último recurso
        
    st.sidebar.caption(f"🤖 Modelo ativo: `{modelo_nome.replace('models/', '')}`")

    instrucao_sistema = """Você é um analista técnico de alto rigor metodológico especializado no Plano de Espaço Marinho (PEM) do Brasil. 
    Regra de Ouro: Baseie sua resposta ESTRITAMENTE nos trechos fornecidos. Não invente ou presuma informações.
    Se a resposta não estiver nos trechos, declare claramente: 'Não encontrei essa informação nos cadernos selecionados'.
    Citação Obrigatória: Ao final de cada afirmação técnica, cite (Região | Caderno | Página X)."""

    model = genai.GenerativeModel(
        model_name=modelo_nome,
        system_instruction=instrucao_sistema,
        generation_config=genai.GenerationConfig(
            temperature=0.1,       # Extrema precisão
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192 # Evita que a resposta seja cortada
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
def buscar_paginas_relevantes(pergunta, todas_as_paginas, limite_paginas=50):
    """Busca páginas com limite aumentado para mais contexto"""
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
# 🎯 EXTRATOR DE TRECHOS - VERSÃO QUALIDADE (NÃO CORTA TANTO)
# ============================================================================
def extrair_trechos_relevantes(paginas_filtradas, pergunta, max_caracteres_por_trecho=800):
    """
    Extrai parágrafos relevantes PRESERVANDO o contexto completo.
    Limite maior (800 vs 500) para não perder informações importantes.
    """
    palavras_chave = set(re.findall(r'\w{4,}', pergunta.lower()))
    trechos = []
    
    for pag in paginas_filtradas:
        # Divide em parágrafos
        paragrafos = pag['texto_original'].split('\n\n')
        
        for i, paragrafo in enumerate(paragrafos):
            paragrafo_limpo = paragrafo.strip()
            if len(paragrafo_limpo) < 40:
                continue
                
            # Score de relevância
            score = sum(1 for palavra in palavras_chave if palavra.lower() in paragrafo_limpo.lower())
            
            # Se o parágrafo é relevante OU está próximo de um parágrafo relevante
            if score >= 1:
                # Inclui parágrafo anterior e seguinte para contexto (se existirem)
                contexto_completo = []
                if i > 0 and len(paragrafos[i-1].strip()) > 30:
                    contexto_completo.append(paragrafos[i-1].strip())
                contexto_completo.append(paragrafo_limpo)
                if i < len(paragrafos) - 1 and len(paragrafos[i+1].strip()) > 30:
                    contexto_completo.append(paragrafos[i+1].strip())
                
                texto_final = '\n\n'.join(contexto_completo)[:max_caracteres_por_trecho]
                
                trechos.append({
                    'cabecalho': pag['cabecalho'],
                    'texto': texto_final,
                    'score': score
                })
    
    # Ordena por relevância e limita (mais trechos para respostas completas)
    trechos.sort(key=lambda x: x['score'], reverse=True)
    return trechos[:25]  # Aumentado de 15 para 25

# ============================================================================
# 📏 CONTROLE DE TOKENS - LIMITE MAIOR
# ============================================================================
def contar_tokens_estimado(texto):
    """Estimativa: 1 token ≈ 4 caracteres em português"""
    return len(texto) // 4
    
def limitar_contexto(contexto, max_tokens=100000): # ← AUMENTE DE 4500 PARA 100.000
    """Limite ampliado radicalmente para aproveitar a janela do Gemini 1.5"""
    tokens_atuais = contar_tokens_estimado(contexto)
    
    if tokens_atuais <= max_tokens:
        return contexto, tokens_atuais
    # ... resto da função igual ...
    
    linhas = contexto.split('\n')
    contexto_reduzido = []
    tokens_usados = 0
    
    for linha in linhas:
        tokens_linha = contar_tokens_estimado(linha)
        if tokens_usados + tokens_linha <= max_tokens:
            contexto_reduzido.append(linha)
            tokens_usados += tokens_linha
        else:
            break
    
    return '\n'.join(contexto_reduzido), tokens_usados

# ============================================================================
# 🎯 DETECTOR DE TIPO DE PERGUNTA
# ============================================================================
def detectar_tipo_pergunta(pergunta):
    """Detecta o tipo de pergunta para ajustar o prompt"""
    p = pergunta.lower()
    
    if any(word in p for word in ['compare', 'diferença', 'diferenças', 'entre', 'vs', 'versus']):
        return "comparacao"
    elif any(word in p for word in ['liste', 'listar', 'quais', 'cite', 'mencione']):
        return "lista"
    elif any(word in p for word in ['resumo', 'explique', 'o que', 'como funciona', 'defina']):
        return "explicacao"
    elif any(word in p for word in ['impacto', 'consequência', 'efeito', 'resultado', 'análise']):
        return "analise"
    elif any(word in p for word in ['legislação', 'lei', 'norma', 'regulamento', 'marco legal']):
        return "legislacao"
    else:
        return "padrao"

# ============================================================================
# 🎯 PROMPTS OTIMIZADOS - FOCO EM QUALIDADE + PRECISÃO
# ============================================================================
def criar_prompt_final(pergunta, contexto, tipo_pergunta="padrao"):
    """
    Prompts balanceados: precisão anti-alucinação + respostas completas
    """
    
    prompts = {
        "padrao": f"""
### PAPEL
Você é um assistente técnico especializado em Plano de Espaço Marinho (PEM) do Brasil.
Sua função é fornecer respostas COMPLETAS e BEM FUNDAMENTADAS baseadas nos documentos.

### CONTEXTO DOCUMENTAL
{contexto}

### DIRETRIZES DE RESPOSTA
1. **Completeza**: Desenvolva a resposta de forma abrangente, explorando todos os aspectos relevantes encontrados nos documentos
2. **Precisão**: Use APENAS informações presentes no contexto acima
3. **Citações**: Formato obrigatório → `(Região | Caderno | Pág. X)` após cada afirmação importante
4. **Estrutura**: 
   - Comece com uma visão geral (2-3 frases)
   - Desenvolva com tópicos detalhados
   - Use bullet points para organizar informações
5. **Transparência**: Se alguma informação não estiver nos documentos, declare claramente
6. **Extensão**: Resposta completa (400-700 palavras)

### PERGUNTA
{pergunta}

### RESPOSTA
""",

        "comparacao": f"""
### PAPEL
Analista técnico comparativo de Plano de Espaço Marinho (PEM).

### CONTEXTO DOCUMENTAL
{contexto}

### TAREFA
Compare de forma DETALHADA as abordagens regionais encontradas nos documentos.

### ESTRUTURA DA RESPOSTA
1. **Visão Geral**: Síntese das principais similaridades e diferenças
2. **Tabela Comparativa**: Use tabela Markdown com aspectos relevantes
3. **Análise por Tópico**: Desenvolva cada aspecto com citações
4. **Conclusão**: Destaque implicações das diferenças encontradas

### REGRAS
✓ Cite: `(Região | Caderno | Pág. X)` para cada afirmação
✓ Se não houver dados para uma região, informe explicitamente
✓ Não especule sobre diferenças não documentadas
✓ Resposta completa (500-800 palavras)

### PERGUNTA
{pergunta}

### RESPOSTA
""",

        "lista": f"""
### PAPEL
Assistente técnico de PEM especializado em catalogação de informações.

### CONTEXTO DOCUMENTAL
{contexto}

### TAREFA
Liste de forma COMPLETA todos os itens relevantes encontrados nos documentos.

### ESTRUTURA
- Cada item deve ter descrição detalhada (2-3 frases)
- Inclua citação para cada item: `(Região | Caderno | Pág. X)`
- Agrupe itens por categoria quando aplicável
- Informe o total de itens encontrados

### REGRAS
✓ Não omita informações relevantes encontradas
✓ Se encontrar poucos itens, informe que a documentação é limitada
✓ Não adicione informações externas

### PERGUNTA
{pergunta}

### RESPOSTA
""",

        "explicacao": f"""
### PAPEL
Especialista em explicação técnica didática de PEM.

### CONTEXTO DOCUMENTAL
{contexto}

### TAREFA
Explique o conceito de forma COMPLETA e ACESSÍVEL.

### ESTRUTURA
1. **Definição**: Conceito principal (2-3 frases)
2. **Contexto**: Como se aplica ao PEM
3. **Detalhamento**: Aspectos importantes com exemplos dos documentos
4. **Implicações**: Relevância prática

### REGRAS
✓ Use linguagem técnica mas acessível
✓ Cite fontes para cada afirmação
✓ Se o conceito não estiver completo nos documentos, avise
✓ Resposta completa (400-600 palavras)

### PERGUNTA
{pergunta}

### RESPOSTA
""",

        "analise": f"""
### PAPEL
Analista de impactos e consequências do Plano de Espaço Marinho.

### CONTEXTO DOCUMENTAL
{contexto}

### TAREFA
Analise de forma ABRANGENTE os impactos/consequências mencionados.

### ESTRUTURA
1. **Resumo Executivo**: Principais impactos identificados
2. **Por Categoria**:
   - 🌿 Ambiental
   - 👥 Social
   - 💰 Econômico
   - ⚖️ Institucional
3. **Inter-relações**: Como os impactos se conectam
4. **Lacunas**: O que não está documentado

### REGRAS
✓ Cite fontes para cada afirmação
✓ Distinga impactos diretos e indiretos quando possível
✓ Não extrapole além do documentado
✓ Resposta completa (500-800 palavras)

### PERGUNTA
{pergunta}

### RESPOSTA
""",

        "legislacao": f"""
### PAPEL
Especialista em marco legal do Plano de Espaço Marinho.

### CONTEXTO DOCUMENTAL
{contexto}

### TAREFA
Explique as questões legislativas de forma DETALHADA.

### ESTRUTURA
1. **Marco Legal Principal**: Leis e normas citadas
2. **Competências**: Quem regula o quê
3. **Processos**: Fluxos de licenciamento, fiscalização, etc.
4. **Desafios**: Lacunas ou conflitos mencionados
5. **Por Região**: Diferenças entre Sul e Nordeste quando aplicável

### REGRAS
✓ Cite leis/normas específicas quando mencionadas
✓ Inclua citação de página para cada informação
✓ Se houver lacunas na documentação, informe
✓ Resposta completa (500-800 palavras)

### PERGUNTA
{pergunta}

### RESPOSTA
"""
    }
    
    return prompts.get(tipo_pergunta, prompts["padrao"])

# ============================================================================
# 📚 BARRA LATERAL
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0; background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 100%); 
                border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(12, 74, 110, 0.3);">
        <div style="font-size: 4em; margin-bottom: 5px;">📚</div>
        <h3 style="color: white; margin: 10px 0; font-weight: 700;">Biblioteca PEM</h3>
        <p style="color: rgba(255,255,255,0.85); font-size: 0.85em; margin: 0;">Cadernos Setoriais Oficiais</p>
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
    if "stats_tokens" not in st.session_state:
        st.session_state.stats_tokens = {"total": 0, "ultima_resposta": 0}
    
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
            turismo, pesca, legislação e demais temas dos cadernos PEM.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    chat_box = st.container()
    
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
                with st.spinner("🔍 Buscando e analisando documentos..."):
                    # 1. Busca páginas relevantes (limite aumentado)
                    paginas_filtradas = buscar_paginas_relevantes(
                        pergunta, 
                        st.session_state.todas_as_paginas_lidas, 
                        limite_paginas=10
                    )
                    
                    # 2. Extrai trechos com contexto preservado
                    trechos = extrair_trechos_relevantes(paginas_filtradas, pergunta)
                    
                    # 3. Monta contexto
                    contexto_enxuto = ""
                    for trecho in trechos:
                        contexto_enxuto += f"\n[{trecho['cabecalho']}]\n{trecho['texto']}\n"
                    
                    # 4. Limita tokens (limite aumentado para qualidade)
                    contexto_otimizado, tokens_contexto = limitar_contexto(contexto_enxuto, max_tokens=4500)
                    
                    # 5. Detecta tipo de pergunta
                    tipo_pergunta = detectar_tipo_pergunta(pergunta)
                    
                    # 6. Cria prompt otimizado para qualidade
                    prompt_final = criar_prompt_final(pergunta, contexto_otimizado, tipo_pergunta)
                    
                    # 7. Mostra fontes com indicador de qualidade
                    with st.expander(f"📚 {len(trechos)} trechos consultados ({tokens_contexto} tokens)", expanded=False):
                        for t in trechos:
                            st.markdown(f"**{t['cabecalho']}** | Relevância: {'🟢' if t['score'] >= 3 else '🟡' if t['score'] >= 2 else '🔵'} ({t['score']})")
                        st.success(f"✅ Contexto otimizado: ~{int((1 - tokens_contexto/10000) * 100)} de economia vs. documento completo")
                
                # BLOCO TRY/EXCEPT CORRIGIDO (Alinhado com o 'with st.spinner')
                try:
                    # stream=True faz a resposta aparecer palavra por palavra
                    res_stream = model.generate_content(prompt_final, stream=True)
                    
                    # Gerador seguro para ignorar partes vazias da resposta da API
                    def stream_generator():
                        for chunk in res_stream:
                            if chunk.text:
                                yield chunk.text
                                
                    # Mostra a resposta sendo digitada ao vivo no Streamlit
                    resposta_completa = st.write_stream(stream_generator())
                    
                    # Salva a resposta completa no histórico para o chat não sumir
                    st.session_state.mensagens.append({"role": "assistant", "content": resposta_completa})
                
                except Exception as e:
                    st.error(f"⚠️ Erro durante a geração: {e}")

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
        
        if st.button("🚀 Executar Comparação", type="primary", use_container_width=True):
            with st.spinner("📊 Analisando diretrizes em ambos os cadernos..."):
                paginas_comp = buscar_paginas_relevantes(
                    "diretrizes conflitos zoneamento conservação impacto", 
                    st.session_state.todas_as_paginas_lidas, 
                    limite_paginas=15
                )
                
                trechos_comp = extrair_trechos_relevantes(paginas_comp, "diretrizes zoneamento conservação impacto")
                
                contexto_comp = ""
                for t in trechos_comp:
                    contexto_comp += f"\n[{t['cabecalho']}]\n{t['texto']}\n"
                
                contexto_comp, tokens_comp = limitar_contexto(contexto_comp, max_tokens=5500)
                
                prompt_comp = f"""
### PAPEL
Analista técnico sênior de Plano de Espaço Marinho (PEM).

### CONTEXTO
{contexto_comp}

### TAREFA
Compare de forma DETALHADA e TÉCNICA as abordagens das regiões Sul e Nordeste.

### ESTRUTURA OBRIGATÓRIA
1. **Resumo Executivo** (3-4 frases)
2. **Tabela Comparativa** com aspectos principais
3. **Análise por Dimensão**:
   - Zoneamento e Uso
   - Licenciamento
   - Fiscalização
   - Conflitos
   - Conservação
4. **Similaridades Estratégicas**
5. **Diferenças Relevantes**
6. **Recomendações** (se aplicável)

### REGRAS
✓ Cite: `(Região | Caderno | Pág. X)` para cada afirmação
✓ Use tabelas Markdown para comparações
✓ Se não houver dados para uma região, informe explicitamente
✓ Resposta completa e fundamentada (700-1000 palavras)

### RESPOSTA
"""
                
                try:
                    res_comp = model.generate_content(prompt_comp)
                    st.markdown(res_comp.text)
                    
                    with st.expander(f"📚 {len(trechos_comp)} fontes da comparação"):
                        for t in trechos_comp:
                            st.markdown(f"- {t['cabecalho']} (score: {t['score']})")
                except Exception as e:
                    st.error("⚠️ Erro na comparação.")

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
