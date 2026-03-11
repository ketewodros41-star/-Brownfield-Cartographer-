import os
from typing import Dict, Set, Tuple, List
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

    def analyze_file(self, file_path: str) -> Dict[str, List[Tuple[str, List[int]]]]:
        if not file_path.endswith(".py"):
            return {"reads": [], "writes": []}

        with open(file_path, "rb") as f:
            content = f.read()

        tree = self.parser.parse(content)
        reads: List[Tuple[str, List[int]]] = []
        writes: List[Tuple[str, List[int]]] = []

        for call_node in self._find_calls(tree.root_node):
            func_name = self._get_call_name(call_node, content)
            if not func_name:
                continue

            arg_value = self._get_first_string_arg(call_node, content)
            if not arg_value:
                continue

            line_range = [call_node.start_point[0] + 1, call_node.end_point[0] + 1]
            if func_name in self.read_functions:
                reads.append((arg_value, line_range))
            elif func_name in self.write_functions:
                writes.append((arg_value, line_range))

        return {"reads": reads, "writes": writes}

    def _find_calls(self, node):
        stack = [node]
        while stack:
            current = stack.pop()
            if current.type == "call":
                yield current
            for child in current.children:
                stack.append(child)

    def _get_call_name(self, call_node, content: bytes) -> str:
        func = call_node.child_by_field_name("function")
        if func is None:
            return ""

        if func.type == "identifier":
            return content[func.start_byte:func.end_byte].decode("utf-8")

        if func.type == "attribute":
            # Use the last attribute name (e.g., pd.read_csv -> read_csv)
            attr = func.child_by_field_name("attribute")
            if attr:
                return content[attr.start_byte:attr.end_byte].decode("utf-8")

        return ""

    def _get_first_string_arg(self, call_node, content: bytes) -> str:
        args = call_node.child_by_field_name("arguments")
        if args is None:
            return ""

        for child in args.children:
            if child.type == "string":
                raw = content[child.start_byte:child.end_byte].decode("utf-8")
                return self._strip_quotes(raw)

        return ""

    def _strip_quotes(self, raw: str) -> str:
        raw = raw.strip()
        if raw.startswith(("'''", '"""')) and raw.endswith(("'''", '"""')):
            return raw[3:-3]
        if raw.startswith(("'", '"')) and raw.endswith(("'", '"')):
            return raw[1:-1]
        return raw
