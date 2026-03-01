import streamlit as st
import requests
import urllib3
import pandas as pd

# Configurações iniciais da página
st.set_page_config(page_title="Resultados Loterias Caixa", page_icon="💰")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Função para buscar dados da API
def obter_ultimo_resultado(modalidade):
    url = f"https://servicebus2.caixa.gov.br/portalloterias/api/{modalidade}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return None

# Interface do Streamlit
st.title("🎰 Últimos Resultados - Loterias Caixa")
st.markdown("Consulte os resultados oficiais do último concurso de forma simplificada.")

# Sidebar para seleção
loterias_disponiveis = [
    "megasena", "lotofacil", "quina", "lotomania", 
    "timemania", "duplasena", "maismilionaria", "diadesorte"
]

selecao = st.sidebar.multiselect(
    "Escolha as Loterias:", 
    options=loterias_disponiveis, 
    default=["megasena", "lotofacil", "quina"]
)

if st.button("🔄 Atualizar Resultados"):
    st.rerun()

# Exibição dos dados
if selecao:
    for loteria in selecao:
        with st.spinner(f"Buscando {loteria}..."):
            dados = obter_ultimo_resultado(loteria)
            
            if dados:
                with st.expander(f"📊 {loteria.upper()} - Concurso {dados.get('numero')}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Data do Sorteio", dados.get('dataApuracao'))
                        st.write("**Dezenas Sorteadas:**")
                        # Formata as dezenas em pequenas "bolas" ou badges
                        dezenas = dados.get('listaDezenas', [])
                        st.subheader("  ".join([f"[{d}]" for d in dezenas]))
                    
                    with col2:
                        proximo_premio = dados.get('valorEstimadoProximoConcurso', 0)
                        st.metric("Próximo Prêmio Estimado", f"R$ {proximo_premio:,.2f}")
                        st.info(f"Acumulou: {'Sim' if dados.get('acumulado') else 'Não'}")
            else:
                st.error(f"Não foi possível carregar os dados da {loteria}.")
else:
    st.info("Selecione ao menos uma loteria na barra lateral para começar.")

st.divider()
st.caption("Dados obtidos diretamente da API pública da Caixa Econômica Federal.")
