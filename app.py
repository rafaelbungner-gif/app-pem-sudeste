import streamlit as st
import google.generativeai as genai

# 1. Configuração da página (DEVE SER A PRIMEIRA LINHA)
st.set_page_config(page_title="Assistente PEM Sudeste", page_icon="🌊", layout="wide")

# 2. O Novo Design Moderno (CSS Customizado)
st.markdown("""
<style>
    /* Fundo geral da aplicação bem limpo */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Criação de um Banner/Cabeçalho moderno em CSS (sem imagens gigantes) */
    .cabecalho-moderno {
        background: linear-gradient(135deg, #1E3A8A 0%, #0284C7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .cabecalho-moderno h1 {
        color: white !important;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        padding-bottom: 0.5rem;
    }
    .cabecalho-moderno p {
        margin: 0;
        font-size: 1.1rem;
        color: #E0F2FE;
    }
    
    /* Estilizando os Títulos das Abas */
    h2, h3 {
        color: #0F172A !important;
    }
</style>

<div class="cabecalho-moderno">
    <h1>🌊 Assistente IA - PEM Sudeste</h1>
    <p>Portal de Apoio Técnico ao Caderno de Conservação</p>
</div>
""", unsafe_allow_html=True)

# 3. Conectando a Chave Secreta do Streamlit
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("⚠️ Chave de API não encontrada nos Secrets do Streamlit.")

# 4. Criando a Personalidade: O Acadêmico Rigoroso
instrucao_sistema = """Você é um Acadêmico Rigoroso e Consultor Técnico-Jurídico especialista em Planejamento Espacial Marinho (PEM).
Seu objetivo é auxiliar na construção do Caderno de Conservação da Região Sudeste do Brasil, usando como base de referência as diretrizes, leis e dados dos cadernos das regiões Sul e Nordeste.
Regras de conduta:
1. Use vocabulário formal, técnico e científico.
2. Seja preciso e rigoroso. Baseie-se em fatos sobre zoneamento, biologia marinha e economia azul.
3. Se referencie a leis ambientais, resoluções (ex: CONAMA) e marcos regulatórios brasileiros sempre que possível.
4. Estruture suas respostas com clareza (tópicos, prós e contras técnicos).
5. Se não tiver certeza absoluta de um dado geográfico, não invente: diga que 'é necessária a consulta ao anexo técnico original'."""

# Inicializando o modelo
modelo = genai.GenerativeModel(model_name="gemini-1.5-pro", system_instruction=instrucao_sistema)

# 5. Memória do Chat
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# 6. Criando as duas abas
aba1, aba2 = st.tabs(["🔮 Consulta Técnica (Chat)", "⚖️ Comparador de Zoneamento"])

# --- ABA 1: O ORÁCULO ---
with aba1:
    st.info("💡 **Dica Técnica:** Faça perguntas diretas sobre regulações de portos, áreas de proteção ou regras de pesca.")
    
    for msg in st.session_state.mensagens:
        st.chat_message(msg["role"]).write(msg["content"])
    
    pergunta = st.chat_input("Ex: Quais as diretrizes jurídicas para mitigar impactos de dutos de óleo e gás?")
    
    if pergunta:
        st.chat_message("user").write(pergunta)
        st.session_state.mensagens.append({"role": "user", "content": pergunta})
        
        with st.spinner("Analisando bases técnicas, jurídicas e dados oceanográficos..."):
            resposta = modelo.generate_content(pergunta)
            st.chat_message("assistant").write(resposta.text)
            st.session_state.mensagens.append({"role": "assistant", "content": resposta.text})

# --- ABA 2: O COMPARADOR ---
with aba2:
    st.write("Selecione os eixos temáticos para gerar um relatório analítico cruzando as abordagens do Sul e do Nordeste.")
    
    col1, col2 = st.columns(2)
    with col1:
        tema_sul = st.selectbox("Foco na Região Sul:", ["Atividade Portuária e Cabotagem", "Pesca Industrial e Artesanal", "Turismo Costeiro", "Unidades de Conservação"])
    with col2:
        tema_nordeste = st.selectbox("Foco na Região Nordeste:", ["Atividade Portuária e Cabotagem", "Pesca Industrial e Artesanal", "Turismo Costeiro", "Unidades de Conservação"])
        
    if st.button("Gerar Relatório Analítico"):
        with st.spinner("Compilando dados técnicos comparativos..."):
            comando_comparacao = f"Faça uma análise acadêmica comparando como o PEM lidou com '{tema_sul}' na Região Sul versus '{tema_nordeste}' na Região Nordeste. Extraia lições que podem ser aplicadas no Sudeste."
            resposta_comparador = modelo.generate_content(comando_comparacao)
            st.success("✅ Relatório analítico estruturado com sucesso!")
            st.markdown(resposta_comparador.text)
