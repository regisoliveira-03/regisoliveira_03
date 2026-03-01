import streamlit as st
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Loterias Caixa - Oficial", page_icon="🎰", layout="wide")

def buscar_loteria_ultra_estavel(modalidade_slug):
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            url = f"https://loterias.caixa.gov.br/Paginas/{modalidade_slug}.aspx"
            
            # Aumentamos o tempo de espera inicial para páginas pesadas (Lotofácil/Lotomania)
            page.goto(url, wait_until="networkidle", timeout=90000)
            
            # Forçamos a espera até que as dezenas estejam realmente visíveis e com texto
            page.wait_for_selector("#ulDezenas li", state="visible", timeout=45000)
            
            # Pequena pausa extra para garantir que o JavaScript da Caixa preencheu os números
            page.wait_for_timeout(2000) 
            
            titulo = page.locator(".title-bar").first.inner_text()
            
            # Captura todas as dezenas e filtra apenas o que for número real
            raw_dezenas = page.locator("#ulDezenas li").all_inner_texts()
            dezenas_limpas = [d.strip() for d in raw_dezenas if d.strip().isdigit()]
            
            # Se a lista vier vazia (comum na Lotofácil em conexões lentas), tenta um seletor alternativo
            if not dezenas_limpas:
                dezenas_limpas = page.evaluate('() => Array.from(document.querySelectorAll("#ulDezenas li")).map(li => li.innerText.trim()).filter(t => t !== "")')

            try:
                proximo = page.locator(".next-prize .value").first.inner_text()
            except:
                proximo = "Consulte o site oficial"
                
            return {"titulo": titulo, "dezenas": dezenas_limpas, "proximo": proximo}
        
        except Exception as e:
            return f"Erro: O site da Caixa não enviou os dados a tempo. Tente novamente em instantes. ({str(e)})"
        finally:
            browser.close()

# --- Interface ---
st.title("🎰 Consulta Oficial de Loterias")
st.markdown("Busca dedicada para maior estabilidade nos resultados.")

loterias = {
    "Mega-Sena": "Mega-Sena",
    "Lotofácil": "Lotofacil",
    "Quina": "Quina",
    "Lotomania": "Lotomania",
    "Dupla Sena": "Dupla-Sena",
    "Dia de Sorte": "Dia-de-Sorte"
}

st.write("Selecione para consultar:")
cols = st.columns(3)
placeholder = st.empty()

for i, (nome, slug) in enumerate(loterias.items()):
    with cols[i % 3]:
        if st.button(f"Consultar {nome}", use_container_width=True):
            with st.spinner(f"Carregando {nome}..."):
                res = buscar_loteria_ultra_estavel(slug)
                
                with placeholder.container():
                    if isinstance(res, dict) and len(res["dezenas"]) > 0:
                        st.success(f"Dados da {nome} carregados com sucesso!")
                        with st.container(border=True):
                            st.subheader(res["titulo"])
                            
                            # Exibição visual das dezenas
                            bolas = "".join([
                                f'<div style="background-color: #209869; color: white; width: 45px; height: 45px; '
                                f'border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; '
                                f'font-weight: bold; margin: 4px; box-shadow: 1px 1px 3px rgba(0,0,0,0.2);">'
                                f'{d}</div>' for d in res["dezenas"]
                            ])
                            st.markdown(bolas, unsafe_allow_html=True)
                            
                            st.divider()
                            st.metric("Próximo Prêmio Estimado", res["proximo"])
                    else:
                        st.error(f"Não foi possível extrair as dezenas da {nome}. O site da Caixa pode estar instável.")

st.info("💡 A Lotofácil e a Lotomania possuem muitos números, por isso o carregamento pode demorar alguns segundos a mais.")
