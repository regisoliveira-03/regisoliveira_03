import streamlit as st
from playwright.sync_api import sync_playwright

# Configuração da página
st.set_page_config(page_title="Resultados Individuais Loterias", page_icon="🎰")

def buscar_loteria_unica(modalidade_slug):
    """Busca apenas uma modalidade por vez para garantir estabilidade"""
    with sync_playwright() as p:
        try:
            # Lançamento do browser com configurações de estabilidade
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            page = context.new_page()
            
            url = f"https://loterias.caixa.gov.br/Paginas/{modalidade_slug}.aspx"
            
            # Navegação focada
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("#ulDezenas", timeout=20000)
            
            # Extração
            titulo = page.locator(".title-bar").inner_text()
            dezenas = page.locator("#ulDezenas li").all_inner_texts()
            
            try:
                proximo = page.locator(".next-prize .value").first.inner_text()
            except:
                proximo = "Verificar no site"
                
            return {"titulo": titulo, "dezenas": dezenas, "proximo": proximo}
        except Exception as e:
            return f"Erro: O site da Caixa demorou a responder. Tente novamente. ({str(e)})"
        finally:
            browser.close()

# --- Interface ---
st.title("🎰 Consulta Individual de Loterias")
st.write("Selecione a loteria desejada para uma busca dedicada e estável.")

loterias = {
    "Mega-Sena": "Mega-Sena",
    "Lotofácil": "Lotofacil",
    "Quina": "Quina",
    "Lotomania": "Lotomania",
    "Dupla Sena": "Dupla-Sena",
    "Dia de Sorte": "Dia-de-Sorte",
    "Timemania": "Timemania"
}

# Usando colunas para criar botões de acesso rápido
st.subheader("Qual resultado deseja conferir?")
cols = st.columns(3)

for i, nome in enumerate(loterias.keys()):
    with cols[i % 3]:
        if st.button(f"Ver {nome}", use_container_width=True):
            with st.spinner(f"Acessando {nome}..."):
                res = buscar_loteria_unica(loterias[nome])
                
                if isinstance(res, dict):
                    st.toast(f"Resultado da {nome} carregado!", icon="✅")
                    # Exibição do Card de Resultado
                    with st.container(border=True):
                        st.header(nome)
                        st.caption(res["titulo"])
                        
                        # Dezenas estilizadas
                        bolas = "".join([f'<span style="background-color: #209869; color: white; padding: 8px 15px; border-radius: 50%; margin: 5px; display: inline-block; font-weight: bold; font-size: 20px;">{d}</span>' for d in res["dezenas"] if d.strip()])
                        st.markdown(bolas, unsafe_allow_html=True)
                        
                        st.divider()
                        st.metric("Estimativa Próximo Prêmio", res["proximo"])
                else:
                    st.error(res)

st.divider()
st.info("💡 Consultar uma por vez evita bloqueios de tráfego e garante que os dados carreguem corretamente.")
