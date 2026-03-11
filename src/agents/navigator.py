from typing import List, Dict, Any, Union
import networkx as nx
from src.graph.knowledge_graph import KnowledgeGraph

class Navigator:
    def __init__(self, module_kg: KnowledgeGraph, lineage_kg: KnowledgeGraph):
        self.module_kg = module_kg
        self.lineage_kg = lineage_kg

    def find_implementation(self, concept: str) -> List[Dict[str, Any]]:
        """
        Uses semantic search over the module index.
        (Placeholder for actual vector store query)
        """
        results = []
        for node, data in self.module_kg.graph.nodes(data=True):
            purpose = data.get("purpose_statement", "")
            if concept.lower() in purpose.lower() or concept.lower() in node.lower():
                results.append({
                    "file": node,
                    "purpose": purpose,
                    "method": "semantic_match"
                })
        return results

    def trace_lineage(self, dataset: str, direction: str = "upstream") -> List[str]:
        """
        Traces data lineage in the given direction.
        """
        if dataset not in self.lineage_kg.graph:
            return []
        
        if direction == "upstream":
            return list(nx.ancestors(self.lineage_kg.graph, dataset))
        else:
            return list(nx.descendants(self.lineage_kg.graph, dataset))

    def blast_radius(self, module_path: str) -> List[str]:
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
            
        return list(impacted)

    def explain_module(self, path: str) -> Dict[str, Any]:
        if path in self.module_kg.graph:
            return self.module_kg.get_node(path)
        return {}

    def query(self, user_query: str) -> str:
        """
        Naive query dispatcher. In a real system, this would be a LangGraph agent.
        """
        # Logic to route user_query to one of the tools above
        return "Query result placeholder"
