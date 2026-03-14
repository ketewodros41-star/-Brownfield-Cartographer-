import yaml
import os
from typing import Dict, List, Any, Set

class DAGConfigParser:
    def __init__(self):
        pass

    def parse_dbt_schema(self, file_path: str) -> Dict[str, Any]:
        """
        Parses dbt schema.yml files to extract model descriptions and relationships.
        """
        with open(file_path, "r") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError:
                return {}

        results = {"models": [], "relationships": []}
        if not data or "models" not in data:
            return results

        for model in data["models"]:
            model_info = {
                "name": model.get("name"),
                "description": model.get("description"),
                "columns": [col.get("name") for col in model.get("columns", [])],
                "tests": []
            }
            results["models"].append(model_info)

            depends_on = model.get("depends_on", {})
            nodes = depends_on.get("nodes", []) if isinstance(depends_on, dict) else []
            for dep in nodes:
                results["relationships"].append({"source": dep, "target": model.get("name")})
        
        return results

    def parse_airflow_dag(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Naive Airflow DAG parser (can be improved with tree-sitter or dynamic analysis).
        For now, looks for operator definitions and bitshift operators.
        """
        try:
            with open(file_path, "r") as f:
                content = f.read()
        except Exception:
            return []

        results: List[Dict[str, Any]] = []

        # Simple pattern for task dependencies using >> or <<
        # Handles: task1 >> task2, task1 >> [task2, task3], [task1, task2] >> task3
        import re
        lines = content.splitlines()
        pattern = re.compile(r"(.+?)\s*(>>|<<)\s*(.+)")

        def _extract_task_names(expr: str) -> List[str]:
            # Strip brackets and split by comma
            expr = expr.strip()
            if expr.startswith("(") and expr.endswith(")"):
                expr = expr[1:-1]
            expr = expr.strip()
            if expr.startswith("[") and expr.endswith("]"):
                expr = expr[1:-1]
            parts = [p.strip() for p in expr.split(",") if p.strip()]
            # Filter to identifier-like tokens
            names = []
            for p in parts:
                m = re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", p)
                if m:
                    names.append(p)
            return names

        for idx, line in enumerate(lines, start=1):
            match = pattern.search(line)
            if not match:
                continue
            left_expr, op, right_expr = match.groups()
            left_tasks = _extract_task_names(left_expr)
            right_tasks = _extract_task_names(right_expr)
            if not left_tasks or not right_tasks:
                continue
            if op == ">>":
                for l in left_tasks:
                    for r in right_tasks:
                        results.append({"source": l, "target": r, "line_range": [idx, idx]})
            else:
                # left << right means right -> left
                for l in left_tasks:
                    for r in right_tasks:
                        results.append({"source": r, "target": l, "line_range": [idx, idx]})

        return results
