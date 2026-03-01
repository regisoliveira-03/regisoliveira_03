import streamlit as st
import requests
import urllib3
import pandas as pd

# 1. Configurações de Segurança e Interface
st.set_page_config(page_title="Loterias Caixa - Resultados", page_icon="💰", layout="wide")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. Função Robusta para buscar os dados
def obter_resultado_caixa(modalidade):
    # Usar Session ajuda a manter cookies que o servidor da Caixa pode exigir
    session = requests.Session()
    
    url = f"https://servicebus2.caixa.gov.br/portalloterias/api/{modalidade}"
    
    # Headers completos para simular um navegador Chrome real
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Host": "servicebus2.caixa.gov.br",
        "Origin": "https://loterias.caixa.gov.br",
        "Referer": "https://loterias.caixa.gov.br/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        # Timeout maior (20s) pois o servidor da Caixa costuma ser lento
        response = session.get(url, headers=headers, verify=False, timeout=20)
        
        if response.status_code == 200:
            return response.json()
        else:
            return f"Erro {response.status_code}: Servidor recusou a conexão."
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# 3. Interface Streamlit
st.title("🎰 Resultados Oficiais Loterias Caixa")
st.markdown("Consulta em tempo real dos últimos sorteios via API oficial.")

# Sidebar - Configurações
st.sidebar.header("Configurações")
loterias_lista = [
    "megasena", "lotofacil", "quina", "lotomania", 
    "timemania", "duplasena", "maismilionaria", "diadesorte"
]

selecionadas = st.sidebar.multiselect(
    "Selecione as modalidades:",
    options=loterias_lista,
    default=["megasena", "lotofacil"]
)

if st.sidebar.button("🔄 Atualizar Dados"):
    st.rerun()

# 4. Exibição dos Resultados
if selecionadas:
    for loteria in selecionadas:
        with st.spinner(f"Consultando {loteria.upper()}..."):
            dados = obter_resultado_caixa(loteria)

            if isinstance(dados, dict):
                # Layout de colunas para cada card
                with st.container():
                    st.markdown(f"### {loteria.upper()}")
                    c1, c2, c3 = st.columns([1, 2, 1])
