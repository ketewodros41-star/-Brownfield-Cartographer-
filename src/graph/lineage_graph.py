import json
from typing import Dict, Any, List, Type, Union, Iterable

import networkx as nx
from pydantic import BaseModel

from src.models.pydantic_schemas import DatasetNode, TransformationNode, Edge, EdgeType, NodeType


class DataLineageGraph:
    """
    Lineage-only graph: Dataset <-> Transformation nodes with edge metadata.
    """

    _NODE_MODEL_BY_TYPE: Dict[NodeType, Type[BaseModel]] = {
        "Dataset": DatasetNode,
        "Transformation": TransformationNode,
    }

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(
        self,
        node_id: str,
        data: Union[BaseModel, Dict[str, Any]],
        node_type: NodeType,
    ):
        model_cls = self._NODE_MODEL_BY_TYPE.get(node_type)
        if model_cls is None:
            raise ValueError(f"Unknown node_type for lineage graph: {node_type}")

        model = data if isinstance(data, BaseModel) else model_cls(**data)
        payload = model.model_dump() if hasattr(model, "model_dump") else model.dict()
        self.graph.add_node(node_id, **payload, node_type=node_type)

    def add_dataset(self, name: str, storage_type: str = "table", **kwargs):
        if name in self.graph:
            return
        payload = {"name": name, "storage_type": storage_type}
        payload.update(kwargs)
        self.add_node(name, payload, "Dataset")

    def add_transformation(
        self,
        transformation_id: str,
        source_datasets: List[str],
        target_datasets: List[str],
        transformation_type: str,
        source_file: str,
        line_range: List[int],
        sql_query_if_applicable: str = None,
        unresolved_references: List[Dict[str, Any]] = None,
    ):
        payload = {
            "source_datasets": source_datasets,
            "target_datasets": target_datasets,
            "transformation_type": transformation_type,
            "source_file": source_file,
            "line_range": line_range,
            "sql_query_if_applicable": sql_query_if_applicable,
            "unresolved_references": unresolved_references,
        }
        self.add_node(transformation_id, payload, "Transformation")

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

    def dataset_nodes(self) -> Iterable[str]:
        for node_id, data in self.graph.nodes(data=True):
            if data.get("node_type") == "Dataset":
                yield node_id

    def blast_radius(self, dataset_name: str, return_paths: bool = False, include_transformations: bool = False):
        if dataset_name not in self.graph:
            return []
        if not return_paths:
            nodes = nx.descendants(self.graph, dataset_name)
            if include_transformations:
                return list(nodes)
            return [n for n in nodes if self.graph.nodes[n].get("node_type") == "Dataset"]

        paths = []
        for target in nx.descendants(self.graph, dataset_name):
            try:
                for path in nx.all_simple_paths(self.graph, dataset_name, target):
                    if not include_transformations:
                        filtered = [p for p in path if self.graph.nodes[p].get("node_type") == "Dataset"]
                    else:
                        filtered = path
                    paths.append({"target": target, "path": filtered})
            except Exception:
                continue
        return paths

    def find_sources(self) -> List[str]:
        return [
            n for n in self.dataset_nodes()
            if self.graph.in_degree(n) == 0
        ]

    def find_sinks(self) -> List[str]:
        return [
            n for n in self.dataset_nodes()
            if self.graph.out_degree(n) == 0
        ]

    def save(self, file_path: str):
        def sanitize(o):
            if isinstance(o, dict):
                return {k: sanitize(v) for k, v in o.items()}
            if isinstance(o, (list, tuple, set)):
                return [sanitize(i) for i in o]
            return o

        data = nx.node_link_data(self.graph)
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

    def merge(self, other: "DataLineageGraph"):
        for node_id, data in other.graph.nodes(data=True):
            if node_id in self.graph:
                self.graph.nodes[node_id].update(data)
            else:
                self.graph.add_node(node_id, **data)
        for u, v, data in other.graph.edges(data=True):
            self.graph.add_edge(u, v, **data)

    def remove_nodes_by_source_files(self, source_files: List[str]):
        to_remove = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get("source_file") in source_files:
                to_remove.append(node_id)
        for node_id in to_remove:
            if node_id in self.graph:
                self.graph.remove_node(node_id)

    def remove_edges_by_source_files(self, source_files: List[str]):
        to_remove = []
        for u, v, data in self.graph.edges(data=True):
            if data.get("source_file") in source_files:
                to_remove.append((u, v))
        for u, v in to_remove:
            if self.graph.has_edge(u, v):
                self.graph.remove_edge(u, v)
