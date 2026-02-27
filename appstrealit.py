import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Calculadora de Risco (QP)", layout="wide")

# --- ESTADO DA SESSÃO (Para manter os dados entre interações) ---
if "heubach_data" not in st.session_state:
    st.session_state.heubach_data = []
if "qp_log" not in st.session_state:
    st.session_state.qp_log = []
if "last_refinement_dose" not in st.session_state:
    st.session_state.last_refinement_dose = None
if "last_refinement_source" not in st.session_state:
    st.session_state.last_refinement_source = ""
if "last_refinement_details" not in st.session_state:
    st.session_state.last_refinement_details = {}

# --- LÓGICA DE CÁLCULO ---
Fatores_Deposito = {
    "MILHO": 17.0, "CEREAIS": 9.9, "BETERRABA": 0.03, "CANOLA": 0.11, "OUTRA": 17.0
}

def calcular_qp(dose_ia_ha, dl50, cultura, uso_defletor=False):
    t_dep = Fatores_Deposito.get(cultura.upper(), Fatores_Deposito["OUTRA"])
    if uso_defletor: t_dep /= 10
    
    qp = (dose_ia_ha * (t_dep / 100)) / dl50
    risco = "ACEITÁVEL" if qp < 50 else "POTENCIAL RISCO"
    cor = "green" if qp < 50 else "red"
    return qp, risco, t_dep, cor

# --- INTERFACE STREAMLIT ---
st.title("🛡️ Avaliação de Risco de Poeira (QP)")

tab1, tab2, tab3 = st.tabs(["Fase 1 (Bula)", "Refinamento (Heubach)", "Log Consolidado"])

# --- TAB 1: FASE 1 ---
with tab1:
    st.header("Cálculo Fase 1 - Pior Caso da Bula")
    col1, col2 = st.columns(2)
    with col1:
        dose_bula = st.number_input("Dose g i.a./100kg", min_value=0.0, format="%.4f")
        taxa_sem = st.number_input("Taxa de Semeadura (kg/ha)", min_value=0.0, format="%.2f")
    
    if st.button("Calcular Dose Fase 1"):
        dose_ha = (dose_bula * taxa_sem) / 100
        st.session_state.last_refinement_dose = dose_ha
        st.session_state.last_refinement_source = "FASE 1"
        st.success(f"Dose calculada: {dose_ha:.4f} g i.a./ha")

# --- TAB 2: REFINAMENTO ---
with tab2:
    st.header("Ensaios Heubach")
    with st.expander("Adicionar Novo Ensaio"):
        c1, c2, c3, c4 = st.columns(4)
        amostra = c1.text_input("Amostra")
        teor_ia = c2.number_input("Teor i.a. na Poeira", min_value=0.0, format="%.4f")
        v_heubach = c3.number_input("Valor Heubach", min_value=0.0, format="%.4f")
        dens_sem = c4.number_input("Densidade (kg/ha)", min_value=0.0, format="%.2f", key="dens_ref")
        
        if st.button("Logar Ensaio"):
            st.session_state.heubach_data.append({
                "Amostra": amostra, "Teor_ia_poeira": teor_ia, 
                "Valor_heubach": v_heubach, "Densidade_semeadura": dens_sem
            })
            st.rerun()

    if st.session_state.heubach_data:
        df_h = pd.DataFrame(st.session_state.heubach_data)
        st.table(df_h)
        
        if st.button("Limpar Ensaios"):
            st.session_state.heubach_data = []
            st.rerun()

        col_a, col_b = st.columns(2)
        if col_a.button("Calcular por Pior Caso I.A."):
            max_ia = df_h["Teor_ia_poeira"].max()
            max_dens = df_h["Densidade_semeadura"].max()
            st.session_state.last_refinement_dose = (max_ia * max_dens) / 100
            st.session_state.last_refinement_source = "REFINAMENTO (I.A.)"
            st.info(f"Dose Refinada: {st.session_state.last_refinement_dose:.4f}")

# --- SEÇÃO DE CÁLCULO DE QP (Global) ---
st.divider()
st.subheader("Cálculo do Quociente de Perigo (QP)")

if st.session_state.last_refinement_dose:
    c1, c2, c3, c4 = st.columns(4)
    dose_atual = c1.number_input("Dose i.a./ha", value=st.session_state.last_refinement_dose, format="%.4f")
    dl50 = c2.number_input("DL50 Contato (µg/abelha)", min_value=0.01, format="%.4f")
    cultura = c3.selectbox("Cultura", list(Fatores_Deposito.keys()))
    defletor = c4.checkbox("Uso de Defletor?")

    if st.button("🔥 CALCULAR QP E REGISTRAR"):
        qp, risco, tdep, cor = calcular_qp(dose_atual, dl50, cultura, defletor)
        
        log_entry = {
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Cultura": cultura, "Dose_ha": round(dose_atual, 4),
            "DL50": dl50, "QP": round(qp, 2), "Risco": risco,
            "Fonte": st.session_state.last_refinement_source + (" (c/ Defletor)" if defletor else "")
        }
        st.session_state.qp_log.append(log_entry)
        st.markdown(f"### Resultado: :{cor}[{risco}] (QP: {qp:.2f})")
else:
    st.warning("Calcule uma Dose na Fase 1 ou Refinamento primeiro.")

# --- TAB 3: LOG ---
with tab3:
    if st.session_state.qp_log:
        df_log = pd.DataFrame(st.session_state.qp_log)
        st.dataframe(df_log, use_container_width=True)
        
        # Exportar CSV
        csv = df_log.to_csv(index=False, sep=';').encode('utf-8')
        st.download_button("📥 Baixar Log CSV", csv, "relatorio_qp.csv", "text/csv")
        
        if st.button("Limpar Tudo"):
            st.session_state.qp_log = []
            st.rerun()
