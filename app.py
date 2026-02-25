import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Assistente PEM Sudeste", page_icon="🌊", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    .cabecalho-moderno {
        background: linear-gradient(135deg, #1E3A8A 0%, #0284C7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .cabecalho-moderno h1 { color: white !important; margin: 0; font-size: 2.2rem; }
    .cabecalho-moderno p { margin: 0; font-size: 1.1rem; color: #E0F2FE; }
    h2, h3 { color: #0F172A !important; }
</style>
<div class="cabecalho-moderno">
    <h1>🌊 Assistente IA - PEM Sudeste</h1>
    <p>Portal de Apoio Técnico ao Caderno de Conservação</p>
</div>
""", unsafe_allow_html=True)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("⚠️ Chave de API não encontrada nos Secrets do Streamlit.")

modelo_valido = None
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            modelo_valido = m.name
            break
except Exception as e:
    st.error(f"Erro ao consultar o servidor do Google: {e}")

if modelo_valido:
    modelo = genai.GenerativeModel(model_name=modelo_valido)
else:
    st.error("Nenhum modelo compatível foi encontrado para esta chave de API.")

# Instrução da Personalidade com Rastreabilidade e Aviso Legal
instrucao = """Você é um Acadêmico Rigoroso especialista em Planejamento Espacial Marinho (PEM).
Regras de conduta OBRIGATÓRIAS:
1. Responda de forma técnica, formal e baseada APENAS em fatos documentados.
2. RASTREABILIDADE: Toda vez que você afirmar um dado, regra ou diretriz, você DEVE citar o nome do caderno e o número da página de onde retirou a informação (Exemplo: "Segundo o Caderno da Região Sul, pág. 42...").
3. TRANSPARÊNCIA: Ao final de TODAS as suas respostas, sem exceção, adicione exatamente esta frase em itálico:
'⚠️ *Aviso: Sou um modelo de Inteligência Artificial criado para auxiliar o projeto PEM. Minhas informações servem como guia e devem ser conferidas nos cadernos oficiais.*'
"""

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

aba1, aba2 = st.tabs(["🔮 Consulta Técnica (Chat)", "⚖️ Comparador de Zoneamento"])

with aba1:
    st.info("💡 **Dica Técnica:** Faça perguntas diretas sobre regulações de portos, áreas de proteção ou regras de pesca.")
    
    # A MÁGICA ACONTECE AQUI: Criando uma caixa rolável de 400 pixels de altura
    caixa_chat = st.container(height=400)
    
    with caixa_chat:
        for msg in st.session_state.mensagens:
            st.chat_message(msg["role"]).write(msg["content"])
    
    pergunta = st.chat_input("Ex: Quais as restrições para pesca de arrasto próximo a portos?")
    
    if pergunta:
        with caixa_chat:
            st.chat_message("user").write(pergunta)
        st.session_state.mensagens.append({"role": "user", "content": pergunta})
        
        with caixa_chat:
            with st.spinner("Analisando bases técnicas e jurídicas..."):
                try:
                    resposta = modelo.generate_content(instrucao + "Pergunta: " + pergunta)
                    st.chat_message("assistant").write(resposta.text)
                    st.session_state.mensagens.append({"role": "assistant", "content": resposta.text})
                except Exception as e:
                    st.error(f"Erro ao gerar resposta: {e}")

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        tema_sul = st.selectbox("Foco na Região Sul:", ["Atividade Portuária", "Pesca", "Turismo Costeiro", "Unidades de Conservação"])
    with col2:
        tema_nordeste = st.selectbox("Foco na Região Nordeste:", ["Atividade Portuária", "Pesca", "Turismo Costeiro", "Unidades de Conservação"])
        
    if st.button("Gerar Relatório Analítico"):
        with st.spinner("Compilando dados..."):
            comando = instrucao + f"Faça uma análise acadêmica comparando como o PEM lidou com '{tema_sul}' no Sul versus '{tema_nordeste}' no Nordeste."
            try:
                resposta_comparador = modelo.generate_content(comando)
                st.success(f"✅ Relatório gerado com sucesso! (Modelo utilizado: {modelo_valido})")
                st.markdown(resposta_comparador.text)
            except Exception as e:
                st.error(f"Erro ao gerar relatório: {e}")
