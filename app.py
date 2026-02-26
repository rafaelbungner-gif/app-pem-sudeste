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
st.set_page_config(page_title="Assistente PEM", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

# ============================================================================
# 💅 ESTILOS CSS
# ============================================================================
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #F0F9FF 0%, #E0F2FE 100%); }
    .main-header {
        background-image: linear-gradient(135deg, rgba(12, 74, 110, 0.85) 0%, rgba(3, 105, 161, 0.80) 50%, rgba(14, 165, 233, 0.85) 100%), url('https://images.unsplash.com/photo-1590523741831-ab7f85327541?w=1600&h=600&fit=crop&q=80');
        background-size: cover; background-position: center; padding: 55px 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 30px; box-shadow: 0 15px 50px rgba(14, 165, 233, 0.35);
    }
    .main-header h1 { font-size: 3.5em; font-weight: 800; margin: 0; text-shadow: 3px 3px 8px rgba(0,0,0,0.5); }
    .status-badge { display: inline-flex; gap: 6px; padding: 7px 18px; border-radius: 25px; font-size: 0.85em; font-weight: 600; margin: 6px; background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.25); }
    .sidebar-section { background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 100%); border-radius: 15px; padding: 20px; margin: 12px 0; border: 1px solid rgba(255,255,255,0.15); }
    .sidebar-section h4 { color: white; margin-bottom: 12px; font-size: 1em; }
    .loaded-notebooks { background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%); border-radius: 12px; padding: 18px; margin: 15px 0; border: 1px solid #86EFAC; }
    .loaded-notebook-item { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid #BBF7D0; font-size: 0.9em; }
    .notebook-region { font-weight: 700; padding: 3px 10px; border-radius: 8px; font-size: 0.75em; text-transform: uppercase; }
    .region-sul { background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; }
    .region-ne { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: white; }
    .metric-card { background: linear-gradient(135deg, #0C4A6E 0%, #0369A1 100%); border-radius: 15px; padding: 22px; text-align: center; color: white; margin: 15px 0; }
    .metric-value { font-size: 2.8em; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

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
# 🔧 CONFIGURAÇÃO DA IA (GEMINI 1.5 PRO - ALTA CAPACIDADE)
# ============================================================================
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    instrucao_sistema = """Você é um analista técnico de alto rigor metodológico especializado no Plano de Espaço Marinho (PEM) do Brasil. 
    Regra de Ouro: Baseie sua resposta ESTRITAMENTE nos trechos fornecidos. Não invente ou presuma informações.
    Se a resposta não estiver nos trechos, declare claramente: 'Não encontrei essa informação nos cadernos selecionados'.
    Citação Obrigatória: Ao final de cada afirmação técnica, cite (Região | Caderno | Página X)."""

    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro',
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
# 📄 LEITURA DE PDF E BUSCA
# ============================================================================
def ler_e_fatiar_pdf(file_id, nome_doc, regiao):
    paginas_fatiadas = []
    try:
        url = f'https://drive.google.com/uc?id={file_id}'
        response = requests.get(url)
        f = io.BytesIO(response.content)
        reader = PdfReader(f)
        for i, page in enumerate(reader.pages):
            texto = page.extract_text()
            if texto:
                paginas_fatiadas.append({
                    "cabecalho": f"[CADERNO: {regiao} - {nome_doc} | PÁGINA: {i+1}]",
                    "texto": texto.lower(),
                    "texto_original": texto
                })
        return paginas_fatiadas
    except Exception as ex:
        st.error(f"Erro ao ler PDF: {ex}")
        return []

def buscar_paginas_relevantes(pergunta, todas_as_paginas, limite_paginas=30):
    palavras_pergunta = re.findall(r'\w+', pergunta.lower())
    palavras_ignoradas = {'o', 'a', 'os', 'as', 'de', 'do', 'da', 'em', 'no', 'na', 'para', 'com', 'que'}
    palavras_chave = [p for p in palavras_pergunta if p not in palavras_ignoradas and len(p) > 2]
    
    if not palavras_chave:
        return []

    resultados = []
    for pag in todas_as_paginas:
        pontuacao = sum(1 for palavra in palavras_chave if palavra in pag["texto"])
        if pontuacao > 0:
            resultados.append((pontuacao, pag))
            
    resultados.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in resultados[:limite_paginas]]

# ============================================================================
# 📚 BARRA LATERAL
# ============================================================================
with st.sidebar:
    st.markdown("<h3 style='color: white; text-align: center;'>📚 Biblioteca PEM</h3>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'><h4>📍 Região Sul</h4>", unsafe_allow_html=True)
    escolha_sul = st.selectbox("", list(CADERNOS_SUL.keys()), key="sul_select", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'><h4>📍 Região Nordeste</h4>", unsafe_allow_html=True)
    escolha_ne = st.selectbox("", list(CADERNOS_NE.keys()), key="ne_select", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    if "cadernos_ativos" not in st.session_state: st.session_state.cadernos_ativos = []
    if "todas_as_paginas_lidas" not in st.session_state: st.session_state.todas_as_paginas_lidas = []
    if "mensagens" not in st.session_state: st.session_state.mensagens = []

    if st.session_state.cadernos_ativos:
        st.markdown("<div class='loaded-notebooks'><h4>✅ Cadernos Carregados</h4>", unsafe_allow_html=True)
        for regiao, nome, _ in st.session_state.cadernos_ativos:
            st.markdown(f"**{regiao}**: {nome}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.todas_as_paginas_lidas)}</div>Páginas Indexadas</div>", unsafe_allow_html=True)

# Atualizar documentos na sessão
cadernos_selecionados_agora = []
if escolha_sul and escolha_sul != "Nenhum": cadernos_selecionados_agora.append(("SUL", escolha_sul, CADERNOS_SUL[escolha_sul]))
if escolha_ne and escolha_ne != "Nenhum": cadernos_selecionados_agora.append(("NE", escolha_ne, CADERNOS_NE[escolha_ne]))

if cadernos_selecionados_agora != st.session_state.cadernos_ativos:
    st.session_state.todas_as_paginas_lidas = []
    st.session_state.cadernos_ativos = cadernos_selecionados_agora.copy()
    if cadernos_selecionados_agora:
        with st.sidebar.status("📖 Lendo PDFs oficiais...", expanded=True):
            for regiao, nome, file_id in cadernos_selecionados_agora:
                paginas = ler_e_fatiar_pdf(file_id, nome, regiao)
                st.session_state.todas_as_paginas_lidas.extend(paginas)
        st.rerun()

# ============================================================================
# 📑 ABAS PRINCIPAIS
# ============================================================================
aba1, aba2 = st.tabs(["🔮 Oráculo (Chat)", "⚖️ Comparador Regional"])

# ABA 1: CHAT COM STREAMING
with aba1:
    for m in st.session_state.mensagens:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    pergunta = st.chat_input("Pergunte sobre os cadernos selecionados...")
    if pergunta:
        if not st.session_state.cadernos_ativos:
            st.error("⚠️ Selecione um caderno na barra lateral primeiro!")
        else:
            st.session_state.mensagens.append({"role": "user", "content": pergunta})
            with st.chat_message("user"): st.markdown(pergunta)
            
            with st.chat_message("assistant"):
                with st.spinner("Analisando documentos..."):
                    paginas_relevantes = buscar_paginas_relevantes(pergunta, st.session_state.todas_as_paginas_lidas, limite_paginas=30)
                    
                    contexto_estruturado = ""
                    for p in paginas_relevantes:
                        contexto_estruturado += f"\n{p['cabecalho']}\n{p['texto_original']}\n"

                if not paginas_relevantes:
                    st.warning("Não encontrei referências exatas nos documentos carregados.")
                else:
                    with st.expander(f"📚 {len(paginas_relevantes)} páginas serviram de contexto"):
                        for p in paginas_relevantes: st.caption(p['cabecalho'])

                    prompt_final = f"Baseado APENAS no contexto abaixo, responda à pergunta:\n\nCONTEXTO:\n{contexto_estruturado[:95000]}\n\nPERGUNTA: {pergunta}"
                    
                    try:
                        # Geração com Streaming (texto aparece aos poucos)
                        response_stream = model.generate_content(prompt_final, stream=True)
                        
                        def stream_generator():
                            for chunk in response_stream:
                                if chunk.text: yield chunk.text
                                
                        texto_completo = st.write_stream(stream_generator())
                        st.session_state.mensagens.append({"role": "assistant", "content": texto_completo})
                    except Exception as e:
                        st.error(f"⚠️ Erro ao gerar resposta: {e}")

# ABA 2: COMPARAÇÃO
with aba2:
    if len(st.session_state.cadernos_ativos) < 2:
        st.info("💡 Selecione um caderno do Sul e um do Nordeste para habilitar a comparação.")
    else:
        if st.button("🚀 Gerar Comparação Estratégica", use_container_width=True):
            with st.spinner("Lendo e comparando diretrizes de ambas as regiões..."):
                paginas_comp = buscar_paginas_relevantes("diretrizes desafios zoneamento", st.session_state.todas_as_paginas_lidas, limite_paginas=40)
                
                contexto_comp = ""
                for p in paginas_comp: contexto_comp += f"\n{p['cabecalho']}\n{p['texto_original']}\n"
                
                prompt_comp = f"""Analise técnica e comparativamente as regiões Sul e Nordeste baseado APENAS nestes textos:
                {contexto_comp[:95000]}
                Crie uma tabela Markdown com as principais diferenças e cite as páginas e cadernos de origem."""
                
                try:
                    res_comp = model.generate_content(prompt_comp)
                    st.markdown(res_comp.text)
                except Exception as e:
                    st.error("Erro na comparação.")
