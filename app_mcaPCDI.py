import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de MCA Profissional", layout="wide")

# --- CLASSE DE GERAÇÃO DE PDF ---
class MCA_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Relatorio de Modelo Conceitual de Area (MCA)', 0, 1, 'C')
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

    # Inserção da Imagem (Representação Gráfica)
    if imagem_upload is not None:
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, "Representacao Grafica do Modelo Conceitual:", ln=True)
        img = Image.open(imagem_upload)
        temp_path = "temp_mca_img.png"
        img.save(temp_path)
        pdf.image(temp_path, x=10, w=160)
        pdf.ln(10)
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # Matriz de Dados
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "Corpo do Modelo e Matriz de Incertezas", ln=True, fill=True)
    pdf.ln(2)
    
    for label, texto in respostas.items():
        pdf.set_font("Arial", 'B', 10)
        status = "[INCERTO]" if incertezas[label] else "[CONFIRMADO]"
        pdf.multi_cell(0, 7, f"{label.upper()} {status}:")
        pdf.set_font("Arial", size=10)
        txt_limpo = texto.encode('latin-1', 'replace').decode('latin-1') if texto else "Informacao nao preenchida."
        pdf.multi_cell(0, 6, txt_limpo)
        pdf.ln(2)

    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- INTERFACE DO USUÁRIO ---
st.title("🌱 Assistente de Modelo Conceitual de Área (MCA)")
st.markdown("Sistema de suporte à decisão em conformidade com as normas ABNT NBR 15515 e 16784.")

# Barra Lateral
st.sidebar.header("Configurações")
tipo_modelo = st.sidebar.selectbox(
    "Selecione a Etapa:",
    ["Avaliação Preliminar (MCA-P)", 
     "Investigação Confirmatória (MCA-C)", 
     "Investigação Detalhada (MCA-D)", 
     "Plano de Intervenção (MCA-I)"]
)

st.sidebar.divider()
st.sidebar.subheader("🖼️ Representação Gráfica")
imagem_area = st.sidebar.file_uploader("Upload de Mapa ou Representação Gráfica", type=["jpg", "png", "jpeg"])

# Dicionário de Perguntas Estruturadas por Norma
perguntas_config = {
    "Avaliação Preliminar (MCA-P)": [
        ("1. Identificação da área", "Localização, denominação, responsável e tipo de atividade atual/pretérita."),
        ("2. Levantamento histórico", "Histórico operacional, atividades potenciais, acidentes e registros de entrevistas."),
        ("3. Inspeção de reconhecimento", "Datas, condições observadas (vazamentos, manchas) e estado de sistemas de drenagem."),
        ("4. Fontes suspeitas de contaminação", "Fontes potenciais/reais, substâncias, resíduos, efluentes e sistemas de armazenamento."),
        ("5. Substâncias químicas de interesse (SQI)", "Lista de substâncias presentes ou historicamente utilizadas."),
        ("6. Uso e ocupação do solo", "Uso atual, pretérito e do entorno (até 250 m). Identificação dos bens a proteger."),
        ("7. Estudo do meio físico", "Geologia, hidrogeologia, fluxo, profundidade do NA e áreas suscetíveis a inundação."),
        ("8. Áreas suspeitas de contaminação", "Definição baseada em histórico/inspeção e associação entre fontes e meios afetados."),
        ("9. Vias potenciais de transporte", "Meios de migração (solo, água, ar) e condições que favorecem o transporte."),
        ("10. Receptores potenciais", "População exposta, fauna, flora e infraestrutura no entorno."),
        ("11. Incertezas e lacunas", "Informações não disponíveis e necessidades de investigação posterior.")
    ],
    "Investigação Confirmatória (MCA-C)": [
        ("1. Meio físico refinado", "Nível de água, sentido/velocidade do fluxo e hidroestratigrafia."),
        ("2. Concentração e distribuição", "Concentrações medidas, distribuição horizontal/vertical e presença de fase livre."),
        ("3. Confirmação das fontes", "Fontes primárias/secundárias confirmadas e mecanismos de liberação."),
        ("4. Mecanismos de migração", "Meios de transporte (água, ar, solo) e mecanismos envolvidos."),
        ("5. Vias de exposição existentes", "Mapeamento de vias completas/potenciais e avaliação preliminar de exposição."),
        ("6. Receptores potenciais e reais", "Identificação de receptores humanos e ecológicos confirmados ou expostos."),
        ("7. Dados analíticos representativos", "Resultados, comparação com VI e consideração de incertezas analíticas."),
        ("8. Localização dos pontos de amostragem", "Relação entre os pontos e as fontes suspeitas (mapa)."),
        ("9. Ferramentas de resposta rápida", "Dados complementares (geofísica, sensores) que indicam plumas."),
        ("10. Incertezas confirmatórias", "Representatividade das amostras e incertezas de métodos."),
        ("11. Representação gráfica atualizada", "Plantas e seções verticais com plumas, fontes, vias e receptores.")
    ],
    "Investigação Detalhada (MCA-D)": [
        ("1. Consolidação e atualização", "Instalações antigas/atuais, fontes confirmadas e medidas já adotadas."),
        ("2. Caracterização do meio físico", "Unidades geológicas, perfis, condutividade hidráulica e mapas potenciométricos."),
        ("3. Propriedades físicas do meio", "Porosidade, granulometria, carbono orgânico e unidades hidroestratigráficas."),
        ("4. Delimitação da contaminação (ZNS e ZS)", "Delimitação H/V no solo, ar do solo e plumas dissolvidas."),
        ("5. Fase Líquida Imiscível (FLI/NAPL)", "Delimitação de FLI, espessura, volume e limites de LNAPL e DNAPL."),
        ("6. Quantificação de massa e volume", "Estimativa de massa de SQI com base na projeção da pluma e porosidade."),
        ("7. Prognósticos da evolução", "Simulação do comportamento das plumas e atingimento de receptores."),
        ("8. Revisão das SQI", "Atualização da lista de substâncias com base nos resultados detalhados."),
        ("9. Vias de exposição e receptores", "Identificação detalhada de vias completas e riscos associados."),
        ("10. Incertezas detalhadas", "Incertezas do meio físico, distribuição de contaminantes e modelagem."),
        ("11. Representação gráfica detalhada", "Mapas potenciométricos, seções verticais e representação 3D.")
    ],
    "Plano de Intervenção (MCA-I)": [
        ("1. Metas de remediação e justificativas", "Metas definidas e justificativas baseadas em riscos avaliados e uso pretendido."),
        ("2. Técnicas de intervenção selecionadas", "Técnicas escolhidas (remediação, engenharia, controle) e justificativa de viabilidade."),
        ("3. Mapa de intervenção", "Representação espacial das medidas para cada SQI em escala apropriada."),
        ("4. Mapa de pontos de conformidade", "Localização dos pontos para verificação das metas e limites de risco."),
        ("5. Plano de monitoramento", "Frequência, parâmetros e indicadores para avaliar o desempenho das medidas."),
        ("6. Cronograma detalhado", "Cronograma físico com marcos intermediários e etapas de aprovação ambiental."),
        ("7. Procedimentos das Medidas Institucionais (MIs)", "Diretrizes operacionais, restrições de uso e procedimentos de fiscalização."),
        ("8. Participação de terceiros", "Responsabilidades e custos caso a operação seja realizada por terceiros."),
        ("9. Integração com o Modelo de Exposição (MCE)", "Unidades de exposição, caminhos, vias de ingresso e somatório de riscos."),
        ("10. Áreas de risco e restrição", "Mapa de risco (níveis inaceitáveis) e mapa de restrição de uso."),
        ("11. Representação espacial das plumas", "Delimitação das fases livre, dissolvida, retida e vapor e áreas críticas."),
        ("12. Premissas e limitações", "Premissas adotadas, incertezas operacionais e limitações técnicas das medidas.")
    ]
}

# Renderização do Formulário
respostas = {}
incertezas = {}

st.header(f"📝 Formulário: {tipo_modelo}")

for label, help_text in perguntas_config[tipo_modelo]:
    col1, col2 = st.columns([4, 1])
    with col1:
        respostas[label] = st.text_area(label, placeholder=help_text, key=f"txt_{label}")
    with col2:
        st.write("---")
        incertezas[label] = st.checkbox("Dado Incerto", key=f"inc_{label}")

# Botões de Ação
st.divider()
c1, c2 = st.columns(2)

with c1:
    if st.button("📊 Verificar Matriz de Incertezas"):
        total_inc = sum(incertezas.values())
        if total_inc > 0:
            st.warning(f"O modelo apresenta {total_inc} ponto(s) de incerteza.")
        else:
            st.success("Informações dadas como confirmadas.")

with c2:
    pdf_bytes = gerar_pdf(tipo_modelo, respostas, incertezas, imagem_area)
    st.download_button(
        label="📥 Gerar e Baixar PDF",
        data=pdf_bytes,
        file_name=f"Relatorio_{tipo_modelo.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
