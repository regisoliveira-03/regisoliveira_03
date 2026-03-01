import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

st.set_page_config(page_title="Rio Doce - Busca de Dados", page_icon="💧")

st.title("💧 Consulta de Dados PMQQS")
st.write("Simulando busca por: **Todos os Pontos, Matrizes e Parâmetros**")

# Configurações da Requisição
URL_AJAX = "https://monitoramentoriodoce.org/wp-admin/admin-ajax.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest"
}

if st.button('Executar Pesquisa Completa'):
    try:
        with st.spinner('Solicitando dados ao servidor...'):
            # Payload configurado para simular o filtro "Todos" selecionado nas imagens
            payload = {
                "action": "get_pmqqs_data",
                "origem": "manual",
                "ponto[]": "all",      # Simula o "Todos" da imagem
                "matriz[]": "all",     # Simula o "Todos" da imagem
                "parametro[]": "all",  # Simula o "Todos" da imagem
                "tipo_amostra": "",
                "data_inicio": "",
                "data_fim": "",
                "paged": "1",
                "posts_per_page": "20"
            }

            response = requests.post(URL_AJAX, headers=HEADERS, data=payload, timeout=30)
            
        if response.status_code == 200:
            json_res = response.json()
            html_tabela = json_res.get('data', {}).get('html', '')
            
            if html_tabela and "tr" in html_tabela:
                # Processando a tabela HTML retornada
                soup = BeautifulSoup(html_tabela, 'html.parser')
                rows = []
                
                # Captura os cabeçalhos
                headers_table = [th.get_text(strip=True) for th in soup.find_all('th')]
                
                # Captura as linhas de dados
                for tr in soup.find_all('tr'):
                    cells = [td.get_text(strip=True) for td in tr.find_all('td')]
                    if cells:
                        rows.append(cells)
                
                if rows:
                    df = pd.DataFrame(rows, columns=headers_table if headers_table else None)
                    
                    st.success("### Dados Encontrados na Tabela")
                    st.dataframe(df, use_container_width=True)
                    
                    # Destaque para a data mais recente (como na sua imagem)
                    if 'DataAmostra' in df.columns:
                        data_recente = df['DataAmostra'].iloc[0]
                        st.info(f"📅 **Amostra mais recente detectada:** {data_recente}")
                else:
                    st.warning("A tabela foi retornada vazia pelo servidor.")
            else:
                st.error("O servidor não retornou dados para estes filtros.")
        else:
            st.error(f"Erro no servidor: {response.status_code}. O site pode estar instável.")

    except Exception as e:
        st.error(f"Erro de conexão: {e}")

st.divider()
st.caption("Nota: Este script reproduz a ação do botão 'Pesquisar' do portal oficial.")
