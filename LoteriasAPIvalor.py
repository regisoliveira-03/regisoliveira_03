import streamlit as st
import requests

# Configuração visual do Painel
st.set_page_config(page_title="Loterias API GitHub", page_icon="💰", layout="wide")

def consultar_api_comunitaria(modalidade):
    url = f"https://loteriascaixa-api.herokuapp.com/api/{modalidade}/latest"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        try:
            url_reserva = f"https://loterica.com.br/api/v1/{modalidade}/ultimo"
            return requests.get(url_reserva, timeout=10).json()
        except:
            return None

def formatar_moeda(valor):
    """Auxiliar para formatar números em R$"""
    try:
        if isinstance(valor, (int, float)):
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return str(valor)
    except:
        return "Consulte o site"

# --- Interface do Usuário ---
st.title("💰 Painel de Resultados - Loterias")
st.markdown("Resultados em tempo real com estimativa de prêmio.")

loterias_map = {
    "Mega-Sena": "megasena",
    "Lotofácil": "lotofacil",
    "Quina": "quina",
    "Lotomania": "lotomania",
    "Timemania": "timemania",
    "Dupla Sena": "duplasena",
    "Dia de Sorte": "diadesorte"
}

if st.button("🔄 Sincronizar Todos os Resultados Agora"):
    st.divider()
    cols = st.columns(2)
    
    for i, (nome, slug) in enumerate(loterias_map.items()):
        with cols[i % 2]:
            with st.spinner(f"Sincronizando {nome}..."):
                dados = consultar_api_comunitaria(slug)
                
                if dados:
                    with st.container(border=True):
                        st.subheader(nome)
                        st.caption(f"Concurso {dados.get('concurso')} | Data: {dados.get('data')}")
                        
                        # Renderização das Dezenas
                        dezenas = dados.get('dezenas', dados.get('resultado', []))
                        
                        bolas_html = "".join([
                            f'<span style="background-color: #209869; color: white; padding: 5px 12px; '
                            f'border-radius: 50%; margin: 3px; display: inline-block; font-weight: bold; '
                            f'font-family: sans-serif;">{d}</span>' for d in dezenas
                        ])
                        st.markdown(bolas_html, unsafe_allow_html=True)
                        
                        # --- Lógica do Valor do Prêmio ---
                        # Tenta buscar o valor estimado para o próximo concurso
                        valor_bruto = dados.get('valorEstimadoProximoConcurso') or \
                                      dados.get('valor_estimado_proximo_concurso') or \
                                      dados.get('proximo_estimado')
                        
                        # Se não achar o próximo, tenta ver se está acumulado
                        if not valor_bruto:
                             valor_bruto = dados.get('valorAcumuladoProximoConcurso', 0)

                        valor_formatado = formatar_moeda(valor_bruto)
                        
                        st.write("")
                        st.metric(label="Estimativa Próximo Prêmio", value=valor_formatado)
                else:
                    st.error(f"Não foi possível sincronizar a {nome}.")
else:
    st.info("Clique no botão acima para carregar os resultados.")
