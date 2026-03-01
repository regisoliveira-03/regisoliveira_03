import streamlit as st
import requests

# Configuração visual do Painel
st.set_page_config(page_title="Loterias API GitHub", page_icon="💰", layout="wide")

def consultar_api_comunitaria(modalidade):
    """
    Consome a API de resultados hospedada em serviços comunitários.
    Esta abordagem é mais leve e evita bloqueios de firewall.
    """
    # Endpoint de uma das APIs mais utilizadas no ecossistema GitHub
    url = f"https://loteriascaixa-api.herokuapp.com/api/{modalidade}/latest"
    
    try:
        # Timeout curto para não travar a interface se a API demorar
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        # Fallback para outro endpoint caso o primeiro falhe
        try:
            url_reserva = f"https://loterica.com.br/api/v1/{modalidade}/ultimo"
            return requests.get(url_reserva, timeout=10).json()
        except:
            return None

# --- Interface do Usuário ---
st.title("💰 Painel de Resultados - API Comunitária")
st.markdown("Resultados obtidos via integração com projetos open-source do GitHub.")

# Mapeamento para garantir que o slug da URL esteja correto
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
    
    # Criamos colunas para mostrar os resultados lado a lado
    cols = st.columns(2)
    
    for i, (nome, slug) in enumerate(loterias_map.items()):
        with cols[i % 2]:
            with st.spinner(f"Sincronizando {nome}..."):
                dados = consultar_api_comunitaria(slug)
                
                if dados:
                    with st.container(border=True):
                        st.subheader(nome)
                        # A API costuma retornar os campos 'concurso' e 'data'
                        st.caption(f"Concurso {dados.get('concurso')} | Data: {dados.get('data')}")
                        
                        # Renderização das Dezenas
                        dezenas = dados.get('dezenas', [])
                        if not dezenas: # Algumas APIs usam o nome 'resultado'
                             dezenas = dados.get('resultado', [])
                        
                        bolas_html = "".join([
                            f'<span style="background-color: #209869; color: white; padding: 5px 12px; '
                            f'border-radius: 50%; margin: 3px; display: inline-block; font-weight: bold; '
                            f'font-family: sans-serif;">{d}</span>' for d in dezenas
                        ])
                        st.markdown(bolas_html, unsafe_allow_html=True)
                        
                        # Valor do prêmio
                        valor = dados.get('valor_estimado_proximo_concurso', 'Consulte o site')
                        st.write("")
                        st.metric("Estimativa Próximo Prêmio", f"R$ {valor}")
                else:
                    st.error(f"Não foi possível sincronizar a {nome} no momento.")
else:
    st.info("Clique no botão acima para carregar os resultados via API.")

st.divider()
st.caption("Nota: Este app depende de APIs mantidas por terceiros no GitHub. A precisão dos dados é de responsabilidade dos provedores.")
