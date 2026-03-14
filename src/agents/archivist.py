import os
import datetime
import json
from typing import List, Dict, Any, Optional


class Archivist:
    def __init__(self, output_dir: str = ".cartography"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.trace_file = os.path.join(self.output_dir, "cartography_trace.jsonl")

    # ------------------------------------------------------------------ #
    #  Trace Logging                                                      #
    # ------------------------------------------------------------------ #

    def log_action(
        self,
        agent: str,
        operation: str,
        evidence: str,
        confidence: float,
        method: str = "static",
        source_files: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Append a structured JSONL trace entry with full audit metadata."""
        entry: Dict[str, Any] = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent,
            "operation": operation,
            "evidence": evidence,
            "confidence": confidence,
            "method": method,
        }
        if source_files:
            entry["source_files"] = source_files
        if details:
            entry["details"] = details
        with open(self.trace_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    # ------------------------------------------------------------------ #
    #  CODEBASE.md                                                        #
    # ------------------------------------------------------------------ #

    def generate_codebase_md(self, context: Dict[str, Any]):
        """
        Produce a living-context markdown file with:
        * Generation metadata (timestamp, confidence per section)
        * All six required sections
        * A delta summary when a previous CODEBASE.md exists
        """
        path = os.path.join(self.output_dir, "CODEBASE.md")

        # Detect previous artifact for change-aware regeneration
        prev_sections: Dict[str, int] = {}
        if os.path.exists(path):
            prev_sections = self._count_previous_sections(path)

        now = datetime.datetime.now().isoformat()

        lines: List[str] = []
        lines.append("# CODEBASE.md\n")
        lines.append(f"> **Generated:** {now}  ")
        lines.append(f"> **Mode:** automated static + LLM analysis\n")

        # -- Section helpers ------------------------------------------------ #
        def _section(title: str, items: List[str], confidence_hint: str):
            """Write a section with item count and confidence badge."""
            count = len(items)
            conf = self._section_confidence(items, confidence_hint)
            lines.append(f"## {title}")
            lines.append(f"*{count} item(s) - confidence: **{conf}***\n")
            if items:
                for item in items:
                    lines.append(f"- {item}")
            else:
                lines.append("_No data available._")
            lines.append("")

        # -- Architecture Overview ------------------------------------------ #
        overview = context.get("overview", "N/A")
        overview_conf = "high" if overview and overview != "N/A" else "low"
        lines.append("## Architecture Overview")
        lines.append(f"*confidence: **{overview_conf}***\n")
        lines.append(overview + "\n")

        # -- Required sections ---------------------------------------------- #
        _section(
            "Critical Path (Top Modules by PageRank)",
            context.get("critical_modules", []),
            "critical_modules",
        )

        # Data Sources & Sinks side-by-side
        sources = context.get("sources", [])
        sinks = context.get("sinks", [])
        src_conf = self._section_confidence(sources, "sources")
        snk_conf = self._section_confidence(sinks, "sinks")

        lines.append("## Data Sources & Sinks\n")
        lines.append(f"### Sources - *{len(sources)} item(s) - confidence: **{src_conf}***\n")
        for s in sources:
            lines.append(f"- {s}")
        lines.append("")
        lines.append(f"### Sinks - *{len(sinks)} item(s) - confidence: **{snk_conf}***\n")
        for s in sinks:
            lines.append(f"- {s}")
        lines.append("")

        _section(
            "Known Technical Debt",
            context.get("tech_debt", []),
            "tech_debt",
        )
        _section(
            "High-Velocity Files",
            context.get("high_velocity", []),
            "high_velocity",
        )
        _section(
            "Module Purpose Index",
            context.get("module_purposes", []),
            "module_purposes",
        )

        # -- Change Summary (delta vs previous run) ------------------------- #
        if prev_sections:
            lines.append("## Change Summary (vs. previous run)\n")
            cur_sections = {
                "critical_modules": len(context.get("critical_modules", [])),
                "sources": len(sources),
                "sinks": len(sinks),
                "tech_debt": len(context.get("tech_debt", [])),
                "high_velocity": len(context.get("high_velocity", [])),
                "module_purposes": len(context.get("module_purposes", [])),
            }
            lines.append("| Section | Previous | Current | Delta |")
            lines.append("|---|---|---|---|")
            for key, cur in cur_sections.items():
                prev = prev_sections.get(key, 0)
                delta = cur - prev
                sign = "+" if delta > 0 else ""
                lines.append(f"| {key} | {prev} | {cur} | {sign}{delta} |")
            lines.append("")

        # -- Write ---------------------------------------------------------- #
        with open(path, "w") as f:
            f.write("\n".join(lines))

        self.log_action(
            "Archivist",
            "generate_codebase_md",
            f"Wrote {path} with {len(lines)} lines",
            0.95,
            method="static",
            details={
                "sections_written": 6,
                "has_change_summary": bool(prev_sections),
            },
        )

    # ------------------------------------------------------------------ #
    #  Onboarding Brief                                                   #
    # ------------------------------------------------------------------ #

    def generate_onboarding_brief(self, answers: str):
        """
        Produce a structured onboarding_brief.md with:
        * A quick-reference summary table
        * Five clearly separated Day-One question sections
        """
        path = os.path.join(self.output_dir, "onboarding_brief.md")
        now = datetime.datetime.now().isoformat()

        parsed = self._parse_day_one_answers(answers)

        lines: List[str] = []
        lines.append("# Onboarding Brief\n")
        lines.append(f"> **Generated:** {now}  ")
        lines.append("> **Purpose:** Quick-start guide answering the five FDE Day-One questions\n")

        # Quick-reference table
        lines.append("## Quick Reference\n")
        lines.append("| # | Question | Status |")
        lines.append("|---|---|---|")
        for i, (q, a) in enumerate(parsed, start=1):
            status = "[OK] Answered" if a.strip() else "[--] No data"
            lines.append(f"| Q{i} | {q[:80]} | {status} |")
        lines.append("")

        # Full sections
        for i, (question, answer) in enumerate(parsed, start=1):
            lines.append(f"## Q{i}: {question}\n")
            lines.append(answer.strip() if answer.strip() else "_No data available._")
            lines.append("")

        with open(path, "w") as f:
            f.write("\n".join(lines))

        self.log_action(
            "Archivist",
            "generate_onboarding_brief",
            f"Wrote {path} with {len(parsed)} questions",
            0.9,
            method="static",
            details={"questions_answered": sum(1 for _, a in parsed if a.strip())},
        )

    # ------------------------------------------------------------------ #
    #  Private Helpers                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _section_confidence(items: List[str], hint: str) -> str:
        """Derive a confidence label from data completeness."""
        if not items:
            return "low"
        if len(items) >= 3:
            return "high"
        return "medium"

    @staticmethod
    def _count_previous_sections(path: str) -> Dict[str, int]:
        """Count bullet items in each section of the previous CODEBASE.md."""
        section_map: Dict[str, int] = {}
        current_key: Optional[str] = None
        key_mapping = {
            "critical path": "critical_modules",
            "sources": "sources",
            "sinks": "sinks",
            "known technical debt": "tech_debt",
            "high-velocity": "high_velocity",
            "module purpose index": "module_purposes",
        }
        try:
            with open(path, "r") as f:
                for line in f:
                    stripped = line.strip().lower()
                    for marker, key in key_mapping.items():
                        if stripped.startswith("##") and marker in stripped:
                            current_key = key
                            section_map.setdefault(current_key, 0)
                            break
                    if current_key and line.strip().startswith("- "):
                        section_map[current_key] = section_map.get(current_key, 0) + 1
        except Exception:
            pass
        return section_map

    @staticmethod
    def _parse_day_one_answers(answers: str) -> List[tuple]:
        """
        Split a Day-One answers blob into (question, answer) tuples.
        Handles both 'Q1: ...' and 'Q1. ...' prefixes.
        """
        import re
        import json

        # Prefer structured JSON output when available
        try:
            parsed = json.loads(answers)
            if isinstance(parsed, dict) and isinstance(parsed.get("questions"), list):
                results = []
                for item in parsed["questions"]:
                    q = (item.get("question") or "").strip()
                    a = (item.get("answer") or "").strip()
                    if q:
                        results.append((q, a))
                if results:
                    return results
        except Exception:
            pass

        # Try to split on Q-number patterns
        parts = re.split(r"(?=\bQ\d[\.:]\s)", answers)
        results: List[tuple] = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            match = re.match(r"Q\d[\.:]\s*(.+?)[\?\n]", part, re.DOTALL)
            if match:
                question = match.group(1).strip().rstrip("?")
                answer = part[match.end():].strip()
                results.append((question, answer))
            elif results:
                # Continuation of the previous answer
                prev_q, prev_a = results[-1]
                results[-1] = (prev_q, prev_a + "\n" + part)

        # Fallback: if parsing produced nothing, wrap entire text as one answer
        if not results:
            default_questions = [
                "What does this system do at a high level",
                "What are the most critical modules",
                "What are the primary data sources and sinks",
                "Where is the technical debt or risk",
                "What changes frequently and should be watched closely",
            ]
            # Try to split by blank-line-separated paragraphs
            paragraphs = [p.strip() for p in re.split(r"\n{2,}", answers) if p.strip()]
            for i, q in enumerate(default_questions):
                a = paragraphs[i] if i < len(paragraphs) else ""
                results.append((q, a))

        return results

