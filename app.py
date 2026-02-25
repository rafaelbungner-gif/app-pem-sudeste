import streamlit as st
import google.generativeai as genai

# 1. Configuração visual da página
st.set_page_config(page_title="Assistente PEM Sudeste", page_icon="🌊", layout="wide")

st.title("🌊 Assistente IA - PEM Sudeste")
st.markdown("Portal de apoio técnico à construção do Caderno de Conservação. Base: Regiões Sul e Nordeste.")

# 2. Conectando a Chave Secreta do Streamlit
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("⚠️ Chave de API não encontrada nos Secrets do Streamlit.")

# 3. Criando a Personalidade: O Acadêmico Rigoroso
instrucao_sistema = """Você é um Acadêmico Rigoroso e Consultor Técnico-Jurídico especialista em Planejamento Espacial Marinho (PEM).
Seu objetivo é auxiliar na construção do Caderno de Conservação da Região Sudeste do Brasil, usando como base de referência as diretrizes, leis e dados dos cadernos das regiões Sul e Nordeste.
Regras de conduta:
1. Use vocabulário formal, técnico e científico.
2. Seja preciso e rigoroso. Baseie-se em fatos sobre zoneamento, biologia marinha e economia azul.
3. Se referencie a leis ambientais, resoluções (ex: CONAMA) e marcos regulatórios brasileiros sempre que possível.
4. Estruture suas respostas com clareza (tópicos, prós e contras técnicos).
5. Se não tiver certeza absoluta de um dado geográfico, não invente: diga que 'é necessária a consulta ao anexo técnico original'."""

# Inicializando o modelo de IA com a personalidade
modelo = genai.GenerativeModel(model_name="gemini-1.5-pro", system_instruction=instrucao_sistema)

# 4. Memória do Chat (Para a IA lembrar do que foi falado)
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# 5. Criando as duas abas
aba1, aba2 = st.tabs(["🔮 Oráculo do PEM (Chat)", "⚖️ Comparador Regional"])

# --- ABA 1: O ORÁCULO ---
with aba1:
    st.header("Consulta Técnica Aprofundada")
    st.write("Digite sua pergunta. O assistente responderá com base no rigor técnico exigido para o PEM.")
    
    # Mostra o histórico na tela
    for msg in st.session_state.mensagens:
        st.chat_message(msg["role"]).write(msg["content"])
    
    # Caixa de digitação
    pergunta = st.chat_input("Ex: Quais as restrições jurídicas para pesca de arrasto próximo a portos?")
    
    if pergunta:
        # Mostra a pergunta do usuário
        st.chat_message("user").write(pergunta)
        st.session_state.mensagens.append({"role": "user", "content": pergunta})
        
        # Pede a resposta para a IA
        with st.spinner("Analisando bases técnicas e jurídicas..."):
            resposta = modelo.generate_content(pergunta)
            st.chat_message("assistant").write(resposta.text)
            st.session_state.mensagens.append({"role": "assistant", "content": resposta.text})

# --- ABA 2: O COMPARADOR ---
with aba2:
    st.header("Análise Comparativa de Zoneamento")
    st.write("Selecione os temas para gerar um relatório técnico comparativo entre as regiões.")
    
    col1, col2 = st.columns(2)
    with col1:
        tema_sul = st.selectbox("Foco na Região Sul:", ["Atividade Portuária", "Pesca Industrial/Artesanal", "Turismo Costeiro", "Conservação de Biodiversidade"])
    with col2:
        tema_nordeste = st.selectbox("Foco na Região Nordeste:", ["Atividade Portuária", "Pesca Industrial/Artesanal", "Turismo Costeiro", "Conservação de Biodiversidade"])
        
    if st.button("Gerar Relatório Comparativo"):
        with st.spinner("Compilando dados técnicos comparativos..."):
            comando_comparacao = f"Faça uma análise acadêmica comparando como o PEM lidou com '{tema_sul}' na Região Sul versus '{tema_nordeste}' na Região Nordeste. Extraia lições que podem ser aplicadas no Sudeste."
            resposta_comparador = modelo.generate_content(comando_comparacao)
            st.success("Relatório gerado com sucesso.")
            st.markdown(resposta_comparador.text)
