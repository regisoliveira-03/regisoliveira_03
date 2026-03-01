import streamlit as st
from playwright.sync_api import sync_playwright
import os

st.set_page_config(page_title="Painel Loterias Caixa", page_icon="🎰", layout="wide")

def buscar_resultados():
    modalidades = {
        "Mega-Sena": "Mega-Sena",
        "Lotofácil": "Lotofacil",
        "Quina": "Quina",
        "Lotomania": "Lotomania",
        "Dupla Sena": "Dupla-Sena",
        "Dia de Sorte": "Dia-de-Sorte"
    }
    
    resultados = {}

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            page = context.new_page()

            progresso = st.progress(0)
            status_text = st.empty()

            for i, (nome, slug) in enumerate(modalidades.items()):
                status_text.text(f"Consultando {nome}...")
                url = f"https://loterias.caixa.gov.br/Paginas/{slug}.aspx"
                
                # Sistema de tentativa dupla para evitar o erro de "Falha ao carregar"
                sucesso = False
                for tentativa in range(2): 
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=45000)
                        # Espera especificamente pelas dezenas ou pela classe de erro
                        page.wait_for_selector("#ulDezenas", timeout=15000)
                        
                        concurso = page.locator(".title-bar").inner_text()
                        dezenas = page.locator("#ulDezenas li").all_inner_texts()
                        
                        # Limpa dezenas vazias se houver
                        dezenas = [d for d in dezenas if d.strip()]
                        
                        try:
                            proximo = page.locator(".next-prize .value").first.inner_text()
                        except:
                            proximo = "Acumulado / Ver site"

                        resultados[nome] = {
                            "concurso": concurso,
                            "dezenas": dezenas,
                            "proximo": proximo
                        }
                        sucesso = True
                        break # Sai do loop de tentativa se funcionar
                    except:
                        continue # Tenta de novo se falhar a primeira vez
                
                if not sucesso:
                    resultados[nome] = {"erro": "Site da Caixa não respondeu a tempo."}
                
                progresso.progress((i + 1) / len(modalidades))
            
            status_text.empty()
            progresso.empty()
            return resultados

        except Exception as e:
            return f"Erro Crítico: {str(e)}"
        finally:
            if 'browser' in locals():
                browser.close()

st.title("🎰 Painel Completo de Loterias")

if st.button("🔄 Sincronizar Todos os Resultados"):
    dados = buscar_resultados()
    
    if isinstance(dados, dict):
        # Exibição em cards
        cols = st.columns(2)
        for idx, (nome, info) in enumerate(dados.items()):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.header(nome)
                    if "erro" in info:
                        st.warning(info["erro"])
                        if st.button(f"Tentar {nome} individualmente"):
                             # Lógica simples para re-tentar apenas um poderia ser add aqui
                             pass
                    else:
                        st.caption(info["concurso"])
                        # Renderização das bolas
                        bolas_html = "".join([f'<span style="background-color: #209869; color: white; padding: 6px 12px; border-radius: 50%; margin: 3px; display: inline-block; font-weight: bold; border: 1px solid #146e4b;">{d}</span>' for d in info["dezenas"]])
                        st.markdown(bolas_html, unsafe_allow_html=True)
                        st.write("")
                        st.metric("Estimativa Próximo Prêmio", info["proximo"])
    else:
        st.error(dados)

st.caption("Nota: Se algumas loterias falharem, clique em atualizar novamente. O servidor da Caixa possui limites de conexão.")
