import os
from typing import List, Dict, Any, Optional
import tree_sitter
import tree_sitter_python as tspython
import tree_sitter_sql as tssql
import tree_sitter_yaml as tsyaml

class LanguageRouter:
    def __init__(self):
        self.py_language = tree_sitter.Language(tspython.language())
        self.sql_language = tree_sitter.Language(tssql.language())
        self.yaml_language = tree_sitter.Language(tsyaml.language())
        self.parsers = {
            ".py": tree_sitter.Parser(self.py_language),
            ".sql": tree_sitter.Parser(self.sql_language),
            ".yaml": tree_sitter.Parser(self.yaml_language),
            ".yml": tree_sitter.Parser(self.yaml_language),
        }

    def get_parser(self, file_path: str) -> Optional[tree_sitter.Parser]:
        ext = os.path.splitext(file_path)[1].lower()
        return self.parsers.get(ext)

    def get_language(self, file_path: str) -> Optional[tree_sitter.Language]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".py": return self.py_language
        if ext == ".sql": return self.sql_language
        if ext in [".yaml", ".yml"]: return self.yaml_language
        return None

class TreeSitterAnalyzer:
    def __init__(self, repo_root: Optional[str] = None):
        self.router = LanguageRouter()
        self.repo_root = repo_root

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        parser = self.router.get_parser(file_path)
        if not parser:
            return {}

        try:
            with open(file_path, "rb") as f:
                content = f.read()
        except Exception:
            return {}

        try:
            tree = parser.parse(content)
            language = self.router.get_language(file_path)
        except Exception:
            return {}
        
        results = {
            "path": file_path,
            "imports": [],
            "resolved_imports": [],
            "functions": [],
            "classes": [],
            "public_api": [],
            "sql_tables": [],
            "yaml_keys": [],
            "function_signatures": [],
            "class_inheritance": [],
            "decorators": [],
        }

        if file_path.endswith(".py"):
            self._analyze_python(tree, content, results)
        elif file_path.endswith(".sql"):
            self._analyze_sql(tree, content, results)
        elif file_path.endswith((".yaml", ".yml")):
            self._analyze_yaml(tree, content, results)
        
        return results

    def _analyze_python(self, tree, content, results):
        # Queries for Python
        import_query = self.router.py_language.query("""
            (import_from_statement (dotted_name) @import_name)
            (import_statement (dotted_name) @import_name)
        """)
        
        func_query = self.router.py_language.query("""
            (function_definition
                name: (identifier) @func_name
                parameters: (parameters) @params)
        """)
        
        class_query = self.router.py_language.query("""
            (class_definition
                name: (identifier) @class_name
                superclasses: (argument_list)? @bases)
        """)

        decorator_query = self.router.py_language.query("""
            (decorated_definition
                decorator: (decorator) @decorator)
        """)

        # Extract Imports
        captures = import_query.captures(tree.root_node)
        for node, tag in captures:
            results["imports"].append(content[node.start_byte:node.end_byte].decode("utf-8"))

        if self.repo_root:
            for imp in results["imports"]:
                resolved = self._resolve_import(imp)
                if resolved:
                    results["resolved_imports"].append(resolved)

        # Extract Functions
        captures = func_query.captures(tree.root_node)
        for i in range(0, len(captures), 2):
            node, tag = captures[i]
            if tag == "func_name":
                name = content[node.start_byte:node.end_byte].decode("utf-8")
                results["functions"].append(name)
                if not name.startswith("_"):
                    results["public_api"].append(name)
                # Capture parameters as a signature string
                params_node, _ = captures[i + 1]
                params = content[params_node.start_byte:params_node.end_byte].decode("utf-8")
                results["function_signatures"].append(f"{name}{params}")

        # Extract Classes
        captures = class_query.captures(tree.root_node)
        current_class = None
        for node, tag in captures:
            if tag == "class_name":
                current_class = content[node.start_byte:node.end_byte].decode("utf-8")
                results["classes"].append(current_class)
            elif tag == "bases" and current_class:
                bases = content[node.start_byte:node.end_byte].decode("utf-8")
                results["class_inheritance"].append(f"{current_class}{bases}")

        captures = decorator_query.captures(tree.root_node)
        for node, _ in captures:
            results["decorators"].append(content[node.start_byte:node.end_byte].decode("utf-8"))

    def _resolve_import(self, import_name: str) -> str:
        # Resolve dotted import to a local file path if possible
        candidate = import_name.replace(".", os.sep)
        py_path = os.path.join(self.repo_root, f"{candidate}.py")
        init_path = os.path.join(self.repo_root, candidate, "__init__.py")
        if os.path.exists(py_path):
            return os.path.relpath(py_path, self.repo_root)
        if os.path.exists(init_path):
            return os.path.relpath(init_path, self.repo_root)
        return ""

    def _analyze_sql(self, tree, content, results):
        # Extract table identifiers using SQL tree-sitter nodes
        tables = set()
        for node in self._walk(tree.root_node):
            if node.type in {"table_reference", "object_reference", "object_name"}:
                for child in node.children:
                    if child.type == "identifier":
                        tables.add(content[child.start_byte:child.end_byte].decode("utf-8"))
            if node.type == "identifier":
                # Fallback for dialects where tables show as identifiers under from/join
                parent = node.parent
                if parent and parent.type in {"from_clause", "join_clause"}:
                    tables.add(content[node.start_byte:node.end_byte].decode("utf-8"))
        results["sql_tables"] = sorted(tables)

    def _analyze_yaml(self, tree, content, results):
        # Extract key hierarchies from YAML mapping pairs
        key_paths = []
        for pair in self._find_yaml_pairs(tree.root_node):
            key_text = self._yaml_key_text(pair, content)
            if key_text:
                path = self._build_yaml_path(pair, content)
                if path:
                    key_paths.append(path)
        results["yaml_keys"] = sorted(set(key_paths))

    def _walk(self, node):
        stack = [node]
        while stack:
            current = stack.pop()
            yield current
            for child in current.children:
                stack.append(child)

    def _find_yaml_pairs(self, node):
        for current in self._walk(node):
            if current.type in {"block_mapping_pair", "flow_mapping_pair"}:
                yield current

    def _yaml_key_text(self, pair_node, content):
        key_node = pair_node.child_by_field_name("key")
        if not key_node:
            return ""
        return content[key_node.start_byte:key_node.end_byte].decode("utf-8").strip()

    def _build_yaml_path(self, pair_node, content):
        # Walk up through parent mapping pairs to build a path
        parts = []
        current = pair_node
        while current:
            if current.type in {"block_mapping_pair", "flow_mapping_pair"}:
                key_text = self._yaml_key_text(current, content)
                if key_text:
                    parts.append(key_text)
            current = current.parent
        if not parts:
            return ""
        return ".".join(reversed(parts))
