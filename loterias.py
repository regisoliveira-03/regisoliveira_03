import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configuração da página
st.set_page_config(page_title="Scraper Loterias", page_icon="🔍")

def scraping_loteria(modalidade):
    # Configurações do Chrome para rodar sem abrir janela (Headless)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # User-agent para evitar detecção de robô
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    url = f"https://loterias.caixa.gov.br/Paginas/{modalidade}.aspx"
    
    try:
        driver.get(url)
        
        # Aguarda até que o elemento que contém as dezenas apareça (timeout de 20s)
        wait = WebDriverWait(driver, 20)
        # O seletor abaixo busca a lista de dezenas na estrutura do site da Caixa
        elemento_resultado = wait.until(EC.presence_of_element_located((By.ID, "ulDezenas")))
        
        # Extração dos dados
        concurso_info = driver.find_element(By.CLASS_NAME, "title-bar").text
        dezenas = [li.text for li in elemento_resultado.find_elements(By.TAG_NAME, "li")]
        
        return {
            "info": concurso_info,
            "dezenas": dezenas
        }
    except Exception as e:
        return f"Erro: {e}"
    finally:
        driver.quit()

# Interface Streamlit
st.title("🔍 Web Scraping Loterias")
st.write("Extraindo dados diretamente do portal oficial via Selenium.")

modalidade_escolhida = st.selectbox("Selecione a Loteria", ["Mega-Sena", "Lotofacil", "Quina"])
mapa_url = {"Mega-Sena": "Mega-Sena", "Lotofacil": "Lotofacil", "Quina": "Quina"}

if st.button("Buscar Resultado"):
    with st.spinner("Simulando navegador e acessando o site da Caixa..."):
        resultado = scraping_loteria(mapa_url[modalidade_escolhida])
        
        if isinstance(resultado, dict):
            st.success("Dados extraídos com sucesso!")
            st.subheader(resultado["info"])
            
            # Mostra as dezenas em destaque
            colunas = st.columns(len(resultado["dezenas"]))
            for i, dezena in enumerate(resultado["dezenas"]):
                colunas[i].metric("", dezena)
        else:
            st.error(resultado)

st.warning("Nota: Web scraping é mais lento que API e pode falhar se a Caixa mudar a estrutura do site.")
