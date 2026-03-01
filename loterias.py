import streamlit as st
from playwright.sync_api import sync_playwright
import time

st.set_page_config(page_title="Loterias Scraper", page_icon="🎰")

def scrape_caixa(modalidade):
    with sync_playwright() as p:
        # Abre um navegador "escondido"
        browser = p.chromium.launch(headless=True)
        # Cria um contexto com um User-Agent de pessoa real
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        url = f"https://loterias.caixa.gov.br/Paginas/{modalidade}.aspx"
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            # Aguarda o elemento das dezenas carregar
            page.wait_for_selector("#ulDezenas", timeout=30000)
            
            # Extrai o título do concurso e as dezenas
            titulo = page.locator(".title-bar").inner_text()
            dezenas = page.locator("#ulDezenas li").all_inner_texts()
            
            return {"titulo": titulo, "dezenas": dezenas}
        except Exception as e:
            return f"Erro ao acessar: {str(e)}"
        finally:
            browser.close()

st.title("🎰 Scraping Oficial Loterias")

option = st.selectbox("Escolha a loteria:", ["Mega-Sena", "Lotofacil", "Quina"])

if st.button("Buscar Resultado Atual"):
    with st.spinner("Navegando no site da Caixa..."):
        # Ajusta o nome para a URL (ex: Mega-Sena)
        resultado = scrape_caixa(option)
        
        if isinstance(resultado, dict):
            st.success("Dados capturados!")
            st.markdown(f"### {resultado['titulo']}")
            
            # Mostra as dezenas de forma bonita
            cols = st.columns(len(resultado['dezenas']))
            for i, d in enumerate(resultado['dezenas']):
                cols[i].markdown(f"## {d}")
        else:
            st.error(resultado)
            st.info("Dica: O site da Caixa pode estar lento ou bloqueando o servidor da nuvem.")
