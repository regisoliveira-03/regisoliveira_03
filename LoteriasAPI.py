import streamlit as st
import requests

# Configuração da página
st.set_page_config(page_title="Resultados Loterias API", page_icon="💰", layout="wide")

def consultar_loteria_v2(modalidade):
    """
    Consulta uma API alternativa e estável baseada em projetos do GitHub.
    """
    # Usando a API v2 da Loteriascaixa-api (uma das mais estáveis)
    url = f"https://loterica.com.br/api/v1/{modalidade}/ultimo"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# --- Interface Streamlit ---
st.title("💰 Painel de Loterias - API GitHub")
st.markdown("Consulte todos os resultados atuais de uma só vez via API JSON.")

# Lista de loterias suportadas
loterias_slugs = {
    "Mega-Sena": "mega-sena",
    "Lotofácil": "lotofacil",
    "Quina": "quina",
    "Lotomania": "lotomania",
    "Timemania": "timemania",
    "Dupla Sena": "dupla-sena",
    "Dia de Sorte": "dia-de-sorte"
}

if st.button("🔄 Sincronizar Todos os Resultados"):
    # Criamos uma grade de colunas
    cols = st.columns(2)
    
    for i, (nome, slug) in enumerate(loterias_slugs.items()):
        with cols[i % 2]:
            with st.spinner(f"Buscando {nome}..."):
                dados = consultar_loteria_v2(slug)
                
                if dados:
                    with st.container(border=True):
                        st.subheader(nome)
                        st.caption(f"Concurso {dados.get('concurso')} ({dados.get('data')})")
                        
                        # Exibição das dezenas
                        dezenas = dados.get('dezenas', [])
                        bolas_html = "".join([
                            f'<span style="background-color: #209869; color: white; padding: 5px 10px; '
                            f'border-radius: 50%; margin: 3px; display: inline-block; font-weight: bold;">'
                            f'{d}</span>' for d in dezenas
                        ])
                        st.markdown(bolas_html, unsafe_allow_html=True)
                        
                        st.write("")
                        # Valor estimado do próximo prêmio
                        proximo = dados.get('estimativa_proximo_concurso', 'Consulte o site')
                        st.metric("Próximo Prêmio", f"R$ {proximo}")
                else:
                    st.error(f"Falha ao obter dados da {nome}.")
else:
    st.info("Clique no botão acima para carregar os resultados via API.")

st.divider()
st.caption("Fonte: API baseada em repositórios comunitários do GitHub.")
