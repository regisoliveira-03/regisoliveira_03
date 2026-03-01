import streamlit as st
import requests

# 1. Configurações da Página
st.set_page_config(page_title="Loterias Caixa - Resultados", page_icon="💰", layout="centered")

# Função para buscar dados da API estável
def buscar_resultado(modalidade):
    # Esta API é mantida por terceiros e costuma ignorar bloqueios que o site da Caixa impõe
    url = f"https://loterica.com.br/api/v1/{modalidade}/ultimo"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

# 2. Interface do Usuário
st.title("🎰 Resultados Loterias Caixa")
st.markdown("Consulte os dados do último concurso de forma estável e rápida.")

# Dicionário para mapear nomes amigáveis para os endpoints da API
loterias_map = {
    "Mega-Sena": "mega-sena",
    "Lotofácil": "lotofacil",
    "Quina": "quina",
    "Lotomania": "lotomania",
    "TimeMania": "timemania",
    "Dupla Sena": "dupla-sena",
    "Dia de Sorte": "dia-de-sorte",
    "Mais Milionária": "mais-milionaria"
}

# Menu Lateral
st.sidebar.header("Configurações")
selecionadas = st.sidebar.multiselect(
    "Selecione as Loterias:",
    options=list(loterias_map.keys()),
    default=["Mega-Sena", "Lotofácil"]
)

if st.sidebar.button("🔄 Atualizar Dados"):
    st.rerun()

# 3. Processamento e Exibição
if selecionadas:
    for nome_exibicao in selecionadas:
        slug = loterias_map[nome_exibicao]
        
        with st.spinner(f"Carregando {nome_exibicao}..."):
            dados = buscar_resultado(slug)
            
            if dados:
                # Criando um card visual para cada loteria
                with st.container():
                    st.subheader(f"📊 {nome_exibicao}")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.metric("Número do Concurso", dados.get('concurso'))
                        st.write(f"**Data do Sorteio:** {dados.get('data')}")
                    
                    with col2:
                        # Tratamento para o prêmio estimado
                        premio = dados.get('estimativa_proximo_concurso', 0)
                        try:
                            # Tenta converter para float para formatar como moeda
                            valor_formatado = f"R$ {float(premio):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                            st.metric("Próximo Prêmio", valor_formatado)
                        except:
                            st.metric("Próximo Prêmio", f"R$ {premio}")
                    
                    # Exibição das Dezenas
                    dezenas = dados.get('dezenas', [])
                    if dezenas:
                        st.markdown("**Dezenas Sorteadas:**")
                        # Cria uma linha de "bolinhas" visuais
                        st.info("  •  ".join(dezenas))
                    
                    st.divider()
            else:
                st.error(f"Não foi possível obter dados para: {nome_exibicao}. O servidor pode estar em manutenção.")
else:
    st.info("Utilize o menu lateral para selecionar as loterias que deseja consultar.")

st.caption("Nota: Dados fornecidos via API Loterica (Fonte alternativa estável).")
