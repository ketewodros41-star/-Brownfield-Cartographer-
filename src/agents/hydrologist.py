import os
import networkx as nx
from typing import List, Dict, Any
from src.analyzers.sql_lineage import SQLLineageAnalyzer
from src.analyzers.dag_config_parser import DAGConfigParser
from src.analyzers.python_data_flow import PythonDataFlowAnalyzer
from src.graph.knowledge_graph import KnowledgeGraph
from src.models.pydantic_schemas import DatasetNode, TransformationNode

class Hydrologist:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.sql_analyzer = SQLLineageAnalyzer()
        self.dag_parser = DAGConfigParser()
        self.python_flow = PythonDataFlowAnalyzer()
        self.lineage_kg = KnowledgeGraph()

    def analyze(self, file_filter: List[str] = None) -> KnowledgeGraph:
        file_filter_set = set(file_filter or [])
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.repo_path)
                if file_filter_set and rel_path not in file_filter_set:
                    continue

                try:
                    if file.endswith(".sql"):
                        self._analyze_sql_file(file_path, rel_path)
                    elif file.endswith((".yaml", ".yml")) and "schema" in file.lower():
                        self._analyze_yaml_file(file_path, rel_path)
                    elif file.endswith(".py"):
                        self._analyze_python_file(file_path, rel_path)
                except Exception:
                    continue
                
        return self.lineage_kg

    def _analyze_sql_file(self, file_path: str, rel_path: str):
        with open(file_path, "r") as f:
            content = f.read()
        line_count = max(1, len(content.splitlines()))
        
        # dbt specific analysis first
        lineage = self.sql_analyzer.analyze_dbt_model(content)
        if not lineage["sources"]:
            # Fallback to generic SQL lineage
            lineage = self.sql_analyzer.extract_lineage(content)

        model_name = os.path.splitext(os.path.basename(rel_path))[0]
        
        # Add the model as a dataset node
        dataset = DatasetNode(name=model_name, storage_type="table")
        self.lineage_kg.add_node(model_name, dataset, "Dataset")

        # Add transformation node for the SQL file
        transformation_id = f"{rel_path}::sql"
        transformation = TransformationNode(
            source_datasets=list(lineage["sources"]),
            target_datasets=[model_name],
            transformation_type="sql",
            source_file=rel_path,
            line_range=[1, line_count],
            sql_query_if_applicable=content[:2000],
        )
        self.lineage_kg.add_node(transformation_id, transformation, "Transformation")

        # Add sources as dataset nodes and link them
        for source in lineage["sources"]:
            if not source: continue
            if source not in self.lineage_kg.graph:
                self.lineage_kg.add_node(source, DatasetNode(name=source, storage_type="table"), "Dataset")
            self.lineage_kg.add_edge(source, transformation_id, "CONSUMES", {"source_file": rel_path, "transformation_type": "sql", "line_range": [1, line_count], "dialect_used": lineage.get("dialect_used")})
        self.lineage_kg.add_edge(transformation_id, model_name, "PRODUCES", {"source_file": rel_path, "transformation_type": "sql", "line_range": [1, line_count], "dialect_used": lineage.get("dialect_used")})

    def _analyze_yaml_file(self, file_path: str, rel_path: str):
        # Basic dbt schema parsing
        data = self.dag_parser.parse_dbt_schema(file_path)
        for model in data.get("models", []):
            name = model.get("name")
            if name:
                if name not in self.lineage_kg.graph:
                    self.lineage_kg.add_node(name, DatasetNode(name=name, storage_type="table"), "Dataset")
                # Add metadata to existing node if possible
        for rel in data.get("relationships", []):
            src = rel.get("source")
            tgt = rel.get("target")
            if not src or not tgt:
                continue
            if src not in self.lineage_kg.graph:
                self.lineage_kg.add_node(src, DatasetNode(name=src, storage_type="table"), "Dataset")
            if tgt not in self.lineage_kg.graph:
                self.lineage_kg.add_node(tgt, DatasetNode(name=tgt, storage_type="table"), "Dataset")
            # Represent relationship as a transformation node to retain metadata
            transformation_id = f"{rel_path}::yaml::{src}>>{tgt}"
            transformation = TransformationNode(
                source_datasets=[src],
                target_datasets=[tgt],
                transformation_type="yaml",
                source_file=rel_path,
                line_range=[1, 1],
            )
            if transformation_id not in self.lineage_kg.graph:
                self.lineage_kg.add_node(transformation_id, transformation, "Transformation")
            self.lineage_kg.add_edge(src, transformation_id, "CONSUMES", {"source_file": rel_path, "transformation_type": "yaml", "line_range": [1, 1]})
            self.lineage_kg.add_edge(transformation_id, tgt, "PRODUCES", {"source_file": rel_path, "transformation_type": "yaml", "line_range": [1, 1]})

    def _analyze_python_file(self, file_path: str, rel_path: str):
        try:
            with open(file_path, "r") as f:
                line_count = max(1, len(f.read().splitlines()))
        except Exception:
            line_count = 1

        airflow_edges = self.dag_parser.parse_airflow_dag(file_path)
        if airflow_edges:
            for edge in airflow_edges:
                src = edge.get("source")
                tgt = edge.get("target")
                lr = edge.get("line_range", [1, 1])
                if not src or not tgt:
                    continue
                if src not in self.lineage_kg.graph:
                    self.lineage_kg.add_node(src, DatasetNode(name=src, storage_type="task"), "Dataset")
                if tgt not in self.lineage_kg.graph:
                    self.lineage_kg.add_node(tgt, DatasetNode(name=tgt, storage_type="task"), "Dataset")
                transformation_id = f"{rel_path}::airflow::{src}>>{tgt}"
                transformation = TransformationNode(
                    source_datasets=[src],
                    target_datasets=[tgt],
                    transformation_type="airflow",
                    source_file=rel_path,
                    line_range=lr,
                )
                if transformation_id not in self.lineage_kg.graph:
                    self.lineage_kg.add_node(transformation_id, transformation, "Transformation")
                self.lineage_kg.add_edge(src, transformation_id, "CONSUMES", {"source_file": rel_path, "transformation_type": "airflow", "line_range": lr})
                self.lineage_kg.add_edge(transformation_id, tgt, "PRODUCES", {"source_file": rel_path, "transformation_type": "airflow", "line_range": lr})

        flow = self.python_flow.analyze_file(file_path)
        if not flow or (not flow.get("reads") and not flow.get("writes") and not flow.get("unresolved")):
            return

        transformation_id = f"{rel_path}::python"
        transformation = TransformationNode(
            source_datasets=[name for name, _ in flow.get("reads", [])],
            target_datasets=[name for name, _ in flow.get("writes", [])],
            transformation_type="python",
            source_file=rel_path,
            line_range=[1, line_count],
            unresolved_references=flow.get("unresolved"),
        )
        self.lineage_kg.add_node(transformation_id, transformation, "Transformation")

        for name, line_range in flow.get("reads", []):
            if name not in self.lineage_kg.graph:
                self.lineage_kg.add_node(name, DatasetNode(name=name, storage_type="file"), "Dataset")
            self.lineage_kg.add_edge(name, transformation_id, "CONSUMES", {"source_file": rel_path, "transformation_type": "python", "line_range": line_range})

        for name, line_range in flow.get("writes", []):
            if name not in self.lineage_kg.graph:
                self.lineage_kg.add_node(name, DatasetNode(name=name, storage_type="file"), "Dataset")
            self.lineage_kg.add_edge(transformation_id, name, "PRODUCES", {"source_file": rel_path, "transformation_type": "python", "line_range": line_range})

    def blast_radius(self, dataset_name: str, return_paths: bool = False):
        """Find all downstream dependents of a dataset."""
        if dataset_name not in self.lineage_kg.graph:
            return []
        if not return_paths:
            return list(nx.descendants(self.lineage_kg.graph, dataset_name))
        paths = []
        for target in nx.descendants(self.lineage_kg.graph, dataset_name):
            try:
                for path in nx.all_simple_paths(self.lineage_kg.graph, dataset_name, target):
                    paths.append({"target": target, "path": path})
            except Exception:
                continue
        return paths

    def find_sources(self) -> List[str]:
        """Nodes with in-degree 0."""
        return [n for n in self.lineage_kg.graph.nodes if self.lineage_kg.graph.in_degree(n) == 0]

    def find_sinks(self) -> List[str]:
        """Nodes with out-degree 0."""
        return [n for n in self.lineage_kg.graph.nodes if self.lineage_kg.graph.out_degree(n) == 0]
