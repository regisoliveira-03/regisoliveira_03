import streamlit as st
from playwright.sync_api import sync_playwright
import os

# Configuração da página
st.set_page_config(page_title="Loterias Oficiais", page_icon="🎰")

def buscar_resultado_caixa(modalidade):
    # O navegador já foi instalado pelo setup.sh, então apenas iniciamos
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
            
            url = f"https://loterias.caixa.gov.br/Paginas/{modalidade}.aspx"
            
            # Navega até o site
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Aguarda o elemento das dezenas
            page.wait_for_selector("#ulDezenas", timeout=30000)
            
            concurso_texto = page.locator(".title-bar").inner_text()
            dezenas = page.locator("#ulDezenas li").all_inner_texts()
            
            # Tenta pegar o prêmio, se não existir, define como N/A
            try:
                proximo_premio = page.locator(".next-prize .value").first.inner_text()
            except:
                proximo_premio = "Consulte o site"
            
            return {
                "concurso": concurso_texto,
                "dezenas": dezenas,
                "proximo": proximo_premio
            }
        except Exception as e:
            return f"Erro ao acessar site da Caixa: {str(e)}"
        finally:
            if 'browser' in locals():
                browser.close()

# --- Interface Streamlit ---
st.title("🎰 Resultados Loterias Caixa")

opcoes = {
    "Mega-Sena": "Mega-Sena",
    "Lotofácil": "Lotofacil",
    "Quina": "Quina",
    "Lotomania": "Lotomania"
}

selecao = st.selectbox("Escolha a modalidade:", list(opcoes.keys()))

if st.button("Consultar Resultado Atual"):
    with st.spinner(f"Acessando o portal oficial..."):
        resultado = buscar_resultado_caixa(opcoes[selecao])
        
        if isinstance(resultado, dict):
            st.success("Dados atualizados!")
            st.subheader(resultado["concurso"])
            
            st.write("**Dezenas Sorteadas:**")
            # Exibe as dezenas em badges horizontais
            st.write("  ".join([f"**[{d}]**" for d in resultado["dezenas"]]))
                
            st.metric("Estimativa Próximo Prêmio", resultado["proximo"])
        else:
            st.error(resultado)
