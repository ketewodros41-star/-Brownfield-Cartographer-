import json
import networkx as nx
from typing import Dict, Any, List, Type, Union
from pydantic import BaseModel
from src.models.pydantic_schemas import (
    ModuleNode,
    DatasetNode,
    FunctionNode,
    TransformationNode,
    Edge,
    EdgeType,
    NodeType,
)

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    _NODE_MODEL_BY_TYPE: Dict[NodeType, Type[BaseModel]] = {
        "Module": ModuleNode,
        "Dataset": DatasetNode,
        "Function": FunctionNode,
        "Transformation": TransformationNode,
    }

    def add_node(
        self,
        node_id: str,
        data: Union[BaseModel, Dict[str, Any]],
        node_type: NodeType,
    ):
        model_cls = self._NODE_MODEL_BY_TYPE.get(node_type)
        if model_cls is None:
            raise ValueError(f"Unknown node_type: {node_type}")

        model = data if isinstance(data, BaseModel) else model_cls(**data)
        payload = model.model_dump() if hasattr(model, "model_dump") else model.dict()
        self.graph.add_node(node_id, **payload, node_type=node_type)

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: EdgeType,
        metadata: Dict[str, Any] = None,
    ):
        edge = Edge(source=source, target=target, type=edge_type, metadata=metadata or {})
        self.graph.add_edge(edge.source, edge.target, type=edge.type, **edge.metadata)

    def get_node(self, node_id: str) -> Dict[str, Any]:
        return self.graph.nodes[node_id]

    def save(self, file_path: str):
        import datetime
        
        def json_serializable(obj):
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()
            if isinstance(obj, set):
                return list(obj)
            return str(obj)

        data = nx.node_link_data(self.graph)
        # Deeply sanitize the data for JSON
        def sanitize(o):
            if isinstance(o, dict):
                return {k: sanitize(v) for k, v in o.items()}
            if isinstance(o, (list, tuple, set)):
                return [sanitize(i) for i in o]
            if isinstance(o, (datetime.datetime, datetime.date)):
                return o.isoformat()
            return o

        sanitized_data = sanitize(data)
        with open(file_path, "w") as f:
            json.dump(sanitized_data, f, indent=2)



    @classmethod
    def load(cls, file_path: str):
        with open(file_path, "r") as f:
            data = json.load(f)
        kg = cls()
        kg.graph = nx.node_link_graph(data)
        return kg
