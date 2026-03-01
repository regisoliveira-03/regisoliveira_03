import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

st.set_page_config(page_title="Rio Doce - Monitor de Dados", page_icon="💧")

st.title("🔍 Verificador de Novos Dados - Rio Doce")

url_page = "https://monitoramentoriodoce.org/download-dos-dados/"
# Endpoint interno que o site usa para buscar os dados da tabela
url_api_busca = "https://monitoramentoriodoce.org/wp-admin/admin-ajax.php"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

if st.button('Buscar Dados Recentes na Tabela'):
    try:
        # Payload que simula a busca padrão do site (sem filtros específicos)
        payload = {
            "action": "get_pmqqs_data",
            "paged": 1,
            "posts_per_page": 10  # Pegamos os 10 primeiros para ver o que há de novo
        }

        response = requests.post(url_api_busca, headers=headers, data=payload)
        
        if response.status_code == 200:
            json_data = response.json()
            # O site retorna o HTML da tabela dentro de um JSON
            html_tabela = json_data.get('data', {}).get('html', '')
            
            if html_tabela:
                soup = BeautifulSoup(html_tabela, 'html.parser')
                rows = []
                # Extraindo linhas da tabela
                for tr in soup.find_all('tr')[1:]: # Pula o cabeçalho
                    cols = [td.get_text(strip=True) for td in tr.find_all('td')]
                    if cols:
                        rows.append(cols)
                
                # Criando um DataFrame para facilitar a visualização
                df = pd.DataFrame(rows, columns=["Ponto", "Data Amostra", "Hora", "Lat", "Long", "Matriz", "Tipo", "Cianobactéria"])
                
                st.success("### Dados mais recentes encontrados na tabela:")
                st.table(df.head(5))
                
                # Identificando a data mais recente
                ultima_data = df['Data Amostra'].iloc[0]
                st.info(f"💡 **Conclusão:** O dado mais recente inserido no sistema é do dia **{ultima_data}**.")
            else:
                st.warning("A busca retornou vazia. O site pode ter mudado o formato da requisição.")
        else:
            st.error(f"Erro na requisição: {response.status_code}")

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")

st.divider()
st.caption("Nota: Este script acessa o formulário de pesquisa dinâmico do site.")
