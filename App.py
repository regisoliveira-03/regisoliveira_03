import gradio as gr
from huggingface_hub import InferenceClient
import os

client = InferenceClient(api_key=os.environ.get("HF_TOKEN"))

def analisar_texto_conama(texto):
    termos_busca = {
        "fontes": ["posto", "tanque", "ust", "vazamento", "indústria", "aterro", "resíduos", "efluente"],
        "meios": ["solo", "aquífero", "água subterrânea", "vapor", "zona não saturada", "franja capilar"],
        "receptores": ["residencial", "comercial", "poço", "rio", "trabalhador", "criança", "consumo"]
    }
    encontrados = []
    texto_low = texto.lower()
    for categoria, palavras in termos_busca.items():
        for p in palavras:
            if p in texto_low:
                encontrados.append(p)
    return ", ".join(set(encontrados)) if encontrados else "área contaminada"

def gerar_mca(file):
    if file is None: return None, "⚠️ Envie um .txt"
    try:
        try:
            with open(file.name, "r", encoding="utf-8") as f: conteudo = f.read()
        except:
            with open(file.name, "r", encoding="latin-1") as f: conteudo = f.read()
        
        elementos = analisar_texto_conama(conteudo)
        prompt = (f"Technical 2D environmental engineering cross-section diagram, "
                  f"Conceptual Site Model, Scenario: {elementos}. "
                  f"Geological layers, contamination plume, infographic style, high quality.")

        # MODELO GRATUITO: stabilityai/stable-diffusion-xl-base-1.0
        imagem = client.text_to_image(prompt=prompt, model="stabilityai/stable-diffusion-xl-base-1.0")
        
        return imagem, f"✅ Gerado com sucesso! Elementos: {elementos}"
    except Exception as e:
        return None, f"❌ Erro: {str(e)}"

with gr.Blocks() as demo:
    gr.Markdown("# 🌍 Gerador de MCA (Versão Gratuita)")
    with gr.Row():
        with gr.Column():
            input_file = gr.File(label="Relatório .txt")
            btn = gr.Button("🚀 GERAR DIAGRAMA")
        with gr.Column():
            output_img = gr.Image(label="Diagrama")
            output_text = gr.Textbox(label="Status")
    btn.click(fn=gerar_mca, inputs=input_file, outputs=[output_img, output_text])

demo.launch(theme=gr.themes.Soft())
