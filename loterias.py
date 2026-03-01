import streamlit as st
import requests
import urllib3

# Desativa avisos de segurança
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obter_ultimo_resultado(modalidade):
    # Criamos uma sessão para persistir cookies, o que ajuda a evitar bloqueios
    session = requests.Session()
    
    url = f"https://servicebus2.caixa.gov.br/portalloterias/api/{modalidade}"
    
    # Headers mais robustos
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://loterias.caixa.gov.br/",
        "Origin": "https://loterias.caixa.gov.br"
    }

    try:
        # Aumentei o timeout para 15 segundos, pois o servidor da Caixa é lento
        response = session.get(url, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            return f"Erro HTTP {response.status_code}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- Resto do código do Streamlit permanece igual ---
