import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Configurações iniciais
st.set_page_config(page_title="Monitor Rio Doce", page_icon="💧")
st.title("💧 Monitor de Atualizações Rio Doce")

URL = "https://monitoramentoriodoce.org/download-dos-dados/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

if st.button('Verificar Status do Portal'):
    try:
        with st.spinner('Acessando o site...'):
            response = requests.get(URL, headers=HEADERS, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Captura a data de modificação do conteúdo (SEO)
            meta_mod = soup.find("meta", property="article:modified_time")
            data_site = meta_mod['content'] if meta_mod else "Não disponível"
            
            st.success("✅ Conexão bem-sucedida!")
            
            col1, col2 = st.columns(2)
            col1.metric("Página do Site Editada em:", data_site.split('T')[0] if 'T' in data_site else data_site)
            
            # 2. Busca por arquivos em 'Informações Complementares'
            st.subheader("📂 Arquivos e Planilhas Disponíveis")
            st.write("Verificando links de downloads diretos (PDF/ZIP/XLSX):")
            
            links_files = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if any(ext in href.lower() for ext in ['.pdf', '.zip', '.xlsx', '.csv']):
                    links_files.append({"Documento": a.get_text(strip=True), "Link": href})
            
            if links_files:
                df_links = pd.DataFrame(links_files)
                st.dataframe(df_links, use_container_width=True)
            else:
                st.info("Nenhum link de arquivo direto encontrado no HTML estático.")

            # 3. Explicação sobre a Data da Amostra
            st.warning("⚠️ **Observação sobre a Tabela Dinâmica**")
            st.info("Conforme suas capturas de tela, os dados mais recentes no sistema manual são de **02/02/2026**. O servidor bloqueia o acesso via script (Erro 400) para proteger a base de dados de raspagens automáticas.")
            
        else:
            st.error(f"Erro ao acessar: {response.status_code}")
            
    except Exception as e:
        st.error(f"Erro técnico: {e}")

st.divider()
st.caption("Nota: Este monitor foca em metadados para evitar bloqueios do servidor.")
