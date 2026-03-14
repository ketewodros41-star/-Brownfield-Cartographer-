import os
from typing import Dict, Set, Tuple, List, Any, Optional
import tree_sitter
import tree_sitter_python as tspython


class PythonDataFlowAnalyzer:
    def __init__(self):
        self.language = tree_sitter.Language(tspython.language())
        self.parser = tree_sitter.Parser(self.language)

        self.read_functions = {
            "read_csv",
            "read_parquet",
            "read_sql",
            "read_table",
        }
        self.write_functions = {
            "to_csv",
            "to_parquet",
            "to_sql",
            "to_table",
        }
        self.spark_read_calls = {"csv", "parquet", "table", "json", "orc", "text", "format", "load"}
        self.spark_write_calls = {"csv", "parquet", "table", "json", "orc", "text", "save", "saveAsTable"}

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        if not file_path.endswith(".py"):
            return {"reads": [], "writes": [], "unresolved": []}

        with open(file_path, "rb") as f:
            content = f.read()

        tree = self.parser.parse(content)
        reads: List[Tuple[str, List[int]]] = []
        writes: List[Tuple[str, List[int]]] = []
        unresolved: List[Dict[str, Any]] = []

        for call_node in self._find_calls(tree.root_node):
            call_path = self._get_call_path(call_node, content)
            if not call_path:
                continue
            call_name = ".".join(call_path)

            arg_value = self._get_first_string_arg(call_node, content)

            line_range = [call_node.start_point[0] + 1, call_node.end_point[0] + 1]
            call_type = self._classify_call(call_path)
            if call_type is None:
                continue

            if arg_value:
                # Special-case SQLAlchemy execute: infer read/write by SQL verb.
                if call_path[-1] == "execute":
                    verb = arg_value.strip().lower()
                    if verb.startswith(("insert", "update", "delete", "merge", "create", "drop")):
                        writes.append((arg_value, line_range))
                    else:
                        reads.append((arg_value, line_range))
                elif call_type == "read":
                    reads.append((arg_value, line_range))
                elif call_type == "write":
                    writes.append((arg_value, line_range))
            else:
                unresolved.append({
                    "call": call_name,
                    "line_range": line_range,
                    "reason": "non_literal_or_missing_arg"
                })

        return {"reads": reads, "writes": writes, "unresolved": unresolved}

    def _find_calls(self, node):
        stack = [node]
        while stack:
            current = stack.pop()
            if current.type == "call":
                yield current
            for child in current.children:
                stack.append(child)

    def _get_call_path(self, call_node, content: bytes) -> List[str]:
        func = call_node.child_by_field_name("function")
        if func is None:
            return []
        return self._extract_attr_chain(func, content)

    def _extract_attr_chain(self, node, content: bytes) -> List[str]:
        if node.type == "identifier":
            return [content[node.start_byte:node.end_byte].decode("utf-8")]
        if node.type == "attribute":
            obj = node.child_by_field_name("object")
            attr = node.child_by_field_name("attribute")
            left = self._extract_attr_chain(obj, content) if obj else []
            right = [content[attr.start_byte:attr.end_byte].decode("utf-8")] if attr else []
            return left + right
        return []

    def _get_first_string_arg(self, call_node, content: bytes) -> str:
        args = call_node.child_by_field_name("arguments")
        if args is None:
            return ""

        for child in args.children:
            if child.type == "string":
                raw = content[child.start_byte:child.end_byte].decode("utf-8")
                return self._strip_quotes(raw)

        return ""

    def _classify_call(self, call_path: List[str]) -> Optional[str]:
        if not call_path:
            return None
        last = call_path[-1]

        # Pandas read/write
        if last in self.read_functions:
            return "read"
        if last in self.write_functions:
            return "write"

        # PySpark read/write patterns (spark.read.csv, df.write.parquet, etc.)
        if "read" in call_path and last in self.spark_read_calls:
            return "read"
        if "write" in call_path and last in self.spark_write_calls:
            return "write"

        # SQLAlchemy / generic execute
        if last == "execute":
            return "read"

        return None

    def _strip_quotes(self, raw: str) -> str:
        raw = raw.strip()
        if raw.startswith(("'''", '"""')) and raw.endswith(("'''", '"""')):
            return raw[3:-3]
        if raw.startswith(("'", '"')) and raw.endswith(("'", '"')):
            return raw[1:-1]
        return raw
