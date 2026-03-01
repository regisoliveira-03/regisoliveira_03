import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Data de Atualização Rio Doce", page_icon="📅")

st.title("📅 Monitor de Atualização de Dados")
st.write("Acessando metadados internos via WordPress REST API...")

# O ID 28 foi identificado no seu cabeçalho como a página de downloads
api_url = "https://monitoramentoriodoce.org/wp-json/wp/v2/pages/28"

if st.button('Consultar Data de Inclusão/Atualização'):
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extraindo as datas do JSON da API
            data_criacao = data.get('date')
            data_modificacao = data.get('modified')
            titulo_pagina = data.get('title', {}).get('rendered', 'Página de Downloads')

            # Formatando as datas para PT-BR
            dt_cria = datetime.fromisoformat(data_criacao).strftime('%d/%m/%Y %H:%M:%S')
            dt_mod = datetime.fromisoformat(data_modificacao).strftime('%d/%m/%Y %H:%M:%S')

            st.success(f"### {titulo_pagina}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Página Criada em", dt_cria)
            with col2:
                st.metric("Última Atualização", dt_mod)

            st.info("💡 **O que isso significa?** A 'Última Atualização' indica quando um administrador alterou o conteúdo desta página (ex: substituiu um link de download ou editou o texto).")
            
            with st.expander("Ver resposta bruta da API"):
                st.json(data)
        else:
            st.error(f"Não foi possível acessar a API. Status: {response.status_code}")

    except Exception as e:
        st.error(f"Erro na requisição: {e}")

st.divider()
st.caption("Nota: Se os arquivos CSV são atualizados sem alterar o link na página, esta data pode não mudar. Para monitorar os arquivos físicos, seria necessário listar o diretório /wp-content/uploads/ (geralmente protegido).")
