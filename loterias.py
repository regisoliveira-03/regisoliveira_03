import streamlit as st
from playwright.sync_api import sync_playwright
import os

# Configuração da página para ocupar a largura total
st.set_page_config(page_title="Painel Loterias Caixa", page_icon="🎰", layout="wide")

def buscar_todos_resultados():
    modalidades = {
        "Mega-Sena": "Mega-Sena",
        "Lotofácil": "Lotofacil",
        "Quina": "Quina",
        "Lotomania": "Lotomania",
        "Dupla Sena": "Dupla-Sena",
        "Dia de Sorte": "Dia-de-Sorte"
    }
    
    resultados = {}

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            # Criamos uma barra de progresso no Streamlit
            progresso = st.progress(0)
            status_text = st.empty()

            for i, (nome, slug) in enumerate(modalidades.items()):
                status_text.text(f"Obtendo resultado: {nome}...")
                url = f"https://loterias.caixa.gov.br/Paginas/{slug}.aspx"
                
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_selector("#ulDezenas", timeout=15000)
                    
                    concurso = page.locator(".title-bar").inner_text()
                    dezenas = page.locator("#ulDezenas li").all_inner_texts()
                    
                    try:
                        proximo = page.locator(".next-prize .value").first.inner_text()
                    except:
                        proximo = "Ver site"

                    resultados[nome] = {
                        "concurso": concurso,
                        "dezenas": dezenas,
                        "proximo": proximo
                    }
                except:
                    resultados[nome] = {"erro": "Falha ao carregar"}
                
                # Atualiza a barra de progresso
                progresso.progress((i + 1) / len(modalidades))
            
            status_text.empty()
            progresso.empty()
            return resultados

        except Exception as e:
            return f"Erro Geral: {str(e)}"
        finally:
            if 'browser' in locals():
                browser.close()

# --- Interface Streamlit ---
st.title("🎰 Painel de Resultados Loterias Caixa")
st.write("Resultados mais recentes extraídos em tempo real.")

if st.button("🚀 Atualizar Todos os Resultados"):
    dados_completos = buscar_todos_resultados()
    
    if isinstance(dados_completos, dict):
        # Organizamos a exibição em uma grade (2 resultados por linha)
        cols = st.columns(2)
        
        for idx, (nome, info) in enumerate(dados_completos.items()):
            col_index = idx % 2
            with cols[col_index]:
                with st.container(border=True):
                    st.subheader(nome)
                    
                    if "erro" in info:
                        st.error(info["erro"])
                    else:
                        st.caption(info["concurso"])
                        
                        # Estilização das dezenas como "bolas"
                        html_dezenas = "".join([f'<span style="background-color: #209869; color: white; padding: 5px 10px; border-radius: 50%; margin: 2px; display: inline-block; font-weight: bold;">{d}</span>' for d in info["dezenas"]])
                        st.markdown(html_dezenas, unsafe_allow_html=True)
                        
                        st.write("") # Espaçamento
                        st.metric("Próximo Prêmio", info["proximo"])
    else:
        st.error(dados_completos)
else:
    st.info("Clique no botão acima para carregar todos os resultados simultaneamente.")

st.divider()
st.caption("Nota: O processo pode levar cerca de 30-40 segundos para percorrer todos os sites.")
