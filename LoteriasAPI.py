import streamlit as st
import requests

# 1. Configuração da Página
st.set_page_config(page_title="Loterias + Conferidor", page_icon="🍀", layout="wide")

def consultar_api(modalidade):
    """Consulta a API comunitária estável (Projeto GitHub)"""
    url = f"https://loterica.com.br/api/v1/{modalidade}/ultimo"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# --- Interface Principal ---
st.title("🍀 Loterias Caixa & Conferidor de Jogos")
st.markdown("Consulte os resultados e verifique seus acertos automaticamente.")

# Mapeamento de Slugs
loterias_map = {
    "Mega-Sena": "mega-sena",
    "Lotofácil": "lotofacil",
    "Quina": "quina",
    "Lotomania": "lotomania",
    "Timemania": "timemania",
    "Dupla Sena": "dupla-sena",
    "Dia de Sorte": "dia-de-sorte"
}

# 2. Barra Lateral para Seleção
st.sidebar.header("Configurações")
selecionadas = st.sidebar.multiselect(
    "Quais loterias deseja conferir?",
    options=list(loterias_map.keys()),
    default=["Mega-Sena", "Lotofácil"]
)

if st.sidebar.button("🔄 Atualizar Resultados"):
    st.rerun()

# 3. Exibição e Conferência
if selecionadas:
    cols = st.columns(len(selecionadas) if len(selecionadas) <= 2 else 2)
    
    for i, nome in enumerate(selecionadas):
        slug = loterias_map[nome]
        with cols[i % 2]:
            with st.spinner(f"Sincronizando {nome}..."):
                dados = consultar_api(slug)
                
                if dados:
                    with st.container(border=True):
                        st.header(nome)
                        st.caption(f"Concurso {dados.get('concurso')} ({dados.get('data')})")
                        
                        # Resultados Oficiais (Dezenas da API)
                        dezenas_oficiais = [str(d).zfill(2) for d in dados.get('dezenas', [])]
                        
                        # Estilização das dezenas oficiais
                        bolas_html = "".join([
                            f'<span style="background-color: #209869; color: white; padding: 5px 10px; '
                            f'border-radius: 50%; margin: 2px; display: inline-block; font-weight: bold;">'
                            f'{d}</span>' for d in dezenas_oficiais
                        ])
                        st.markdown(f"**Sorteio:** {bolas_html}", unsafe_allow_html=True)
                        
                        st.divider()
                        
                        # --- SEÇÃO CONFERIDOR ---
                        st.subheader("🕵️ Conferir meu jogo")
                        meu_jogo_input = st.text_input(
                            f"Digite seus números da {nome} (separe por espaço ou vírgula):",
                            key=f"input_{slug}"
                        )
                        
                        if meu_jogo_input:
                            # Trata o input do usuário (limpa espaços e vírgulas)
                            meus_numeros = meu_jogo_input.replace(",", " ").split()
                            meus_numeros = [n.zfill(2) for n in meus_numeros if n.isdigit()]
                            
                            if meus_numeros:
                                # Lógica de comparação
                                acertos = [n for n in meus_numeros if n in dezenas_oficiais]
                                qtd_acertos = len(acertos)
                                
                                # Exibe o resultado da conferência
                                if qtd_acertos > 0:
                                    st.success(f"🔥 Você acertou **{qtd_acertos}** número(s)!")
                                    st.write(f"**Números acertados:** {', '.join(acertos)}")
                                else:
                                    st.warning("Não houve acertos neste jogo.")
                                    
                                # Feedback visual rápido
                                if nome == "Mega-Sena" and qtd_acertos >= 4:
                                    st.balloons()
                                    st.write("🎊 PARABÉNS! Você premiou!")
                            else:
                                st.error("Formato inválido. Digite apenas números.")
                        
                        st.divider()
                        st.metric("Estimativa Próximo Prêmio", f"R$ {dados.get('estimativa_proximo_concurso', '0,00')}")
                else:
                    st.error(f"Falha ao carregar {nome}.")
else:
    st.info("Selecione as loterias na barra lateral para começar.")
