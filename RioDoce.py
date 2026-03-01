import streamlit as st
import requests

# Configuração da página (opcional)
st.set_page_config(page_title="Monitoramento Rio Doce - Verificador", page_icon="💧")

st.title("Verificador de Atualização de Dados")
st.write("Verificando a última data de modificação da página de downloads do Rio Doce...")

url = "https://monitoramentoriodoce.org/download-dos-dados/"

# Botão para disparar a verificação
if st.button('Verificar agora'):
    try:
        # Fazemos a requisição HEAD para economizar banda (não baixa o conteúdo, apenas o cabeçalho)
        response = requests.head(url, allow_redirects=True)
        
        # Tenta obter o cabeçalho 'Last-Modified'
        last_modified = response.headers.get('Last-Modified')
        
        if last_modified:
            st.success(f"✅ **Data de modificação informada pelo servidor:**")
            st.info(last_modified)
            st.caption("Nota: Esta data refere-se à última alteração na estrutura da página ou arquivo no servidor.")
        else:
            st.warning("⚠️ O servidor não fornece uma data 'Last-Modified' direta nos cabeçalhos HTTP.")
            st.write("Isso é comum em sites dinâmicos (WordPress/CMS).")
            
        # Exibe outros detalhes técnicos úteis para o desenvolvedor
        with st.expander("Ver detalhes técnicos (Headers)"):
            st.json(dict(response.headers))

    except Exception as e:
        st.error(f"Erro ao acessar o site: {e}")

# Rodapé informando a URL monitorada
st.divider()
st.caption(f"Monitorando: {url}")
