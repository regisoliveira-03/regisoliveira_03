import streamlit as st
from playwright.sync_api import sync_playwright
import subprocess
import os

# Configuração da página
st.set_page_config(page_title="Loterias Oficiais", page_icon="🎰")

def instalar_browser():
    """Instala o Chromium do Playwright se não estiver presente"""
    try:
        # Verifica se o diretório do browser existe no cache do Streamlit
        if not os.path.exists("/home/adminuser/.cache/ms-playwright"):
            with st.spinner("Instalando navegadores (isso ocorre apenas na primeira execução)..."):
                subprocess.run(["python", "-m", "playwright", "install", "chromium"], check=True)
    except Exception as e:
        st.error(f"Erro na instalação do browser: {e}")

def buscar_resultado_caixa(modalidade):
    instalar_browser()
    
    with sync_playwright() as p:
        # Lança o navegador com argumentos para evitar bloqueios em containers
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        
        # Simula um navegador real com User-Agent e viewport
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        url = f"https://loterias.caixa.gov.br/Paginas/{modalidade}.aspx"
        
        try:
            # Navega até o site com timeout estendido (60s)
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Aguarda o elemento específico das dezenas (ID ulDezenas)
            page.wait_for_selector("#ulDezenas", timeout=30000)
            
            # Extração dos dados via seletores CSS
            concurso_texto = page.locator(".title-bar").inner_text()
            dezenas = page.locator("#ulDezenas li").all_inner_texts()
            proximo_premio = page.locator(".next-prize .value").first.inner_text() if page.locator(".next-prize .value").count() > 0 else "N/A"
            
            return {
                "concurso": concurso_texto,
                "dezenas": dezenas,
                "proximo": proximo_premio
            }
        except Exception as e:
            return f"Erro de carregamento: {str(e)}"
        finally:
            browser.close()

# Interface Streamlit
st.title("🎰 Resultados Loterias Caixa")
st.write("Dados extraídos via Web Scraping (Playwright).")

opcoes = {
    "Mega-Sena": "Mega-Sena",
    "Lotofácil": "Lotofacil",
    "Quina": "Quina",
    "Lotomania": "Lotomania"
}

selecao = st.selectbox("Escolha a modalidade:", list(opcoes.keys()))

if st.button("Consultar Resultado Atual"):
    with st.spinner(f"Acessando o portal oficial da {selecao}..."):
        resultado = buscar_resultado_caixa(opcoes[selecao])
        
        if isinstance(resultado, dict):
            st.success("Dados obtidos diretamente do site da Caixa!")
            
            st.subheader(resultado["concurso"])
            
            # Exibição visual das dezenas
            st.write("**Dezenas Sorteadas:**")
            colunas = st.columns(len(resultado["dezenas"]))
            for i, dezena in enumerate(resultado["dezenas"]):
                colunas[i].markdown(f"### {dezena}")
                
            st.metric("Estimativa Próximo Prêmio", resultado["proximo"])
        else:
            st.error(resultado)
            st.warning("O site da Caixa pode estar com tráfego intenso ou bloqueando o IP do servidor.")
