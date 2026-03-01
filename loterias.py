import streamlit as st
import os
import subprocess
from playwright.sync_api import sync_playwright

# COMANDO MÁGICO: Instala o Chromium se ele não existir no servidor
@st.cache_resource
def install_playwright_browsers():
    subprocess.run(["playwright", "install", "chromium"])
    subprocess.run(["playwright", "install-deps"])

# Executa a instalação antes de qualquer coisa
install_playwright_browsers()

def scrape_caixa(modalidade):
    with sync_playwright() as p:
        # Lançamos o navegador com argumentos para rodar em containers (nuvem)
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # O restante do seu código de scraping aqui...
        url = f"https://loterias.caixa.gov.br/Paginas/{modalidade}.aspx"
        try:
            page.goto(url, wait_until="load", timeout=90000)
            page.wait_for_selector("#ulDezenas", timeout=30000)
            
            titulo = page.locator(".title-bar").inner_text()
            dezenas = page.locator("#ulDezenas li").all_inner_texts()
            
            return {"titulo": titulo, "dezenas": dezenas}
        except Exception as e:
            return f"Erro: {str(e)}"
        finally:
            browser.close()

# Interface do Streamlit... (o restante do seu código)
