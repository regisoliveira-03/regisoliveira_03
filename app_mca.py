import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Modelo Conceitual (MCA)", layout="wide")

# --- CLASSE DE GERAÇÃO DE PDF ---
class MCA_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Relatorio de Modelo Conceitual de Area (MCA) - ABNT NBR 16210', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def gerar_pdf(tipo, respostas, incertezas, imagem_upload):
    pdf = MCA_PDF()
    pdf.add_page()
    
    # Cabeçalho do Relatório
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Etapa: {tipo}", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Data de Emissao: {datetime.date.today().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)

    # Inserção da Imagem (se houver)
    if imagem_upload is not None:
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, "Representacao Grafica da Area / Mapa de Pluma:", ln=True)
        img = Image.open(imagem_upload)
        # Salva temporariamente para o FPDF ler
        temp_path = "temp_mca_img.png"
        img.save(temp_path)
        pdf.image(temp_path, x=10, w=160)
        pdf.ln(10)
        # Remove arquivo temporário após uso
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # Matriz de Dados e Incertezas
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "Corpo do Modelo e Matriz de Incertezas", ln=True, fill=True)
    pdf.ln(2)
    
    for label, texto in respostas.items():
        pdf.set_font("Arial", 'B', 10)
        status = "[INCERTO]" if incertezas[label] else "[CONFIRMADO]"
        pdf.multi_cell(0, 7, f"{label.upper()} {status}:")
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 7, texto if texto.strip() != "" else "Informacao nao preenchida.")
        pdf.ln(3)

    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- INTERFACE DO USUÁRIO (STREAMLIT) ---
st.title("🌱 Gerador de Modelo Conceitual de Área")
st.markdown("""
Este aplicativo auxilia na elaboração do **MCA** conforme as normas **ABNT NBR 15515 e 16210**.
Preencha os dados da etapa atual e gere o relatório PDF com a Matriz de Incertezas.
""")

# Barra Lateral
st.sidebar.header("Configurações do Relatório")
tipo_modelo = st.sidebar.selectbox(
    "Selecione a Etapa:",
    ["Avaliação Preliminar (MCA-P)", 
     "Investigação Confirmatória (MCA-C)", 
     "Investigação Detalhada (MCA-D)", 
     "Plano de Intervenção (MCA-I)"]
)

st.sidebar.divider()
st.sidebar.subheader("🖼️ Representação Gráfica")
imagem_area = st.sidebar.file_uploader("Upload de Mapa, Planta ou Bloco-Diagrama", type=["jpg", "png", "jpeg"])

if imagem_area:
    st.sidebar.image(imagem_area, caption="Visualização do anexo", use_container_width=True)

# Definição das perguntas por tipo de modelo
perguntas_config = {
    "Avaliação Preliminar (MCA-P)": [
        ("Histórico", "Descreva o histórico de uso e ocupação da área."),
        ("Fontes Potenciais", "Quais as fontes potenciais de contaminação identificadas?"),
        ("SQI", "Quais as Substâncias Químicas de Interesse (SQI)?"),
        ("Meio Físico Regional", "Geologia e Hidrogeologia regional esperada.")
    ],
    "Investigação Confirmatória (MCA-C)": [
        ("Confirmação", "Houve valores acima do Valor de Intervenção (VI)?"),
        ("Meios Atingidos", "Quais meios apresentam contaminação (Solo, Água, Vapor)?"),
        ("Litologia Local", "Descrição das camadas de solo identificadas nas sondagens."),
        ("Fluxo Hidrogeológico", "Direção do fluxo e profundidade do nível estático.")
    ],
    "Investigação Detalhada (MCA-D)": [
        ("Delimitação", "Extensão horizontal e vertical das plumas de contaminação."),
        ("Massa de Contaminantes", "Estimativa da massa total de contaminantes na área."),
        ("Vias de Exposição", "Quais vias de exposição estão completas (ex: ingestão, inalação)?"),
        ("Receptores", "Identificação dos bens a proteger e receptores críticos.")
    ],
    "Plano de Intervenção (MCA-I)": [
        ("Metas de Remediação", "Concentrações alvo para a reabilitação da área."),
        ("Técnicas Escolhidas", "Tecnologias de remediação ou medidas de engenharia."),
        ("Monitoramento", "Plano de amostragem para verificar a eficácia da intervenção."),
        ("Incertezas Residuais", "Quais incertezas ainda persistem após o plano?")
    ]
}

# Renderização do Formulário
respostas = {}
incertezas = {}

st.header(f"📝 Dados para: {tipo_modelo}")

for label, help_text in perguntas_config[tipo_modelo]:
    col1, col2 = st.columns([4, 1])
    with col1:
        respostas[label] = st.text_area(label, placeholder=help_text, key=f"txt_{label}")
    with col2:
        st.write("---")
        incertezas[label] = st.checkbox("Dado Incerto", key=f"inc_{label}", help="Marque se esta informação é uma hipótese ou requer mais dados.")

# Ações Finais
st.divider()
c1, c2 = st.columns(2)

with c1:
    if st.button("📊 Analisar Incertezas"):
        total_inc = sum(incertezas.values())
        if total_inc > 0:
            st.warning(f"Atenção: Seu modelo possui {total_inc} ponto(s) de incerteza. Isso é normal em etapas iniciais, mas deve ser reduzido no MCA-D.")
        else:
            st.success("Modelo robusto: Todos os campos foram marcados como confirmados.")

with c2:
    try:
        pdf_bytes = gerar_pdf(tipo_modelo, respostas, incertezas, imagem_area)
        st.download_button(
            label="📥 Baixar Relatório PDF",
            data=pdf_bytes,
            file_name=f"MCA_{tipo_modelo.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}. Tente remover caracteres especiais complexos.")
