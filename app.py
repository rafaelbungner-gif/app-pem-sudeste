import streamlit as st
import google.generativeai as genai

# Configuração visual da página
st.set_page_config(page_title="Assistente PEM Sudeste", page_icon="🌊", layout="wide")

st.title("🌊 Assistente IA - PEM Sudeste")
st.markdown("Portal de apoio à construção do Caderno de Conservação. Baseado nos dados das regiões Sul e Nordeste.")

# Criando as duas abas que escolhemos!
aba1, aba2 = st.tabs(["🔮 Oráculo do PEM (Chat)", "⚖️ Comparador Regional"])

# --- ABA 1: O ORÁCULO ---
with aba1:
    st.header("Pergunte aos Cadernos")
    st.write("Digite sua dúvida e a IA buscará a resposta nos 22 cadernos do Google Drive.")
    
    # Caixa de chat
    pergunta = st.chat_input("Ex: Quais são as diretrizes para a pesca artesanal?")
    if pergunta:
        st.chat_message("user").write(pergunta)
        st.chat_message("assistant").write("⚙️ Conectando ao Google Drive e analisando os PDFs... (A resposta da IA aparecerá aqui!)")

# --- ABA 2: O COMPARADOR ---
with aba2:
    st.header("Comparador de Estratégias")
    st.write("Selecione os temas para cruzar os dados das diferentes regiões.")
    
    col1, col2 = st.columns(2)
    with col1:
        tema_sul = st.selectbox("Foco na Região Sul:", ["Portos e Navegação", "Pesca Artesanal", "Turismo Sustentável", "Extração de Petróleo"])
    with col2:
        tema_nordeste = st.selectbox("Foco na Região Nordeste:", ["Portos e Navegação", "Pesca Artesanal", "Turismo Sustentável", "Extração de Petróleo"])
        
    if st.button("Gerar Tabela Comparativa"):
        st.info(f"Cruzando dados de {tema_sul} (Sul) com {tema_nordeste} (Nordeste)...")
