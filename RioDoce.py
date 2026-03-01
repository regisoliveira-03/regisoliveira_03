import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
import json

st.set_page_config(page_title="Rio Doce - Busca Total", page_icon="💧")
st.title("💧 Consulta de Dados PMQQS")

URL_PORTAL = "https://monitoramentoriodoce.org/download-dos-dados/"
URL_AJAX = "https://monitoramentoriodoce.org/wp-admin/admin-ajax.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": URL_PORTAL
}

if st.button('Executar Pesquisa Completa (Todos)'):
    try:
        session = requests.Session()
        
        with st.spinner('Sincronizando com o portal...'):
            # Passo 1: Pega a página e tenta achar tokens de segurança
            page = session.get(URL_PORTAL, headers=HEADERS, timeout=20)
            soup_page = BeautifulSoup(page.text, 'html.parser')
            
        with st.spinner('Enviando filtros conforme imagem...'):
            # Payload ajustado para simular a seleção "Todos" em todos os campos
            payload = {
                "action": "get_pmqqs_data",
                "origem": "manual",
                "ponto[]": "all",
                "matriz[]": "all",
                "parametro[]": "all",
                "tipo_amostra": "all", # Adicionado conforme imagem
                "data_inicio": "",
                "data_fim": "",
                "paged": "1",
                "posts_per_page": "50"
            }

            # Passo 2: Tenta a busca
            response = session.post(URL_AJAX, headers=HEADERS, data=payload, timeout=30)
            
        if response.status_code == 200:
            try:
                res_json = response.json()
                html_tabela = res_json.get('data', {}).get('html', '')
                
                if html_tabela and "<tr" in html_tabela:
                    soup = BeautifulSoup(html_tabela, 'html.parser')
                    
                    # Extração dos dados
                    headers_table = [th.get_text(strip=True) for th in soup.find_all('th')]
                    rows = []
                    for tr in soup.find_all('tr'):
                        cells = [td.get_text(strip=True) for td in tr.find_all('td')]
                        if cells: rows.append(cells)
                    
                    if rows:
                        df = pd.DataFrame(rows, columns=headers_table if headers_table else None)
                        st.success("### ✅ Dados Recuperados!")
                        st.dataframe(df, use_container_width=True)
                        
                        # Monitoramento da Data Amostra (O seu objetivo principal)
                        if 'DataAmostra' in df.columns:
                            st.info(f"📅 **Amostra mais recente na tabela:** {df['DataAmostra'].iloc[0]}")
                    else:
                        st.warning("A pesquisa não retornou linhas. Tente selecionar filtros menos abrangentes.")
                else:
                    st.error("O servidor aceitou a conexão, mas não enviou a tabela. O site pode estar bloqueando o acesso automatizado via Firewall.")
            except Exception:
                st.error("Erro ao processar a resposta do servidor. O formato pode ter mudado.")
        else:
            st.error(f"Erro {response.status_code}. O servidor recusou a requisição.")
            st.info("Dica: Se o erro 400 persistir, o site pode estar usando o Cloudflare para bloquear scripts Python.")

    except Exception as e:
        st.error(f"Falha na conexão: {e}")

st.divider()
st.caption("Filtros aplicados: Origem: Manual | Pontos: Todos | Matriz: Todos | Parâmetros: Todos")
