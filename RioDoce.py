import streamlit as st
import requests
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Download PMQQS", page_icon="📥")
st.title("📥 Downloader de Dados PMQQS")
st.write("Extraindo as coletas manuais mais recentes diretamente em CSV.")

# URLs de backend do portal
URL_PORTAL = "https://monitoramentoriodoce.org/download-dos-dados/"
URL_AJAX = "https://monitoramentoriodoce.org/wp-admin/admin-ajax.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": URL_PORTAL
}

if st.button('Gerar e Baixar CSV (Todos os Dados Manuais)'):
    try:
        session = requests.Session()
        
        with st.spinner('Conectando ao servidor da Fundação Renova...'):
            # Passo 1: Visita a página para validar a sessão e cookies
            session.get(URL_PORTAL, headers=HEADERS, timeout=20)
            
            # Passo 2: Payload configurado para buscar "Todos" conforme suas imagens anteriores
            # A 'action' pode variar se o site usar um exportador específico, 
            # aqui usamos a base da busca manual.
            payload = {
                "action": "get_pmqqs_data",
                "origem": "manual",
                "ponto[]": "all",
                "matriz[]": "all",
                "parametro[]": "all",
                "tipo_amostra": "all",
                "paged": "1",
                "posts_per_page": "1000" # Tentativa de capturar o máximo de linhas
            }

            response = session.post(URL_AJAX, headers=HEADERS, data=payload, timeout=60)

        if response.status_code == 200:
            data_json = response.json()
            # O WordPress retorna o HTML da tabela. Vamos converter para DataFrame.
            html_content = data_json.get('data', {}).get('html', '')
            
            if html_content:
                # O pandas consegue ler tabelas HTML diretamente
                df_list = pd.read_html(html_content)
                if df_list:
                    df = df_list[0]
                    
                    st.success(f"✅ {len(df)} registros encontrados!")
                    st.dataframe(df.head(10)) # Mostra prévia
                    
                    # Conversão para CSV em memória
                    csv_buffer = BytesIO()
                    df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
                    csv_buffer.seek(0)
                    
                    # Botão de download do Streamlit
                    st.download_button(
                        label="Clique aqui para baixar o arquivo .CSV",
                        data=csv_buffer,
                        file_name="dados_pmqqs_manual.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("A tabela foi processada, mas nenhum dado foi encontrado.")
            else:
                st.error("O servidor não retornou dados para os filtros selecionados.")
        else:
            st.error(f"Erro no servidor: {response.status_code}. O acesso automatizado pode estar bloqueado.")

    except Exception as e:
        st.error(f"Ocorreu um erro técnico: {e}")

st.divider()
st.caption("Nota: Este script simula a pesquisa manual 'Todos' e exporta o resultado visível.")
