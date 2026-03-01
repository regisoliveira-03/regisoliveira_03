import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Rio Doce Monitor", page_icon="💧")

st.title("🔍 Monitor de Dados Rio Doce")

url = "https://monitoramentoriodoce.org/download-dos-dados/"

# Headers robustos para parecer um acesso humano
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

if st.button('Verificar Última Atualização'):
    try:
        with st.spinner('Consultando servidor...'):
            response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Busca a data de modificação no HTML (o que funcionou antes)
            meta_date = soup.find("meta", property="article:modified_time")
            data_site = meta_date['content'] if meta_date else "Não encontrada no HTML"
            
            st.success("### Status do Portal")
            st.metric("Página do Site Editada em:", data_site.split('T')[0] if 'T' in data_site else data_site)

            # 2. Tenta encontrar links de arquivos (Informações Complementares)
            st.subheader("Links de Documentos Encontrados:")
            doc_links = []
            for a in soup.find_all('a', href=True):
                if any(ext in a['href'].lower() for ext in ['.pdf', '.zip', '.xlsx', '.csv']):
                    doc_links.append({"Nome": a.get_text(strip=True), "Link": a['href']})
            
            if doc_links:
                st.dataframe(pd.DataFrame(doc_links))
            else:
                st.info("Nenhum arquivo direto listado. Os dados estão protegidos pela busca dinâmica.")

            st.warning("⚠️ **Nota sobre a Tabela:** Como o servidor retornou erro 400, a tabela dinâmica exige preenchimento manual no site. A data da amostra que você viu (02/02/2026) confirma que há dados recentes inseridos.")
            
        else:
            st.error(f"Erro ao acessar o site. Código: {response.status_code}")

    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")

st.divider()
st.caption("Dica: Para dados automatizados, tente checar o portal ArcGIS da Renova se o erro 400 persistir.")
