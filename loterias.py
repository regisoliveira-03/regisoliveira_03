import streamlit as st
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Resultados Loterias", page_icon="🎰", layout="wide")

def buscar_loteria_estavel(modalidade_slug):
    with sync_playwright() as p:
        try:
            # Lançamos o navegador
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            # Definimos uma resolução de tela para o site não achar que é celular
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            url = f"https://loterias.caixa.gov.br/Paginas/{modalidade_slug}.aspx"
            
            # 1. Vai até a página e espera o carregamento básico
            page.goto(url, wait_until="load", timeout=60000)
            
            # 2. O PULO DO GATO: Esperar o seletor estar VISÍVEL (state='visible')
            # Aumentamos o tempo para 40 segundos para dar fôlego ao servidor da Caixa
            page.wait_for_selector("#ulDezenas", state="visible", timeout=40000)
            
            # 3. Extração com garantias
            titulo = page.locator(".title-bar").first.inner_text()
            dezenas = page.locator("#ulDezenas li").all_inner_texts()
            
            # Limpa dezenas (remove espaços ou itens vazios)
            dezenas_limpas = [d.strip() for d in dezenas if d.strip().isdigit()]
            
            try:
                # O valor do prêmio às vezes demora mais que as dezenas
                page.wait_for_selector(".next-prize .value", state="visible", timeout=5000)
                proximo = page.locator(".next-prize .value").first.inner_text()
            except:
                proximo = "Acumulado / Ver no site"
                
            return {"titulo": titulo, "dezenas": dezenas_limpas, "proximo": proximo}
        
        except Exception as e:
            return f"O site da Caixa está instável no momento. Detalhe: {str(e)}"
        finally:
            browser.close()

# --- Interface ---
st.title("🎰 Consulta Individual Estável")

loterias = {
    "Mega-Sena": "Mega-Sena",
    "Lotofácil": "Lotofacil",
    "Quina": "Quina",
    "Lotomania": "Lotomania",
    "Dupla Sena": "Dupla-Sena",
    "Dia de Sorte": "Dia-de-Sorte",
    "Timemania": "Timemania"
}

st.write("Escolha uma modalidade abaixo:")
cols = st.columns(4)

# Criamos um local vazio para exibir o resultado logo abaixo dos botões
espaco_resultado = st.empty()

for i, nome in enumerate(loterias.keys()):
    with cols[i % 4]:
        if st.button(f"Ver {nome}", key=nome, use_container_width=True):
            with st.spinner(f"Consultando {nome}..."):
                res = buscar_loteria_estavel(loterias[nome])
                
                with espaco_resultado.container():
                    if isinstance(res, dict):
                        st.success(f"Resultado {nome} obtido!")
                        with st.container(border=True):
                            st.subheader(res["titulo"])
                            
                            # Bolinhas estilizadas
                            bolas_html = "".join([
                                f'<div style="background-color: #209869; color: white; width: 50px; height: 50px; '
                                f'border-radius: 50%; display: flex; align-items: center; justify-content: center; '
                                f'font-weight: bold; font-size: 1.2rem; margin: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">'
                                f'{d}</div>' for d in res["dezenas"]
                            ])
                            st.markdown(f'<div style="display: flex; flex-wrap: wrap;">{bolas_html}</div>', unsafe_allow_html=True)
                            
                            st.divider()
                            st.metric("Estimativa Próximo Prêmio", res["proximo"])
                    else:
                        st.error(res)

st.info("Nota: Aumentamos o tempo de espera para 40 segundos para garantir que os números carreguem mesmo em conexões lentas.")
