import streamlit as st
import json
from streamlit_agraph import agraph, Node, Edge, Config

# Configuração da página para usar a largura total
st.set_page_config(page_title="Gerador de MCA Online", layout="wide")

# Função para carregar a ontologia do arquivo JSON
@st.cache_data
def load_ontology():
    try:
        with open('MCA_nodes_conection.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Erro: Arquivo 'MCA_nodes_conection.json' não encontrado na raiz.")
        return None

ontology = load_ontology()

if ontology:
    st.title("🛠️ Modelagem Conceitual de Área (MCA)")
    st.markdown("Selecione os elementos da área na barra lateral para gerar o diagrama de grafos.")

    # --- Barra Lateral de Seleção ---
    st.sidebar.header("Configurações do Modelo")
    
    # Agrupando nós por categorias para facilitar a seleção
    categorias = {}
    for nome, dados in ontology['regras_de_conexao'].items():
        cat = dados['categoria']
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append(nome)

    selecionados = []
    st.sidebar.subheader("Elementos Identificados")
    for cat, itens in categorias.items():
        escolhas = st.sidebar.multiselect(f"📁 {cat}", itens)
        selecionados.extend(escolhas)

    # --- Construção do Grafo ---
    nodes = []
    edges = []
    
    # Cores baseadas na categoria (Padrão ambiental)
    cores = {
        "Origem": "#FF4B4B",           # Vermelho (Fonte Primária)
        "Fonte Secundária": "#FF8C00", # Laranja
        "Meio / Fonte": "#F0E68C",      # Amarelo
        "Meio de Transporte": "#3498DB", # Azul
        "Cadeia Trófica": "#9B59B6",    # Roxo
        "Ponto Final de Exposição": "#2ECC71", # Verde
        "Alvo": "#27AE60"              # Verde Escuro
    }

    if selecionados:
        # Criar os Nós
        for item in selecionados:
            cat_item = ontology['regras_de_conexao'][item]['categoria']
            nodes.append(Node(
                id=item, 
                label=item, 
                size=25, 
                color=cores.get(cat_item, "#CCCCCC")
            ))

        # Criar as Arestas (Conexões) apenas entre itens selecionados
        for item in selecionados:
            conexoes_possiveis = ontology['regras_de_conexao'][item]['conecta_with']
            mecanismos = ontology['regras_de_conexao'][item].get('mecanismos', [])
            
            for destino in conexoes_possiveis:
                if destino in selecionados:
                    # Tenta pegar o primeiro mecanismo correspondente ou usa "Transporte"
                    label_aresta = mecanismos[0] if mecanismos else "Migração"
                    edges.append(Edge(
                        source=item, 
                        target=destino, 
                        label=label_aresta,
                        color="#2C3E50"
                    ))

        # --- Configuração Visual do Grafo ---
        config = Config(
            width=1000, 
            height=600, 
            directed=True, 
            nodeHighlightBehavior=True, 
            highlightColor="#F1C40F",
            collapsible=False,
            staticGraph=False # Permite que o usuário arraste os ícones
        )

        # Renderização
        agraph(nodes=nodes, edges=edges, config=config)
        
        # --- Verificação de Via Completa ---
        st.divider()
        st.subheader("Análise de Risco")
        tem_origem = any(ontology['regras_de_conexao'][n]['categoria'] == "Origem" for n in selecionados)
        tem_alvo = any(ontology['regras_de_conexao'][n]['categoria'] in ["Alvo", "Ponto Final de Exposição"] for n in selecionados)
        
        if tem_origem and tem_alvo:
            st.warning("⚠️ Atenção: O modelo contém Fontes e Receptores. Verifique se as conexões no grafo formam uma via completa.")
        else:
            st.info("ℹ️ Adicione Fontes e Receptores para analisar o caminho de exposição.")
    else:
        st.write("Aguardando seleção de itens na barra lateral...")

else:
    st.warning("Carregue a ontologia para iniciar.")
