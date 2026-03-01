import streamlit as st
import requests

# Configurações da página
st.set_page_config(page_title="API Loterias GitHub", page_icon="📈")

def consultar_api_github(loteria):
    """
    Utiliza uma API pública mantida pela comunidade no GitHub.
    Fonte base: https://github.com/guto-viana/loterias-api
    """
    # Endpoint da API (esta é uma das mais estáveis)
    url = f"https://loteriacaixa.com.br/api/{loteria}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Erro na API: Status {response.status_code}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- Interface Streamlit ---
st.title("📈 Painel Loterias via API Comunitária")
st.markdown("Este app utiliza dados de APIs mantidas por desenvolvedores no GitHub.")

# Mapeamento de nomes para a API
loterias_api = {
    "Mega-Sena": "megasena",
    "Lotofácil": "lotofacil",
    "Quina": "quina",
    "Lotomania": "lotomania",
    "Timemania": "timemania",
    "Dia de Sorte": "diadesorte"
}

# Layout em colunas
st.subheader("Resultados Atuais")
if st.button("🔄 Sincronizar Tudo Agora"):
    cols = st.columns(2)
    for idx, (nome, slug) in enumerate(loterias_api.items()):
        with cols[idx % 2]:
            with st.spinner(f"Lendo {nome}..."):
                dados = consultar_api_github(slug)
                
                if isinstance(dados, dict):
                    with st.container(border=True):
                        st.markdown(f"### {nome}")
                        st.caption(f"Concurso {dados.get('concurso')} • {dados.get('data')}")
                        
                        # Exibição das dezenas (geralmente vêm como lista ou string separada)
                        dezenas = dados.get('dezenas', [])
                        
                        # Estilização visual
                        bolas = " ".join([f"**[{d}]**" for d in dezenas])
                        st.markdown(bolas)
                        
                        proximo = dados.get('proximo_estimativa', 'Consulte o site')
                        st.metric("Estimativa Próximo Prêmio", f"R$ {proximo}")
                else:
                    st.error(f"{nome}: {dados}")
else:
    st.info("Clique no botão para buscar todos os dados via API externa.")

st.divider()
st.caption("Nota: Os dados são provenientes de repositórios do GitHub. A precisão depende da atualização dos mantenedores dessas APIs.")
