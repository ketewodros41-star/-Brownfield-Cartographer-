import os
import networkx as nx
from typing import List, Dict, Any
from src.analyzers.tree_sitter_analyzer import TreeSitterAnalyzer
from src.graph.knowledge_graph import KnowledgeGraph
from src.models.pydantic_schemas import ModuleNode
import subprocess

class Surveyor:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.analyzer = TreeSitterAnalyzer(repo_root=repo_path)
        self.kg = KnowledgeGraph()

    def analyze(self) -> KnowledgeGraph:
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith((".py", ".sql", ".yaml", ".yml")):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.repo_path)
                    try:
                        analysis = self.analyzer.analyze_file(file_path)
                        if not analysis:
                            continue

                        node = ModuleNode(
                            path=rel_path,
                            language=os.path.splitext(file)[1][1:],
                            change_velocity_30d=self._get_git_velocity(file_path),
                        )

                        self.kg.add_node(rel_path, node, "Module")

                        # Add edges for imports
                        resolved_imports = analysis.get("resolved_imports", [])
                        if resolved_imports:
                            for imp in resolved_imports:
                                self.kg.add_edge(rel_path, imp, "IMPORTS")
                        else:
                            for imp in analysis.get("imports", []):
                                resolved = self._resolve_import(imp)
                                self.kg.add_edge(rel_path, resolved or imp, "IMPORTS")
                    except Exception:
                        # Per-file isolation to keep the pipeline moving
                        continue

        self._compute_graph_metrics()
        return self.kg

    def _get_git_velocity(self, file_path: str) -> int:
        try:
            cmd = ["git", "-C", self.repo_path, "log", "--since='30 days ago'", "--oneline", "--", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
        except Exception:
            return 0

    def _resolve_import(self, import_name: str) -> str:
        # Resolve dotted import to a local file path if possible
        candidate = import_name.replace(".", os.sep)
        py_path = os.path.join(self.repo_path, f"{candidate}.py")
        init_path = os.path.join(self.repo_path, candidate, "__init__.py")
        if os.path.exists(py_path):
            return os.path.relpath(py_path, self.repo_path)
        if os.path.exists(init_path):
            return os.path.relpath(init_path, self.repo_path)
        return ""

    def _compute_graph_metrics(self):
        if len(self.kg.graph.nodes) == 0:
            return
            
        # PageRank for hub detection
        try:
            pagerank = nx.pagerank(self.kg.graph)
            for node, rank in pagerank.items():
                self.kg.graph.nodes[node]["pagerank"] = rank
        except Exception:
            pass

        # Dead code candidates (nodes with 0 in-degree and not entry points)
        # Simplified: nodes with 0 in-degree
        for node in self.kg.graph.nodes:
            if self.kg.graph.in_degree(node) == 0:
                self.kg.graph.nodes[node]["is_dead_code_candidate"] = True

        # Circular dependency detection
        try:
            for component in nx.strongly_connected_components(self.kg.graph):
                if len(component) > 1:
                    for node in component:
                        self.kg.graph.nodes[node]["is_in_circular_dependency"] = True
        except Exception:
            pass

        # 80/20 high-velocity files
        velocities = []
        for node_id, data in self.kg.graph.nodes(data=True):
            velocity = data.get("change_velocity_30d", 0)
            if isinstance(velocity, int) and velocity > 0:
                velocities.append((node_id, velocity))
        velocities.sort(key=lambda x: x[1], reverse=True)
        if velocities:
            cutoff = max(1, int(len(velocities) * 0.2))
            for node_id, _ in velocities[:cutoff]:
                self.kg.graph.nodes[node_id]["is_high_velocity"] = True
