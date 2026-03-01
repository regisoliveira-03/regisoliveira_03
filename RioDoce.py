import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Configuração visual
st.set_page_config(page_title="Rio Doce Monitor", page_icon="💧")
st.title("💧 Monitor de Dados - Rio Doce")

url = "https://monitoramentoriodoce.org/download-dos-dados/"

# Headers para evitar bloqueios (Erro 400/401)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

if st.button('Verificar Atualizações no Site'):
    try:
        with st.spinner('Acessando o portal...'):
            response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Captura a data de modificação estrutural (SEO)
            meta_date = soup.find("meta", property="article:modified_time")
            data_iso = meta_date['content'] if meta_date else None
            
            st.success("### ✅ Conexão Estabelecida")
            
            col1, col2 = st.columns(2)
            if data_iso:
                # Formatando a data ISO para legível
                data_limpa = data_iso.split('T')[0]
                col1.metric("Página Editada em:", data_limpa)
            
            # 2. Monitoramento de Links de Documentos
            st.subheader("📄 Documentos e Planilhas Extras")
            links_encontrados = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if any(ext in href.lower() for ext in ['.pdf', '.zip', '.xlsx', '.csv']):
                    links_encontrados.append({"Documento": a.get_text(strip=True), "Link": href})
            
            if links_encontrados:
                st.dataframe(pd.DataFrame(links_encontrados), use_container_width=True)
            else:
                st.info("Nenhum arquivo direto (.csv/.zip) listado no HTML estático.")

            # 3. Explicação sobre a Data da Amostra (Sua imagem do site)
            st.warning("⚠️ **Nota sobre a Tabela Dinâmica:**")
            st.write("""
                O portal utiliza uma busca assíncrona que bloqueia acessos automáticos (causando o Erro 400). 
                Conforme verificado manualmente, os dados mais recentes no sistema são de **02/02/2026**.
            """)
            
        else:
            st.error(f"O servidor recusou a conexão. Código: {response.status_code}")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")

st.divider()
st.caption("Dica: Se precisar de automação total dos dados brutos, a melhor via é o ArcGIS Hub da Fundação Renova.")
