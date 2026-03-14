import sqlglot
from sqlglot import exp
from typing import Set, Dict, List, Optional, Tuple

class SQLLineageAnalyzer:
    def __init__(self, dialect: str = "auto"):
        self.dialect = dialect
        self.dialect_candidates = ["postgres", "bigquery", "snowflake", "duckdb", "spark", "mysql", "sqlite", "ansi"]

    def extract_lineage(self, sql_content: str) -> Dict[str, Set[str]]:
        """
        Extracts sources and sinks from a SQL query.
        Returns a dict: {"sources": set(), "sinks": set()}
        """
        sources = set()
        sinks = set()
        if "{% macro" in sql_content or "{%macro" in sql_content:
            return {"sources": sources, "sinks": sinks, "dialect_used": "jinja_skipped"}

        expressions = []
        dialect_used = "generic"
        try:
            cleaned = self._strip_jinja(sql_content)
            expressions, dialect_used = self._parse_with_dialects(cleaned)

            for expression in expressions:
                # Find all table references (sources)
                for table in expression.find_all(exp.Table):
                    sources.add(self._format_table(table))

                # Check for sinks (INSERT, CREATE TABLE AS, etc.)
                if isinstance(expression, exp.Create):
                    sink_table = self._extract_table_name(expression.this)
                    if sink_table:
                        sinks.add(sink_table)
                elif isinstance(expression, exp.Insert):
                    sink_table = self._extract_table_name(expression.this)
                    if sink_table:
                        sinks.add(sink_table)
                elif isinstance(expression, (exp.Update, exp.Delete)):
                    sink_table = self._extract_table_name(expression.this)
                    if sink_table:
                        sinks.add(sink_table)

            # Remove CTE names from sources (they aren't external sources)
            for expression in expressions:
                ctes = []
                for cte in expression.find_all(exp.CTE):
                    alias = cte.alias_or_name
                    if alias:
                        ctes.append(alias)
                sources = sources - set(ctes)
                sinks = sinks - set(ctes)

        except Exception:
            return {"sources": set(), "sinks": set(), "dialect_used": "parse_error"}

        return {"sources": sources, "sinks": sinks, "dialect_used": dialect_used}

    def analyze_dbt_model(self, sql_content: str) -> Dict[str, Set[str]]:
        """
        Specifically handles dbt models which often use {{ ref(...) }} and {{ source(...) }}
        """
        import re
        sources = set()
        
        # Simple regex for ref and source
        refs = re.findall(r"\{\{\s*ref\(['\"](.+?)['\"]\)\s*\}\}", sql_content)
        srcs = re.findall(r"\{\{\s*source\(['\"].+?['\"]\s*,\s*['\"](.+?)['\"]\)\s*\}\}", sql_content)
        
        sources.update(refs)
        sources.update(srcs)
        
        return {"sources": sources, "sinks": set(), "dialect_used": "dbt_regex"}

    def _parse_with_dialects(self, sql_content: str) -> Tuple[List[exp.Expression], str]:
        if self.dialect and self.dialect != "auto":
            return sqlglot.parse(sql_content, read=self.dialect), self.dialect

        last_error = None
        for dialect in self.dialect_candidates:
            try:
                expressions = sqlglot.parse(sql_content, read=dialect)
                return expressions, dialect
            except Exception as e:
                last_error = e
                continue
        # Fallback to generic
        return sqlglot.parse(sql_content), "default"

    def _strip_jinja(self, sql_content: str) -> str:
        import re
        # Remove Jinja control blocks and expressions
        cleaned = re.sub(r"\{%-?[\s\S]*?-?%\}", " ", sql_content)
        cleaned = re.sub(r"\{\{[\s\S]*?\}\}", " ", cleaned)
        return cleaned

    def _extract_table_name(self, node) -> str:
        if node is None:
            return ""
        if isinstance(node, exp.Table):
            return self._format_table(node)
        # Some nodes wrap a table in a schema or identifier
        if hasattr(node, "this") and isinstance(node.this, exp.Table):
            return self._format_table(node.this)
        return ""

    def _format_table(self, table: exp.Table) -> str:
        if table is None:
            return ""
        parts = []
        catalog = getattr(table, "catalog", None)
        db = getattr(table, "db", None)
        name = getattr(table, "name", None)
        if catalog:
            parts.append(catalog)
        if db:
            parts.append(db)
        if name:
            parts.append(name)
        return ".".join(parts) if parts else ""
