import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json

# Configuração da página
st.set_page_config(layout="wide")
st.title("Gerador de MCA Online")

# Carregar sua ontologia
with open('MCA_nodes_connection.json', 'r', encoding='utf-8') as f:
    ontology = json.load(f)

# Sidebar para seleção de itens
st.sidebar.header("Configuração da Área")
fontes_selecionadas = st.sidebar.multiselect("Selecione as Fontes", list(ontology['regras_de_conexao'].keys()))

# Lógica para criar os Nós e Arestas do Grafo
nodes = []
edges = []

for fonte in fontes_selecionadas:
    nodes.append(Node(id=fonte, label=fonte, size=25, color="#ff4d4d")) # Vermelho para fontes
    
    # Adiciona conexões automáticas baseadas no seu JSON
    destinos = ontology['regras_de_conexao'][fonte]['conecta_with']
    for destino in destinos:
        nodes.append(Node(id=destino, label=destino, size=20, color="#3498db")) # Azul para meios
        edges.append(Edge(source=fonte, target=destino, label="Mecanismo"))

# Configuração visual do Grafo
config = Config(width=800, height=600, directed=True, nodeHighlightBehavior=True)

# Renderização
agraph(nodes=nodes, edges=edges, config=config)
