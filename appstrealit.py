import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Calculadora de Risco (QP)", layout="wide")

# --- ESTADO DA SESSÃO (Persistência de dados) ---
if "heubach_data" not in st.session_state:
    st.session_state.heubach_data = []
if "qp_log" not in st.session_state:
    st.session_state.qp_log = []
if "last_refinement_dose" not in st.session_state:
    st.session_state.last_refinement_dose = 0.0
if "last_refinement_source" not in st.session_state:
    st.session_state.last_refinement_source = "Não definido"

# --- LÓGICA DE CÁLCULO ---
Fatores_Deposito = {
    "MILHO": 17.0, 
    "CEREAIS": 9.9, 
    "BETERRABA": 0.03, 
    "CANOLA": 0.11, 
    "OUTRA": 17.0
}

def calcular_qp(dose_ia_ha, dl50, cultura, uso_defletor=False):
    t_dep = Fatores_Deposito.get(cultura.upper(), Fatores_Deposito["OUTRA"])
    if uso_defletor: 
        t_dep /= 10
    
    # Cálculo: QP = (Dose * TDep) / DL50
    qp = (dose_ia_ha * (t_dep / 100)) / dl50
    risco = "ACEITÁVEL" if qp < 50 else "POTENCIAL RISCO"
    cor = "green" if qp < 50 else "red"
    return qp, risco, t_dep, cor

# --- INTERFACE ---
st.title("🛡️ Avaliação de Risco de Poeira (QP)")

tab1, tab2, tab3 = st.tabs(["Fase 1 (Bula)", "Refinamento (Heubach)", "Log Consolidado"])

# --- TAB 1: FASE 1 ---
with tab1:
    st.header("Cálculo Fase 1 - Pior Caso da Bula")
    col1, col2 = st.columns(2)
    with col1:
        dose_bula = st.number_input("Dose g i.a./100kg", min_value=0.0, format="%.4f", step=0.1)
        taxa_sem = st.number_input("Taxa de Semeadura (kg/ha)", min_value=0.0, format="%.2f", step=1.0)
    
    if st.button("Calcular Dose Fase 1"):
        dose_ha = (dose_bula * taxa_sem) / 100
        st.session_state.last_refinement_dose = dose_ha
        st.session_state.last_refinement_source = "FASE 1 (Bula)"
        st.success(f"Dose calculada: {dose_ha:.4f} g i.a./ha")

# --- TAB 2: REFINAMENTO ---
with tab2:
    st.header("Ensaios Heubach")
    with st.expander("Adicionar Novo Ensaio"):
        c1, c2, c3, c4 = st.columns(4)
        amostra_nome = c1.text_input("Amostra")
        teor_ia_ref = c2.number_input("Teor i.a. na Poeira", min_value=0.0, format="%.4f", step=0.01)
        v_heubach_ref = c3.number_input("Valor Heubach", min_value=0.0, format="%.4f", step=0.01)
        dens_sem_ref = c4.number_input("Densidade (kg/ha)", min_value=0.0, format="%.2f", key="dens_ref_input")
        
        if st.button("Logar Ensaio"):
            st.session_state.heubach_data.append({
                "Amostra": amostra_nome, 
                "Teor_ia_poeira": teor_ia_ref, 
                "Valor_heubach": v_heubach_ref, 
                "Densidade_semeadura": dens_sem_ref
            })
            st.rerun()

    if st.session_state.heubach_data:
        df_h = pd.DataFrame(st.session_state.heubach_data)
        st.table(df_h)
        
        col_a, col_b = st.columns(2)
        if col_a.button("Calcular por Pior Caso I.A."):
            max_ia = df_h["Teor_ia_poeira"].max()
            max_dens = df_h["Densidade_semeadura"].max()
            st.session_state.last_refinement_dose = (max_ia * max_dens) / 100
            st.session_state.last_refinement_source = "REFINAMENTO (I.A. Poeira)"
            st.info(f"Dose Refinada: {st.session_state.last_refinement_dose:.4f} g i.a./ha")
            
        if col_b.button("Limpar Ensaios"):
            st.session_state.heubach_data = []
            st.rerun()

# --- SEÇÃO DE CÁLCULO DE QP ---
st.divider()
st.subheader("Cálculo do Quociente de Perigo (QP)")

# Colunas para entrada de dados do QP
c1, c2, c3, c4 = st.columns(4)

# A dose é puxada automaticamente dos cálculos anteriores
dose_final = c1.number_input("Dose i.a./ha", value=st.session_state.last_refinement_dose, format="%.4f")

# CORREÇÃO AQUI: min_value=0.0 e format com mais casas decimais para aceitar 0,0003
dl50_input = c2.number_input("DL50 Contato (µg/abelha)", min_value=0.0, format="%.6f", step=0.0001)

cultura_sel = c3.selectbox("Cultura", list(Fatores_Deposito.keys()))
defletor_on = c4.checkbox("Uso de Defletor?")

if st.button("🔥 CALCULAR QP E REGISTRAR"):
    if dl50_input > 0:
        qp_val, risco_txt, tdep_val, cor_txt = calcular_qp(dose_final, dl50_input, cultura_sel, defletor_on)
        
        # Salva no Log
        log_entry = {
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Cultura": cultura_sel,
            "Dose_ha": round(dose_final, 4),
            "DL50": dl50_input,
            "TDep (%)": tdep_val,
            "QP": round(qp_val, 2),
            "Risco": risco_txt,
            "Fonte": st.session_state.last_refinement_source + (" (c/ Defletor)" if defletor_on else " (s/ Defletor)")
        }
        st.session_state.qp_log.append(log_entry)
        
        # Exibe resultado
        st.markdown(f"### Resultado: :{cor_txt}[{risco_txt}]")
        st.metric("Quociente de Perigo (QP)", f"{qp_val:.2f}", delta=f"{tdep_val}% TDep", delta_color="off")
    else:
        st.error("A DL50 deve ser maior que zero.")

# --- TAB 3: LOG CONSOLIDADO ---
with tab3:
    if st.session_state.qp_log:
        df_log = pd.DataFrame(st.session_state.qp_log)
        st.dataframe(df_log, use_container_width=True)
        
        # Exportação para CSV
        csv_buffer = io.StringIO()
        df_log.to_csv(csv_buffer, index=False, sep=';')
        st.download_button(
            label="📥 Baixar Log em CSV",
            data=csv_buffer.getvalue(),
            file_name=f"relatorio_qp_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        if st.button("Limpar Histórico de QP"):
            st.session_state.qp_log = []
            st.rerun()
    else:
        st.info("Nenhum cálculo registrado ainda.")
