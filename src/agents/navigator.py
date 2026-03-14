from typing import List, Dict, Any, Union, Optional
import os
import networkx as nx
from src.graph.knowledge_graph import KnowledgeGraph
from langgraph.graph import StateGraph, END
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import openai

class Navigator:
    def __init__(self, module_kg: KnowledgeGraph, lineage_kg: KnowledgeGraph):
        self.module_kg = module_kg
        self.lineage_kg = lineage_kg
        self._embed_client = None
        self._embedding_model = "text-embedding-3-small"
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            self._embed_client = openai.OpenAI(api_key=openai_key)
        self._build_semantic_index()
        self._build_graph()

    def find_implementation(self, concept: str) -> List[Dict[str, Any]]:
        """
        Uses semantic search over the module index.
        Vector similarity via TF-IDF fallback.
        """
        if self._embedding_matrix is not None and self._embed_client:
            query_vec = self._embed_text(concept)
            if query_vec is not None:
                sims = self._cosine_sim(query_vec, self._embedding_matrix)
                top_idx = sims.argsort()[-5:][::-1]
                results = []
                for i in top_idx:
                    node = self._embedding_index_paths[i]
                    data = self.module_kg.graph.nodes[node]
                    results.append(self._with_evidence({
                        "file": node,
                        "purpose": data.get("purpose_statement", ""),
                        "score": float(sims[i]),
                        "method": "vector_embedding",
                    }, node, analysis_method="llm"))
                return results

        if not self._tfidf_matrix is None:
            query_vec = self._vectorizer.transform([concept])
            sims = cosine_similarity(query_vec, self._tfidf_matrix).ravel()
            top_idx = sims.argsort()[-5:][::-1]
            results = []
            for i in top_idx:
                node = self._index_paths[i]
                data = self.module_kg.graph.nodes[node]
                results.append(self._with_evidence({
                    "file": node,
                    "purpose": data.get("purpose_statement", ""),
                    "score": float(sims[i]),
                    "method": "vector_tfidf",
                }, node))
            return results

        # Fallback substring search
        results = []
        for node, data in self.module_kg.graph.nodes(data=True):
            purpose = data.get("purpose_statement", "")
            if concept.lower() in purpose.lower() or concept.lower() in node.lower():
                results.append(self._with_evidence({
                    "file": node,
                    "purpose": purpose,
                    "method": "semantic_match"
                }, node))
        return results

    def trace_lineage(self, dataset: str, direction: str = "upstream") -> List[Dict[str, Any]]:
        """
        Traces data lineage in the given direction.
        """
        if dataset not in self.lineage_kg.graph:
            return [{"error": "dataset_not_found", "dataset": dataset, "message": "Dataset not found in lineage graph.", "analysis_method": "static"}]
        
        nodes = list(nx.ancestors(self.lineage_kg.graph, dataset)) if direction == "upstream" else list(nx.descendants(self.lineage_kg.graph, dataset))
        results = []
        for n in nodes:
            evidence = self._edge_evidence_between(dataset, n) if direction == "downstream" else self._edge_evidence_between(n, dataset)
            results.append({"dataset": n, "evidence": evidence})
        return results

    def blast_radius(self, module_path: str) -> List[Dict[str, Any]]:
        """
        Computes the blast radius of a module change.
        Checks both module imports and data lineage if applicable.
        """
        impacted = set()
        if module_path in self.module_kg.graph:
            impacted.update(nx.descendants(self.module_kg.graph, module_path))
        
        # If it's a data model, check lineage too
        model_name = module_path.split("/")[-1].split(".")[0]
        if model_name in self.lineage_kg.graph:
            impacted.update(nx.descendants(self.lineage_kg.graph, model_name))
        
        if not impacted and module_path not in self.module_kg.graph and model_name not in self.lineage_kg.graph:
            return [{"error": "module_not_found", "module": module_path, "message": "Module or dataset not found in graphs.", "analysis_method": "static"}]

        results = []
        for n in sorted(impacted):
            results.append(self._with_evidence({"node": n, "method": "static"}, n))
        return results

    def explain_module(self, path: str) -> Dict[str, Any]:
        if path in self.module_kg.graph:
            data = self.module_kg.get_node(path)
            return self._with_evidence(data, path)
        return {"error": "module_not_found", "module": path, "message": "Module not found in module graph.", "analysis_method": "static"}

    def query(self, user_query: str) -> str:
        """
        LangGraph-based query router.
        """
        state = self.graph.invoke({"query": user_query})
        return self._format_response(state.get("result"))

    def _build_semantic_index(self):
        texts = []
        paths = []
        embeddings = []
        for node, data in self.module_kg.graph.nodes(data=True):
            purpose = data.get("purpose_statement", "")
            if purpose:
                texts.append(purpose)
                paths.append(node)
                vec = data.get("purpose_embedding")
                if isinstance(vec, list) and vec:
                    embeddings.append(vec)
                else:
                    embeddings.append(None)
        if not texts:
            self._vectorizer = None
            self._tfidf_matrix = None
            self._index_paths = []
            self._embedding_matrix = None
            self._embedding_index_paths = []
            return
        self._vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        self._tfidf_matrix = self._vectorizer.fit_transform(texts)
        self._index_paths = paths

        # Build embedding index when available on all nodes
        if all(isinstance(v, list) and v for v in embeddings):
            try:
                self._embedding_matrix = np.array(embeddings, dtype=float)
                self._embedding_index_paths = paths
            except Exception:
                self._embedding_matrix = None
                self._embedding_index_paths = []
        else:
            self._embedding_matrix = None
            self._embedding_index_paths = []

    def _build_graph(self):
        def router(state: Dict[str, Any]) -> Dict[str, Any]:
            q = state.get("query", "").lower()
            if "explain" in q and any(k in q for k in ["lineage", "upstream", "downstream", "source", "sink"]):
                return {"tool": "chain_lineage_explain"}
            if "explain" in q and any(k in q for k in ["find", "implementation", "where is"]):
                return {"tool": "chain_find_explain"}
            if any(k in q for k in ["blast", "impact", "break", "radius"]):
                return {"tool": "blast"}
            if any(k in q for k in ["lineage", "upstream", "downstream", "source", "sink"]):
                return {"tool": "lineage"}
            if any(k in q for k in ["explain", "what does", "describe"]):
                return {"tool": "explain"}
            return {"tool": "find"}

        def run_find(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": self.find_implementation(state.get("query", ""))}

        def run_lineage(state: Dict[str, Any]) -> Dict[str, Any]:
            q = state.get("query", "").lower()
            direction = "downstream" if "downstream" in q or "impact" in q else "upstream"
            dataset = self._extract_dataset_from_query(state.get("query", ""))
            return {"result": self.trace_lineage(dataset, direction)}

        def run_blast(state: Dict[str, Any]) -> Dict[str, Any]:
            module = self._extract_path_from_query(state.get("query", ""))
            return {"result": self.blast_radius(module)}

        def run_explain(state: Dict[str, Any]) -> Dict[str, Any]:
            module = self._extract_path_from_query(state.get("query", ""))
            return {"result": self.explain_module(module)}

        def run_chain_lineage_explain(state: Dict[str, Any]) -> Dict[str, Any]:
            q = state.get("query", "").lower()
            direction = "downstream" if "downstream" in q or "impact" in q else "upstream"
            dataset = self._extract_dataset_from_query(state.get("query", ""))
            lineage = self.trace_lineage(dataset, direction)
            modules = []
            for item in lineage[:3]:
                if isinstance(item, dict) and "dataset" in item:
                    modules.extend(self._resolve_dataset_to_modules(item["dataset"]))
            explanations = [self.explain_module(m) for m in modules[:3]]
            return {"result": {"lineage": lineage, "explanations": explanations}}

        def run_chain_find_explain(state: Dict[str, Any]) -> Dict[str, Any]:
            found = self.find_implementation(state.get("query", ""))
            paths = [f.get("file") for f in found if isinstance(f, dict) and f.get("file")]
            explanations = [self.explain_module(p) for p in paths[:3]]
            return {"result": {"found": found, "explanations": explanations}}

        graph = StateGraph(dict)
        graph.add_node("router", router)
        graph.add_node("find", run_find)
        graph.add_node("lineage", run_lineage)
        graph.add_node("blast", run_blast)
        graph.add_node("explain", run_explain)
        graph.add_node("chain_lineage_explain", run_chain_lineage_explain)
        graph.add_node("chain_find_explain", run_chain_find_explain)
        graph.add_conditional_edges("router", lambda s: s["tool"], {
            "find": "find",
            "lineage": "lineage",
            "blast": "blast",
            "explain": "explain",
            "chain_lineage_explain": "chain_lineage_explain",
            "chain_find_explain": "chain_find_explain",
        })
        graph.add_edge("find", END)
        graph.add_edge("lineage", END)
        graph.add_edge("blast", END)
        graph.add_edge("explain", END)
        graph.add_edge("chain_lineage_explain", END)
        graph.add_edge("chain_find_explain", END)
        graph.set_entry_point("router")
        self.graph = graph.compile()

    def _extract_dataset_from_query(self, query: str) -> str:
        # naive heuristic: last token
        tokens = query.strip().split()
        return tokens[-1].strip("'\"") if tokens else ""

    def _extract_path_from_query(self, query: str) -> str:
        # naive heuristic: look for token with .py/.sql/.yml
        tokens = query.strip().split()
        for t in tokens:
            if any(ext in t for ext in [".py", ".sql", ".yml", ".yaml"]):
                return t.strip("'\"")
        return tokens[-1].strip("'\"") if tokens else ""

    def _with_evidence(self, payload: Dict[str, Any], path: str, analysis_method: str = "static") -> Dict[str, Any]:
        payload = dict(payload)
        line_range = self._node_line_range(path)
        payload["evidence"] = {
            "file": path,
            "line_range": line_range,
            "method": "static",
            "analysis_method": analysis_method,
        }
        return payload

    def _embed_text(self, text: str) -> Optional[np.ndarray]:
        if not self._embed_client:
            return None
        try:
            response = self._embed_client.embeddings.create(
                model=self._embedding_model,
                input=[text],
            )
            vec = response.data[0].embedding
            return np.array(vec, dtype=float)
        except Exception:
            return None

    @staticmethod
    def _cosine_sim(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        q = query_vec / (np.linalg.norm(query_vec) + 1e-12)
        m = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12)
        return np.dot(m, q)

    def _edge_evidence_between(self, src: str, tgt: str) -> List[Dict[str, Any]]:
        if not self.lineage_kg.graph.has_node(src) or not self.lineage_kg.graph.has_node(tgt):
            return []
        evidence = []
        try:
            path = nx.shortest_path(self.lineage_kg.graph, src, tgt)
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                data = self.lineage_kg.graph.get_edge_data(u, v) or {}
                evidence.append({
                    "file": data.get("source_file", ""),
                    "line_range": data.get("line_range", [1, 1]),
                    "method": "static",
                    "analysis_method": "static",
                })
        except Exception:
            return []
        return evidence

    def _node_line_range(self, node_id: str) -> List[int]:
        if node_id in self.module_kg.graph:
            data = self.module_kg.graph.nodes[node_id]
            lr = data.get("line_range")
            if isinstance(lr, list) and len(lr) == 2:
                return lr
        if node_id in self.lineage_kg.graph:
            data = self.lineage_kg.graph.nodes[node_id]
            lr = data.get("line_range")
            if isinstance(lr, list) and len(lr) == 2:
                return lr
        # Fallback: try any connected edge metadata
        for u, v, d in self.lineage_kg.graph.edges(data=True):
            if u == node_id or v == node_id:
                lr = d.get("line_range")
                if isinstance(lr, list) and len(lr) == 2:
                    return lr
        return [1, 1]

    def _resolve_dataset_to_modules(self, dataset: str) -> List[str]:
        matches = []
        dataset = (dataset or "").lower()
        if not dataset:
            return matches
        for node in self.module_kg.graph.nodes:
            base = node.split("/")[-1].split(".")[0].lower()
            if base == dataset or dataset in base:
                matches.append(node)
        return matches

    def _format_response(self, result: Any) -> str:
        return json.dumps(result, indent=2, default=str)
