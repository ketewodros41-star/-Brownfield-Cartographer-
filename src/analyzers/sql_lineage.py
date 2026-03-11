import sqlglot
from sqlglot import exp
from typing import Set, Dict, List, Optional

class SQLLineageAnalyzer:
    def __init__(self, dialect: str = "generic"):
        self.dialect = dialect

    def extract_lineage(self, sql_content: str) -> Dict[str, Set[str]]:
        """
        Extracts sources and sinks from a SQL query.
        Returns a dict: {"sources": set(), "sinks": set()}
        """
        sources = set()
        sinks = set()
        
        try:
            # Parse the SQL
            expressions = sqlglot.parse(sql_content, read=self.dialect)
            
            for expression in expressions:
                # Find all table references (sources)
                for table in expression.find_all(exp.Table):
                    # Check if it's not a CTE name or part of a sink
                    sources.add(table.name)
                
                # Check for sinks (INSERT, CREATE TABLE AS, etc.)
                if isinstance(expression, (exp.Create, exp.Insert, exp.Update, exp.Delete)):
                    sink_table = expression.find(exp.Table)
                    if sink_table:
                        sinks.add(sink_table.name)
                
                # Handle dbt ref() calls - usually passed as {{ ref('table') }}
                # These might be unparseable by standard sqlglot but we can regex them if needed
                # or assume the orchestrator pre-processes them.
                # For now, let's keep it simple.

            # Remove CTE names from sources (they aren't external sources)
            for expression in expressions:
                ctes = []
                for cte in expression.find_all(exp.CTE):
                    alias = cte.alias_or_name
                    if alias:
                        ctes.append(alias)
                
                sources = sources - set(ctes)

        except Exception as e:
            print(f"Error parsing SQL: {e}")

        return {"sources": sources, "sinks": sinks}

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
        
        return {"sources": sources, "sinks": set()}
