import os
from typing import List, Dict, Any
from src.agents.surveyor import Surveyor
from src.agents.hydrologist import Hydrologist
from src.agents.semanticist import Semanticist
from src.agents.archivist import Archivist
from src.graph.knowledge_graph import KnowledgeGraph

class Orchestrator:
    def __init__(self, repo_path: str, output_dir: str = ".cartography"):
        self.repo_path = repo_path
        self.output_dir = output_dir
        self.surveyor = Surveyor(repo_path)
        self.hydrologist = Hydrologist(repo_path)
        self.semanticist = Semanticist()
        self.archivist = Archivist(output_dir)

    def run_analysis(self, incremental: bool = False):
        os.makedirs(self.output_dir, exist_ok=True)
        changed_files = None
        if incremental:
            try:
                last_commit_file = os.path.join(self.output_dir, "last_run_commit")
                head_cmd = ["git", "-C", self.repo_path, "rev-parse", "HEAD"]
                import subprocess
                head = subprocess.run(head_cmd, capture_output=True, text=True).stdout.strip()
                base = "HEAD~1"
                if os.path.exists(last_commit_file):
                    with open(last_commit_file, "r") as f:
                        base = f.read().strip() or base
                cmd = ["git", "-C", self.repo_path, "diff", "--name-only", base, "HEAD"]
                import subprocess
                result = subprocess.run(cmd, capture_output=True, text=True)
                changed_files = [l for l in result.stdout.splitlines() if l.strip()]
            except Exception:
                print("Could not detect changes, running full analysis.")

        self.archivist.log_action("Orchestrator", "Start Analysis", f"Repo: {self.repo_path} (Incremental: {incremental})", 1.0, method="static")


        # 1. Structural Analysis
        print("Running Surveyor...")
        module_graph_path = os.path.join(self.output_dir, "module_graph.json")
        if incremental and os.path.exists(module_graph_path) and changed_files:
            module_kg = KnowledgeGraph.load(module_graph_path)
            # prune changed files
            for path in changed_files:
                if path in module_kg.graph:
                    module_kg.graph.remove_node(path)
        else:
            module_kg = KnowledgeGraph()

        new_module_kg = self.surveyor.analyze(file_filter=changed_files if incremental else None)
        module_kg.merge(new_module_kg)
        module_kg.save(os.path.join(self.output_dir, "module_graph.json"))
        self.archivist.log_action(
            "Surveyor", "structural_analysis",
            f"Analyzed {len(module_kg.graph.nodes)} modules, {len(module_kg.graph.edges)} import edges",
            0.95, method="static",
            source_files=list(module_kg.graph.nodes)[:20],
            details={"module_count": len(module_kg.graph.nodes), "edge_count": len(module_kg.graph.edges)},
        )

        # 2. Lineage Analysis
        print("Running Hydrologist...")
        lineage_graph_path = os.path.join(self.output_dir, "lineage_graph.json")
        if incremental and os.path.exists(lineage_graph_path) and changed_files:
            lineage_kg = KnowledgeGraph.load(lineage_graph_path)
            lineage_kg.remove_nodes_by_source_files(changed_files)
            lineage_kg.remove_edges_by_source_files(changed_files)
        else:
            lineage_kg = KnowledgeGraph()

        new_lineage_kg = self.hydrologist.analyze(file_filter=changed_files if incremental else None)
        lineage_kg.merge(new_lineage_kg)
        lineage_kg.save(os.path.join(self.output_dir, "lineage_graph.json"))
        dataset_count = sum(1 for _, d in lineage_kg.graph.nodes(data=True) if d.get("node_type") == "Dataset")
        transform_count = sum(1 for _, d in lineage_kg.graph.nodes(data=True) if d.get("node_type") == "Transformation")
        self.archivist.log_action(
            "Hydrologist", "lineage_analysis",
            f"Built lineage graph: {dataset_count} datasets, {transform_count} transformations, {len(lineage_kg.graph.edges)} edges",
            0.9, method="static",
            details={"dataset_count": dataset_count, "transformation_count": transform_count, "edge_count": len(lineage_kg.graph.edges)},
        )

        # 3. Semantic Analysis (Mocked or real LLM calls)
        print("Running Semanticist...")
        self._run_semantic_analysis(module_kg)
        module_kg.save(os.path.join(self.output_dir, "module_graph.json"))
        purpose_count = sum(1 for _, d in module_kg.graph.nodes(data=True) if d.get("purpose_statement"))
        drift_count = sum(1 for _, d in module_kg.graph.nodes(data=True) if d.get("docstring_drift", {}).get("severity") not in (None, "none"))
        cluster_labels = set(d.get("domain_cluster") for _, d in module_kg.graph.nodes(data=True) if d.get("domain_cluster"))
        self.archivist.log_action(
            "Semanticist", "semantic_analysis",
            f"Generated {purpose_count} purpose statements, detected {drift_count} drifts, {len(cluster_labels)} domain clusters",
            0.85, method="llm",
            details={
                "purpose_statements": purpose_count,
                "drift_detections": drift_count,
                "cluster_count": len(cluster_labels),
                "token_budget": self.semanticist.budget.summary(),
            },
        )
        context = self._build_day_one_context(module_kg, lineage_kg)
        answers = self.semanticist.answer_day_one_questions(context)
        
        # 4. Archivist (Generate Documentation)
        print("Running Archivist...")
        summary_context = {
            "overview": context.get("overview", "N/A"),
            "critical_modules": context.get("critical_path", []),
            "sources": context.get("data_sources", []),
            "sinks": context.get("data_sinks", []),
            "tech_debt": context.get("tech_debt", []),
            "high_velocity": context.get("high_velocity", []),
            "module_purposes": context.get("module_purposes", []),
        }
        self.archivist.generate_codebase_md(summary_context)
        self.archivist.generate_onboarding_brief(answers)
        self.archivist.log_action(
            "Archivist", "artifact_generation",
            "Generated CODEBASE.md and onboarding_brief.md",
            0.95, method="static",
            details={
                "artifacts": ["CODEBASE.md", "onboarding_brief.md", "cartography_trace.jsonl"],
                "output_dir": self.output_dir,
            },
        )
        self.archivist.log_action("Orchestrator", "Finish Analysis", "All steps completed", 1.0, method="static")
        print("Analysis complete. Artifacts generated in .cartography/")

        if incremental:
            try:
                head_cmd = ["git", "-C", self.repo_path, "rev-parse", "HEAD"]
                import subprocess
                head = subprocess.run(head_cmd, capture_output=True, text=True).stdout.strip()
                with open(os.path.join(self.output_dir, "last_run_commit"), "w") as f:
                    f.write(head)
            except Exception:
                pass

    def _run_semantic_analysis(self, module_kg: KnowledgeGraph):
        for node_id, data in module_kg.graph.nodes(data=True):
            file_path = os.path.join(self.repo_path, node_id)
            if not os.path.exists(file_path):
                continue
            try:
                with open(file_path, "r") as f:
                    content = f.read()
            except Exception:
                continue
            purpose = self.semanticist.generate_purpose_statement(content)
            drift = self.semanticist.detect_docstring_drift(content, purpose)
            data["purpose_statement"] = purpose
            data["docstring_drift"] = drift

        # Embeddings for semantic search (optional, requires embedding client)
        node_ids = []
        texts = []
        for node_id, data in module_kg.graph.nodes(data=True):
            purpose = data.get("purpose_statement") or ""
            if purpose:
                node_ids.append(node_id)
                texts.append(purpose)
        embeddings = self.semanticist.get_embeddings_for_texts(texts) if texts else None
        if embeddings and len(embeddings) == len(node_ids):
            for node_id, vec in zip(node_ids, embeddings):
                if node_id in module_kg.graph:
                    module_kg.graph.nodes[node_id]["purpose_embedding"] = vec

        # Domain clustering
        modules = []
        from src.models.pydantic_schemas import ModuleNode
        for node_id, data in module_kg.graph.nodes(data=True):
            payload = {k: data.get(k) for k in ["path", "language", "purpose_statement", "domain_cluster", "complexity_score", "change_velocity_30d", "is_dead_code_candidate", "docstring_drift"] if k in data}
            if "path" not in payload:
                payload["path"] = node_id
            if "language" not in payload:
                payload["language"] = (node_id.split(".")[-1] if "." in node_id else "")
            modules.append(ModuleNode(**payload))
        clustered = self.semanticist.cluster_into_domains(modules)
        for mod in clustered:
            if mod.path in module_kg.graph:
                module_kg.graph.nodes[mod.path]["domain_cluster"] = mod.domain_cluster

    def _build_day_one_context(self, module_kg: KnowledgeGraph, lineage_kg: KnowledgeGraph) -> Dict[str, Any]:
        # Critical path = top pagerank
        pageranks = []
        for node_id, data in module_kg.graph.nodes(data=True):
            rank = data.get("pagerank", 0.0)
            pageranks.append((node_id, rank))
        pageranks.sort(key=lambda x: x[1], reverse=True)
        critical = []
        for p in pageranks[:5]:
            node_id = p[0]
            lr = module_kg.graph.nodes.get(node_id, {}).get("line_range", [1, 1])
            critical.append(f"{node_id} (evidence: {node_id}:{lr[0]}-{lr[1]}, method: static)")

        high_velocity = []
        for n, d in module_kg.graph.nodes(data=True):
            if d.get("is_high_velocity"):
                lr = d.get("line_range", [1, 1])
                high_velocity.append(f"{n} (evidence: {n}:{lr[0]}-{lr[1]}, method: static)")
        module_purposes = []
        for node_id, data in module_kg.graph.nodes(data=True):
            purpose = data.get("purpose_statement", "")
            domain = data.get("domain_cluster", "")
            if purpose:
                lr = data.get("line_range", [1, 1])
                module_purposes.append(f"{node_id} - {purpose} [{domain}] (evidence: {node_id}:{lr[0]}-{lr[1]}, method: static)")

        tech_debt = []
        for node_id, data in module_kg.graph.nodes(data=True):
            if data.get("is_in_circular_dependency"):
                lr = data.get("line_range", [1, 1])
                tech_debt.append(f"Circular dependency: {node_id} (evidence: {node_id}:{lr[0]}-{lr[1]}, method: static)")
            if data.get("is_dead_code_candidate"):
                lr = data.get("line_range", [1, 1])
                tech_debt.append(f"Dead code candidate: {node_id} (evidence: {node_id}:{lr[0]}-{lr[1]}, method: static)")

        data_sources = []
        for s in self._find_sources(lineage_kg):
            ev = self._dataset_evidence(lineage_kg, s)
            data_sources.append(f"{s} (evidence: {ev})")
        data_sinks = []
        for s in self._find_sinks(lineage_kg):
            ev = self._dataset_evidence(lineage_kg, s)
            data_sinks.append(f"{s} (evidence: {ev})")

        context = {
            "overview": "Automated architecture summary derived from static analysis and lineage graph.",
            "critical_path": critical,
            "data_sources": data_sources,
            "data_sinks": data_sinks,
            "high_velocity": high_velocity,
            "module_purposes": module_purposes,
            "tech_debt": tech_debt,
            "evidence": {
                "modules": [{"file": n.split(" (evidence: ")[0], "line_range": module_kg.graph.nodes.get(n.split(" (evidence: ")[0], {}).get("line_range", [1, 1]), "method": "static"} for n in critical],
                "lineage": [{"file": d.get("source_file", ""), "line_range": d.get("line_range", [1, 1]), "method": "static"}
                            for _, _, d in lineage_kg.graph.edges(data=True)][:20],
            }
        }
        return context

    def _dataset_evidence(self, lineage_kg: KnowledgeGraph, dataset: str) -> str:
        for u, v, d in lineage_kg.graph.edges(data=True):
            if u == dataset or v == dataset:
                sf = d.get("source_file", "")
                lr = d.get("line_range", [1, 1])
                return f"{sf}:{lr[0]}-{lr[1]}, method: static"
        return f"{dataset}:1-1, method: static"

    def _find_sources(self, lineage_kg: KnowledgeGraph) -> List[str]:
        return [n for n in lineage_kg.graph.nodes if lineage_kg.graph.in_degree(n) == 0]

    def _find_sinks(self, lineage_kg: KnowledgeGraph) -> List[str]:
        return [n for n in lineage_kg.graph.nodes if lineage_kg.graph.out_degree(n) == 0]

    def get_navigator(self):
        # Load graphs if they exist
        module_kg = KnowledgeGraph.load(os.path.join(self.output_dir, "module_graph.json"))
        lineage_kg = KnowledgeGraph.load(os.path.join(self.output_dir, "lineage_graph.json"))
        from src.agents.navigator import Navigator
        return Navigator(module_kg, lineage_kg)
