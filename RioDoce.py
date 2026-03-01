import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Monitor Rio Doce", page_icon="💧")

st.title("🔍 Verificador de Atualização de Dados")
st.write("Tentando extrair datas de modificação via HTML (Web Scraping)...")

url = "https://monitoramentoriodoce.org/download-dos-dados/"

# Headers para simular um navegador real e evitar o erro 401/403
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

if st.button('Verificar Site'):
    try:
        # Realiza a requisição GET completa
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Estratégia 1: Procurar por metadados de SEO (Yoast ou similar)
            # Geralmente o WordPress insere a data de modificação em tags <meta>
            meta_modified = soup.find("meta", property="article:modified_time") or \
                            soup.find("meta", {"name": "last-modified"})
            
            # Estratégia 2: Procurar dentro do JSON-LD (Scripts de metadados)
            json_ld = soup.find_all('script', type='application/ld+json')
            date_found = None
            
            if meta_modified:
                date_found = meta_modified.get('content')
            else:
                # Busca por padrões de data no texto ou em scripts internos
                for script in json_ld:
                    match = re.search(r'"dateModified":"([^"]+)"', script.string if script.string else "")
                    if match:
                        date_found = match.group(1)
                        break

            if date_found:
                st.success("### Data de Modificação Encontrada!")
                st.metric("Última alteração no conteúdo:", date_found)
                st.info("Esta data indica a última vez que o conteúdo da página (incluindo links de download) foi editado no sistema.")
            else:
                st.warning("O site não expõe a data de modificação de forma visível no HTML.")
                st.write("Isso acontece quando o cache do servidor está mascarando os metadados.")
                
            # Extra: Listar links de download para ver se há datas nos nomes dos arquivos
            st.subheader("Arquivos detectados para download:")
            links = soup.find_all('a', href=True)
            zip_links = [l['href'] for l in links if '.zip' in l['href'] or '.csv' in l['href']]
            
            if zip_links:
                for link in zip_links:
                    st.write(f"📄 {link.split('/')[-1]}")
            else:
                st.write("Nenhum link direto de arquivo (.zip/.csv) encontrado nesta página.")

        else:
            st.error(f"Erro ao acessar o site. Status: {response.status_code}")
            if response.status_code == 401:
                st.info("O servidor continua bloqueando o acesso automático. O site pode estar usando um Firewall (WAF) agressivo.")

    except Exception as e:
        st.error(f"Erro na conexão: {e}")

st.divider()
st.caption("Nota: Se o site for atualizado apenas via banco de dados sem alterar o HTML, o scraping pode não refletir a mudança instantaneamente.")
