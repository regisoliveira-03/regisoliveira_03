import React, { useCallback } from 'react';
import ReactFlow, { 
  addEdge, 
  Background, 
  Controls, 
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';

// Em produção, carregue o ficheiro MCA_nodes_connection.json via fetch/axios
import ontology from './MCA_nodes_connection.json';

const initialNodes = [
  { 
    id: 'n1', 
    type: 'input', 
    data: { label: 'Tanque', tipo_mca: 'Fonte Primária' }, 
    position: { x: 250, y: 0 },
    style: { border: '2px solid #ff4d4d', borderRadius: '8px', padding: '10px' }
  },
  { 
    id: 'n2', 
    data: { label: 'Solo', tipo_mca: 'Solo (Fonte Secundária)' }, 
    position: { x: 250, y: 150 } 
  },
  { 
    id: 'n3', 
    type: 'output', 
    data: { label: 'Residente', tipo_mca: 'Receptor Humano' }, 
    position: { x: 250, y: 300 },
    style: { border: '2px solid #2ecc71', borderRadius: '8px', padding: '10px' }
  }
];

const VisualizadorMCA = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback((params) => {
    const sourceNode = nodes.find((n) => n.id === params.source);
    const targetNode = nodes.find((n) => n.id === params.target);

    const tipoOrigem = sourceNode.data.tipo_mca;
    const tipoDestino = targetNode.data.tipo_mca;

    // Validação lógica baseada no JSON
    const regrasOrigem = ontology.regras_de_conexao[tipoOrigem];

    if (regrasOrigem && regrasOrigem.conecta_with.includes(tipoDestino)) {
      // Se a conexão for válida, cria a aresta com estilo
      const newEdge = {
        ...params,
        animated: true,
        label: 'Mecanismo: ' + (regrasOrigem.mecanismos[0] || 'Transporte'),
        style: { stroke: '#3498db', strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#3498db' }
      };
      setEdges((eds) => addEdge(newEdge, eds));
    } else {
      alert(`Conexão Inválida: ${tipoOrigem} não se conecta diretamente a ${tipoDestino} conforme as normas técnicas.`);
    }
  }, [nodes, setEdges]);

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#f8f9fa' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background color="#ccc" gap={20} />
        <Controls />
        <MiniMap nodeColor={(n) => (n.type === 'input' ? '#ff4d4d' : '#2ecc71')} />
      </ReactFlow>
    </div>
  );
};

export default VisualizadorMCA;
