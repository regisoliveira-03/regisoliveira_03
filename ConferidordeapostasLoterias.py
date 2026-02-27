import streamlit as st
import requests
import urllib3
import re

# Desativa avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def buscar_resultado(loteria, concurso):
    url = f"https://servicebus2.caixa.gov.br/portalloterias/api/{loteria}/{concurso}"
    try:
        # Timeout curto para não travar o app se a Caixa demorar
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

REGRAS_PREMIOS = {
    "megasena": {4: "Quadra", 5: "Quina", 6: "Sena"},
    "lotofacil": {11: "11 Acertos", 12: "12 Acertos", 13: "13 Acertos", 14: "14 Acertos", 15: "15 Acertos"},
    "quina": {2: "Duque", 3: "Terno", 4: "Quadra", 5: "Quina"},
    "lotomania": {0: "Zero Acertos", 15: "15 Acertos", 16: "16 Acertos", 17: "17 Acertos", 18: "18 Acertos", 19: "19 Acertos", 20: "20 Acertos"}
}

st.set_page_config(page_title="Loterias", page_icon="💰")
st.title("🎰 Conferidor de Loterias")

tipo_loteria = st.selectbox("Selecione a Loteria", list(REGRAS_PREMIOS.keys()))
num_concurso = st.number_input("Concurso", min_value=1, value=3000)
input_usuario = st.text_area("Seus números (ex: 01, 02, 03...)")

if st.button("Conferir"):
    if not input_usuario:
        st.error("Digite seus números!")
    else:
        dados = buscar_resultado(tipo_loteria, num_concurso)
        if dados:
            sorteados = [int(n) for n in dados['listaDezenas']]
            meus_nums = [int(n) for n in re.findall(r'\d+', input_usuario)]
            acertos = set(meus_nums).intersection(set(sorteados))
            qtd = len(acertos)
            
            st.write(f"**Resultado oficial:** {sorted(sorteados)}")
            st.metric("Total de Acertos", qtd)
            
            premio = REGRAS_PREMIOS[tipo_loteria].get(qtd)
            if premio:
                st.success(f"🏆 Ganhou: {premio}!")
            else:
                st.info("Não foi dessa vez.")
        else:
            st.error("Não achei esse sorteio. Verifique o número.")
