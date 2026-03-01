import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

st.set_page_config(page_title="Rio Doce - Busca de Dados", page_icon="💧")

st.title("💧 Consulta de Dados PMQQS")
st.write("Esta versão utiliza **Cookies de Sessão** para evitar o Erro 400.")

# URLS do Portal
URL_PORTAL = "https://monitoramentoriodoce.org/download-dos-dados/"
URL_AJAX = "https://monitoramentoriodoce.org/wp-admin/admin-ajax.php"

# Headers base
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": URL_PORTAL
}

if st.button('Executar Pesquisa Completa'):
    try:
        # 1. Iniciamos uma sessão para manter os cookies
        session = requests.Session()
        
        with st.spinner('Passo 1: Autenticando no portal...'):
            # Visita a página inicial para pegar o Cookie e o Nonce (segurança do WordPress)
            first_response = session.get(URL_PORTAL, headers=HEADERS, timeout=20)
            
        if first_response.status_code == 200:
            with st.spinner('Passo 2: Enviando filtros (Todos)...'):
                # Payload idêntico ao que o navegador envia ao clicar em "Pesquisar"
                payload = {
                    "action": "get_pmqqs_data",
                    "origem": "manual",
                    "ponto[]": "all",
                    "matriz[]": "all",
                    "parametro[]": "all",
                    "tipo_amostra": "",
                    "data_inicio": "",
                    "data_fim": "",
                    "paged": "1",
                    "posts_per_page": "50" # Aumentamos para pegar mais linhas
                }

                # Fazemos o POST usando a mesma sessão que já tem o Cookie
                response = session.post(URL_AJAX, headers=HEADERS, data=payload, timeout=30)
                
            if response.status_code == 200:
                json_res = response.json()
                html_tabela = json_res.get('data', {}).get('html', '')
                
                if html_tabela and "tr" in html_tabela:
                    soup = BeautifulSoup(html_tabela, 'html.parser')
                    
                    # Extração inteligente dos dados
                    headers_table = [th.get_text(strip=True) for th in soup.find_all('th')]
                    rows = []
                    for tr in soup.find_all('tr'):
                        cells = [td.get_text(strip=True) for td in tr.find_all('td')]
                        if cells:
                            rows.append(cells)
                    
                    if rows:
                        df = pd.DataFrame(rows, columns=headers_table if headers_table else None)
                        
                        st.success("### ✅ Dados Carregados com Sucesso!")
                        st.dataframe(df, use_container_width=True)
                        
                        if 'DataAmostra' in df.columns:
                            st.info(f"📅 **Amostra mais recente:** {df['DataAmostra'].iloc[0]}")
                    else:
                        st.warning("O servidor respondeu, mas a tabela veio sem linhas.")
                else:
                    st.error("Resposta vazia. Verifique se os filtros 'Todos' ainda são válidos no site.")
            else:
                st.error(f"Erro no Passo 2 (Busca): {response.status_code}")
                st.write("O servidor recusou os parâmetros enviados.")
        else:
            st.error(f"Erro no Passo 1 (Acesso): {first_response.status_code}")

    except Exception as e:
        st.error(f"Ocorreu um erro técnico: {e}")

st.divider()
st.caption("Nota: Caso o erro persista, o site pode estar usando proteção via Cloudflare (JavaScript Challenge).")
